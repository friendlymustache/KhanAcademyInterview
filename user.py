class User:
	def __init__(self, version, user_id, students=None, coached_by=None):
		'''
		Creates a new user object using the passed in version.
		Stores adjacent students (people being coached by the current user)
		and coaches (people who coach the current user) in two adjacency
		lists (represented by sets).
		'''

		self.id = user_id
		self.students = set() if students is None else students
		self.coached_by = set() if coached_by is None else coached_by	
		self.version = version

	def pprint(self):
		print "User %s, version: %s\n"%(self.id, self.version)
