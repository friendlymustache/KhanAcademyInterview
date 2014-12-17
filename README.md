# How to Run:
- <h5>Tests:</h5>
    - Run tests.py from the root folder
- <h5>Command-line Interface:</h5>
  - Run cli.py from the root folder
  - Enter one of the following commands:
    * <b>clear:</b> <br/> Removes all users from the graph
    * <b>lookup &lt;user_id>:</b> <br/> Looks up the user with the specified ID and prints his/her info
    * <b>list:</b> <br/> Prints all users in the graph
    * <b>add &lt;num_users> &lt;version>:</b> <br/> Adds &lt;num_users> users with the specified version to the graph
    * <b>delete &lt;user_id> :</b> <br/> Deletes the user with the specified id from the graph
    * <b>connect &lt;coach_id> &lt;student_id>:</b> <br/> Adds a coaching relationship (edge) between the specified coach and student users
    * <b>disconnect &lt;coach_id> &lt;student_id>:</b> <br/> Removes the coaching relationship (edge) between the specified coach and student users
    * <b>total_infection &lt;root_id> &lt;version>:</b> <br/> Totally infects the component containing the user with id root_id with the version.
    * <b>limited_infection &lt;quantity> &lt;version>:</b> <br/>  Infects the specified quantity of users with the specified version. Partially infects a component if necessary.
    * <b>approx_infection &lt;quantity> &lt;version> &lt;epsilon>:</b> <br/> Employing a strategy of totally infecting connected components, attempts to infect a number of users that is as close to the specified quantity as possible. If we can't infect some number of users in the range &lt;quantity> &plusmn; &lt;epsilon> purely through total infection, infection fails.
    * <b>exact_infection &lt;quantity> &lt;version>:</b> <br/> Runs approximate infection with a tolerance of 0; we either
        can infect exactly the target amount via the total infection of some components, or infection fails.

# Possible improvements/additions:
- It could be useful to add in another parameter to approximate_infection that took into account the importance of variation in the sizes of the components we infected (it may be more important to try out a new version of the site on classrooms of various sizes than to target a specific number of users)
- An actual GUI for viewing and manipulating the graph; something that lets users select individual or multiple nodes and manipulate them. Nodes with different versions could have different colors, etc.
- Integration with an actual database -- this would help us reduce space complexity, as we'd be able to store coach-student edges in their own table (so that each edge is stored only once) without significantly slowing down the process of finding adjacent users. A table containing user information would also be significantly better than a single dict mapping user