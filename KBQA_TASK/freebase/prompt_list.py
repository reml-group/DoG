
filter_best_rel_prompt = """
For a multi-constraint problem, solving it requires first answering the initial question and then constraining the answer to the initial question to get the correct answer. Given a multi-constraint problem and multiple relations, choose the best relations that are most helpful in answering the initial sub-question.
Example 1:
Q:Which of team owners Tom Hicks sports team are in the ?
Relations:relation_1: kg.object_profile.prominent_type, relation_2: sports.sports_league.teams, relation_3: organization.organization.parent, relation_4: sports.sports_league.sport, relation_5: baseball.baseball_division.league, relation_6: sports.sports_league.championship, relation_7: baseball.baseball_division.teams
explain:Because to answer this question, you first need to find the teams included in the American League West, and then constrain the answer: Who knows that the owner of the team is Tom Hicks. So the most helpful relationship to the initial question would be to do with which teams there are.
A:relation_2: sports.sports_league.teams;relation_7: baseball.baseball_division.teams.

Example 2:
Q: Name the president of the country whose main spoken language was Brahui in 1980?
Relations: relation_1: language.human_language.main_country; relation_2: language.human_language.language_family; relation_3: language.human_language.iso_639_3_code; relation_4: base.rosetta.languoid.parent; relation_5: language.human_language.writing_system; relation_6: base.rosetta.languoid.languoid_class; relation_7: language.human_language.countries_spoken_in; relation_8: kg.object_profile.prominent_type; relation_9: base.rosetta.languoid.document; relation_10: base.ontologies.ontology_instance.equivalent_instances; relation_11: base.rosetta.languoid.local_name; relation_12: language.human_language.region
explain:To answer this question, you first need to know which countries have Brahui as their language, and then get the information about the presidents of these countries. So for the initial question, the most helpful relationship would be with the country to which the language corresponds.
A: relation_1: language.human_language.main_country, relation_7: language.human_language.countries_spoken_in

Example 3:
Q: where is the headquarters of bank of america?
Relations: relation_1: base.schemastaging.organization_extra.phone_number, relation_2: business.consumer_company.brands, relation_3: architecture.architectural_structure_owner.structures_owned, relation_4: user.avh.default_domain.ellerdale_topic.ellerdale_id, relation_5: business.business_operation.net_profit, relation_6: organization.organization.founders, relation_7: award.ranked_item.appears_in_ranked_lists, relation_8: business.business_operation.industry, relation_9: organization.organization_partnership.members, relation_10: business.business_operation.liabilities, relation_11: organization.organization.headquarters
explain: In the question, we asked about the location of the headquarters of "Bank of America". Relation 11 mentions "organization.organization.headquarters", which is directly related to the location of the headquarters of an organization. In this case, we need to find the exact information about the location of the headquarters of Bank of America, which is what relationship 11 can provide.
A: relation_11:organization.organization.headquarters

The number and content of the relationship you selected must be given (for example: relation_x:xxx).
You need to choose the most relevant relationship.
Your task:
"""

enough_ans_prompt = """Given a question and the associated retrieved knowledge graph triples (entity, relation, entity), you are asked to answer whether it's sufficient for you to answer the question with these triples and your knowledge (Yes or No).
Here are some examples:
Q: Find the person who said \"Taste cannot be controlled by law\", what did this person die from?
Knowledge Triples: Taste cannot be controlled by law., media_common.quotation.author, Thomas Jefferson
A: {No}. Based on the given knowledge triples, it's not sufficient to answer the entire question. The triples only provide information about the person who said "Taste cannot be controlled by law," which is Thomas Jefferson. To answer the second part of the question, it's necessary to have additional knowledge about where Thomas Jefferson's dead.

Q: The artist nominated for The Long Winter lived where?
Knowledge Triples: The Long Winter, book.written_work.author, Laura Ingalls Wilder
Laura Ingalls Wilder, people.person.places_lived, Unknown-Entity
Unknown-Entity, people.place_lived.location, De Smet
A: {Yes}. Based on the given knowledge triples, the author of The Long Winter, Laura Ingalls Wilder, lived in De Smet. Therefore, the answer to the question is {De Smet}.

Q: Who is the coach of the team owned by Steve Bisciotti?                                                                                               
Knowledge Triples: triple_1: Steve Bisciotti, sports.professional_sports_team.owner_s, Baltimore Ravens
triple_2: Steve Bisciotti, sports.sports_team_owner.teams_owned, Baltimore Ravens
triple_3: Steve Bisciotti, organization.organization_founder.organizations_founded, Allegis Group
A: {No}. Based on the given knowledge triples, the coach of the team owned by Steve Bisciotti is not explicitly mentioned. However, it can be inferred that the team owned by Steve Bisciotti is the Baltimore Ravens, a professional sports team. Therefore, additional knowledge about the current coach of the Baltimore Ravens can be used to answer the question.

Q: Rift Valley Province is located in a nation that uses which form of currency?
Knowledge Triples: triple_1: Rift Valley Province, location.administrative_division.country, Kenya
triple_2: Rift Valley Province, location.location.geolocation, UnName_Entity
triple_3: Rift Valley Province, location.mailing_address.state_province_region, UnName_Entity
triple_4: Kenya, location.country.currency_used, Kenyan shilling
A: {Yes}. Based on the given knowledge triples, Rift Valley Province is located in Kenya, which uses the Kenyan shilling as its currency. Therefore, the answer to the question is {Kenyan shilling}.

Q: The country with the National Anthem of Bolivia borders which nations?
Knowledge Triples: triple_1: National Anthem of Bolivia, government.national_anthem_of_a_country.anthem, UnName_Entity
triple_2: National Anthem of Bolivia, music.composition.composer, Leopoldo Benedetto Vincenti
triple_3: National Anthem of Bolivia, music.composition.lyricist, José Ignacio de Sanjinés
triple_4: UnName_Entity, government.national_anthem_of_a_country.country, Bolivia
triple_5: Bolivia, location.country.national_anthem, UnName_Entity
A: {No}. Based on the given knowledge triples, we can infer that the National Anthem of Bolivia is the anthem of Bolivia. Therefore, the country with the National Anthem of Bolivia is Bolivia itself. However, the given knowledge triples do not provide information about which nations border Bolivia. To answer this question, we need additional knowledge about the geography of Bolivia and its neighboring countries.
When the triple information is enough to answer the question, please ensure that your answer must be based on the information in the triple, and the answer must be consistent with the entities in the triple to avoid final matching failure!
Be sure to type Yes/No first to indicate whether you have enough information to answer the question. And explain why, if there is enough information to answer the question, give all possible answers from the reasoning path. The answers must be faithful to the expressions in the reasoning path and cannot be modified.
Here is your task:
"""

