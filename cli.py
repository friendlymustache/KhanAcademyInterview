import sys
from graph import *

class InteractiveRunner:
	def __init__(self, graph=None):
		if graph is None:
			graph = Graph()
		self.graph = graph

	def clear_graph(self):
		self.graph.users = {}
		print "Cleared graph of all users\n"
	def lookup(self, user_id):
		user = self.graph.lookup_user(user_id)
		if user:
			user.pprint()
		else:
			print "No user exists with id %s"%user_id

	def list_users(self):
		users = self.graph.users.values()
		if len(users) == 0:
			print "No users currently in the graph\n"
		else:
			print "%s users in the graph:\n"%(len(users))
			for user in users:
				user.pprint()

	def add_users(self, count, version):
		for i in range(count):
			self.graph.create_user(version)
		print "Added %s users with version %s\n"%(count, version)

	def delete_user(self, user_id):
		success = self.graph.remove_user(user_id)
		if success:
			print "Deleted user with id %s\n"%(user_id)
		else:
			print "No user exists with id %s\n"%(user_id)

	def connect(self, coach_id, student_id):
		success = self.graph.add_edge(coach_id, student_id)
		if success:
			print "Added user %s as a coach of user %s\n"%(coach_id, student_id)
		else:
			print "One or more of the supplied user IDs does not belong to a user\n"

	def disconnect(self, coach_id, student_id):
		success = self.graph.remove_edge(coach_id, student_id)
		if success:
			print "Removed user %s as a coach of user %s\n"%(coach_id, student_id)
		else:
			print "One or more of the supplied user IDs does not belong to a user\n"

	def total_infection(self, root_id, version):
		num_infected = self.graph.total_infection(root_id, version)
		print "Infected %s nodes with version %s\n"%(num_infected, version)


	def limited_infection(self, quantity, version):
		num_infected = self.graph.limited_infection_simple(quantity, version)
		print "Infected %s users with version %s\n"%(num_infected, version)		

	def approx_infection(self, quantity, version, epsilon):
		num_infected = self.graph.approximate_infection(quantity, version, epsilon)
		if num_infected is False:
			print "Unable to find satisfactory components to infect "\
			"for approximate infection\n"
		else:
			print "Infected %s users with version %s\n"%(num_infected, version)

	def exact_infection(self, quantity, version):
		num_infected = self.graph.exact_infection(quantity, version)
		if num_infected is False:
			print "Unable to find satisfactory components to infect "\
			" =for exact infection\n"
		else:
			print "Infected %s users with version %s\n"%(num_infected, version)		

	def parse(self, line):

		try:
			args = line.split()
			command = args[0]

			if command == "clear":
				self.clear_graph()

			elif command == "lookup":
				user_id = int(args[1])
				self.lookup(user_id)

			elif command == "list":
				self.list_users()

			elif command == "add":
				count = int(args[1])
				version = int(args[2])
				self.add_users(count, version)

			elif command == "delete":
				user_id = int(args[1])
				self.delete_user(user_id)

			elif command == "connect":
				coach_id = int(args[1])
				student_id = int(args[2])
				self.connect(coach_id, student_id)

			elif command == "disconnect":
				coach_id = int(args[1])
				student_id = int(args[2])
				self.disconnect(coach_id, student_id)

			elif command == "total_infection":
				root_id = int(args[1])
				version = int(args[2])
				self.total_infection(root_id, version)

			elif command == "limited_infection":
				quantity = int(args[1])
				version = int(args[2])
				self.limited_infection(quantity, version)

			elif command == "approx_infection":
				quantity = int(args[1])
				version = int(args[2])
				epsilon = int(args[3])
				self.approx_infection(quantity, version, epsilon)

			elif command == "exact_infection":
				quantity = int(args[1])
				version = int(args[2])
				self.exact_infection(quantity, version)
			else:
				raise Exception

		except Exception as e:
			print e
			print("Your command could not be executed - please see the README " \
				"for a description of available commands\n")


	def run(self):
		while True:
			line = raw_input("--- Enter a command, or enter 'exit' to exit the program ---\n")
			if line == "exit":
				break
			self.parse(line)






if __name__ == "__main__":
	runner = InteractiveRunner()
	runner.run()
	


