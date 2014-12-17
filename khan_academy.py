from collections import deque
from user import User 
import random
import copy
# NOTE:
# Need size of each connected component, not just 
# size of adjacency list of each node


class Graph:
	def __init__(self, users=None):
		'''
		self.users - a dict that maps user ids to users
		'''
		self.max_id = 0
		self.users = {} if users is None else users

	def add_edge(self, coach, student):
		'''
		Adds a coaching relationship between the user objects
		<coach> and <student> if it does not already exist
		'''
		if coach.id not in student.coached_by:
			student.coached_by[coach.id] = coach
		if student.id not in coach.students:
			coach.students[student.id] = student

	def remove_edge(self, coach, student):
		'''
		Removes the coaching relationship (if it exists)
		between the user objects <coach> and <student>
		'''
		if coach.id in student.coached_by:
			student.coached_by.pop(coach.id)
			coach.students.pop(student.id)

	def lookup_user(self, user_id):
		'''
		Looks up a user using the provided user-id. Returns None
		if no user is found
		'''
		if user_id in self.users:
			return self.users[user_id]
		return None

	def create_user(self, version, coaches=None, coached_by=None):
		'''
		Creates and adds a new user with the specified attributes
		to the graph 
		'''
		new_id = self.max_id + 1 
		self.max_id += 1
		self.users[new_id] = User(version, new_id, coaches, coached_by)

			
	def remove_user(self, user):
		'''
		Removes a user (if it's part of the graph) from the graph.
		'''
		if self.lookup_user(user.id):
			# Remove user from appropriate adjacency lists
			for student in user.students:
				student.coached_by.pop(user)
			for coach in user.coached_by:
				coach.students.pop(user)

			# Remove user from graph
			self.users.pop(user.id)
			return True
		return False

	def invert_dict(self, dictionary):
		'''
		Inverts a dictionary -- returns a new dict whose keys 
		are the old dict's values and whose values are arrays
		of keys that mapped to a given value in the original
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
		Uses a breadth-first traversal to totally infect the connected
		component containing the user <root> with version <version>.

		Continues the infection process until the entire component is infected
		or the passed in condition becomes false (whichever comes first)
		'''

		# Dict of visited users - used to avoid revisiting users
		visited = {} if visited is None else visited
		visited[root_id] = 1
		bft_queue = deque([root_id])

		while len(bft_queue) != 0 and condition(num_infected):
			current_user = self.lookup_user(bft_queue.popleft())
			current_user.version = version
			num_infected += 1
			for student in current_user.students:
				if student not in visited: 
					bft_queue.append(student)
					visited[student] = 1

			for coach in current_user.coached_by:
				if coach not in visited:
					bft_queue.append(coach)
					visited[coach] = 1

		return (num_infected, visited)

	def total_infection(self, root_id, version):
		'''
		Uses a breadth-first traversal to totally infect the subgraph containing
		the user <root> by setting the version attribute of all users in said
		subgraph to <version>.
		'''

		condition = lambda num_infected : True
		return self.infect_while_condition(root_id, version, condition)[0]

	def limited_infection_simple(self, target_quantity, version):
		'''
		A simple version of limited infection in which we attempt to totally 
		connected components of the graph -- we stop the infection 
		process once we've infected the target number of users, which may
		occur in the middle of infecting a connected component.
		'''
		condition = lambda num_infected : num_infected < target_quantity
		visited = {}
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
		the provided root node
		'''

		visited_users = {} if visited_users is None else visited_users
		visited_users[root_id] = 1
		component_size = 0
		bft_queue = deque([root_id])

		while len(bft_queue) != 0:
			current_user = self.lookup_user(bft_queue.popleft())
			component_size += 1

			for student_id in current_user.students:
				if student_id not in visited_users:
					bft_queue.append(student_id)
					visited_users[student_id] = 1

			for coach_id in current_user.coached_by:
				if coach_id not in visited_users:
					bft_queue.append(coach_id)
					visited_users[coach_id] = 1

		return component_size

	def get_component_sizes(self):
		'''
		Returns a dict mapping users to the size of the connected component
		that contains them. Each connected component is represented by one
		user and so appears only once.
		'''
		user_to_size = {}
		visited_users = {}
		for user_id in self.users:
			if user_id not in visited_users:
				component_size = self.component_size(user_id, visited_users)	
				user_to_size[user_id] = component_size
		return user_to_size


	def total_infection_multiple(self, roots, version):
		'''
		Totally infects the connected component of the graph containing 
		each user in <roots> with version <version>.
		'''
		num_infected = 0
		for user_id in roots:
			num_infected += self.total_infection(user_id, version)

		return num_infected

	def subsets_to_infect(self, target, epsilon):
		'''
		Dynamic programming algorithm to determine which quantities
		of infected users in the range [0, target + epsilon] can 
		be obtained by totally infecting some set of connected
		components.

		Returns a dict mapping various integer sizes to lists of sets
		of components that could be infected in order to infect a given
		number of users.

		Output is sorted in increasing value of offset from target quantity.
		'''

		users_to_sizes = self.get_component_sizes()
		sizes_to_users = self.invert_dict(users_to_sizes)

		# partial_sols maps each quantity in the range [0, target + epsilon]
		# to a list of dictionaries. Each dictionary in the list corresponding
		# to quantity q consists of user_ids whose connected components have
		# sizes that sum up to q.

		# We start off with the solution for the quantity 0 - there
		# is one solution, consisting of an empty set of components, so we
		# have a single-element list consisting of an empty dict.
		partial_sols = {0: [{}] }

		print "Getting data for range 1 through %s"%(target + epsilon)
		for i in range(1, target + epsilon + 1):
			print "--------Finding solutions for infecting %s users-----------"%i
			possible_ways = []
			for j in range(i):
				difference = i - j


				# Get all sets of components with sizes adding up to j
				candidate_solutions = partial_sols[j]
				print "Extending %s solutions for infecting %s users"%(len(candidate_solutions), j)


				# Get all components with size i - j
				if difference in sizes_to_users:
					candidates = sizes_to_users[difference]
				else:
					candidates = []

				print "# of components of size %s: %s"%(difference, len(candidates))
				
				# Extend each solution in <candidate_solutions> by adding
				# an element of <candidates> if said element is not already
				# in the solution being considered
				for solution in candidate_solutions:
					for candidate in candidates:
						if candidate not in solution:
							new_solution = copy.deepcopy(solution)
							new_solution[candidate] = 1
							possible_ways.append(new_solution)

			partial_sols[i] = possible_ways
		return partial_sols


	def _approximate_infection(self, target_quantity, epsilon):
		'''
		Returns the list of solutions (dicts of user ids, each of which represents a
		connected component) whose size is closest to target_quantity. If no such
		solution exists within a range of target_quantity +- epsilon, returns False
		'''

		# Get a dict mapping quantities to lists of solutions to the limited_infection
		# problem for said quantity

		quantity_to_solution = self.subsets_to_infect(target_quantity, epsilon)
		# print "Solutions: %s"%quantity_to_solution
		for i in range(epsilon + 1):
			closest_lower_sum = target_quantity - epsilon
			closest_upper_sum = target_quantity + epsilon

			if quantity_to_solution[closest_lower_sum] != []:
				return quantity_to_solution[closest_lower_sum]
			elif quantity_to_solution[closest_upper_sum] != []:
				return partial_sols[closest_upper_sum]			
		return False


	def approximate_infection(self, version, target_quantity, epsilon=None, subgraph_diversity=0):

		'''
		Parameters:

		version: The version with which we infect users

		target_quantity: The desired number of infected users

		epsilon: A slack variable -- indicates how strictly we want to enforce our
		constraint on the number of infected users

		subgraph_diversity: Indicates how significant it is to find subgraphs of different
		size while attempting to reach our target quantity of infected users
		'''

		if epsilon is None:
			epsilon = target_quantity

		# Get a list of possible solutions to our limited infection problem. If
		# there were no such solutions, <candidate_solutions> will be false
		candidate_solutions = self._approximate_infection(target_quantity, epsilon)


		# If we had at least one solution, pick one at random and infect the
		# components comprising the solution.
		if candidate_solutions:
			solution = random.choice(candidate_solutions)
			return self.total_infection_multiple(solution, version)
		return False


	def exact_infection(self, target_quantity, version):
		'''
		Runs approximate infection with a tolerance of 0 (i.e. we either
		infect exactly the target amount or nobody) and returns the result
		'''
		return self.approximate_infection(version, target_quantity, 0)


if __name__ == "__main__":
	print "Currently doing nothing - see if name == main yo"
	