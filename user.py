class User:
	def __init__(self, version, user_id, students=None, coached_by=None):
		'''
		Creates a new user object using the passed in version.
		Stores adjacent students (people being coached by the current user)
		and coaches (people who coach the current user) in two adjacency
		dicts.
		'''

		self.id = user_id
		self.students = {} if students is None else students
		self.coached_by = {} if coached_by is None else coached_by	
		self.version = version


	def limited_infection_imperfect(self, version, target_quantity):
		'''
		Infects target quantity even if some student/coach pairs do not have
		the same version of the site.
		'''

		# Ensure that we're not trying to infect more users than there are
		assert(target_quantity <= len(self.users))

		epsilon = target_quantity
		# Get a list of possible solutions to our limited infection problem.
		solutions = self._limited_infection(target_quantity, epsilon)

		# We pick the solution that gives us a quantity of infected users closest
		# to our target quantity
		for i in range(target_quantity):
			current_quantity = target_quantity - i
			if current_quantity in solutions:
				solution = solutions[current_quantity]
				closest_quantity = current_quantity
				break

		# Infect all of the users in our selected components
		self.total_infection_multiple(solution)

		# If we infected the right number of users, return
		to_infect = target_quantity - closest_quantity
		if to_infect == 0:
			return

		# We have a way to infect <closest_quantity> users by totally infecting
		# connected components, so we must partially infect some other connected
		# component in order to infect the remaining <to_infect> elements. 
		# We choose to infect the component of minimal size containing at least
		# <to_infect> users.
		
		all_component_sizes = self.get_component_sizes()
		component_sizes = {}

		# Filter out all connected components involved in our solution -- we can
		# only partially infect a component we haven't already totally infected
		for user_id, size in all_component_sizes.iteritems():
			if user_id not in solution:
				component_sizes[user_id] = size

		# Pick the component of minimal size containing at least <to_infect>
		# users and infect <to_infect> users of that  component
		size_to_component = self.invert_dict(component_sizes)
		sorted_sizes = sorted(size_to_component.keys())
		candidate_sizes = filter(lambda size: size >= to_infect)

		# There should be at least one connected component that...aghh
		assert(len(candidate_sizes) > 0)


		if len(candidate_sizes) > 0:
			optimal_size = candidate_sizes[0]
			target_components = size_to_component[optimal_size]
			target_component = random.choice(target_components)

			return partial_infection(target_component, to_infect, version)