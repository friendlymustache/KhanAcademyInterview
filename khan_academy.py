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

	def add_edge(self, coach, student):
		'''
		Adds a coaching relationship between two user objects if it does not
		already exist.

		Args:
			coach (User): A User object being set as the coach of <student>.
			student (User): A User object being set as a student of <coach>.

		Returns: None
		'''
		if coach.id not in student.coached_by:
			student.coached_by[coach.id] = coach
			self.update_cache = True
		if student.id not in coach.students:
			coach.students[student.id] = student
			self.update_cache = True

	def remove_edge(self, coach, student):
		'''
		Removes the coaching relationship between two user objects if it
		exists.

		Args:
			coach (User): A User object being removed as a coach of <student>.
			student (User): A User object being removed as a student of <coach>.

		Returns: None
		'''
		if coach.id in student.coached_by:
			student.coached_by.pop(coach.id)
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
		to the graph 

		Args:
			version (int): The site version of the new user.
			students (set): The IDs of users who are students of the new user
			coached_by (set): The IDs of users who coach the new user
		'''
		new_id = self.next_user_id
		self.next_user_id += 1
		self.users[new_id] = User(version, new_id, students, coached_by)
		self.update_cache = True

			
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
			self.update_cache = True
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

		if not self.update_cache:
			return self.cached_component_sizes

		self.cached_component_sizes = {}
		visited_users = {}
		for user_id in self.users:
			if user_id not in visited_users:
				component_size = self.component_size(user_id, visited_users)	
				self.cached_component_sizes[user_id] = component_size

		self.update_cache = False
		return self.cached_component_sizes


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

		users_to_sizes = self.get_component_sizes().items()
		# Get a list of tuples of the form (user_id, component_size)
		# sorted in decreasing order of component size
		users_to_sizes.sort(key=lambda id_and_size: -id_and_size[1])

		num_components = len(users_to_sizes)

		# The entry at index i, j represents the existence of some subset
		# of the first j components whose sizes sum up to i. If the entry
		# is False, then no such subset exists. If the entry is a tuple,
		# then some such subset does exist. 

		# The tuple will take the form (elem_included, prev_i, prev_j). 
		# elem_included is a bool describing whether or not the jth
		# component is included in our solution. prev_i and prev_j together
		# represent the indices of some previously-computed solution 
		# (prev_i <= i and prev_j < j) that can be extended to obtain 
		# our current solution.

		# If prev_i and prev_j are None, then our solution is either
		# the jth component (if elem_incuded is True) or the empty set
		# (if elem_included is False)

		# Initialize all solutions to False (impossible)
		num_rows = target + epsilon + 1
		num_cols = num_components + 1
		partial_sols = [[False] * num_cols for i in range(num_rows)]

		# The empty set gives us a sum of 0
		for j in range(num_components + 1):
			partial_sols[0][j] = (False, None, None)

		# For all target sums i
		for i in range(1, target + 1):
			for j in range(1, num_components + 1):
				current_size = users_to_sizes[j - 1][1]
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
		Returns a list of user ids - each referenced user is contained in a
		distinct connected component that should be infected in order to
		infect a total of <target_quantity> users.

		If such a solution does not exist, returns False.
		'''

		users_to_sizes = self.get_component_sizes().items()
		
		# Get a list of tuples of the form (user_id, component_size)
		# sorted in decreasing order of component size
		users_to_sizes.sort(key=lambda id_and_size: -id_and_size[1])

		# Get a list of the user_ids in the above list of tuples
		components = map(lambda component: component[0], users_to_sizes)
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
		of users as close to <target_quantity> as possible. If we can't
		infect any quantities within target_quantity +/- epsilon via the
		total infection of some number of connected components, return False.
		'''

		solution_table = self.subsets_to_infect(target_quantity, epsilon)

		exact_solution = self.extract_solution(solution_table, target_quantity)
		if exact_solution != False:
			return exact_solution

		for i in range(1, epsilon):
			lower_target = target_quantity - epsilon
			upper_target = target_quantity + epsilon

			lower_sol = self.extract_solution(solution_table, lower_target)
			if lower_sol:
				return lower_sol

			upper_sol = self.extract_solution(solution_table, upper_target)
			if upper_sol:
				return upper_sol

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

		# Get a list of user_ids from distinct connected components upon which
		# we should perform total infection in order to infect a quantity
		# that is as close to <target_quantity> as possible. If no quantity
		# within target_quantity +- epsilon can be achieved, <solution> will
		# be False.
		solution = self._approximate_infection(target_quantity, epsilon)

		# If we found a valid solution, perform total infection on the necessary
		# components. Otherwise, return False.
		if solution != False:
			return self.total_infection_multiple(solution, version)
		return False


	def exact_infection(self, target_quantity, version):
		'''
		Runs approximate infection with a tolerance of 0 (i.e. we either
		infect exactly the target amount or nobody) and returns the result
		'''
		return self.approximate_infection(version, target_quantity, 0)
