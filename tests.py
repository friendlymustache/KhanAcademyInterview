import random
import unittest
from khan_academy import *
MAX_USERS = 100

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):

        self.old_version = 1
        self.new_version = 2

        self.graph = Graph()

        self.num_users = random.randint(1, MAX_USERS)
        self.num_components = random.randint(1, self.num_users)
        version = 1

        for i in range(self.num_users):
            self.graph.create_user(self.old_version)

        # List of lists of users, each of which represents a connected
        # component of the graph
        self.components = []

        # Maps the index of each component in the <components> list
        # to the component's size.
        self.component_to_size = {}

        # Create and connect components, populating self.components and
        # self.component_to_size
        self.setup_components()


    def setup_components(self):

        users = self.graph.users.values()
        random.shuffle(users)

        # Add one user to each component so that there are no
        # empty components
        for i in range(self.num_components):
            current_user = users[i]
            self.components.append([current_user])
            self.component_to_size[i] = 1

        # Randomly distribute the remaining users across
        # the existing components
        for j in range(self.num_components, self.num_users):
            current_user = users[j]

            index = random.randint(0, self.num_components - 1)
            component = self.components[index]

            component.append(current_user)
            self.component_to_size[index] += 1

        # Add edges to make each component a connected component
        for component in self.components:
            # Keep an array of users that are already connected
            # to other users in the component.
            connected_users = component[0:1]

            # For each user, pick a random user in the connected portion
            # of the component and connect the two users with an edge
            for i in range(1, len(component)):
                current_user = component[i]
                coach = random.choice(connected_users)
                self.graph.add_edge(coach, current_user)
                connected_users.append(current_user)


        user_ids = sorted(map(lambda x: x.id, users))
        for i in range(len(user_ids) - 1):
            assert( user_ids[i] + 1 == user_ids[i + 1] )



    def set_all_versions(self, version):
        for user in self.graph.users.values():
            user.version = version

    def etest_total_infection(self):
        
        # Set all users' version to <old_version>
        self.set_all_versions(self.old_version)

        # Pick a random component
        index = random.randint(0, self.num_components - 1)
        component = self.components[index]
        size = self.component_to_size[index]

        # Infect the component with <new_version>
        root = random.choice(component)
        num_infected = self.graph.total_infection(root.id, self.new_version)

        # Check that the correct number of users was infected
        self.assertEquals(size, num_infected)

        # Check that all users in the component have the new version
        for user in component:
            self.assertEquals(user.version, self.new_version)

        # Restore old version to all users
        self.set_all_versions(self.old_version)

    def etest_limited_infection_simple(self):
        '''
        Tests limited_infection_simple.
        '''

        # Set the version of all users to <old_version>
        self.set_all_versions(self.old_version)

        # Run limited infection with a random target quantity
        # and check that the correct number of users were infected
        target_quantity = random.randint(0, self.num_users)
        num_infected = self.graph.limited_infection_simple(target_quantity, self.new_version)
        self.assertEquals(num_infected, target_quantity)

        # Check that at most one component has two different versions
        num_partially_infected = 0
        for component in self.components:
            versions = map(lambda user : user.version, component)
            for i in range(len(versions) - 1):
                if versions[i] != versions[i + 1]:
                    num_partially_infected += 1
                    break

        self.assertTrue(num_partially_infected <= 1)

        # Set the version of all users to <old_version>
        self.set_all_versions(self.old_version)



    def etest_component_size(self):
        # Test component_size()
        for component in self.components:
            size = len(component)            
            for user in component:
                computed_size = self.graph.component_size(user.id)
                self.assertEquals(computed_size, size)

    def etest_get_component_sizes(self):
        sizes = sorted(self.graph.get_component_sizes().values())
        known_sizes = sorted(self.component_to_size.values())
        self.assertEquals(sizes, known_sizes)        


    def test_exact_infection(self):
        '''
        Tests exact infection
        '''

        # Set the version of all users to <old_version>
        self.set_all_versions(self.old_version)

        # Pick a random subset of connected components in the
        # graph and determine the number of contained users
        subset_size = random.randint(0, min(self.num_components, 10))

        indices = range(0, self.num_components)
        subset_indices = random.sample(indices, subset_size)

        num_users = sum([ self.component_to_size[index] for index in subset_indices ])
        components = [self.components[index] for index in subset_indices]


        print "Num users is %s"%num_users
        print "Subset size is %s"%subset_size

        # We should be able to infect <num_users> elements via total infection
        # by totally infecting the components in <components>
        
        num_infected = self.graph.exact_infection(num_users, self.new_version)
        print "Infected %s, target was %s"%(num_infected, num_users)
        # self.assertEquals(num_users, num_infected)


        # Set the version of all users to <old_version>
        self.set_all_versions(self.old_version)






if __name__ == '__main__':
    unittest.main()