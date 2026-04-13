import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from .base_generator import BaseQuestionGenerator

class SPOQuestionGenerator(BaseQuestionGenerator):
    """
    Динамический генератор вопросов по модулю Sentence Structure Basics (SPO)
    Создает уникальные вопросы для каждой темы интересов
    56 типов вопросов (распределены по 6 урокам)
    """

    # Темы интересов с расширенными словарями
    TOPICS = {
        2: {
            "name": "Shopping and money",
            "subjects": ["the customer", "the cashier", "the manager", "the buyer", "my friend"],
            "action_verbs": ["buy", "sell", "pay", "shop", "spend", "save"],
            "state_verbs": ["like", "want", "need", "prefer"],
            "intransitive_verbs": ["shop", "arrive", "wait", "leave"],
            "transitive_verbs": ["buy", "sell", "pay", "choose", "find"],
            "objects": ["products", "money", "clothes", "food", "gifts"],
            "adjectives": ["expensive", "cheap", "busy", "happy", "tired"],
            "locations": ["at the store", "at the mall", "in the shop"],
            "professions": ["a customer", "a cashier", "a seller", "a manager"],
            "names": ["Maria", "John", "Sarah", "Tom"],
            "cities": ["Berlin", "Madrid", "Rome"],
            "countries": ["Germany", "Spain", "Italy"],
            "idioms": ["by the way", "to be honest", "in fact"]
        },
        3: {
            "name": "Weather and nature",
            "subjects": ["the sun", "the rain", "the wind", "the snow", "nature"],
            "action_verbs": ["rain", "snow", "shine", "blow", "freeze"],
            "state_verbs": ["like", "love", "enjoy", "prefer"],
            "intransitive_verbs": ["rain", "snow", "shine", "fall"],
            "transitive_verbs": ["enjoy", "watch", "love", "study"],
            "objects": ["nature", "the weather", "the forecast", "the temperature"],
            "adjectives": ["sunny", "rainy", "cold", "hot", "beautiful"],
            "locations": ["at the park", "in the forest", "at the beach"],
            "professions": ["a meteorologist", "a farmer", "a gardener"],
            "names": ["Alex", "Emma", "David", "Lisa"],
            "cities": ["Toronto", "London", "Oslo"],
            "countries": ["Canada", "England", "Norway"],
            "idioms": ["under the weather", "rain or shine", "on cloud nine"]
        },
        4: {
            "name": "Health and medicine",
            "subjects": ["the doctor", "the patient", "the nurse", "the hospital"],
            "action_verbs": ["treat", "examine", "cure", "help", "recover"],
            "state_verbs": ["feel", "need", "want", "prefer"],
            "intransitive_verbs": ["recover", "rest", "wait", "sleep"],
            "transitive_verbs": ["treat", "examine", "take", "need"],
            "objects": ["medicine", "treatment", "advice", "help"],
            "adjectives": ["sick", "healthy", "tired", "weak", "strong"],
            "locations": ["at the hospital", "at the clinic", "in the pharmacy"],
            "professions": ["a doctor", "a nurse", "a surgeon", "a therapist"],
            "names": ["Dr. Smith", "Anna", "Michael", "Kate"],
            "cities": ["Boston", "Geneva", "Stockholm"],
            "countries": ["the USA", "Switzerland", "Sweden"],
            "idioms": ["as fit as a fiddle", "under the weather", "in good shape"]
        },
        5: {
            "name": "Home and daily routines",
            "subjects": ["my family", "my mom", "my dad", "my brother", "the house"],
            "action_verbs": ["cook", "clean", "wash", "sleep", "wake up"],
            "state_verbs": ["like", "love", "prefer", "need"],
            "intransitive_verbs": ["sleep", "wake up", "rest", "arrive"],
            "transitive_verbs": ["cook", "clean", "wash", "make", "prepare"],
            "objects": ["breakfast", "dinner", "the house", "dishes", "laundry"],
            "adjectives": ["clean", "tidy", "comfortable", "cozy", "busy"],
            "locations": ["at home", "in the kitchen", "in the bedroom"],
            "professions": ["a housewife", "a cook", "a cleaner"],
            "names": ["Mom", "Dad", "Anna", "Peter"],
            "cities": ["home", "Moscow", "Kiev"],
            "countries": ["Russia", "Ukraine", "Belarus"],
            "idioms": ["make yourself at home", "home sweet home", "hit the hay"]
        },
        6: {
            "name": "Transportation and directions",
            "subjects": ["the bus", "the train", "the driver", "the passenger"],
            "action_verbs": ["drive", "travel", "go", "take", "ride"],
            "state_verbs": ["need", "want", "prefer", "like"],
            "intransitive_verbs": ["arrive", "leave", "stop", "wait"],
            "transitive_verbs": ["drive", "take", "catch", "miss"],
            "objects": ["the bus", "the train", "the ticket", "directions"],
            "adjectives": ["fast", "slow", "late", "early", "busy"],
            "locations": ["at the station", "at the airport", "on the road"],
            "professions": ["a driver", "a pilot", "a conductor"],
            "names": ["Jack", "Sophie", "Robert", "Emma"],
            "cities": ["Paris", "Tokyo", "Dubai"],
            "countries": ["France", "Japan", "UAE"],
            "idioms": ["on the go", "hit the road", "in the fast lane"]
        },
        7: {
            "name": "Leisure and hobbies",
            "subjects": ["my friend", "the player", "the artist", "the musician"],
            "action_verbs": ["play", "read", "watch", "paint", "sing"],
            "state_verbs": ["like", "love", "enjoy", "prefer"],
            "intransitive_verbs": ["play", "sing", "dance", "rest"],
            "transitive_verbs": ["read", "watch", "play", "paint", "enjoy"],
            "objects": ["music", "books", "movies", "games", "art"],
            "adjectives": ["interesting", "boring", "fun", "exciting", "relaxing"],
            "locations": ["at home", "at the park", "at the cinema"],
            "professions": ["an artist", "a musician", "a player", "a writer"],
            "names": ["Mike", "Lucy", "James", "Helen"],
            "cities": ["Vienna", "Nashville", "Hollywood"],
            "countries": ["Austria", "the USA", "Italy"],
            "idioms": ["for fun", "in your spare time", "pass the time"]
        },
        8: {
            "name": "Relationships and emotions",
            "subjects": ["my friend", "my sister", "my partner", "the family"],
            "action_verbs": ["meet", "talk", "help", "support", "care"],
            "state_verbs": ["love", "like", "trust", "understand", "feel"],
            "intransitive_verbs": ["smile", "laugh", "cry", "talk"],
            "transitive_verbs": ["love", "help", "support", "trust", "understand"],
            "objects": ["friends", "family", "love", "support", "trust"],
            "adjectives": ["happy", "sad", "angry", "calm", "friendly"],
            "locations": ["at home", "at the cafe", "in the park"],
            "professions": ["a friend", "a partner", "a therapist"],
            "names": ["Jessica", "Daniel", "Chris", "Nicole"],
            "cities": ["Paris", "Rome", "Prague"],
            "countries": ["France", "Italy", "Czech Republic"],
            "idioms": ["heart to heart", "break the ice", "on good terms"]
        },
        9: {
            "name": "Technology and gadgets",
            "subjects": ["the computer", "the phone", "the user", "the programmer"],
            "action_verbs": ["use", "program", "fix", "install", "download"],
            "state_verbs": ["need", "want", "understand", "know"],
            "intransitive_verbs": ["work", "crash", "load", "start"],
            "transitive_verbs": ["use", "fix", "install", "download", "program"],
            "objects": ["apps", "software", "computers", "phones", "data"],
            "adjectives": ["fast", "slow", "new", "old", "modern"],
            "locations": ["at home", "at the office", "online"],
            "professions": ["a programmer", "a developer", "an engineer"],
            "names": ["Steve", "Bill", "Mark", "Elon"],
            "cities": ["Silicon Valley", "Seoul", "Tokyo"],
            "countries": ["the USA", "South Korea", "Japan"],
            "idioms": ["tech-savvy", "cutting edge", "up to date"]
        },
        11: {
            "name": "Job interviews and CVs",
            "subjects": ["the candidate", "the interviewer", "the manager", "the applicant"],
            "action_verbs": ["interview", "hire", "apply", "prepare", "answer"],
            "state_verbs": ["want", "need", "hope", "expect"],
            "intransitive_verbs": ["arrive", "wait", "prepare", "succeed"],
            "transitive_verbs": ["interview", "hire", "prepare", "send", "write"],
            "objects": ["the CV", "questions", "answers", "experience", "skills"],
            "adjectives": ["nervous", "confident", "qualified", "experienced", "ready"],
            "locations": ["at the office", "at the interview", "at the company"],
            "professions": ["a candidate", "an interviewer", "a manager"],
            "names": ["Mr. Brown", "Ms. Johnson", "Robert", "Jennifer"],
            "cities": ["New York", "London", "Singapore"],
            "countries": ["the USA", "the UK", "Singapore"],
            "idioms": ["land a job", "ace the interview", "make a good impression"]
        },
        12: {
            "name": "Meetings and negotiations",
            "subjects": ["the team", "the manager", "the client", "the partner"],
            "action_verbs": ["discuss", "negotiate", "meet", "agree", "decide"],
            "state_verbs": ["want", "need", "prefer", "agree"],
            "intransitive_verbs": ["meet", "arrive", "wait", "agree"],
            "transitive_verbs": ["discuss", "negotiate", "present", "propose"],
            "objects": ["the deal", "terms", "proposals", "contracts", "ideas"],
            "adjectives": ["important", "urgent", "serious", "productive", "successful"],
            "locations": ["at the office", "in the meeting room", "at the conference"],
            "professions": ["a manager", "a negotiator", "a director"],
            "names": ["Mr. Lee", "Ms. Garcia", "Tom", "Susan"],
            "cities": ["Brussels", "Geneva", "Dubai"],
            "countries": ["Belgium", "Switzerland", "UAE"],
            "idioms": ["strike a deal", "on the same page", "win-win situation"]
        },
        13: {
            "name": "Presentations and public speaking",
            "subjects": ["the speaker", "the presenter", "the audience", "the expert"],
            "action_verbs": ["present", "speak", "explain", "show", "demonstrate"],
            "state_verbs": ["know", "understand", "believe", "think"],
            "intransitive_verbs": ["speak", "present", "stand", "wait"],
            "transitive_verbs": ["present", "explain", "show", "demonstrate"],
            "objects": ["slides", "ideas", "data", "results", "information"],
            "adjectives": ["clear", "confident", "nervous", "interesting", "professional"],
            "locations": ["at the conference", "on stage", "in the hall"],
            "professions": ["a speaker", "a presenter", "an expert"],
            "names": ["Dr. White", "Professor Green", "Sarah", "Michael"],
            "cities": ["Las Vegas", "Barcelona", "Dubai"],
            "countries": ["the USA", "Spain", "UAE"],
            "idioms": ["break the ice", "get the ball rolling", "speak volumes"]
        },
        14: {
            "name": "Emails and business correspondence",
            "subjects": ["the sender", "the recipient", "the manager", "the colleague"],
            "action_verbs": ["send", "write", "reply", "forward", "attach"],
            "state_verbs": ["need", "want", "expect", "hope"],
            "intransitive_verbs": ["reply", "wait", "arrive"],
            "transitive_verbs": ["send", "write", "reply", "forward", "attach"],
            "objects": ["emails", "messages", "documents", "files", "reports"],
            "adjectives": ["urgent", "important", "formal", "polite", "clear"],
            "locations": ["at the office", "at work", "online"],
            "professions": ["a manager", "an assistant", "a secretary"],
            "names": ["John", "Mary", "David", "Linda"],
            "cities": ["New York", "London", "Tokyo"],
            "countries": ["the USA", "the UK", "Japan"],
            "idioms": ["FYI", "ASAP", "keep someone in the loop"]
        },
        15: {
            "name": "Office communication and teamwork",
            "subjects": ["the team", "the colleague", "the boss", "the employee"],
            "action_verbs": ["work", "cooperate", "help", "support", "collaborate"],
            "state_verbs": ["trust", "respect", "understand", "like"],
            "intransitive_verbs": ["work", "cooperate", "collaborate", "meet"],
            "transitive_verbs": ["help", "support", "respect", "trust"],
            "objects": ["tasks", "projects", "goals", "colleagues", "work"],
            "adjectives": ["friendly", "professional", "helpful", "busy", "efficient"],
            "locations": ["at the office", "at work", "in the team"],
            "professions": ["a colleague", "a manager", "an employee"],
            "names": ["Alex", "Rachel", "Kevin", "Monica"],
            "cities": ["Chicago", "Toronto", "Sydney"],
            "countries": ["the USA", "Canada", "Australia"],
            "idioms": ["team player", "on the same wavelength", "pull your weight"]
        },
        16: {
            "name": "Project management vocabulary",
            "subjects": ["the manager", "the team", "the project", "the deadline"],
            "action_verbs": ["manage", "plan", "execute", "monitor", "deliver"],
            "state_verbs": ["need", "want", "require", "expect"],
            "intransitive_verbs": ["succeed", "fail", "start", "finish"],
            "transitive_verbs": ["manage", "plan", "execute", "monitor", "deliver"],
            "objects": ["projects", "tasks", "deadlines", "resources", "goals"],
            "adjectives": ["complex", "urgent", "important", "challenging", "successful"],
            "locations": ["at the office", "at work", "in the project"],
            "professions": ["a manager", "a coordinator", "a leader"],
            "names": ["Paul", "Diana", "Frank", "Laura"],
            "cities": ["Boston", "Frankfurt", "Singapore"],
            "countries": ["the USA", "Germany", "Singapore"],
            "idioms": ["on track", "behind schedule", "meet the deadline"]
        },
        17: {
            "name": "Customer service and support",
            "subjects": ["the customer", "the agent", "the representative", "the client"],
            "action_verbs": ["help", "serve", "assist", "support", "solve"],
            "state_verbs": ["want", "need", "expect", "appreciate"],
            "intransitive_verbs": ["wait", "call", "arrive", "complain"],
            "transitive_verbs": ["help", "serve", "assist", "support", "solve"],
            "objects": ["problems", "questions", "issues", "customers", "requests"],
            "adjectives": ["helpful", "polite", "patient", "friendly", "professional"],
            "locations": ["at the office", "on the phone", "at the desk"],
            "professions": ["an agent", "a representative", "a specialist"],
            "names": ["Karen", "Bob", "Tim", "Jane"],
            "cities": ["Dublin", "Manila", "Mumbai"],
            "countries": ["Ireland", "Philippines", "India"],
            "idioms": ["go the extra mile", "the customer is king", "bend over backwards"]
        },
        18: {
            "name": "Marketing and sales English",
            "subjects": ["the marketer", "the salesperson", "the customer", "the brand"],
            "action_verbs": ["sell", "promote", "advertise", "market", "launch"],
            "state_verbs": ["want", "need", "prefer", "like"],
            "intransitive_verbs": ["sell", "succeed", "grow", "launch"],
            "transitive_verbs": ["sell", "promote", "advertise", "market", "launch"],
            "objects": ["products", "services", "campaigns", "brands", "sales"],
            "adjectives": ["successful", "popular", "effective", "creative", "innovative"],
            "locations": ["at the store", "at the market", "online"],
            "professions": ["a marketer", "a salesperson", "a manager"],
            "names": ["Steve", "Amy", "Richard", "Claire"],
            "cities": ["New York", "Los Angeles", "Hong Kong"],
            "countries": ["the USA", "China", "Singapore"],
            "idioms": ["seal the deal", "hard sell", "foot in the door"]
        },
        20: {
            "name": "At the airport and hotel",
            "subjects": ["the passenger", "the guest", "the receptionist", "the tourist"],
            "action_verbs": ["check in", "book", "stay", "fly", "travel"],
            "state_verbs": ["need", "want", "prefer", "like"],
            "intransitive_verbs": ["arrive", "leave", "wait", "stay"],
            "transitive_verbs": ["book", "check", "reserve", "need"],
            "objects": ["tickets", "rooms", "luggage", "keys", "reservations"],
            "adjectives": ["comfortable", "expensive", "nice", "convenient", "available"],
            "locations": ["at the airport", "at the hotel", "at the reception"],
            "professions": ["a receptionist", "a porter", "a pilot"],
            "names": ["Mr. Anderson", "Mrs. Taylor", "Jack", "Emily"],
            "cities": ["Dubai", "Singapore", "London"],
            "countries": ["UAE", "Singapore", "the UK"],
            "idioms": ["check in", "check out", "on the fly"]
        },
        21: {
            "name": "Sightseeing and excursions",
            "subjects": ["the tourist", "the guide", "the visitor", "the traveler"],
            "action_verbs": ["visit", "see", "explore", "tour", "discover"],
            "state_verbs": ["like", "love", "enjoy", "prefer"],
            "intransitive_verbs": ["walk", "travel", "arrive", "rest"],
            "transitive_verbs": ["visit", "see", "explore", "tour", "discover"],
            "objects": ["museums", "monuments", "sights", "places", "attractions"],
            "adjectives": ["beautiful", "interesting", "famous", "historical", "amazing"],
            "locations": ["at the museum", "at the monument", "in the city"],
            "professions": ["a guide", "a tourist", "a traveler"],
            "names": ["Carlos", "Maria", "Hans", "Sophie"],
            "cities": ["Paris", "Rome", "Athens"],
            "countries": ["France", "Italy", "Greece"],
            "idioms": ["off the beaten path", "see the sights", "tourist trap"]
        },
        22: {
            "name": "Emergencies abroad",
            "subjects": ["the tourist", "the police", "the doctor", "the officer"],
            "action_verbs": ["help", "call", "report", "assist", "contact"],
            "state_verbs": ["need", "want", "fear", "worry"],
            "intransitive_verbs": ["wait", "arrive", "hurry", "call"],
            "transitive_verbs": ["help", "call", "report", "contact", "need"],
            "objects": ["help", "police", "ambulance", "documents", "assistance"],
            "adjectives": ["urgent", "serious", "dangerous", "safe", "worried"],
            "locations": ["at the hospital", "at the police station", "at the embassy"],
            "professions": ["a police officer", "a doctor", "an officer"],
            "names": ["Officer Smith", "Dr. Brown", "John", "Anna"],
            "cities": ["any city", "the capital", "abroad"],
            "countries": ["any country", "abroad"],
            "idioms": ["in trouble", "safe and sound", "call for help"]
        },
        23: {
            "name": "Cultural etiquette and customs",
            "subjects": ["the guest", "the host", "the visitor", "people"],
            "action_verbs": ["greet", "bow", "shake hands", "respect", "follow"],
            "state_verbs": ["understand", "respect", "know", "appreciate"],
            "intransitive_verbs": ["bow", "smile", "wait", "arrive"],
            "transitive_verbs": ["greet", "respect", "follow", "understand"],
            "objects": ["customs", "traditions", "rules", "etiquette", "culture"],
            "adjectives": ["polite", "respectful", "appropriate", "traditional", "formal"],
            "locations": ["in the country", "at the ceremony", "at the event"],
            "professions": ["a guest", "a host", "a diplomat"],
            "names": ["various names", "Mr. Tanaka", "Ms. Chen"],
            "cities": ["Tokyo", "Beijing", "Delhi"],
            "countries": ["Japan", "China", "India"],
            "idioms": ["when in Rome", "mind your manners", "show respect"]
        },
        24: {
            "name": "Talking about countries and nationalities",
            "subjects": ["people", "tourists", "the person", "the visitor"],
            "action_verbs": ["come", "live", "travel", "visit", "move"],
            "state_verbs": ["be", "like", "prefer", "know"],
            "intransitive_verbs": ["live", "travel", "move", "arrive"],
            "transitive_verbs": ["visit", "know", "like", "love"],
            "objects": ["countries", "cities", "languages", "cultures", "places"],
            "adjectives": ["American", "British", "Chinese", "French", "international"],
            "locations": ["in the USA", "in Europe", "in Asia"],
            "professions": ["a traveler", "a tourist", "an expat"],
            "names": ["John", "Pierre", "Yuki", "Hans"],
            "cities": ["New York", "Paris", "Tokyo", "Berlin"],
            "countries": ["the USA", "France", "Japan", "Germany"],
            "idioms": ["around the world", "from all walks of life", "global citizen"]
        },
        26: {
            "name": "Idioms",
            "subjects": ["people", "my friend", "the speaker", "someone"],
            "action_verbs": ["use", "say", "understand", "learn", "practice"],
            "state_verbs": ["know", "understand", "like", "remember"],
            "intransitive_verbs": ["speak", "learn", "practice", "talk"],
            "transitive_verbs": ["use", "say", "understand", "learn", "know"],
            "objects": ["idioms", "expressions", "phrases", "English", "language"],
            "adjectives": ["common", "useful", "interesting", "difficult", "popular"],
            "locations": ["in English", "in conversation", "in the language"],
            "professions": ["a student", "a teacher", "a learner"],
            "names": ["students", "learners", "Tom", "Mary"],
            "cities": ["everywhere", "in English-speaking countries"],
            "countries": ["the USA", "the UK", "Australia"],
            "idioms": ["piece of cake", "break a leg", "costs an arm and a leg", "hit the nail on the head"]
        },
        27: {
            "name": "Slang",
            "subjects": ["young people", "teenagers", "friends", "the speaker"],
            "action_verbs": ["use", "say", "understand", "learn", "hear"],
            "state_verbs": ["know", "understand", "like", "get"],
            "intransitive_verbs": ["talk", "speak", "chat", "hang out"],
            "transitive_verbs": ["use", "say", "understand", "hear", "get"],
            "objects": ["slang", "words", "expressions", "language", "phrases"],
            "adjectives": ["cool", "awesome", "popular", "modern", "informal"],
            "locations": ["on the street", "online", "in conversation"],
            "professions": ["a teenager", "a student", "a young person"],
            "names": ["cool kids", "young people", "Jake", "Lisa"],
            "cities": ["big cities", "urban areas"],
            "countries": ["the USA", "the UK", "Australia"],
            "idioms": ["hang out", "chill out", "no worries", "what's up"]
        },
        28: {
            "name": "Phrasal verbs",
            "subjects": ["students", "learners", "people", "the speaker"],
            "action_verbs": ["learn", "use", "understand", "practice", "master"],
            "state_verbs": ["know", "understand", "remember", "need"],
            "intransitive_verbs": ["give up", "break down", "show up", "work out"],
            "transitive_verbs": ["figure out", "look up", "pick up", "turn down"],
            "objects": ["phrasal verbs", "meanings", "English", "grammar", "usage"],
            "adjectives": ["difficult", "common", "important", "useful", "tricky"],
            "locations": ["in English", "in the language", "in sentences"],
            "professions": ["a student", "a learner", "a teacher"],
            "names": ["students", "Tom", "Alice", "learners"],
            "cities": ["in schools", "in classes"],
            "countries": ["English-speaking countries"],
            "idioms": ["look up", "figure out", "give up", "show up"]
        },
        29: {
            "name": "Collocations and word patterns",
            "subjects": ["words", "patterns", "combinations", "students"],
            "action_verbs": ["combine", "use", "learn", "practice", "study"],
            "state_verbs": ["know", "understand", "remember", "recognize"],
            "intransitive_verbs": ["work", "fit", "sound", "occur"],
            "transitive_verbs": ["learn", "use", "practice", "study", "master"],
            "objects": ["collocations", "patterns", "words", "combinations", "phrases"],
            "adjectives": ["natural", "common", "correct", "proper", "fixed"],
            "locations": ["in English", "in language", "in context"],
            "professions": ["a student", "a learner", "a linguist"],
            "names": ["learners", "students", "Tom", "Emma"],
            "cities": ["in classes", "in schools"],
            "countries": ["worldwide", "everywhere"],
            "idioms": ["make sense", "take time", "do homework", "catch a cold"]
        },
        30: {
            "name": "Figurative language and metaphors",
            "subjects": ["writers", "speakers", "people", "the author"],
            "action_verbs": ["use", "create", "understand", "interpret", "write"],
            "state_verbs": ["understand", "appreciate", "like", "love"],
            "intransitive_verbs": ["write", "speak", "create", "work"],
            "transitive_verbs": ["use", "create", "understand", "interpret", "write"],
            "objects": ["metaphors", "language", "imagery", "expressions", "words"],
            "adjectives": ["creative", "poetic", "beautiful", "powerful", "expressive"],
            "locations": ["in literature", "in writing", "in speech"],
            "professions": ["a writer", "a poet", "an author"],
            "names": ["writers", "authors", "Shakespeare", "poets"],
            "cities": ["in literature", "in books"],
            "countries": ["worldwide", "in all cultures"],
            "idioms": ["time flies", "heart of stone", "sea of troubles", "light of my life"]
        },
        31: {
            "name": "Synonyms, antonyms, and nuance",
            "subjects": ["words", "meanings", "students", "learners"],
            "action_verbs": ["learn", "distinguish", "understand", "use", "study"],
            "state_verbs": ["know", "understand", "recognize", "remember"],
            "intransitive_verbs": ["differ", "vary", "change", "work"],
            "transitive_verbs": ["learn", "distinguish", "understand", "use", "study"],
            "objects": ["synonyms", "antonyms", "meanings", "nuances", "differences"],
            "adjectives": ["similar", "different", "opposite", "subtle", "precise"],
            "locations": ["in language", "in context", "in usage"],
            "professions": ["a student", "a linguist", "a learner"],
            "names": ["students", "learners", "Tom", "Alice"],
            "cities": ["in classes", "in schools"],
            "countries": ["worldwide"],
            "idioms": ["big vs large", "little vs small", "happy vs joyful"]
        },
        32: {
            "name": "Register and tone (formal vs informal)",
            "subjects": ["speakers", "writers", "people", "the person"],
            "action_verbs": ["speak", "write", "use", "choose", "adapt"],
            "state_verbs": ["understand", "know", "recognize", "appreciate"],
            "intransitive_verbs": ["speak", "write", "vary", "change"],
            "transitive_verbs": ["use", "choose", "adapt", "understand", "recognize"],
            "objects": ["language", "words", "tone", "register", "style"],
            "adjectives": ["formal", "informal", "polite", "casual", "appropriate"],
            "locations": ["at work", "with friends", "in writing"],
            "professions": ["a professional", "a friend", "a colleague"],
            "names": ["professionals", "friends", "John", "Sarah"],
            "cities": ["in offices", "everywhere"],
            "countries": ["worldwide"],
            "idioms": ["keep it formal", "lighten up", "play it safe"]
        },
        33: {
            "name": "Common grammar pitfalls",
            "subjects": ["students", "learners", "people", "beginners"],
            "action_verbs": ["make", "avoid", "fix", "learn", "understand"],
            "state_verbs": ["know", "understand", "remember", "recognize"],
            "intransitive_verbs": ["learn", "improve", "practice", "study"],
            "transitive_verbs": ["make", "avoid", "fix", "correct", "understand"],
            "objects": ["mistakes", "errors", "grammar", "rules", "problems"],
            "adjectives": ["common", "typical", "frequent", "serious", "simple"],
            "locations": ["in English", "in grammar", "in writing"],
            "professions": ["a student", "a learner", "a beginner"],
            "names": ["students", "learners", "beginners"],
            "cities": ["in classes", "everywhere"],
            "countries": ["worldwide"],
            "idioms": ["trial and error", "learn from mistakes", "practice makes perfect"]
        },
        35: {
            "name": "English for IT",
            "subjects": ["the developer", "the programmer", "the engineer", "the user"],
            "action_verbs": ["code", "program", "develop", "test", "debug"],
            "state_verbs": ["understand", "know", "need", "want"],
            "intransitive_verbs": ["work", "run", "crash", "compile"],
            "transitive_verbs": ["code", "program", "develop", "test", "debug"],
            "objects": ["code", "software", "apps", "systems", "programs"],
            "adjectives": ["complex", "efficient", "fast", "reliable", "secure"],
            "locations": ["at the office", "at work", "online"],
            "professions": ["a developer", "a programmer", "an engineer"],
            "names": ["Steve", "Linus", "Ada", "Grace"],
            "cities": ["Silicon Valley", "Bangalore", "Tel Aviv"],
            "countries": ["the USA", "India", "Israel"],
            "idioms": ["debug the code", "push to production", "ship it"]
        },
        36: {
            "name": "English for Finance / Accounting",
            "subjects": ["the accountant", "the analyst", "the auditor", "the CFO"],
            "action_verbs": ["calculate", "analyze", "audit", "budget", "invest"],
            "state_verbs": ["understand", "know", "need", "expect"],
            "intransitive_verbs": ["increase", "decrease", "fluctuate", "grow"],
            "transitive_verbs": ["calculate", "analyze", "audit", "budget", "manage"],
            "objects": ["numbers", "reports", "budgets", "assets", "accounts"],
            "adjectives": ["accurate", "precise", "detailed", "financial", "important"],
            "locations": ["at the office", "at the bank", "at work"],
            "professions": ["an accountant", "an analyst", "an auditor"],
            "names": ["Mr. Warren", "Ms. Lynch", "John", "Mary"],
            "cities": ["Wall Street", "London", "Hong Kong"],
            "countries": ["the USA", "the UK", "China"],
            "idioms": ["balance the books", "in the red", "in the black"]
        },
        37: {
            "name": "English for Law",
            "subjects": ["the lawyer", "the judge", "the attorney", "the client"],
            "action_verbs": ["represent", "defend", "prosecute", "argue", "advise"],
            "state_verbs": ["understand", "know", "believe", "consider"],
            "intransitive_verbs": ["testify", "appeal", "object", "proceed"],
            "transitive_verbs": ["represent", "defend", "prosecute", "argue", "file"],
            "objects": ["cases", "clients", "evidence", "documents", "appeals"],
            "adjectives": ["legal", "lawful", "guilty", "innocent", "just"],
            "locations": ["in court", "at the office", "at the hearing"],
            "professions": ["a lawyer", "a judge", "an attorney"],
            "names": ["Judge Smith", "Attorney Brown", "John", "Sarah"],
            "cities": ["Washington", "London", "The Hague"],
            "countries": ["the USA", "the UK", "Netherlands"],
            "idioms": ["take the stand", "rest the case", "beyond reasonable doubt"]
        },
        38: {
            "name": "English for Medicine",
            "subjects": ["the doctor", "the surgeon", "the nurse", "the patient"],
            "action_verbs": ["diagnose", "treat", "operate", "prescribe", "examine"],
            "state_verbs": ["understand", "know", "feel", "need"],
            "intransitive_verbs": ["recover", "heal", "improve", "rest"],
            "transitive_verbs": ["diagnose", "treat", "operate", "prescribe", "examine"],
            "objects": ["patients", "symptoms", "diseases", "treatments", "medicine"],
            "adjectives": ["serious", "critical", "stable", "healthy", "sick"],
            "locations": ["in the hospital", "at the clinic", "in the OR"],
            "professions": ["a doctor", "a surgeon", "a nurse"],
            "names": ["Dr. House", "Dr. Grey", "John", "Emma"],
            "cities": ["Boston", "Rochester", "Baltimore"],
            "countries": ["the USA", "Switzerland", "Sweden"],
            "idioms": ["under the weather", "get well soon", "a clean bill of health"]
        },
        39: {
            "name": "English for Marketing and PR",
            "subjects": ["the marketer", "the PR manager", "the brand", "the campaign"],
            "action_verbs": ["promote", "advertise", "launch", "brand", "market"],
            "state_verbs": ["understand", "know", "want", "need"],
            "intransitive_verbs": ["launch", "succeed", "grow", "trend"],
            "transitive_verbs": ["promote", "advertise", "launch", "brand", "create"],
            "objects": ["campaigns", "brands", "products", "content", "strategies"],
            "adjectives": ["viral", "successful", "creative", "engaging", "innovative"],
            "locations": ["at the agency", "at work", "online"],
            "professions": ["a marketer", "a PR manager", "a strategist"],
            "names": ["David", "Sarah", "Alex", "Jessica"],
            "cities": ["New York", "Los Angeles", "London"],
            "countries": ["the USA", "the UK", "France"],
            "idioms": ["go viral", "brand awareness", "buzz marketing"]
        },
        40: {
            "name": "English for HR",
            "subjects": ["the recruiter", "the HR manager", "the candidate", "the employee"],
            "action_verbs": ["hire", "recruit", "interview", "train", "onboard"],
            "state_verbs": ["understand", "know", "need", "want"],
            "intransitive_verbs": ["apply", "resign", "retire", "succeed"],
            "transitive_verbs": ["hire", "recruit", "interview", "train", "fire"],
            "objects": ["candidates", "employees", "positions", "resumes", "interviews"],
            "adjectives": ["qualified", "experienced", "suitable", "professional", "skilled"],
            "locations": ["at the office", "at the interview", "at work"],
            "professions": ["an HR manager", "a recruiter", "a specialist"],
            "names": ["Karen", "Bob", "Linda", "Steve"],
            "cities": ["Chicago", "London", "Singapore"],
            "countries": ["the USA", "the UK", "Singapore"],
            "idioms": ["headhunt", "get the boot", "hire and fire"]
        }
    }

    def __init__(self, seed: Optional[int] = None):
        """
        Инициализация генератора
        Args:
            seed: Seed для воспроизводимости
        """
        self.seed = seed
        if seed is not None:
            random.seed(seed)

    def _shuffle_options(self, correct: str, wrongs: List[str]) -> Tuple[Dict[str, str], str]:
        """Перемешать варианты ответов"""
        all_options = [correct] + wrongs
        random.shuffle(all_options)
        letters = ["A", "B", "C", "D"]
        options = {letter: option for letter, option in zip(letters, all_options)}
        correct_letter = [k for k, v in options.items() if v == correct][0]
        return options, correct_letter

    # ========================================
    # УРОК 1: gram_10_01 - Основы SPO и порядок слов (7 вопросов)
    # ========================================

    def generate_lesson1_q1(self, topic_id: int) -> Dict:
        """L1Q1: Правильный порядок SPO"""
        topic = self.TOPICS[topic_id]
        
        question = "Какой порядок слов является правильным в английском утвердительном предложении?"
        
        correct = "Subject - Predicate - Object"
        wrong_options = [
            "Object - Subject - Predicate",
            "Predicate - Subject - Object",
            "Subject - Object - Predicate"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "easy",
            "explanation": "In English, the correct word order is Subject - Predicate - Object (SPO). This order is fixed and determines the meaning of the sentence."
        }

    def generate_lesson1_q2(self, topic_id: int) -> Dict:
        """L1Q2: Выбор правильного порядка слов"""
        topic = self.TOPICS[topic_id]
        subject = random.choice(topic["subjects"])
        verb = random.choice(topic["transitive_verbs"])
        obj = random.choice(topic["objects"])
        
        question = "Выберите предложение с правильным порядком слов:"
        
        correct = f"The manager {verb}s {obj}."
        wrong_options = [
            f"{obj.capitalize()} {verb}s the manager.",
            f"{verb.capitalize()}s the manager {obj}.",
            f"The manager {obj} {verb}s."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "easy",
            "explanation": f"The correct word order is Subject (the manager) - Predicate ({verb}s) - Object ({obj})."
        }

    def generate_lesson1_q3(self, topic_id: int) -> Dict:
        """L1Q3: Определение Subject"""
        topic = self.TOPICS[topic_id]
        subject = random.choice(topic["subjects"])
        verb = random.choice(topic["action_verbs"])
        location = random.choice(topic["locations"])
        
        sentence = f"{subject.capitalize()} {verb}s {location}."
        question = f'Что является подлежащим (Subject) в предложении "{sentence}"?'
        
        correct = subject.capitalize()
        wrong_options = [
            f"{verb}s",
            location,
            f"{verb}s {location}"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "easy",
            "explanation": f"The subject is '{subject}' - it answers the question 'Who?' or 'What?' and performs the action."
        }

    def generate_lesson1_q4(self, topic_id: int) -> Dict:
        """L1Q4: Порядок слов меняет смысл"""
        topic = self.TOPICS[topic_id]
        
        question = "Какое из этих предложений демонстрирует, что порядок слов меняет смысл?"
        
        correct = "The cat chased the dog / The dog chased the cat"
        wrong_options = [
            "I eat apples / I eat oranges",
            "She reads books / She writes books",
            "They play football / They watch football"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "medium",
            "explanation": "Changing the word order changes who does the action. 'The cat chased the dog' vs 'The dog chased the cat' have completely different meanings."
        }

    def generate_lesson1_q5(self, topic_id: int) -> Dict:
        """L1Q5: Определение Object"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["transitive_verbs"])
        obj = random.choice(topic["objects"])
        
        sentence = f"They {verb} {obj}."
        question = f'Что является дополнением (Object) в предложении "{sentence}"?'
        
        correct = obj
        wrong_options = [
            "They",
            verb,
            f"{verb} {obj}"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "easy",
            "explanation": f"The object is '{obj}' - it answers the question 'What?' or 'Whom?' and receives the action."
        }

    def generate_lesson1_q6(self, topic_id: int) -> Dict:
        """L1Q6: Тип глагола"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["state_verbs"])
        obj = random.choice(topic["objects"])
        
        sentence = f"We {verb} {obj}."
        question = f'Какой тип глагола используется в предложении "{sentence}"?'
        
        correct = "Глагол состояния"
        wrong_options = [
            "Глагол физического действия",
            "Глагол восприятия",
            "Глагол движения"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "medium",
            "explanation": f"'{verb.capitalize()}' is a state verb (like, love, want, need, prefer) that expresses feelings or states, not actions."
        }

    def generate_lesson1_q7(self, topic_id: int) -> Dict:
        """L1Q7: Определение Predicate"""
        topic = self.TOPICS[topic_id]
        
        question = "Выберите правильное определение для Predicate (сказуемого):"
        
        correct = "Действие или состояние"
        wrong_options = [
            "Кто выполняет действие",
            "На что направлено действие",
            "Место действия"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "easy",
            "explanation": "The predicate (сказуемое) expresses an action or state - it answers the question 'What does the subject do?'"
        }

    # ========================================
    # УРОК 2: gram_10_02 - Подлежащее всегда обязательно (7 вопросов)
    # ========================================

    def generate_lesson2_q1(self, topic_id: int) -> Dict:
        """L2Q1: Выбор правильного предложения с подлежащим"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["state_verbs"])
        obj = random.choice(topic["objects"])
        
        question = "Какое предложение грамматически правильное?"
        
        correct = f"She {verb}s {obj} very much."
        wrong_options = [
            f"{verb.capitalize()}s {obj} very much.",
            f"{obj.capitalize()} {verb}s very much.",
            f"Very much {verb}s {obj}."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": f"In English, the subject is always required. The correct sentence needs 'She' as the subject."
        }

    def generate_lesson2_q2(self, topic_id: int) -> Dict:
        """L2Q2: Перевод безличного предложения"""
        topic = self.TOPICS[topic_id]
        adjective = random.choice(topic["adjectives"])
        
        question = f'Как правильно перевести на английский "Сегодня {adjective}"?'
        
        correct = f"It is {adjective} today."
        wrong_options = [
            f"Is {adjective} today.",
            f"{adjective.capitalize()} is today.",
            f"{adjective.capitalize()} today."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": "For impersonal sentences about weather or conditions, we must use 'it' as a formal subject: 'It is [adjective]'."
        }

    def generate_lesson2_q3(self, topic_id: int) -> Dict:
        """L2Q3: Почему нельзя опустить подлежащее"""
        topic = self.TOPICS[topic_id]
        
        question = "Почему в английском нельзя опустить подлежащее?"
        
        correct = "Потому что окончания глаголов не показывают лицо"
        wrong_options = [
            "Потому что так принято в культуре",
            "Потому что предложение будет слишком коротким",
            "Потому что это правило только для письменной речи"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "medium",
            "explanation": "Unlike Russian, English verb endings don't show the person (I/you/they all use 'love'), so the subject is always required."
        }

    def generate_lesson2_q4(self, topic_id: int) -> Dict:
        """L2Q4: Добавить it в безличное предложение"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(["rains", "snows"])
        
        question = f'Какое слово нужно добавить в предложение "__ {verb} today"?'
        
        correct = "It"
        wrong_options = [
            "He",
            "She",
            "They"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": f"For weather expressions, we use 'it' as a formal subject: 'It {verb} today.'"
        }

    def generate_lesson2_q5(self, topic_id: int) -> Dict:
        """L2Q5: Правильное предложение (Speaks English -> He speaks English)"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["action_verbs"])
        obj = random.choice(topic["objects"])
        
        question = "Выберите правильное предложение:"
        
        correct = f"He {verb}s {obj} daily."
        wrong_options = [
            f"{verb.capitalize()}s {obj} daily.",
            f"{obj.capitalize()} {verb}s daily.",
            f"Daily {verb}s {obj}."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": f"The subject 'He' is required. Without it, we don't know who {verb}s."
        }

    def generate_lesson2_q6(self, topic_id: int) -> Dict:
        """L2Q6: Формальное подлежащее"""
        topic = self.TOPICS[topic_id]
        
        question = "Что используется в качестве формального подлежащего в безличных предложениях?"
        
        correct = "It"
        wrong_options = [
            "This",
            "That",
            "There"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": "In impersonal sentences (weather, time, etc.), we use 'it' as the formal subject: 'It is cold', 'It rains'."
        }

    def generate_lesson2_q7(self, topic_id: int) -> Dict:
        """L2Q7: Исправить ошибку (Is sunny -> It is sunny)"""
        topic = self.TOPICS[topic_id]
        adjective = random.choice(topic["adjectives"])
        
        question = f'Исправьте ошибку: "Is {adjective} today."'
        
        correct = f"It is {adjective} today."
        wrong_options = [
            f"Today is {adjective}.",
            f"{adjective.capitalize()} is today.",
            f"Is it {adjective} today?"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": f"The formal subject 'it' is required: 'It is {adjective} today.'"
        }

    # ========================================
    # УРОК 3: gram_10_03 - Сказуемое всегда обязательно (8 вопросов)
    # ========================================

    def generate_lesson3_q1(self, topic_id: int) -> Dict:
        """L3Q1: Правильное предложение (I am a student)"""
        topic = self.TOPICS[topic_id]
        profession = random.choice(topic["professions"])
        
        question = "Какое предложение грамматически правильное?"
        
        correct = f"I am {profession}."
        wrong_options = [
            f"I {profession}.",
            f"Am I {profession}.",
            f"I a {profession}."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": f"In English, the verb 'to be' is always required, even in the present tense: 'I am {profession}.'"
        }

    def generate_lesson3_q2(self, topic_id: int) -> Dict:
        """L3Q2: Форма to be для They"""
        topic = self.TOPICS[topic_id]
        location = random.choice(topic["locations"])
        
        question = f'Какая форма глагола "to be" нужна в предложении "They __ {location}"?'
        
        correct = "are"
        wrong_options = [
            "am",
            "is",
            "be"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": f"'They' (plural) takes 'are': 'They are {location}.'"
        }

    def generate_lesson3_q3(self, topic_id: int) -> Dict:
        """L3Q3: Исправить ошибку (She happy -> She is happy)"""
        topic = self.TOPICS[topic_id]
        adjective = random.choice(topic["adjectives"])
        idiom = random.choice(topic.get("idioms", ["by the way"]))
        
        question = f'Исправьте ошибку: "{idiom.capitalize()}, she {adjective}."'
        
        correct = f"{idiom.capitalize()}, she is {adjective}."
        wrong_options = [
            f"{adjective.capitalize()} she is.",
            f"She {adjective} is.",
            f"Is she {adjective}?"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": f"The verb 'to be' is required with adjectives: 'She is {adjective}.'"
        }

    def generate_lesson3_q4(self, topic_id: int) -> Dict:
        """L3Q4: Когда нужен to be"""
        topic = self.TOPICS[topic_id]
        
        question = "В каком случае обязательно нужен глагол \"to be\"?"
        
        correct = "При описании состояния, профессии, местонахождения"
        wrong_options = [
            "Только при описании действий",
            "Только в вопросительных предложениях",
            "Только с местоимениями"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "medium",
            "explanation": "The verb 'to be' is required for states (I am happy), professions (She is a teacher), and locations (They are at home)."
        }

    def generate_lesson3_q5(self, topic_id: int) -> Dict:
        """L3Q5: Правильное предложение (He is tall)"""
        topic = self.TOPICS[topic_id]
        adjective = random.choice(topic["adjectives"])
        
        question = "Выберите правильное предложение:"
        
        correct = f"He is {adjective}."
        wrong_options = [
            f"He {adjective}.",
            f"{adjective.capitalize()} he is.",
            f"Is he {adjective}?"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": f"Descriptions require 'to be': 'He is {adjective}.'"
        }

    def generate_lesson3_q6(self, topic_id: int) -> Dict:
        """L3Q6: Форма to be для I"""
        topic = self.TOPICS[topic_id]
        
        question = 'Какая форма глагола "to be" используется с подлежащим "I"?'
        
        correct = "am"
        wrong_options = [
            "is",
            "are",
            "be"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": "'I' always takes 'am': 'I am a student', 'I am happy', 'I am here'."
        }

    def generate_lesson3_q7(self, topic_id: int) -> Dict:
        """L3Q7: Перевод (Они дома -> They are at home)"""
        topic = self.TOPICS[topic_id]
        location = random.choice(topic["locations"])
        
        question = f'Как правильно перевести "Они {location[3:]}"?'  # убираем "at "
        
        correct = f"They are {location}."
        wrong_options = [
            f"They {location}.",
            f"{location.capitalize()} they.",
            f"Are they {location}?"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": f"Locations require 'to be': 'They are {location}.'"
        }

    def generate_lesson3_q8(self, topic_id: int) -> Dict:
        """L3Q8: Типичная ошибка (пропуск to be)"""
        topic = self.TOPICS[topic_id]
        
        question = "Что является типичной ошибкой русскоговорящих?"
        
        correct = "Пропуск глагола \"to be\" в настоящем времени"
        wrong_options = [
            "Использование глагола \"to be\" в настоящем времени",
            "Неправильное произношение глагола \"to be\"",
            "Использование слишком многих глаголов"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "medium",
            "explanation": "Russian speakers often forget 'to be' because in Russian we say 'Я студент' (no verb), but English requires 'I am a student'."
        }

    # ========================================
    # УРОК 4: gram_10_04 - Дополнение не всегда обязательно (8 вопросов)
    # ========================================

    def generate_lesson4_q1(self, topic_id: int) -> Dict:
        """L4Q1: Непереходный глагол"""
        topic = self.TOPICS[topic_id]
        intrans = random.choice(topic["intransitive_verbs"])
        
        question = "Какой глагол является непереходным (не требует дополнения)?"
        
        wrong_verbs = [v for v in topic["transitive_verbs"] if v != intrans]
        correct = intrans
        wrong_options = random.sample(wrong_verbs, 3)
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "medium",
            "explanation": f"'{correct.capitalize()}' is intransitive - it doesn't need an object. You can say 'I {correct}' (complete sentence)."
        }

    def generate_lesson4_q2(self, topic_id: int) -> Dict:
        """L4Q2: Полное предложение"""
        topic = self.TOPICS[topic_id]
        intrans_verb = random.choice(topic["intransitive_verbs"])
        trans_verb = random.choice(topic["transitive_verbs"])
        
        question = "Какое предложение грамматически полное?"
        
        correct = f"She {intrans_verb}s every day."
        wrong_options = [
            f"She {trans_verb}s every day.",
            f"He {trans_verb}s in the morning.",
            f"They {trans_verb} on weekends."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "medium",
            "explanation": f"'{intrans_verb.capitalize()}' is intransitive and doesn't need an object, so the sentence is complete."
        }

    def generate_lesson4_q3(self, topic_id: int) -> Dict:
        """L4Q3: Переходный глагол с дополнением"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["transitive_verbs"])
        obj = random.choice(topic["objects"])
        
        question = "Выберите предложение с переходным глаголом, требующим дополнения:"
        
        intrans_verb = random.choice(topic["intransitive_verbs"])
        correct = f"Tom {verb}s {obj} daily."
        wrong_options = [
            f"Birds {intrans_verb} in the sky.",
            f"Children {intrans_verb} loudly.",
            f"Students {intrans_verb} every day."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "medium",
            "explanation": f"'{verb.capitalize()}' is transitive and requires an object: '{obj}'."
        }

    def generate_lesson4_q4(self, topic_id: int) -> Dict:
        """L4Q4: Как определить нужно ли дополнение"""
        topic = self.TOPICS[topic_id]
        
        question = "Как определить, нужно ли дополнение после глагола?"
        
        correct = "Задав вопрос \"Что?\" или \"Кого?\" после глагола"
        wrong_options = [
            "По длине глагола",
            "По времени глагола",
            "По окончанию глагола"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "medium",
            "explanation": "If you can ask 'What?' or 'Whom?' after the verb, it's transitive and needs an object. If not, it's intransitive."
        }

    def generate_lesson4_q5(self, topic_id: int) -> Dict:
        """L4Q5: Неполное предложение"""
        topic = self.TOPICS[topic_id]
        trans_verb = random.choice(topic["transitive_verbs"])
        intrans_verb = random.choice(topic["intransitive_verbs"])
        
        question = "Какое предложение неполное и требует дополнения?"
        
        correct = f"She {trans_verb}s very well."
        wrong_options = [
            f"The baby {intrans_verb}s peacefully.",
            f"Dogs {intrans_verb} loudly.",
            f"We {intrans_verb} in summer."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "medium",
            "explanation": f"'{trans_verb.capitalize()}' is transitive and needs an object. 'She {trans_verb}s what?'"
        }

    def generate_lesson4_q6(self, topic_id: int) -> Dict:
        """L4Q6: Непереходный глагол из списка"""
        topic = self.TOPICS[topic_id]
        
        question = "Выберите непереходный глагол:"
        
        intrans = random.choice(topic["intransitive_verbs"])
        trans_verbs = random.sample(topic["transitive_verbs"], 3)
        
        correct = intrans
        wrong_options = trans_verbs
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "medium",
            "explanation": f"'{correct.capitalize()}' doesn't need an object - it's a complete action by itself."
        }

    def generate_lesson4_q7(self, topic_id: int) -> Dict:
        """L4Q7: Правильное полное предложение"""
        topic = self.TOPICS[topic_id]
        intrans = random.choice(topic["intransitive_verbs"])
        location = random.choice(topic["locations"])
        trans = random.choice(topic["transitive_verbs"])
        
        question = "Какое из предложений правильное и полное?"
        
        correct = f"I {intrans} {location}."
        wrong_options = [
            f"I {trans} very much.",
            f"She {trans} badly.",
            f"He {trans} quickly."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "easy",
            "explanation": f"'{intrans.capitalize()}' is intransitive, so the sentence is complete without an object."
        }

    def generate_lesson4_q8(self, topic_id: int) -> Dict:
        """L4Q8: Глагол требующий дополнение"""
        topic = self.TOPICS[topic_id]
        
        question = "Какой глагол требует обязательного дополнения?"
        
        trans = random.choice(topic["transitive_verbs"])
        intrans_verbs = random.sample(topic["intransitive_verbs"], 3)
        
        correct = trans
        wrong_options = intrans_verbs
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "medium",
            "explanation": f"'{correct.capitalize()}' is transitive - you must say what you {correct}. You can't just say 'I {correct}'."
        }

    # ========================================
    # УРОК 5: gram_10_05 - Сравнение с русским (7 вопросов)
    # ========================================

    def generate_lesson5_q1(self, topic_id: int) -> Dict:
        """L5Q1: Что определяет смысл в английском"""
        topic = self.TOPICS[topic_id]
        
        question = "Что определяет смысл предложения в английском языке?"
        
        correct = "Порядок слов"
        wrong_options = [
            "Окончания слов",
            "Интонация",
            "Длина предложения"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "easy",
            "explanation": "In English, word order determines meaning. Changing the order changes who does what."
        }

    def generate_lesson5_q2(self, topic_id: int) -> Dict:
        """L5Q2: Порядок слов в русском vs английском"""
        topic = self.TOPICS[topic_id]
        
        question = "Какое утверждение верно?"
        
        correct = "В русском порядок слов свободный, в английском строгий"
        wrong_options = [
            "В русском порядок слов строгий, в английском свободный",
            "В обоих языках порядок слов свободный",
            "В обоих языках порядок слов строгий"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "easy",
            "explanation": "Russian has flexible word order (endings show meaning), while English has fixed word order (position shows meaning)."
        }

    def generate_lesson5_q3(self, topic_id: int) -> Dict:
        """L5Q3: Изменение порядка слов"""
        topic = self.TOPICS[topic_id]
        subject1 = "The cat"
        subject2 = "the dog"
        verb = "chased"
        
        question = f'Что происходит при изменении порядка слов в предложении "{subject1} {verb} {subject2}"?'
        
        correct = "Предложение становится неправильным или меняет смысл"
        wrong_options = [
            "Предложение остается правильным с тем же смыслом",
            "Предложение становится более эмоциональным",
            "Ничего не происходит"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "medium",
            "explanation": f"Changing order changes meaning: '{subject1} {verb} {subject2}' vs '{subject2.capitalize()} {verb} the cat' are different!"
        }

    def generate_lesson5_q4(self, topic_id: int) -> Dict:
        """L5Q4: Почему в русском можно опустить подлежащее"""
        topic = self.TOPICS[topic_id]
        
        question = 'Почему в русском языке можно сказать "Люблю кофе" без подлежащего?'
        
        correct = "Потому что окончание глагола показывает лицо"
        wrong_options = [
            "Потому что это разговорная речь",
            "Потому что дополнение важнее подлежащего",
            "Потому что глагол стоит в начале"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "medium",
            "explanation": "Russian verb endings show the person (люблю = I love, любишь = you love), so the subject can be omitted."
        }

    def generate_lesson5_q5(self, topic_id: int) -> Dict:
        """L5Q5: Одинаковый смысл в русском"""
        topic = self.TOPICS[topic_id]
        
        question = "Какие предложения имеют одинаковый смысл в русском языке?"
        
        correct = "\"Мама любит папу\" и \"Папу любит мама\""
        wrong_options = [
            "\"Мама любит папу\" и \"Папа любит маму\"",
            "\"Мама любит папу\" и \"Мама маму любит\"",
            "\"Мама любит папу\" и \"Любит мама папа\""
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "medium",
            "explanation": "In Russian, word endings show the roles, so 'Мама любит папу' = 'Папу любит мама' (same meaning, different emphasis)."
        }

    def generate_lesson5_q6(self, topic_id: int) -> Dict:
        """L5Q6: Эмоциональное ударение в английском"""
        topic = self.TOPICS[topic_id]
        
        question = "Как создать эмоциональное ударение в английском предложении?"
        
        correct = "Использовать интонацию и усилительные слова"
        wrong_options = [
            "Изменить порядок слов",
            "Убрать подлежащее",
            "Добавить больше дополнений"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "medium",
            "explanation": "English uses intonation and emphasizing words (really, very, so) for emotion, not word order changes."
        }

    def generate_lesson5_q7(self, topic_id: int) -> Dict:
        """L5Q7: Что определяет смысл в русском"""
        topic = self.TOPICS[topic_id]
        
        question = "Что определяет смысл предложения в русском языке?"
        
        correct = "Падежные окончания слов"
        wrong_options = [
            "Порядок слов",
            "Количество слов",
            "Наличие союзов"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "easy",
            "explanation": "Russian uses case endings to show meaning: 'мама' (subject) vs 'маму' (object), allowing flexible word order."
        }

    # ========================================
    # УРОК 6: gram_10_06 - Типичные ошибки (10 вопросов)
    # ========================================

    def generate_lesson6_q1(self, topic_id: int) -> Dict:
        """L6Q1: Исправить неправильный порядок"""
        topic = self.TOPICS[topic_id]
        obj = random.choice(topic["objects"])
        verb = random.choice(topic["state_verbs"])
        
        question = f'Найдите и исправьте ошибку: "{obj.capitalize()} they {verb} very much."'
        
        correct = f"They {verb} {obj} very much."
        wrong_options = [
            f"They {obj} {verb} very much.",
            f"{verb.capitalize()} they {obj} very much.",
            f"Very much they {verb} {obj}."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": f"The correct word order is Subject (they) - Predicate ({verb}) - Object ({obj})."
        }

    def generate_lesson6_q2(self, topic_id: int) -> Dict:
        """L6Q2: Ошибка - пропущено подлежащее"""
        topic = self.TOPICS[topic_id]
        adjective = random.choice(topic["adjectives"])
        
        question = f'Какая ошибка в предложении "Is {adjective} today"?'
        
        correct = "Пропущено подлежащее \"it\""
        wrong_options = [
            "Неправильный порядок слов",
            "Пропущен глагол",
            "Пропущено дополнение"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": f"The formal subject 'it' is missing. Correct: 'It is {adjective} today.'"
        }

    def generate_lesson6_q3(self, topic_id: int) -> Dict:
        """L6Q3: Исправить пропуск to be"""
        topic = self.TOPICS[topic_id]
        adjective = random.choice(topic["adjectives"])
        location = random.choice(topic["locations"])
        
        question = f'Исправьте ошибку: "She {adjective} {location}."'
        
        correct = f"She is {adjective} {location}."
        wrong_options = [
            f"{adjective.capitalize()} she is {location}.",
            f"She {location} is {adjective}.",
            f"She {adjective} is {location}."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": f"The verb 'to be' is required: 'She is {adjective} {location}.'"
        }

    def generate_lesson6_q4(self, topic_id: int) -> Dict:
        """L6Q4: Найти предложение с ошибкой"""
        topic = self.TOPICS[topic_id]
        intrans = random.choice(topic["intransitive_verbs"])
        profession = random.choice(topic["professions"])
        
        question = "Какое предложение содержит ошибку?"
        
        correct = f"I {profession[2:]} at this company."  # убираем "a "
        wrong_options = [
            f"The team {intrans}s quickly.",
            f"She {intrans}s at noon.",
            f"They {intrans} together daily."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "medium",
            "explanation": f"The verb 'to be' is missing. Correct: 'I am {profession} at this company.'"
        }

    def generate_lesson6_q5(self, topic_id: int) -> Dict:
        """L6Q5: Правильный порядок слов"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["action_verbs"])
        obj = random.choice(topic["objects"])
        name = random.choice(topic["names"])
        
        question = "В каком предложении правильный порядок слов?"
        
        correct = f"{name} {verb}s {obj} every weekend."
        wrong_options = [
            f"{obj.capitalize()} {verb}s {name} every weekend.",
            f"{verb.capitalize()}s {name} {obj} every weekend.",
            f"{name} {obj} {verb}s every weekend."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": f"Correct SPO order: Subject ({name}) - Predicate ({verb}s) - Object ({obj})."
        }

    def generate_lesson6_q6(self, topic_id: int) -> Dict:
        """L6Q6: Пропущено подлежащее"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["state_verbs"])
        obj = random.choice(topic["objects"])
        
        question = f'Какая типичная ошибка русскоговорящих в предложении "{verb.capitalize()} {obj}"?'
        
        correct = "Пропущено подлежащее"
        wrong_options = [
            "Неправильное дополнение",
            "Неправильный глагол",
            "Неправильный артикль"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": f"The subject is missing. Correct: 'I {verb} {obj}' or 'We {verb} {obj}'."
        }

    def generate_lesson6_q7(self, topic_id: int) -> Dict:
        """L6Q7: Исправить пропуск to be"""
        topic = self.TOPICS[topic_id]
        adj1 = random.choice(topic["adjectives"])
        adj2 = random.choice([a for a in topic["adjectives"] if a != adj1])
        
        question = f'Исправьте: "He {adj1} and {adj2}."'
        
        correct = f"He is {adj1} and {adj2}."
        wrong_options = [
            f"{adj1.capitalize()} and {adj2} he is.",
            f"He is {adj1} and is {adj2}.",
            f"Is he {adj1} and {adj2}?"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": f"The verb 'to be' is required with adjectives: 'He is {adj1} and {adj2}.'"
        }

    def generate_lesson6_q8(self, topic_id: int) -> Dict:
        """L6Q8: Три вопроса при проверке"""
        topic = self.TOPICS[topic_id]
        
        question = "При проверке предложения какие три вопроса нужно задать?"
        
        correct = "Есть ли подлежащее? Есть ли сказуемое? Нужно ли дополнение?"
        wrong_options = [
            "Где? Когда? Почему?",
            "Длинное ли предложение? Есть ли глагол? Понятно ли?",
            "Правильная ли интонация? Есть ли запятые? Есть ли точка?"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "medium",
            "explanation": "Always check: 1) Is there a subject? 2) Is there a predicate (verb/to be)? 3) Does this verb need an object?"
        }

    def generate_lesson6_q9(self, topic_id: int) -> Dict:
        """L6Q9: Правильное предложение"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["transitive_verbs"])
        obj = random.choice(topic["objects"])
        verb2 = random.choice(topic["state_verbs"])
        
        question = "Какое предложение грамматически правильное?"
        
        correct = f"She {verb}s {obj} every evening."
        wrong_options = [
            f"They friends since childhood.",
            f"{verb.capitalize()}s she {obj} fluently.",
            f"{verb2.capitalize()} I {obj} ice cream."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": f"This sentence has correct SPO order and includes all required elements: subject, predicate, and object."
        }

    def generate_lesson6_q10(self, topic_id: int) -> Dict:
        """L6Q10: Множественное число и порядок"""
        topic = self.TOPICS[topic_id]
        
        question = "Что меняется в структуре SPO при изменении числа (singular/plural)?"
        
        correct = "Порядок слов не меняется"
        wrong_options = [
            "Порядок слов меняется",
            "Появляется дополнительное дополнение",
            "Исчезает подлежащее"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "medium",
            "explanation": "SPO word order remains the same in singular and plural: 'The student reads' vs 'The students read'."
        }

    # ========================================
    # Методы генерации тестов
    # ========================================

    def generate_test_for_lesson(
            self,
            lesson_num: int,
            topic_ids_sequence: List[int],
            num_questions: int = None
    ) -> List[Dict]:
        """
        Генерировать тест для урока
        СИНХРОННЫЙ - НЕ работает с БД!

        Args:
            lesson_num: Номер урока (1-6)
            topic_ids_sequence: [2, 3, 2, 4, ...]  ← ГОТОВЫЙ список топиков
            num_questions: Количество вопросов (по умолчанию все для урока)

        Returns:
            Список вопросов для урока
        """

        # Методы генерации для каждого урока
        lesson_methods = {
            1: [
                self.generate_lesson1_q1, self.generate_lesson1_q2,
                self.generate_lesson1_q3, self.generate_lesson1_q4,
                self.generate_lesson1_q5, self.generate_lesson1_q6,
                self.generate_lesson1_q7
            ],
            2: [
                self.generate_lesson2_q1, self.generate_lesson2_q2,
                self.generate_lesson2_q3, self.generate_lesson2_q4,
                self.generate_lesson2_q5, self.generate_lesson2_q6,
                self.generate_lesson2_q7
            ],
            3: [
                self.generate_lesson3_q1, self.generate_lesson3_q2,
                self.generate_lesson3_q3, self.generate_lesson3_q4,
                self.generate_lesson3_q5, self.generate_lesson3_q6,
                self.generate_lesson3_q7, self.generate_lesson3_q8
            ],
            4: [
                self.generate_lesson4_q1, self.generate_lesson4_q2,
                self.generate_lesson4_q3, self.generate_lesson4_q4,
                self.generate_lesson4_q5, self.generate_lesson4_q6,
                self.generate_lesson4_q7, self.generate_lesson4_q8
            ],
            5: [
                self.generate_lesson5_q1, self.generate_lesson5_q2,
                self.generate_lesson5_q3, self.generate_lesson5_q4,
                self.generate_lesson5_q5, self.generate_lesson5_q6,
                self.generate_lesson5_q7
            ],
            6: [
                self.generate_lesson6_q1, self.generate_lesson6_q2,
                self.generate_lesson6_q3, self.generate_lesson6_q4,
                self.generate_lesson6_q5, self.generate_lesson6_q6,
                self.generate_lesson6_q7, self.generate_lesson6_q8,
                self.generate_lesson6_q9, self.generate_lesson6_q10
            ]
        }

        methods = lesson_methods[lesson_num]
        if num_questions is None:
            num_questions = len(methods)
        
        num = min(num_questions, len(methods), len(topic_ids_sequence))

        questions = []

        for i in range(num):
            topic_id = topic_ids_sequence[i]
            question = methods[i](topic_id)
            question['topic_id'] = topic_id
            questions.append(question)

        return questions

    def _get_lesson_methods(self, lesson_num: int) -> List:
        """Получить методы генерации для урока"""
        lesson_methods = {
            1: [
                self.generate_lesson1_q1, self.generate_lesson1_q2,
                self.generate_lesson1_q3, self.generate_lesson1_q4,
                self.generate_lesson1_q5, self.generate_lesson1_q6,
                self.generate_lesson1_q7
            ],
            2: [
                self.generate_lesson2_q1, self.generate_lesson2_q2,
                self.generate_lesson2_q3, self.generate_lesson2_q4,
                self.generate_lesson2_q5, self.generate_lesson2_q6,
                self.generate_lesson2_q7
            ],
            3: [
                self.generate_lesson3_q1, self.generate_lesson3_q2,
                self.generate_lesson3_q3, self.generate_lesson3_q4,
                self.generate_lesson3_q5, self.generate_lesson3_q6,
                self.generate_lesson3_q7, self.generate_lesson3_q8
            ],
            4: [
                self.generate_lesson4_q1, self.generate_lesson4_q2,
                self.generate_lesson4_q3, self.generate_lesson4_q4,
                self.generate_lesson4_q5, self.generate_lesson4_q6,
                self.generate_lesson4_q7, self.generate_lesson4_q8
            ],
            5: [
                self.generate_lesson5_q1, self.generate_lesson5_q2,
                self.generate_lesson5_q3, self.generate_lesson5_q4,
                self.generate_lesson5_q5, self.generate_lesson5_q6,
                self.generate_lesson5_q7
            ],
            6: [
                self.generate_lesson6_q1, self.generate_lesson6_q2,
                self.generate_lesson6_q3, self.generate_lesson6_q4,
                self.generate_lesson6_q5, self.generate_lesson6_q6,
                self.generate_lesson6_q7, self.generate_lesson6_q8,
                self.generate_lesson6_q9, self.generate_lesson6_q10
            ]
        }
        return lesson_methods[lesson_num]

    def generate_full_module_test(
            self,
            topic_ids_sequence: List[int],
            num_questions: int = 56
    ) -> List[Dict]:
        """
        Генерировать полный тест по модулю
        СИНХРОННЫЙ - НЕ работает с БД!

        Args:
            topic_ids_sequence: [2, 3, 2, 4, ...]  ← ГОТОВЫЙ список (56 топиков)
            num_questions: Количество вопросов (по умолчанию 56)

        Returns:
            Список из 56 вопросов (БЕЗ topic_name!)
        """

        # Собираем все методы генерации
        all_methods = []
        for lesson_num in range(1, 7):
            all_methods.extend(self._get_lesson_methods(lesson_num))

        # Перемешиваем для разнообразия
        random.shuffle(all_methods)

        all_questions = []

        for i in range(min(num_questions, len(all_methods), len(topic_ids_sequence))):
            topic_id = topic_ids_sequence[i]
            method = all_methods[i]

            question = method(topic_id)
            question['topic_id'] = topic_id
            all_questions.append(question)

        return all_questions
