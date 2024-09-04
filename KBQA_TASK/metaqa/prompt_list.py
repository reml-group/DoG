filter_best_rel_prompt = """
For a multi-hop problem, solving it requires solving several sub-problems that are logically preceded by the problem. Given a multi-hop problem and several relations, choose which relation should be used to solve the first subproblem. Here are some examples from which you should learn how to make your choices. It is worth noting that the "~" before a relationship means that the relationship is a passive relationship.
example 1
question: what was the release year of The Man Who Laughs?
relation_set :  relation_1: starred_actors, relation_2: release_year, relation_3: has_genre
explaination: this is a one-hop question.you need find out the release date of The Man Who Laughs,so the best relation is relation_2: release_year.
output: relation_2: release_year

example 2
question: Who directed films that share actors with the film Last Passenger?
relation_set : relation_1: written_by, relation_2: directed_by, relation_3: release_year, relation_4: has_tags, relation_5: has_genre, relation_6: starred_actors
explaination: This question contains three sub-questions
1. First you need to find the actors of the movie Last Passenger. 
2. Then find out what other movies these actors have appeared in.
3. Finally found the directors of these movies.
Therefore, the relationship between the sub-problems that needs to be solved first should be relation_6: starred_actors
output: relation_6: starred_actors

example 3
question: Who acted in the films directed by John Landis?
relation_set: relation_1: ~starred_actors, relation_2: ~written_by, relation_3: ~directed_by, relation_4: directed_by
explaination: This question contains two sub-questions
1. First you need to find out which films John Landis directed
2. Then find out who starred in these movies.
Therefore, the relationship between the sub-problems that needs to be solved first should be relation_3: ~directed_by,
Note that the "~" here represents adding passivity to the relationship, so you should choose "~directed_by" instead of "directed", because the actual meaning of the former is "direct", and the director should direct the movie, not be directed.
output: relation_3: ~directed_by

example 4
question:Who acted in the movies written by the writer of Bottle Rocket?
relation_set : relation_1: ~starred_actors, relation_2: written_by, relation_3: ~directed_by
explaination: This question contains three sub-questions
1. First you need to find out  Bottle Rocket written by who.
2. Then you need to find out what movies were written by that people.
3. Finally you need to find out who acte in these movies.
Therefore, the relationship between the sub-problems that needs to be solved first should be relation_2: written_by,
output: relation_2: written_by

example 5
question:The actor of Ruby Cairo also starred in which films?
relation_set : relation_1: ~has_genre, relation_2: ~directed_by, relation_3: starred_actors
explaination: This question contains two sub-questions
1. First you need find out who starred in Ruby Cairo
2. Then you need find out they acted in what films. 
Therefore, the relationship between the sub-problems that needs to be solved first should be relation_3: starred_actors.
output: relation_3: starred_actors

The following is your task. Remember, you can't blindly choose based on examples, you have to make your own judgment. The selected relationship must be one of the candidate relationships provided, and the relationship must help answer the first sub-question of the question. Please choose carefully and make a reasonable choice. Before making a choice, it is necessary to clarify which sub-problems need to be solved, and then reasonably choose the relationships involved in answering this sub-problem. If the problem can be solved in one step, choose a relationship that will solve the problem. Note that the selected relationship must come from the problem itself and cannot be imagined out of thin air.
The chosen relationship must come from the questions given to you below and not from the examples!
You first need to output the number of the relationship you selected (eg: relation_1) and then interpret it.
"""

