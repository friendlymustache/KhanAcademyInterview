from collections import deque
from user import User 

class Graph:
	def __init__(self, users=None):
		'''
		Manages all users and their relationships to each other.

		Args:
			users (dict): A dict mapping integer user IDs to user objects.
			We use user IDs as keys in case we make future modifications to
			the user class that makes user objects unhashable.
		'''

		# ID to be assigned to the next user created
		self.next_user_id = 1
		self.users = {} if users is None else users

		# A dict mapping the IDs of users contained within distinct
		# connected components to the sizes of said components
		self.cached_component_sizes = None

		# Whether or not we need to update our cache of component sizes
		self.update_cache = True

	def add_edge(self, coach_id, student_id):
		'''
		Adds a coaching relationship between two user objects if it does not
		already exist.

		Args:
			coach_id (int): The id of the User object being set as 
			the coach of the User object with ID student_id.
			student_id (int): The id of the User object being set as a
			student of the abovementioned coach.
		'''
		
		coach = self.lookup_user(coach_id)
		student = self.lookup_user(student_id)

		if coach_id not in student.coached_by:
			student.coached_by.add(coach_id)
			self.update_cache = True
		if student_id not in coach.students:
			coach.students.add(student_id)
			self.update_cache = True


	def remove_edge(self, coach_id, student_id):
		'''
		Removes the coaching relationship between two user objects if it
		exists.

		Args:
			coach_id (int): The id of the User object being set as 
			the coach of the User object with ID student_id.
			student_id (int): The id of the User object being set as a
			student of the abovementioned coach.
		'''

		if coach_id in student.coached_by:
			student.coached_by.remove(coach.id)
			coach.students.pop(student.id)
			self.update_cache = True

	def lookup_user(self, user_id):
		'''
		Looks up a user using the provided id.

		Args:
			user_id (int): The id of the user we're looking up

		Returns:
			The User object corresponding to the passed-in id, or None
			if no such user exists.
		'''

		if user_id in self.users:
			return self.users[user_id]
		return None

	def create_user(self, version, students=None, coached_by=None):
		'''
		Creates and adds a new user with the specified attributes
		to the graph.

		Args:
			version (int): The site version of the new user.
			students (set): The IDs of users who are students of the new user
			coached_by (set): The IDs of users who coach the new user
		'''

		new_id = self.next_user_id
		self.next_user_id += 1
		self.users[new_id] = User(version, new_id, students, coached_by)
		self.update_cache = True

			
	def remove_user(self, user_id):
		'''
		Removes the user with the specified ID from the graph. Fails
		if no user with the specified ID exists in the graph.

		Args:
			user_id (int): The ID of the user being removed.

		Returns:
			True on success, False on failure
		'''

		user = self.lookup_user(user_id)
		if user:
			# Remove user from appropriate adjacency lists
			for student_id in user.students:
				student = self.lookup_user(student_id)
				student.coached_by.remove(user_id)
			for coach_id in user.coached_by:
				coach = self.lookup_user(student_id)
				coach.students.remove(user_id)

			# Remove user from graph
			self.users.pop(user.id)
			self.update_cache = True
			return True
		return False

	def invert_dict(self, dictionary):
		'''
		Inverts a dictionary.

		Args:
			dictionary (dict): A dict to invert.

		Returns:
			A new dict whose keys are the old dict's values and whose values 
			are arrays of keys that mapped to a given value in the original
			dict.
		'''

		new_dict = {}
		for key, value in dictionary.iteritems():
			if value in new_dict:
				new_dict[value].append(key)
			else:
				new_dict[value] = [key]
		return new_dict

	def infect_while_condition(self, root_id, version, condition, num_infected=0, visited=None):
		'''
		Uses a breadth-first traversal to attempt to totally infect the connected
		component containing the user with id <root_id> with version <version>.

		Continues the infection process until the entire component is infected
		or the passed in condition becomes false (whichever comes first).

		Args:
			root_id (int): The ID of the user at which to begin infection
			version (int): The version with which to infect users
			condition (lambda): A lambda function that takes in num_infected as 
			an argument and returns a bool.
			num_infected (int): The number of users that have been infected. 
			Defaults to 0, but can be set to a non-zero value.
			visited (set): A set of user IDs representing infected users.

		Returns:
			The passed in number of infected users plus the number of additional
			users infected during the abovementioned traversal.
		'''

		visited = set() if visited is None else visited
		visited.add(root_id)
		bft_queue = deque([root_id])

		while len(bft_queue) != 0 and condition(num_infected):
			current_user = self.lookup_user(bft_queue.popleft())
			current_user.version = version
			num_infected += 1
			for student_id in current_user.students:
				if student_id not in visited: 
					bft_queue.append(student_id)
					visited.add(student_id)

			for coach_id in current_user.coached_by:
				if coach_id not in visited:
					bft_queue.append(coach_id)
					visited.add(coach_id)

		return (num_infected, visited)

	def total_infection(self, root_id, version):
		'''
		Totally infects the connected component containing the user with ID <root_id>.

		Args:
			root_id (int): The ID of the user at which to begin infection
			version (int): The version used to infect users.

		Returns:
			The number of users infected.
		'''

		condition = lambda num_infected : True
		return self.infect_while_condition(root_id, version, condition)[0]

	def limited_infection_simple(self, target_quantity, version):
		'''
		A simple version of limited infection in which we attempt to totally 
		connected components of the graph -- we stop the infection 
		process once we've infected the target number of users, which may
		occur in the middle of infecting a connected component.

		Args:
			target_quantity (int): The number of users to infect.
			version (int): The version used to infect users.

		Returns:
			The number of users infected.
		'''
		condition = lambda num_infected : num_infected < target_quantity
		visited = set()
		num_infected = 0
		for user_id in self.users:
			if user_id not in visited:
				num_infected, visited = self.infect_while_condition(user_id, version,
				 condition, num_infected, visited)
			if num_infected == target_quantity:
				break
		return num_infected

	def component_size(self, root_id, visited_users=None):
		'''
		Returns the size of the connected component of the graph containing
		the provided root node.

		Args:
			root_id: The ID of a user in the abovementioned component.
			visited_users: A set to be updated with the users visited
			during this method's run.

		Returns:
			The number of users in the connected component.
		'''

		visited_users = set() if visited_users is None else visited_users
		visited_users.add(root_id)
		component_size = 0
		bft_queue = deque([root_id])

		while len(bft_queue) != 0:
			current_user = self.lookup_user(bft_queue.popleft())
			component_size += 1

			for student_id in current_user.students:
				if student_id not in visited_users:
					bft_queue.append(student_id)
					visited_users.add(student_id)

			for coach_id in current_user.coached_by:
				if coach_id not in visited_users:
					bft_queue.append(coach_id)
					visited_users.add(coach_id)

		return component_size

	def get_component_sizes(self):
		'''
		Returns a dict mapping users to the size of the connected component
		that contains them. Each connected component is represented by one
		user and so appears only once. After computing this result once, stores
		it and returns it each time this method is called until a change is
		made to the graph.
		'''

		if not self.update_cache:
			return self.cached_component_sizes

		self.cached_component_sizes = {}
		visited_users = set()
		for user_id in self.users:
			if user_id not in visited_users:
				component_size = self.component_size(user_id, visited_users)	
				self.cached_component_sizes[user_id] = component_size

		self.update_cache = False
		return self.cached_component_sizes

	def get_component_sizes_tuples(self):
		'''
		Returns a list of (user_id, component_size) tuples representing the result of
		get_component_sizes sorted in decreasing order of component size
		'''
		users_and_sizes = self.get_component_sizes().items()
		users_and_sizes.sort(key=lambda id_and_size: -id_and_size[1])

		return users_and_sizes

	def total_infection_multiple(self, roots, version):
		'''
		Totally infects the connected component of the graph containing 
		each user in <roots> with version <version>.

		Args:
			roots (list): A list of IDs of users contained in connected
			components we want to totally infect.
			version (int): The version used to infect users.

		Returns:
			The total number of users infected.
		'''
		num_infected = 0
		for user_id in roots:
			num_infected += self.total_infection(user_id, version)

		return num_infected

	def subsets_to_infect(self, target, epsilon):
		'''
		Dynamic Programming method that returns a 2D list representing the connected
		components to totally infect in order to infect each quantity of users 
		in the range [0, target + epsilon].

		Args:
			target (int): A target number of users to infect.
			epsilon (int): The acceptable bound for error in the number of infected
			users.

		Returns:
			A 2D list whose elements are either tuples or bools. 

			The entry at index i, j represents the existence of some subset
			of the first j components (sorted in order of size) whose sizes
			sum up to i. 

			If the entry is False, then no such subset exists. 
			If the entry is a tuple, then some such subset does exist. 

			The tuple will take the form (elem_included, prev_i, prev_j). 
			elem_included is a bool describing whether or not the jth
			component is included in our solution. prev_i and prev_j together
			represent the indices of some previously-computed solution 
			(prev_i <= i and prev_j < j) that can be extended to obtain 
			our current solution.

			If prev_i and prev_j are None, then our solution is either
			the jth component (if elem_incuded is True) or the empty set
			(if elem_included is False)		
		'''	

		# Get a list of tuples of the form (user_id, component_size)
		users_and_sizes = self.get_component_sizes_tuples()
		num_components = len(users_and_sizes)

		# Initialize all solutions to False (impossible)
		num_rows = target + epsilon + 1
		num_cols = num_components + 1
		partial_sols = [[False] * num_cols for i in range(num_rows)]

		# The empty set gives us a sum of 0
		for j in range(num_components + 1):
			partial_sols[0][j] = (False, None, None)

		for i in range(1, target + 1):
			for j in range(1, num_components + 1):
				current_size = users_and_sizes[j - 1][1]

				# Check if some subset of the first j - 1 components sum up to i
				if partial_sols[i][j - 1]:
					prev_solution = partial_sols[i][j - 1]
					new_solution = (False, i, j - 1)
					partial_sols[i][j] = new_solution

				# Check if some subset of the first j - 1 components sum up to
				# i - (size of jth component)
				elif i >= current_size and partial_sols[i - current_size][j - 1]:
					prev_solution = partial_sols[i - current_size][j - 1]
					new_solution = (True, i - current_size, j - 1)
					partial_sols[i][j] = new_solution
		return partial_sols

	def extract_solution(self, solution_table, target_quantity):
		'''
		Given a solution table resulting from subsets_to_infect and 
		a target number of infected users, reads through the solution
		table and assembles a list of components that can be
		totally infected in order to infect the target number of users.

		Args:
			solution_table (list): A 2D list that is the result of calling
			subsets_to_infect.
			target_quantity (int): The desired number of users to infect.

		Returns:
			A list of user ids - each referenced user is contained in a
			distinct connected component that should be infected in order to
			infect a total of <target_quantity> users.

			If such a solution does not exist, returns False.
		'''

		users_and_sizes = self.get_component_sizes_tuples()
		components = map(lambda component: component[0], users_and_sizes)
		num_components = len(components)

		i = target_quantity
		j = num_components

		if not solution_table[i][j]:
			return False

		to_infect = []
		while solution_table[i][j] != (False, None, None):
			elem_included, prev_i, prev_j = solution_table[i][j]
			if elem_included:
				to_infect.append(components[j - 1])
			i = prev_i
			j = prev_j
		return to_infect


	def _approximate_infection(self, target_quantity, epsilon):
		'''
		Returns a list of user ids - each referenced user is contained in a
		distinct connected component that should be totally infected. We
		return the list of ids that results in the infection of a number 
		of users as close to <target_quantity> as possible.

		If we can't infect any quantities within target_quantity +/- epsilon via the
		total infection of some number of connected components, return False.

		Args:
			target_quantity (int): The desired number of users to infect.
			epsilon (int): The acceptable range of error in the number of users we
			infect -- we consider a solution acceptable if it infects some number
			of users in the range target_quantity +- epsilon.

		Returns:
			A list of user ids if a valid infection is possible, False otherwise.
		'''
		solution_table = self.subsets_to_infect(target_quantity, epsilon)
		for i in range(epsilon + 1):
			lower_target = target_quantity - epsilon
			upper_target = target_quantity + epsilon

			lower_sol = self.extract_solution(solution_table, lower_target)
			if lower_sol != False:
				return lower_sol

			upper_sol = self.extract_solution(solution_table, upper_target)
			if upper_sol != False:
				return upper_sol
		return False

	def approximate_infection(self, version, target_quantity, epsilon=None):

		'''
		Attempts to infect a number of users as close to a target quantity
		as possible by totally infecting some number of connected components.
		Our margin for error away from our target_quantity is given by 
		epsilon. 

		This is a form of limited infection in which we only totally-infect
		components and seek to get as close to our target quantity as possible.


		Args:
			version (int): The version with which we infect users

			target_quantity (int): The desired number of infected users

			epsilon (int): Indicates how strictly we want to enforce our
			constraint on the number of infected users - we consider a 
			solution valid if it infects any number of users in the range
			target_quantity +- epsilon. 


		Returns:
			The number of infected users if it is possible to infect an
			acceptable number of users, False otherwise.

		'''
		if epsilon is None:
			epsilon = target_quantity

		solution = self._approximate_infection(target_quantity, epsilon)
		# If we found a valid solution, perform total infection on the necessary
		# components. Otherwise, return False.
		if solution != False:
			return self.total_infection_multiple(solution, version)
		return False


	def exact_infection(self, target_quantity, version):
		'''
		Runs approximate infection with a tolerance of 0 (i.e. we either
		infect exactly the target amount or nobody) and returns the result.

		Args:
			target_quantity (int): The number of users to infect.
			version (int): The version used to infect users.

		Returns:
			The number of infected users if a solution was found, False
			otherwise.
		'''
		return self.approximate_infection(version, target_quantity, 0)
