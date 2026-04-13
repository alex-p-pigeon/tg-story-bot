import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from .base_generator import BaseQuestionGenerator


class ArticlesQuestionGenerator(BaseQuestionGenerator):
    """
    Динамический генератор вопросов по артиклям (Articles)
    Создает уникальные вопросы для каждой темы интересов
    56 вопросов (распределение: 6 + 8 + 8 + 8 + 8 + 8 + 10 по урокам)
    """

    # Темы интересов с расширенными словарями
    TOPICS = {
        2: {
            "name": "Shopping and money",
            "professions": ["a cashier", "a manager", "a seller", "a buyer", "a shopkeeper", "a customer"],
            "singular_countable": ["a product", "a cart", "a bag", "a receipt", "a card", "a wallet"],
            "plural_nouns": ["products", "prices", "customers", "stores", "shops", "markets"],
            "uncountable_nouns": ["money", "cash", "information", "advice", "shopping"],
            "specific_places": ["the store", "the mall", "the shop", "the market", "the checkout"],
            "sports": ["shopping", "bargaining"],
            "instruments": ["the calculator", "the register"],
            "countries": ["Spain", "Germany", "France", "Italy"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["Madrid", "Berlin", "Paris", "Rome"],
            "rivers": ["the Rhine", "the Thames"],
            "mountains": ["Mount Blanc"],
            "mountain_ranges": ["the Alps", "the Pyrenees"],
            "adjectives": ["expensive", "cheap", "good", "bad", "popular"],
            "idioms_prefix": ["By the way", "In fact", "To tell the truth"]
        },
        3: {
            "name": "Weather and nature",
            "professions": ["a meteorologist", "a farmer", "a gardener", "a botanist", "a geologist"],
            "singular_countable": ["a cloud", "a tree", "a flower", "a plant", "a mountain"],
            "plural_nouns": ["clouds", "trees", "flowers", "plants", "forests"],
            "uncountable_nouns": ["weather", "rain", "snow", "air", "nature"],
            "specific_places": ["the park", "the forest", "the beach", "the garden"],
            "sports": ["hiking", "climbing", "camping"],
            "instruments": ["the thermometer", "the barometer"],
            "countries": ["Canada", "Norway", "Iceland", "Switzerland"],
            "countries_with_the": ["the United States", "the Netherlands"],
            "cities": ["Toronto", "Oslo", "Reykjavik", "Geneva"],
            "rivers": ["the Amazon", "the Nile", "the Mississippi"],
            "mountains": ["Mount Everest", "Mount Fuji"],
            "mountain_ranges": ["the Himalayas", "the Andes", "the Rocky Mountains"],
            "adjectives": ["sunny", "rainy", "beautiful", "cold", "hot"],
            "idioms_prefix": ["Speaking of weather", "By the way", "Honestly"]
        },
        4: {
            "name": "Health and medicine",
            "professions": ["a doctor", "a nurse", "a surgeon", "a therapist", "a pharmacist"],
            "singular_countable": ["a pill", "a tablet", "a symptom", "a treatment", "a prescription"],
            "plural_nouns": ["pills", "tablets", "symptoms", "doctors", "patients"],
            "uncountable_nouns": ["health", "medicine", "advice", "information", "treatment"],
            "specific_places": ["the hospital", "the clinic", "the pharmacy", "the doctor's office"],
            "sports": ["jogging", "swimming", "yoga"],
            "instruments": ["the stethoscope", "the thermometer"],
            "countries": ["Switzerland", "Sweden", "Japan", "Singapore"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["Geneva", "Stockholm", "Tokyo", "Singapore"],
            "rivers": ["the Seine", "the Danube"],
            "mountains": ["Mount Fuji"],
            "mountain_ranges": ["the Alps"],
            "adjectives": ["healthy", "sick", "good", "effective", "strong"],
            "idioms_prefix": ["To be honest", "Actually", "In my opinion"]
        },
        5: {
            "name": "Home and daily routines",
            "professions": ["a housewife", "a housekeeper", "a cleaner", "a cook", "a nanny"],
            "singular_countable": ["a room", "a bed", "a table", "a chair", "a sofa"],
            "plural_nouns": ["rooms", "beds", "tables", "chairs", "dishes"],
            "uncountable_nouns": ["furniture", "water", "food", "time", "space"],
            "specific_places": ["the kitchen", "the bathroom", "the bedroom", "the living room"],
            "sports": ["cleaning", "cooking", "gardening"],
            "instruments": ["the vacuum cleaner", "the washing machine"],
            "countries": ["Sweden", "Denmark", "Finland", "Norway"],
            "countries_with_the": ["the Netherlands"],
            "cities": ["Stockholm", "Copenhagen", "Helsinki", "Oslo"],
            "rivers": ["the Thames", "the Seine"],
            "mountains": ["Mount Blanc"],
            "mountain_ranges": ["the Alps", "the Carpathians"],
            "adjectives": ["clean", "dirty", "comfortable", "cozy", "modern"],
            "idioms_prefix": ["By the way", "Actually", "To tell the truth"]
        },
        6: {
            "name": "Transportation and directions",
            "professions": ["a driver", "a pilot", "a conductor", "a mechanic", "a taxi driver"],
            "singular_countable": ["a car", "a bus", "a train", "a ticket", "a map"],
            "plural_nouns": ["cars", "buses", "trains", "tickets", "routes"],
            "uncountable_nouns": ["traffic", "transportation", "information", "fuel"],
            "specific_places": ["the station", "the airport", "the bus stop", "the parking lot"],
            "sports": ["driving", "cycling", "running"],
            "instruments": ["the GPS", "the compass"],
            "countries": ["France", "Spain", "Italy", "Germany"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["Paris", "Madrid", "Rome", "Berlin"],
            "rivers": ["the Seine", "the Thames", "the Rhine"],
            "mountains": ["Mount Vesuvius"],
            "mountain_ranges": ["the Alps", "the Pyrenees"],
            "adjectives": ["fast", "slow", "convenient", "expensive", "direct"],
            "idioms_prefix": ["By the way", "Speaking of which", "Actually"]
        },
        7: {
            "name": "Leisure and hobbies",
            "professions": ["an artist", "a musician", "a photographer", "a writer", "a gamer"],
            "singular_countable": ["a hobby", "a book", "a game", "a movie", "a photo"],
            "plural_nouns": ["hobbies", "books", "games", "movies", "photos"],
            "uncountable_nouns": ["music", "art", "time", "entertainment", "fun"],
            "specific_places": ["the cinema", "the theater", "the museum", "the gallery"],
            "sports": ["football", "tennis", "basketball", "swimming"],
            "instruments": ["the guitar", "the piano", "the violin", "the drums"],
            "countries": ["France", "Italy", "Spain", "Japan"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["Paris", "Rome", "Madrid", "Tokyo"],
            "rivers": ["the Seine", "the Tiber"],
            "mountains": ["Mount Fuji"],
            "mountain_ranges": ["the Alps"],
            "adjectives": ["interesting", "boring", "exciting", "relaxing", "creative"],
            "idioms_prefix": ["By the way", "Actually", "To be honest"]
        },
        8: {
            "name": "Relationships and emotions",
            "professions": ["a psychologist", "a therapist", "a counselor", "a friend", "a partner"],
            "singular_countable": ["a friend", "a partner", "a colleague", "a relationship", "a feeling"],
            "plural_nouns": ["friends", "partners", "colleagues", "relationships", "feelings"],
            "uncountable_nouns": ["love", "happiness", "sadness", "anger", "trust"],
            "specific_places": ["the cafe", "the restaurant", "the park", "the beach"],
            "sports": ["dating", "socializing"],
            "instruments": ["the phone", "the computer"],
            "countries": ["France", "Italy", "Spain", "Greece"],
            "countries_with_the": ["the United States"],
            "cities": ["Paris", "Rome", "Barcelona", "Athens"],
            "rivers": ["the Seine", "the Tiber"],
            "mountains": ["Mount Olympus"],
            "mountain_ranges": ["the Alps"],
            "adjectives": ["happy", "sad", "angry", "emotional", "close"],
            "idioms_prefix": ["To be honest", "Actually", "Speaking frankly"]
        },
        9: {
            "name": "Technology and gadgets",
            "professions": ["an engineer", "a programmer", "a developer", "a technician", "an IT specialist"],
            "singular_countable": ["a computer", "a phone", "a tablet", "a laptop", "a gadget"],
            "plural_nouns": ["computers", "phones", "tablets", "laptops", "gadgets"],
            "uncountable_nouns": ["technology", "software", "information", "data", "internet"],
            "specific_places": ["the office", "the lab", "the store", "the repair shop"],
            "sports": ["gaming", "coding"],
            "instruments": ["the keyboard", "the mouse"],
            "countries": ["Japan", "South Korea", "Taiwan", "Singapore"],
            "countries_with_the": ["the United States"],
            "cities": ["Tokyo", "Seoul", "Taipei", "Singapore"],
            "rivers": ["the Han", "the Sumida"],
            "mountains": ["Mount Fuji"],
            "mountain_ranges": ["the Japanese Alps"],
            "adjectives": ["modern", "advanced", "innovative", "smart", "powerful"],
            "idioms_prefix": ["By the way", "Speaking of tech", "Actually"]
        },
        11: {
            "name": "Job interviews and CVs",
            "professions": ["an interviewer", "a recruiter", "a candidate", "an HR manager", "an applicant"],
            "singular_countable": ["a CV", "a resume", "an interview", "a job", "a position"],
            "plural_nouns": ["CVs", "resumes", "interviews", "jobs", "positions"],
            "uncountable_nouns": ["experience", "work", "information", "advice", "feedback"],
            "specific_places": ["the office", "the interview room", "the company", "the building"],
            "sports": ["networking"],
            "instruments": ["the computer", "the printer"],
            "countries": ["Germany", "France", "Spain", "Italy"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["Berlin", "Paris", "Madrid", "Rome"],
            "rivers": ["the Thames", "the Seine"],
            "mountains": ["Mount Blanc"],
            "mountain_ranges": ["the Alps"],
            "adjectives": ["qualified", "experienced", "suitable", "strong", "impressive"],
            "idioms_prefix": ["To be honest", "Actually", "By the way"]
        },
        12: {
            "name": "Meetings and negotiations",
            "professions": ["a manager", "a director", "a negotiator", "a mediator", "a consultant"],
            "singular_countable": ["a meeting", "a proposal", "an agreement", "a contract", "a deal"],
            "plural_nouns": ["meetings", "proposals", "agreements", "contracts", "deals"],
            "uncountable_nouns": ["business", "information", "time", "progress", "work"],
            "specific_places": ["the office", "the conference room", "the boardroom", "the hotel"],
            "sports": ["negotiating"],
            "instruments": ["the projector", "the microphone"],
            "countries": ["Germany", "Japan", "China", "Singapore"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["Berlin", "Tokyo", "Shanghai", "Singapore"],
            "rivers": ["the Rhine", "the Thames"],
            "mountains": ["Mount Fuji"],
            "mountain_ranges": ["the Alps"],
            "adjectives": ["successful", "productive", "important", "difficult", "long"],
            "idioms_prefix": ["By the way", "Speaking of business", "Actually"]
        },
        13: {
            "name": "Presentations and public speaking",
            "professions": ["a speaker", "a presenter", "a lecturer", "a trainer", "an orator"],
            "singular_countable": ["a presentation", "a speech", "a slide", "a microphone", "an audience"],
            "plural_nouns": ["presentations", "speeches", "slides", "audiences", "speakers"],
            "uncountable_nouns": ["information", "knowledge", "confidence", "practice", "feedback"],
            "specific_places": ["the stage", "the auditorium", "the conference hall", "the room"],
            "sports": ["public speaking"],
            "instruments": ["the microphone", "the projector"],
            "countries": ["USA", "UK", "Germany", "France"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["New York", "London", "Berlin", "Paris"],
            "rivers": ["the Thames", "the Seine"],
            "mountains": ["Mount Blanc"],
            "mountain_ranges": ["the Alps"],
            "adjectives": ["confident", "nervous", "clear", "engaging", "persuasive"],
            "idioms_prefix": ["By the way", "Speaking of presentations", "To be honest"]
        },
        14: {
            "name": "Emails and business correspondence",
            "professions": ["an assistant", "a manager", "a secretary", "a correspondent", "a coordinator"],
            "singular_countable": ["an email", "a letter", "a message", "an attachment", "a reply"],
            "plural_nouns": ["emails", "letters", "messages", "attachments", "replies"],
            "uncountable_nouns": ["correspondence", "information", "mail", "communication", "work"],
            "specific_places": ["the office", "the desk", "the computer", "the inbox"],
            "sports": ["typing", "writing"],
            "instruments": ["the computer", "the keyboard"],
            "countries": ["Germany", "France", "Spain", "Italy"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["Berlin", "Paris", "Madrid", "Rome"],
            "rivers": ["the Rhine", "the Seine"],
            "mountains": ["Mount Blanc"],
            "mountain_ranges": ["the Alps"],
            "adjectives": ["formal", "polite", "clear", "concise", "professional"],
            "idioms_prefix": ["By the way", "Actually", "To be frank"]
        },
        15: {
            "name": "Office communication and teamwork",
            "professions": ["a colleague", "a teammate", "a manager", "a supervisor", "a coordinator"],
            "singular_countable": ["a team", "a project", "a task", "a deadline", "a meeting"],
            "plural_nouns": ["teams", "projects", "tasks", "deadlines", "meetings"],
            "uncountable_nouns": ["teamwork", "communication", "cooperation", "work", "progress"],
            "specific_places": ["the office", "the workplace", "the desk", "the break room"],
            "sports": ["teamwork"],
            "instruments": ["the computer", "the phone"],
            "countries": ["Germany", "Japan", "USA", "UK"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["Berlin", "Tokyo", "New York", "London"],
            "rivers": ["the Rhine", "the Thames"],
            "mountains": ["Mount Fuji"],
            "mountain_ranges": ["the Alps"],
            "adjectives": ["cooperative", "collaborative", "efficient", "productive", "supportive"],
            "idioms_prefix": ["By the way", "Speaking of teamwork", "Actually"]
        },
        16: {
            "name": "Project management vocabulary",
            "professions": ["a manager", "a coordinator", "a planner", "a director", "a supervisor"],
            "singular_countable": ["a project", "a plan", "a task", "a milestone", "a deadline"],
            "plural_nouns": ["projects", "plans", "tasks", "milestones", "deadlines"],
            "uncountable_nouns": ["management", "progress", "work", "time", "planning"],
            "specific_places": ["the office", "the project room", "the site", "the building"],
            "sports": ["planning", "organizing"],
            "instruments": ["the computer", "the planner"],
            "countries": ["Germany", "USA", "UK", "Japan"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["Berlin", "New York", "London", "Tokyo"],
            "rivers": ["the Rhine", "the Thames"],
            "mountains": ["Mount Fuji"],
            "mountain_ranges": ["the Alps"],
            "adjectives": ["important", "urgent", "critical", "complete", "successful"],
            "idioms_prefix": ["By the way", "Speaking of projects", "Actually"]
        },
        17: {
            "name": "Customer service and support",
            "professions": ["a representative", "an agent", "a specialist", "a consultant", "a supporter"],
            "singular_countable": ["a customer", "a client", "a request", "a complaint", "a solution"],
            "plural_nouns": ["customers", "clients", "requests", "complaints", "solutions"],
            "uncountable_nouns": ["service", "support", "help", "assistance", "information"],
            "specific_places": ["the office", "the call center", "the desk", "the counter"],
            "sports": ["helping"],
            "instruments": ["the phone", "the computer"],
            "countries": ["USA", "UK", "India", "Philippines"],
            "countries_with_the": ["the United States", "the United Kingdom", "the Philippines"],
            "cities": ["New York", "London", "Mumbai", "Manila"],
            "rivers": ["the Thames", "the Ganges"],
            "mountains": ["Mount Everest"],
            "mountain_ranges": ["the Himalayas"],
            "adjectives": ["helpful", "patient", "polite", "efficient", "quick"],
            "idioms_prefix": ["By the way", "Speaking of service", "Actually"]
        },
        18: {
            "name": "Marketing and sales English",
            "professions": ["a marketer", "a salesperson", "a manager", "an analyst", "a strategist"],
            "singular_countable": ["a campaign", "a product", "a sale", "a customer", "a target"],
            "plural_nouns": ["campaigns", "products", "sales", "customers", "targets"],
            "uncountable_nouns": ["marketing", "advertising", "promotion", "business", "research"],
            "specific_places": ["the office", "the market", "the store", "the showroom"],
            "sports": ["selling", "promoting"],
            "instruments": ["the computer", "the phone"],
            "countries": ["USA", "UK", "Germany", "France"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["New York", "London", "Berlin", "Paris"],
            "rivers": ["the Thames", "the Seine"],
            "mountains": ["Mount Blanc"],
            "mountain_ranges": ["the Alps"],
            "adjectives": ["successful", "effective", "creative", "innovative", "profitable"],
            "idioms_prefix": ["By the way", "Speaking of sales", "Actually"]
        },
        20: {
            "name": "At the airport and hotel",
            "professions": ["a receptionist", "a porter", "a pilot", "a steward", "a concierge"],
            "singular_countable": ["a ticket", "a passport", "a room", "a flight", "a key"],
            "plural_nouns": ["tickets", "passports", "rooms", "flights", "keys"],
            "uncountable_nouns": ["luggage", "baggage", "information", "service", "accommodation"],
            "specific_places": ["the airport", "the hotel", "the lobby", "the check-in"],
            "sports": ["traveling"],
            "instruments": ["the scanner", "the phone"],
            "countries": ["France", "Spain", "Italy", "Greece"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["Paris", "Madrid", "Rome", "Athens"],
            "rivers": ["the Seine", "the Tiber"],
            "mountains": ["Mount Olympus"],
            "mountain_ranges": ["the Alps"],
            "adjectives": ["comfortable", "convenient", "expensive", "nice", "clean"],
            "idioms_prefix": ["By the way", "Speaking of travel", "Actually"]
        },
        21: {
            "name": "Sightseeing and excursions",
            "professions": ["a guide", "a tourist", "a traveler", "an explorer", "a visitor"],
            "singular_countable": ["a tour", "a museum", "a monument", "a ticket", "a camera"],
            "plural_nouns": ["tours", "museums", "monuments", "tickets", "cameras"],
            "uncountable_nouns": ["sightseeing", "tourism", "culture", "history", "information"],
            "specific_places": ["the museum", "the gallery", "the castle", "the square"],
            "sports": ["sightseeing", "exploring"],
            "instruments": ["the camera", "the phone"],
            "countries": ["France", "Italy", "Spain", "Greece"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["Paris", "Rome", "Barcelona", "Athens"],
            "rivers": ["the Seine", "the Tiber", "the Thames"],
            "mountains": ["Mount Vesuvius", "Mount Olympus"],
            "mountain_ranges": ["the Alps"],
            "adjectives": ["beautiful", "historic", "famous", "ancient", "impressive"],
            "idioms_prefix": ["By the way", "Speaking of sightseeing", "Actually"]
        },
        22: {
            "name": "Emergencies abroad",
            "professions": ["a doctor", "a police officer", "an officer", "a consular", "a helper"],
            "singular_countable": ["an emergency", "a problem", "a hospital", "an accident", "a situation"],
            "plural_nouns": ["emergencies", "problems", "hospitals", "accidents", "situations"],
            "uncountable_nouns": ["help", "assistance", "medicine", "care", "information"],
            "specific_places": ["the hospital", "the embassy", "the police station", "the clinic"],
            "sports": ["helping"],
            "instruments": ["the phone", "the radio"],
            "countries": ["France", "Spain", "Italy", "Germany"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["Paris", "Madrid", "Rome", "Berlin"],
            "rivers": ["the Seine", "the Thames"],
            "mountains": ["Mount Blanc"],
            "mountain_ranges": ["the Alps"],
            "adjectives": ["serious", "urgent", "dangerous", "critical", "safe"],
            "idioms_prefix": ["By the way", "To be honest", "Actually"]
        },
        23: {
            "name": "Cultural etiquette and customs",
            "professions": ["a diplomat", "an ambassador", "a guide", "a consultant", "a teacher"],
            "singular_countable": ["a custom", "a tradition", "a rule", "a manner", "a gesture"],
            "plural_nouns": ["customs", "traditions", "rules", "manners", "gestures"],
            "uncountable_nouns": ["culture", "etiquette", "respect", "politeness", "knowledge"],
            "specific_places": ["the embassy", "the office", "the restaurant", "the home"],
            "sports": ["learning"],
            "instruments": ["the book", "the guide"],
            "countries": ["Japan", "China", "India", "Saudi Arabia"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["Tokyo", "Beijing", "Delhi", "Riyadh"],
            "rivers": ["the Ganges", "the Yellow River"],
            "mountains": ["Mount Fuji", "Mount Everest"],
            "mountain_ranges": ["the Himalayas"],
            "adjectives": ["polite", "respectful", "appropriate", "traditional", "cultural"],
            "idioms_prefix": ["By the way", "Speaking of culture", "To be honest"]
        },
        24: {
            "name": "Talking about countries and nationalities",
            "professions": ["a diplomat", "an ambassador", "a guide", "a teacher", "a translator"],
            "singular_countable": ["a country", "a nationality", "a language", "a passport", "a citizen"],
            "plural_nouns": ["countries", "nationalities", "languages", "passports", "citizens"],
            "uncountable_nouns": ["geography", "culture", "knowledge", "information", "diversity"],
            "specific_places": ["the embassy", "the border", "the airport", "the office"],
            "sports": ["traveling"],
            "instruments": ["the map", "the globe"],
            "countries": ["France", "Germany", "Spain", "Italy", "Japan", "China"],
            "countries_with_the": ["the United States", "the United Kingdom", "the Netherlands", "the Philippines"],
            "cities": ["Paris", "Berlin", "Madrid", "Rome", "Tokyo", "Beijing"],
            "rivers": ["the Thames", "the Seine", "the Rhine", "the Danube"],
            "mountains": ["Mount Everest", "Mount Fuji", "Mount Kilimanjaro"],
            "mountain_ranges": ["the Alps", "the Himalayas", "the Andes"],
            "adjectives": ["international", "diverse", "multicultural", "foreign", "native"],
            "idioms_prefix": ["By the way", "Speaking of countries", "Actually"]
        },
        26: {
            "name": "Idioms",
            "professions": ["a teacher", "a linguist", "a translator", "an interpreter", "a tutor"],
            "singular_countable": ["an idiom", "a phrase", "an expression", "a saying", "a proverb"],
            "plural_nouns": ["idioms", "phrases", "expressions", "sayings", "proverbs"],
            "uncountable_nouns": ["language", "knowledge", "wisdom", "understanding", "practice"],
            "specific_places": ["the classroom", "the library", "the office", "the cafe"],
            "sports": ["learning", "studying"],
            "instruments": ["the book", "the dictionary"],
            "countries": ["USA", "UK", "Canada", "Australia"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["New York", "London", "Toronto", "Sydney"],
            "rivers": ["the Thames", "the Hudson"],
            "mountains": ["Mount Rushmore"],
            "mountain_ranges": ["the Rocky Mountains"],
            "adjectives": ["idiomatic", "common", "useful", "interesting", "colorful"],
            "idioms_prefix": ["By the way", "Speaking of idioms", "To cut a long story short", "At the end of the day"]
        },
        27: {
            "name": "Slang",
            "professions": ["a linguist", "a teacher", "a translator", "a native speaker", "a tutor"],
            "singular_countable": ["a word", "a phrase", "an expression", "a term", "a slang"],
            "plural_nouns": ["words", "phrases", "expressions", "terms", "slangs"],
            "uncountable_nouns": ["slang", "language", "speech", "vocabulary", "usage"],
            "specific_places": ["the street", "the cafe", "the bar", "the club"],
            "sports": ["chatting", "talking"],
            "instruments": ["the phone", "the computer"],
            "countries": ["USA", "UK", "Australia", "Canada"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["New York", "London", "Sydney", "Toronto"],
            "rivers": ["the Thames", "the Hudson"],
            "mountains": ["Mount Rushmore"],
            "mountain_ranges": ["the Rocky Mountains"],
            "adjectives": ["informal", "casual", "colloquial", "modern", "cool"],
            "idioms_prefix": ["Yo", "Hey", "Honestly", "No kidding"]
        },
        28: {
            "name": "Phrasal verbs",
            "professions": ["a teacher", "a linguist", "a tutor", "a trainer", "an instructor"],
            "singular_countable": ["a verb", "a particle", "a meaning", "a sentence", "an example"],
            "plural_nouns": ["verbs", "particles", "meanings", "sentences", "examples"],
            "uncountable_nouns": ["grammar", "language", "knowledge", "practice", "usage"],
            "specific_places": ["the classroom", "the office", "the library", "the school"],
            "sports": ["learning", "studying"],
            "instruments": ["the book", "the dictionary"],
            "countries": ["USA", "UK", "Canada", "Australia"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["New York", "London", "Toronto", "Sydney"],
            "rivers": ["the Thames", "the Hudson"],
            "mountains": ["Mount Rushmore"],
            "mountain_ranges": ["the Rocky Mountains"],
            "adjectives": ["important", "common", "useful", "difficult", "practical"],
            "idioms_prefix": ["By the way", "Speaking of phrasal verbs", "Actually"]
        },
        29: {
            "name": "Collocations and word patterns",
            "professions": ["a teacher", "a linguist", "a tutor", "an editor", "a writer"],
            "singular_countable": ["a collocation", "a pattern", "a word", "a combination", "an example"],
            "plural_nouns": ["collocations", "patterns", "words", "combinations", "examples"],
            "uncountable_nouns": ["language", "vocabulary", "knowledge", "practice", "fluency"],
            "specific_places": ["the classroom", "the library", "the office", "the school"],
            "sports": ["learning", "practicing"],
            "instruments": ["the dictionary", "the book"],
            "countries": ["USA", "UK", "Canada", "Australia"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["New York", "London", "Toronto", "Sydney"],
            "rivers": ["the Thames", "the Hudson"],
            "mountains": ["Mount Rushmore"],
            "mountain_ranges": ["the Rocky Mountains"],
            "adjectives": ["natural", "common", "strong", "appropriate", "correct"],
            "idioms_prefix": ["By the way", "Speaking of collocations", "Actually"]
        },
        30: {
            "name": "Figurative language and metaphors",
            "professions": ["a writer", "a poet", "a teacher", "an author", "a linguist"],
            "singular_countable": ["a metaphor", "a symbol", "an image", "a comparison", "a figure"],
            "plural_nouns": ["metaphors", "symbols", "images", "comparisons", "figures"],
            "uncountable_nouns": ["language", "literature", "poetry", "creativity", "imagination"],
            "specific_places": ["the library", "the classroom", "the study", "the office"],
            "sports": ["writing", "reading"],
            "instruments": ["the pen", "the computer"],
            "countries": ["USA", "UK", "France", "Italy"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["New York", "London", "Paris", "Rome"],
            "rivers": ["the Thames", "the Seine"],
            "mountains": ["Mount Parnassus"],
            "mountain_ranges": ["the Alps"],
            "adjectives": ["figurative", "poetic", "creative", "beautiful", "expressive"],
            "idioms_prefix": ["By the way", "Speaking metaphorically", "Actually"]
        },
        31: {
            "name": "Synonyms, antonyms, and nuance",
            "professions": ["a linguist", "a teacher", "a translator", "an editor", "a writer"],
            "singular_countable": ["a synonym", "an antonym", "a word", "a meaning", "a nuance"],
            "plural_nouns": ["synonyms", "antonyms", "words", "meanings", "nuances"],
            "uncountable_nouns": ["vocabulary", "language", "knowledge", "understanding", "precision"],
            "specific_places": ["the classroom", "the library", "the office", "the study"],
            "sports": ["learning", "studying"],
            "instruments": ["the dictionary", "the thesaurus"],
            "countries": ["USA", "UK", "Canada", "Australia"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["New York", "London", "Toronto", "Sydney"],
            "rivers": ["the Thames", "the Hudson"],
            "mountains": ["Mount Rushmore"],
            "mountain_ranges": ["the Rocky Mountains"],
            "adjectives": ["precise", "subtle", "important", "different", "similar"],
            "idioms_prefix": ["By the way", "Speaking of words", "Actually"]
        },
        32: {
            "name": "Register and tone (formal vs informal)",
            "professions": ["a linguist", "a teacher", "a trainer", "a consultant", "a diplomat"],
            "singular_countable": ["a register", "a tone", "a style", "a context", "a situation"],
            "plural_nouns": ["registers", "tones", "styles", "contexts", "situations"],
            "uncountable_nouns": ["language", "formality", "politeness", "communication", "appropriateness"],
            "specific_places": ["the office", "the classroom", "the conference", "the meeting"],
            "sports": ["speaking", "communicating"],
            "instruments": ["the microphone", "the phone"],
            "countries": ["USA", "UK", "Japan", "Germany"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["New York", "London", "Tokyo", "Berlin"],
            "rivers": ["the Thames", "the Rhine"],
            "mountains": ["Mount Fuji"],
            "mountain_ranges": ["the Alps"],
            "adjectives": ["formal", "informal", "polite", "casual", "appropriate"],
            "idioms_prefix": ["By the way", "Speaking formally", "To be honest"]
        },
        33: {
            "name": "Common grammar pitfalls",
            "professions": ["a teacher", "a tutor", "a linguist", "an editor", "an instructor"],
            "singular_countable": ["a mistake", "an error", "a rule", "a pitfall", "a problem"],
            "plural_nouns": ["mistakes", "errors", "rules", "pitfalls", "problems"],
            "uncountable_nouns": ["grammar", "knowledge", "practice", "accuracy", "attention"],
            "specific_places": ["the classroom", "the office", "the library", "the school"],
            "sports": ["learning", "studying"],
            "instruments": ["the book", "the computer"],
            "countries": ["USA", "UK", "Canada", "Australia"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["New York", "London", "Toronto", "Sydney"],
            "rivers": ["the Thames", "the Hudson"],
            "mountains": ["Mount Rushmore"],
            "mountain_ranges": ["the Rocky Mountains"],
            "adjectives": ["common", "typical", "frequent", "important", "careful"],
            "idioms_prefix": ["By the way", "Speaking of grammar", "Actually"]
        },
        35: {
            "name": "English for IT",
            "professions": ["a programmer", "a developer", "an engineer", "a technician", "an analyst"],
            "singular_countable": ["a computer", "a server", "a database", "a program", "a system"],
            "plural_nouns": ["computers", "servers", "databases", "programs", "systems"],
            "uncountable_nouns": ["software", "hardware", "data", "information", "technology"],
            "specific_places": ["the office", "the lab", "the server room", "the data center"],
            "sports": ["coding", "programming"],
            "instruments": ["the keyboard", "the mouse"],
            "countries": ["USA", "India", "China", "Japan"],
            "countries_with_the": ["the United States"],
            "cities": ["Silicon Valley", "Bangalore", "Beijing", "Tokyo"],
            "rivers": ["the Ganges", "the Yellow River"],
            "mountains": ["Mount Fuji"],
            "mountain_ranges": ["the Himalayas"],
            "adjectives": ["digital", "technical", "advanced", "modern", "efficient"],
            "idioms_prefix": ["By the way", "Speaking of IT", "Actually"]
        },
        36: {
            "name": "English for Finance / Accounting",
            "professions": ["an accountant", "a banker", "an analyst", "a consultant", "an auditor"],
            "singular_countable": ["a bank", "an account", "a transaction", "a statement", "a budget"],
            "plural_nouns": ["banks", "accounts", "transactions", "statements", "budgets"],
            "uncountable_nouns": ["money", "finance", "capital", "accounting", "investment"],
            "specific_places": ["the bank", "the office", "the stock exchange", "the branch"],
            "sports": ["investing", "trading"],
            "instruments": ["the calculator", "the computer"],
            "countries": ["USA", "UK", "Switzerland", "Singapore"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["New York", "London", "Zurich", "Singapore"],
            "rivers": ["the Thames", "the Hudson"],
            "mountains": ["Mount Rushmore"],
            "mountain_ranges": ["the Alps"],
            "adjectives": ["financial", "profitable", "expensive", "valuable", "sound"],
            "idioms_prefix": ["By the way", "Speaking of finance", "Actually"]
        },
        37: {
            "name": "English for Law",
            "professions": ["a lawyer", "an attorney", "a judge", "a prosecutor", "a legal advisor"],
            "singular_countable": ["a law", "a case", "a contract", "a court", "a document"],
            "plural_nouns": ["laws", "cases", "contracts", "courts", "documents"],
            "uncountable_nouns": ["law", "justice", "evidence", "legislation", "litigation"],
            "specific_places": ["the court", "the office", "the courthouse", "the chamber"],
            "sports": ["arguing", "debating"],
            "instruments": ["the gavel", "the computer"],
            "countries": ["USA", "UK", "Canada", "Australia"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["Washington", "London", "Ottawa", "Canberra"],
            "rivers": ["the Thames", "the Potomac"],
            "mountains": ["Mount Rushmore"],
            "mountain_ranges": ["the Rocky Mountains"],
            "adjectives": ["legal", "judicial", "constitutional", "valid", "binding"],
            "idioms_prefix": ["By the way", "Speaking of law", "Legally speaking"]
        },
        38: {
            "name": "English for Medicine",
            "professions": ["a doctor", "a surgeon", "a nurse", "a physician", "a specialist"],
            "singular_countable": ["a patient", "a symptom", "a treatment", "a diagnosis", "a prescription"],
            "plural_nouns": ["patients", "symptoms", "treatments", "diagnoses", "prescriptions"],
            "uncountable_nouns": ["medicine", "health", "care", "treatment", "research"],
            "specific_places": ["the hospital", "the clinic", "the surgery", "the ward"],
            "sports": ["exercising", "running"],
            "instruments": ["the stethoscope", "the scalpel"],
            "countries": ["USA", "UK", "Switzerland", "Sweden"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["Boston", "London", "Geneva", "Stockholm"],
            "rivers": ["the Thames", "the Charles"],
            "mountains": ["Mount Blanc"],
            "mountain_ranges": ["the Alps"],
            "adjectives": ["medical", "clinical", "healthy", "effective", "critical"],
            "idioms_prefix": ["By the way", "Speaking medically", "Actually"]
        },
        39: {
            "name": "English for Marketing and PR",
            "professions": ["a marketer", "a PR specialist", "a manager", "a strategist", "a copywriter"],
            "singular_countable": ["a campaign", "a brand", "a message", "a target", "a strategy"],
            "plural_nouns": ["campaigns", "brands", "messages", "targets", "strategies"],
            "uncountable_nouns": ["marketing", "advertising", "publicity", "branding", "promotion"],
            "specific_places": ["the agency", "the office", "the studio", "the media center"],
            "sports": ["promoting", "branding"],
            "instruments": ["the computer", "the camera"],
            "countries": ["USA", "UK", "France", "Germany"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["New York", "London", "Paris", "Berlin"],
            "rivers": ["the Thames", "the Seine"],
            "mountains": ["Mount Blanc"],
            "mountain_ranges": ["the Alps"],
            "adjectives": ["creative", "viral", "effective", "innovative", "strategic"],
            "idioms_prefix": ["By the way", "Speaking of marketing", "Actually"]
        },
        40: {
            "name": "English for HR",
            "professions": ["an HR manager", "a recruiter", "an HR specialist", "a talent scout", "a coordinator"],
            "singular_countable": ["a candidate", "an employee", "a position", "a vacancy", "an interview"],
            "plural_nouns": ["candidates", "employees", "positions", "vacancies", "interviews"],
            "uncountable_nouns": ["recruitment", "training", "management", "development", "work"],
            "specific_places": ["the office", "the interview room", "the department", "the training center"],
            "sports": ["recruiting", "training"],
            "instruments": ["the computer", "the phone"],
            "countries": ["USA", "UK", "Germany", "France"],
            "countries_with_the": ["the United States", "the United Kingdom"],
            "cities": ["New York", "London", "Berlin", "Paris"],
            "rivers": ["the Thames", "the Seine"],
            "mountains": ["Mount Blanc"],
            "mountain_ranges": ["the Alps"],
            "adjectives": ["qualified", "experienced", "suitable", "professional", "skilled"],
            "idioms_prefix": ["By the way", "Speaking of HR", "Actually"]
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
    # УРОК 1: Что такое артикли (6 вопросов)
    # ========================================

    def generate_lesson1_q1(self, topic_id: int) -> Dict:
        """L1Q1: Сколько типов артиклей? (универсальный)"""
        question = "Сколько типов артиклей существует в английском языке?"
        correct = "Три"
        wrong_options = ["Один", "Два", "Четыре"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "easy",
            "explanation": "В английском языке три типа артиклей: неопределённый (a/an), определённый (the) и нулевой (отсутствие артикля)."
        }

    def generate_lesson1_q2(self, topic_id: int) -> Dict:
        """L1Q2: Какой артикль при первом упоминании? (универсальный)"""
        question = "Какой артикль используется, когда мы говорим о чём-то в первый раз?"
        correct = "A / AN"
        wrong_options = ["THE", "Нулевой артикль", "Любой артикль"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "easy",
            "explanation": "Неопределённый артикль a/an используется, когда мы упоминаем что-то впервые или говорим о чём-то общем, неконкретном."
        }

    def generate_lesson1_q3(self, topic_id: int) -> Dict:
        """L1Q3: I saw ___ X. ___ X was big. (динамический)"""
        topic = self.TOPICS[topic_id]
        thing = random.choice(topic["singular_countable"])

        # Убираем артикль из thing если он есть
        thing_clean = thing.replace("a ", "").replace("an ", "")

        # Определяем правильный артикль для первого упоминания
        first_article = "an" if thing_clean[0].lower() in 'aeiou' else "a"

        question = f"Выберите правильный вариант: \"I saw ___ {thing_clean}. ___ {thing_clean} was big.\""
        correct = f"{first_article} / The"
        wrong_options = [f"a / A", f"the / The", f"the / A"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "medium",
            "explanation": f"При первом упоминании используем \"{first_article} {thing_clean}\", при повторном упоминании той же вещи используем \"the {thing_clean}\"."
        }

    def generate_lesson1_q4(self, topic_id: int) -> Dict:
        """L1Q4: Нулевой артикль с множественным (динамический)"""
        topic = self.TOPICS[topic_id]
        plural = random.choice(topic["plural_nouns"])

        question = f"В каком предложении используется нулевой артикль?"

        thing = random.choice(topic["singular_countable"]).replace("a ", "").replace("an ", "")

        options_list = [
            f"I bought {thing}.",
            f"The {thing} is expensive.",
            f"I like {plural}.",
            f"This is {thing}."
        ]

        correct = options_list[2]
        options = {"A": options_list[0], "B": options_list[1], "C": options_list[2], "D": options_list[3]}
        correct_answer = "C"

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "medium",
            "explanation": f"\"I like {plural}\" — используется нулевой артикль с множественным числом в общем смысле."
        }

    def generate_lesson1_q5(self, topic_id: int) -> Dict:
        """L1Q5: Артикль с конкретным предметом (универсальный)"""
        question = "Какой артикль используется с конкретным, известным собеседнику предметом?"
        correct = "THE"
        wrong_options = ["A", "AN", "Артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "easy",
            "explanation": "Определённый артикль THE используется, когда мы говорим о чём-то конкретном и известном."
        }

    def generate_lesson1_q6(self, topic_id: int) -> Dict:
        """L1Q6: ___ life is beautiful (динамический)"""
        topic = self.TOPICS[topic_id]
        uncountable = random.choice(topic["uncountable_nouns"])

        # Для тем с idioms добавляем префикс
        prefix = ""
        if "idioms_prefix" in topic and random.random() > 0.5:
            prefix = random.choice(topic["idioms_prefix"]) + ", "

        question = f"Выберите правильный вариант: \"{prefix}___ {uncountable.capitalize()} is important.\""
        correct = "Артикль не нужен"
        wrong_options = ["A", "An", "The"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "medium",
            "explanation": f"С абстрактными неисчисляемыми существительными в общем смысле артикль не используется: \"{uncountable.capitalize()} is important.\""
        }

    # ========================================
    # УРОК 2: Неопределённый артикль A/AN (8 вопросов)
    # ========================================

    def generate_lesson2_q1(self, topic_id: int) -> Dict:
        """L2Q1: She is ___ profession (динамический)"""
        topic = self.TOPICS[topic_id]
        profession = random.choice(topic["professions"])

        question = f"Выберите правильный вариант: \"She is ___ {profession.replace('a ', '').replace('an ', '')}.\""

        # Определяем правильный артикль
        prof_clean = profession.replace("a ", "").replace("an ", "")
        correct = "an" if prof_clean[0].lower() in 'aeiou' else "a"

        wrong_options = ["the", "артикль не нужен"]
        if correct == "a":
            wrong_options.insert(0, "an")
        else:
            wrong_options.insert(0, "a")

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": f"С профессиями используется артикль a/an: \"She is {correct} {prof_clean}.\""
        }

    def generate_lesson2_q2(self, topic_id: int) -> Dict:
        """L2Q2: This is ___ umbrella/apple (динамический)"""
        topic = self.TOPICS[topic_id]

        # Выбираем предмет, который начинается с гласной
        thing = random.choice(topic["singular_countable"]).replace("a ", "").replace("an ", "")

        question = f"Выберите правильный вариант: \"This is ___ {thing}.\""

        # Определяем правильный артикль
        correct = "an" if thing[0].lower() in 'aeiou' else "a"

        wrong_options = ["the", "артикль не нужен"]
        if correct == "a":
            wrong_options.insert(0, "an")
        else:
            wrong_options.insert(0, "a")

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": f"AN используется перед гласным звуком, A — перед согласным. Правильно: \"This is {correct} {thing}.\""
        }

    def generate_lesson2_q3(self, topic_id: int) -> Dict:
        """L2Q3: He works at ___ university (универсальный)"""
        question = "Выберите правильный вариант: \"He works at ___ university.\""
        correct = "a"
        wrong_options = ["an", "the", "артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "medium",
            "explanation": "Несмотря на то, что \"university\" начинается с буквы U, первый звук — /j/ (согласный), поэтому используем \"a university\"."
        }

    def generate_lesson2_q4(self, topic_id: int) -> Dict:
        """L2Q4: I waited for ___ hour (универсальный)"""
        question = "Выберите правильный вариант: \"I waited for ___ hour.\""
        correct = "an"
        wrong_options = ["a", "the", "артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "medium",
            "explanation": "В слове \"hour\" буква H не читается, слово начинается с гласного звука /aʊ/, поэтому используем \"an hour\"."
        }

    def generate_lesson2_q5(self, topic_id: int) -> Dict:
        """L2Q5: What ___ beautiful day! (динамический)"""
        topic = self.TOPICS[topic_id]
        adjective = random.choice(topic["adjectives"])

        question = f"Выберите правильный вариант: \"What ___ {adjective} day!\""
        correct = "a"
        wrong_options = ["an", "the", "артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": f"В восклицаниях после \"What\" используется a/an: \"What a {adjective} day!\""
        }

    def generate_lesson2_q6(self, topic_id: int) -> Dict:
        """L2Q6: I have a books - найти ошибку (динамический)"""
        topic = self.TOPICS[topic_id]
        plural = random.choice(topic["plural_nouns"])

        question = "В каком предложении артикль A/AN используется неправильно?"

        thing = random.choice(topic["singular_countable"]).replace("a ", "").replace("an ", "")
        profession = random.choice(topic["professions"]).replace("a ", "").replace("an ", "")

        options_list = [
            f"I need a minute.",
            f"She is an {profession}.",
            f"I have a {plural}.",
            f"This is an {thing}." if thing[0].lower() in 'aeiou' else f"This is a {thing}."
        ]

        correct = options_list[2]
        options = {"A": options_list[0], "B": options_list[1], "C": options_list[2], "D": options_list[3]}
        correct_answer = "C"

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "medium",
            "explanation": f"Артикль a/an используется только с единственным числом. Правильно: \"I have {plural}\" (без артикля) или \"I have a {plural[:-1]}\" (в единственном числе)."
        }

    def generate_lesson2_q7(self, topic_id: int) -> Dict:
        """L2Q7: twice ___ week (универсальный)"""
        question = "Выберите правильный вариант: \"I go to the gym twice ___ week.\""
        correct = "a"
        wrong_options = ["an", "the", "артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": "В выражениях частоты используется a/an: \"twice a week\" (дважды в неделю)."
        }

    def generate_lesson2_q8(self, topic_id: int) -> Dict:
        """L2Q8: He is ___ honest man (универсальный)"""
        question = "Выберите правильный вариант: \"He is ___ honest man.\""
        correct = "an"
        wrong_options = ["a", "the", "артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "medium",
            "explanation": "В слове \"honest\" буква H не читается, слово начинается с гласного звука /ɒ/, поэтому \"an honest man\"."
        }

    # ========================================
    # УРОК 3: Определенный артикль THE (8 вопросов)
    # ========================================

    def generate_lesson3_q1(self, topic_id: int) -> Dict:
        """L3Q1: Close ___ door (динамический)"""
        topic = self.TOPICS[topic_id]

        # Используем конкретное место или предмет
        things = ["door", "window", "book", "computer", "phone"]
        thing = random.choice(things)

        question = f"Выберите правильный вариант: \"Close ___ {thing}, please.\""
        correct = "the"
        wrong_options = ["a", "an", "артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": f"Используем THE, когда понятно из контекста, о каком предмете идёт речь: \"Close the {thing}.\""
        }

    def generate_lesson3_q2(self, topic_id: int) -> Dict:
        """L3Q2: ___ sun is shining (универсальный)"""
        unique_objects = ["sun", "moon", "Earth", "sky"]
        obj = random.choice(unique_objects)

        question = f"Выберите правильный вариант: \"___ {obj.capitalize()} is beautiful today.\""
        correct = "The"
        wrong_options = ["A", "An", "Артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": f"С уникальными объектами (существует только один) используется THE: \"The {obj}.\""
        }

    def generate_lesson3_q3(self, topic_id: int) -> Dict:
        """L3Q3: the best restaurant (динамический)"""
        topic = self.TOPICS[topic_id]

        # Берем существительное из темы
        thing = random.choice(topic["singular_countable"]).replace("a ", "").replace("an ", "")
        adjective = random.choice(topic["adjectives"])
        place = random.choice(topic["cities"])

        question = f"Выберите правильный вариант: \"This is ___ best {thing} in {place}.\""
        correct = "the"
        wrong_options = ["a", "an", "артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": f"С превосходной степенью всегда используется THE: \"the best {thing}\"."
        }

    def generate_lesson3_q4(self, topic_id: int) -> Dict:
        """L3Q4: the second floor (динамический)"""
        ordinals = ["first", "second", "third", "last", "next"]
        ordinal = random.choice(ordinals)
        things = ["floor", "lesson", "time", "day", "week"]
        thing = random.choice(things)

        question = f"Выберите правильный вариант: \"He lives on ___ {ordinal} {thing}.\""
        correct = "the"
        wrong_options = ["a", "an", "артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": f"С порядковыми числительными используется THE: \"the {ordinal} {thing}\"."
        }

    def generate_lesson3_q5(self, topic_id: int) -> Dict:
        """L3Q5: play ___ piano (динамический)"""
        topic = self.TOPICS[topic_id]
        instrument = random.choice(topic["instruments"]).replace("the ", "")

        question = f"Выберите правильный вариант: \"She plays ___ {instrument} very well.\""
        correct = "the"
        wrong_options = ["a", "an", "артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "medium",
            "explanation": f"С музыкальными инструментами (когда играем на них) используется THE: \"play the {instrument}\"."
        }

    def generate_lesson3_q6(self, topic_id: int) -> Dict:
        """L3Q6: in ___ morning (универсальный)"""
        parts_of_day = ["morning", "afternoon", "evening"]
        part = random.choice(parts_of_day)

        question = f"Выберите правильный вариант: \"I'll see you in ___ {part}.\""
        correct = "the"
        wrong_options = ["a", "an", "артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": f"С частями дня после \"in\" используется THE: \"in the {part}\"."
        }

    def generate_lesson3_q7(self, topic_id: int) -> Dict:
        """L3Q7: The rich / the poor (универсальный)"""
        groups = ["rich", "poor", "young", "elderly", "British"]
        group = random.choice(groups)

        question = f"Выберите правильный вариант: \"___ {group} should help others.\""
        correct = "The"
        wrong_options = ["A", "An", "Артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "medium",
            "explanation": f"С прилагательными, обозначающими группу людей, используется THE: \"The {group}\" ({group} люди)."
        }

    def generate_lesson3_q8(self, topic_id: int) -> Dict:
        """L3Q8: The capital of Spain (динамический)"""
        topic = self.TOPICS[topic_id]
        country = random.choice(topic["countries"])

        question = f"В каком предложении артикль THE используется правильно?"

        place = random.choice(topic["specific_places"]).replace("the ", "")

        options_list = [
            "I'm going to the work.",
            f"The {country} is beautiful.",
            f"The capital of {country} is famous.",
            "I speak the English."
        ]

        correct = options_list[2]
        options = {"A": options_list[0], "B": options_list[1], "C": options_list[2], "D": options_list[3]}
        correct_answer = "C"

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "medium",
            "explanation": f"С конструкцией \"the ... of ...\" используется THE: \"The capital of {country}\". Остальные варианты неправильны."
        }

    # ========================================
    # УРОК 4: Нулевой артикль (8 вопросов)
    # ========================================

    def generate_lesson4_q1(self, topic_id: int) -> Dict:
        """L4Q1: I like ___ coffee (динамический)"""
        topic = self.TOPICS[topic_id]
        uncountable = random.choice(topic["uncountable_nouns"])

        question = f"Выберите правильный вариант: \"I like ___ {uncountable}.\""
        correct = "артикль не нужен"
        wrong_options = ["a", "an", "the"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "easy",
            "explanation": f"С неисчисляемыми существительными в общем смысле артикль не нужен: \"I like {uncountable}\" ({uncountable} вообще)."
        }

    def generate_lesson4_q2(self, topic_id: int) -> Dict:
        """L4Q2: ___ children need love (динамический)"""
        topic = self.TOPICS[topic_id]
        plural = random.choice(topic["plural_nouns"])

        question = f"Выберите правильный вариант: \"___ {plural.capitalize()} are important.\""
        correct = "Артикль не нужен"
        wrong_options = ["A", "An", "The"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "easy",
            "explanation": f"С множественным числом в общем смысле артикль не нужен: \"{plural.capitalize()} are important\" ({plural} вообще)."
        }

    def generate_lesson4_q3(self, topic_id: int) -> Dict:
        """L4Q3: ___ Maria lives in Barcelona (динамический)"""
        names = ["Maria", "John", "Sarah", "David", "Anna", "Michael"]
        name = random.choice(names)

        topic = self.TOPICS[topic_id]
        city = random.choice(topic["cities"])

        # Для тем с idioms добавляем префикс (но с ОШИБКОЙ!)
        if "idioms_prefix" in topic and random.random() > 0.5:
            prefix = random.choice(topic["idioms_prefix"]) + ", "
            question = f"Найдите ошибку: \"{prefix}I'm the {name}.\""
            correct = f"Нужно убрать THE"
            wrong_options = ["Нет ошибки", "Нужно добавить AN", "Нужно заменить THE на A"]

            options, correct_answer = self._shuffle_options(correct, wrong_options)

            return {
                "question": question,
                "options": options,
                "correct_answer": correct_answer,
                "topic_id": topic_id,
                "lesson": 4,
                "difficulty": "medium",
                "explanation": f"С именами людей артикль не используется: \"{prefix}I'm {name}.\""
            }
        else:
            question = f"Выберите правильный вариант: \"___ {name} lives in {city}.\""
            correct = "Артикль не нужен"
            wrong_options = ["A", "An", "The"]

            options, correct_answer = self._shuffle_options(correct, wrong_options)

            return {
                "question": question,
                "options": options,
                "correct_answer": correct_answer,
                "topic_id": topic_id,
                "lesson": 4,
                "difficulty": "easy",
                "explanation": f"С именами людей артикль не используется: \"{name} lives in {city}.\""
            }

    def generate_lesson4_q4(self, topic_id: int) -> Dict:
        """L4Q4: I live in ___ Spain (динамический)"""
        topic = self.TOPICS[topic_id]
        country = random.choice(topic["countries"])

        question = f"Выберите правильный вариант: \"I live in ___ {country}.\""
        correct = "артикль не нужен"
        wrong_options = ["a", "an", "the"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "easy",
            "explanation": f"С большинством названий стран артикль не используется: \"I live in {country}.\""
        }

    def generate_lesson4_q5(self, topic_id: int) -> Dict:
        """L4Q5: I speak ___ English (универсальный)"""
        languages = ["English", "Spanish", "German", "French", "Chinese"]
        language = random.choice(languages)

        question = f"Выберите правильный вариант: \"I speak ___ {language}.\""
        correct = "артикль не нужен"
        wrong_options = ["a", "an", "the"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "easy",
            "explanation": f"С языками артикль не используется: \"I speak {language}.\""
        }

    def generate_lesson4_q6(self, topic_id: int) -> Dict:
        """L4Q6: have ___ breakfast (универсальный)"""
        meals = ["breakfast", "lunch", "dinner"]
        meal = random.choice(meals)

        question = f"Выберите правильный вариант: \"I have ___ {meal} at 8 AM.\""
        correct = "артикль не нужен"
        wrong_options = ["a", "an", "the"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "easy",
            "explanation": f"С приемами пищи артикль не используется: \"have {meal}.\""
        }

    def generate_lesson4_q7(self, topic_id: int) -> Dict:
        """L4Q7: play ___ tennis (динамический)"""
        topic = self.TOPICS[topic_id]
        sport = random.choice(topic["sports"])

        question = f"Выберите правильный вариант: \"She plays ___ {sport} every day.\""
        correct = "артикль не нужен"
        wrong_options = ["a", "an", "the"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "easy",
            "explanation": f"С видами спорта артикль не используется: \"play {sport}.\""
        }

    def generate_lesson4_q8(self, topic_id: int) -> Dict:
        """L4Q8: Water is essential (динамический)"""
        topic = self.TOPICS[topic_id]
        uncountable = random.choice(topic["uncountable_nouns"])

        question = "В каком предложении артикль НЕ нужен?"

        thing = random.choice(topic["singular_countable"]).replace("a ", "").replace("an ", "")

        options_list = [
            f"I need a {thing}.",
            f"The {thing} is on the table.",
            f"{uncountable.capitalize()} is essential for life.",
            f"She is an expert."
        ]

        correct = options_list[2]
        options = {"A": options_list[0], "B": options_list[1], "C": options_list[2], "D": options_list[3]}
        correct_answer = "C"

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "medium",
            "explanation": f"\"{uncountable.capitalize()} is essential for life\" — с неисчисляемым существительным в общем смысле артикль не нужен."
        }

    # ========================================
    # УРОК 5: География (8 вопросов)
    # ========================================

    def generate_lesson5_q1(self, topic_id: int) -> Dict:
        """L5Q1: ___ United States (универсальный)"""
        question = "Выберите правильный вариант: \"I visited ___ United States last year.\""
        correct = "the"
        wrong_options = ["a", "an", "артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "easy",
            "explanation": "\"The United States\" (the USA) — исключение, всегда используется с THE."
        }

    def generate_lesson5_q2(self, topic_id: int) -> Dict:
        """L5Q2: She lives in ___ London (динамический)"""
        topic = self.TOPICS[topic_id]
        city = random.choice(topic["cities"])

        question = f"Выберите правильный вариант: \"She lives in ___ {city}.\""
        correct = "артикль не нужен"
        wrong_options = ["a", "an", "the"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "easy",
            "explanation": f"Названия городов используются без артикля: \"She lives in {city}.\""
        }

    def generate_lesson5_q3(self, topic_id: int) -> Dict:
        """L5Q3: ___ Thames flows (динамический)"""
        topic = self.TOPICS[topic_id]
        river = random.choice(topic["rivers"]).replace("the ", "")
        city = random.choice(topic["cities"])

        question = f"Выберите правильный вариант: \"___ {river} flows through {city}.\""
        correct = "The"
        wrong_options = ["A", "An", "Артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "easy",
            "explanation": f"Названия рек всегда используются с THE: \"The {river}.\""
        }

    def generate_lesson5_q4(self, topic_id: int) -> Dict:
        """L5Q4: ___ Lake Michigan (универсальный)"""
        lakes = ["Lake Michigan", "Lake Superior", "Lake Geneva"]
        lake = random.choice(lakes)

        question = f"Выберите правильный вариант: \"We went to ___ {lake}.\""
        correct = "артикль не нужен"
        wrong_options = ["a", "an", "the"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "medium",
            "explanation": f"С названиями озёр со словом \"Lake\" артикль не используется: \"{lake}.\""
        }

    def generate_lesson5_q5(self, topic_id: int) -> Dict:
        """L5Q5: ___ Mount Everest (динамический)"""
        topic = self.TOPICS[topic_id]
        mountain = random.choice(topic["mountains"])

        question = f"Выберите правильный вариант: \"They climbed ___ {mountain}.\""
        correct = "артикль не нужен"
        wrong_options = ["a", "an", "the"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "easy",
            "explanation": f"Названия отдельных гор используются без артикля: \"{mountain}.\""
        }

    def generate_lesson5_q6(self, topic_id: int) -> Dict:
        """L5Q6: ___ Alps are beautiful (динамический)"""
        topic = self.TOPICS[topic_id]
        mountain_range = random.choice(topic["mountain_ranges"]).replace("the ", "")

        question = f"Выберите правильный вариант: \"___ {mountain_range} are beautiful in winter.\""
        correct = "The"
        wrong_options = ["A", "An", "Артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "easy",
            "explanation": f"Названия горных цепей используются с THE: \"The {mountain_range}.\""
        }

    def generate_lesson5_q7(self, topic_id: int) -> Dict:
        """L5Q7: from ___ Netherlands (универсальный)"""
        countries_with_the = ["Netherlands", "Philippines", "United Kingdom"]
        country = random.choice(countries_with_the)

        question = f"Выберите правильный вариант: \"She is from ___ {country}.\""
        correct = "the"
        wrong_options = ["a", "an", "артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "medium",
            "explanation": f"\"The {country}\" — исключение, всегда используется с THE."
        }

    def generate_lesson5_q8(self, topic_id: int) -> Dict:
        """L5Q8: ___ Pacific Ocean (универсальный)"""
        oceans = ["Pacific Ocean", "Atlantic Ocean", "Indian Ocean"]
        ocean = random.choice(oceans)

        question = f"Выберите правильный вариант: \"___ {ocean} is the largest ocean.\""
        correct = "The"
        wrong_options = ["A", "An", "Артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "easy",
            "explanation": f"Названия океанов используются с THE: \"The {ocean}.\""
        }

    # ========================================
    # УРОК 6: Устойчивые выражения (8 вопросов)
    # ========================================

    def generate_lesson6_q1(self, topic_id: int) -> Dict:
        """L6Q1: twice ___ week (универсальный)"""
        question = "Выберите правильный вариант: \"I go to the gym twice ___ week.\""
        correct = "a"
        wrong_options = ["an", "the", "артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": "В выражениях частоты используется A/AN: \"twice a week\" (дважды в неделю)."
        }

    def generate_lesson6_q2(self, topic_id: int) -> Dict:
        """L6Q2: in ___ morning (универсальный)"""
        parts = ["morning", "afternoon", "evening"]
        part = random.choice(parts)

        question = f"Выберите правильный вариант: \"I'll call you in ___ {part}.\""
        correct = "the"
        wrong_options = ["a", "an", "артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": f"С частями дня после \"in\" используется THE: \"in the {part}\"."
        }

    def generate_lesson6_q3(self, topic_id: int) -> Dict:
        """L6Q3: at ___ night (универсальный)"""
        question = "Выберите правильный вариант: \"I always work at ___ night.\""
        correct = "артикль не нужен"
        wrong_options = ["a", "an", "the"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "medium",
            "explanation": "После \"at\" со словом \"night\" артикль не нужен: \"at night\"."
        }

    def generate_lesson6_q4(self, topic_id: int) -> Dict:
        """L6Q4: go to ___ work (универсальный)"""
        places = ["work", "school", "bed", "church"]
        place = random.choice(places)

        question = f"Выберите правильный вариант: \"I go to ___ {place} every day.\""
        correct = "артикль не нужен"
        wrong_options = ["a", "an", "the"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": f"В выражении \"go to {place}\" (как деятельность) артикль не нужен."
        }

    def generate_lesson6_q5(self, topic_id: int) -> Dict:
        """L6Q5: on ___ phone (универсальный)"""
        question = "Выберите правильный вариант: \"She is talking on ___ phone.\""
        correct = "the"
        wrong_options = ["a", "an", "артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": "В выражении \"on the phone\" используется THE."
        }

    def generate_lesson6_q6(self, topic_id: int) -> Dict:
        """L6Q6: by ___ bus (универсальный)"""
        transport = ["bus", "car", "train", "plane", "taxi"]
        vehicle = random.choice(transport)

        question = f"Выберите правильный вариант: \"I travel by ___ {vehicle}.\""
        correct = "артикль не нужен"
        wrong_options = ["a", "an", "the"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": f"Со способом передвижения после \"by\" артикль не нужен: \"by {vehicle}\"."
        }

    def generate_lesson6_q7(self, topic_id: int) -> Dict:
        """L6Q7: on ___ left (универсальный)"""
        directions = ["left", "right"]
        direction = random.choice(directions)

        question = f"Выберите правильный вариант: \"The shop is on ___ {direction}.\""
        correct = "the"
        wrong_options = ["a", "an", "артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": f"В выражениях направления используется THE: \"on the {direction}\"."
        }

    def generate_lesson6_q8(self, topic_id: int) -> Dict:
        """L6Q8: at ___ home (универсальный)"""
        question = "Выберите правильный вариант: \"I'm at ___ home now.\""
        correct = "артикль не нужен"
        wrong_options = ["a", "an", "the"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": "В выражении \"at home\" артикль не используется."
        }

    # ========================================
    # УРОК 7: Ошибки (10 вопросов)
    # ========================================

    def generate_lesson7_q1(self, topic_id: int) -> Dict:
        """L7Q1: She is teacher (динамический)"""
        topic = self.TOPICS[topic_id]
        profession = random.choice(topic["professions"]).replace("a ", "").replace("an ", "")

        question = f"Найдите ошибку: \"She is {profession}.\""
        correct = "Нужно добавить A/AN перед профессией"
        wrong_options = ["Нет ошибки", "Нужно добавить THE", "Нужно убрать профессию"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "easy",
            "explanation": f"С профессиями после глагола BE нужен артикль A/AN: \"She is a/an {profession}.\""
        }

    def generate_lesson7_q2(self, topic_id: int) -> Dict:
        """L7Q2: The Maria lives (динамический)"""
        names = ["Maria", "John", "Sarah"]
        name = random.choice(names)

        topic = self.TOPICS[topic_id]
        city = random.choice(topic["cities"])

        question = f"Найдите ошибку: \"The {name} lives in {city}.\""
        correct = "Нужно убрать THE"
        wrong_options = ["Нет ошибки", "Нужно заменить THE на A", "Нужно заменить THE на AN"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "easy",
            "explanation": f"С именами собственными артикль не используется: \"{name} lives in {city}.\""
        }

    def generate_lesson7_q3(self, topic_id: int) -> Dict:
        """L7Q3: I speak the English (универсальный)"""
        languages = ["English", "Spanish", "German"]
        language = random.choice(languages)

        question = f"Найдите ошибку: \"I speak the {language}.\""
        correct = "Нужно убрать THE"
        wrong_options = ["Нет ошибки", "Нужно заменить THE на A", "Нужно заменить THE на AN"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "easy",
            "explanation": f"С языками артикль не используется: \"I speak {language}.\""
        }

    def generate_lesson7_q4(self, topic_id: int) -> Dict:
        """L7Q4: I need a water (динамический)"""
        topic = self.TOPICS[topic_id]
        uncountable = random.choice(topic["uncountable_nouns"])

        question = f"Найдите ошибку: \"I need a {uncountable}.\""
        correct = "Нужно убрать A"
        wrong_options = ["Нет ошибки", "Нужно заменить A на THE", "Нужно заменить A на AN"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "medium",
            "explanation": f"\"{uncountable.capitalize()}\" — неисчисляемое существительное, A/AN с ним не используется: \"I need {uncountable}\" или \"I need some {uncountable}\"."
        }

    def generate_lesson7_q5(self, topic_id: int) -> Dict:
        """L7Q5: a European city (универсальный)"""
        question = "Выберите правильный вариант: \"This is ___ European city.\""
        correct = "a"
        wrong_options = ["an", "the", "артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "medium",
            "explanation": "\"European\" начинается с согласного звука /j/, поэтому используем A: \"a European city\"."
        }

    def generate_lesson7_q6(self, topic_id: int) -> Dict:
        """L7Q6: I go to the work (универсальный)"""
        question = "Найдите ошибку: \"I go to the work every day.\""
        correct = "Нужно убрать THE"
        wrong_options = ["Нет ошибки", "Нужно заменить THE на A", "Нужно добавить артикль перед DAY"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "easy",
            "explanation": "В выражении \"go to work\" (как деятельность) артикль не нужен: \"I go to work.\""
        }

    def generate_lesson7_q7(self, topic_id: int) -> Dict:
        """L7Q7: The my car (универсальный)"""
        things = ["car", "book", "phone", "house"]
        thing = random.choice(things)

        question = f"Найдите ошибку: \"The my {thing} is new.\""
        correct = "Нужно убрать THE"
        wrong_options = ["Нет ошибки", "Нужно убрать MY", "Можно оставить оба"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "medium",
            "explanation": f"После притяжательных местоимений артикль не используется: \"My {thing} is new.\""
        }

    def generate_lesson7_q8(self, topic_id: int) -> Dict:
        """L7Q8: the other / another (универсальный)"""
        question = "Выберите правильный вариант: \"I have two dogs. One is black, ___ other is white.\""
        correct = "the"
        wrong_options = ["a", "an", "артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "medium",
            "explanation": "\"The other\" используется, когда говорим о втором из двух: \"the other is white\"."
        }

    def generate_lesson7_q9(self, topic_id: int) -> Dict:
        """L7Q9: have ___ cold (универсальный)"""
        question = "Выберите правильный вариант: \"I have ___ cold.\""
        correct = "a"
        wrong_options = ["an", "the", "артикль не нужен"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "medium",
            "explanation": "С некоторыми болезнями используется A: \"have a cold\" (простудиться)."
        }

    def generate_lesson7_q10(self, topic_id: int) -> Dict:
        """L7Q10: I saw a dog. Dog was big (динамический)"""
        topic = self.TOPICS[topic_id]
        thing = random.choice(topic["singular_countable"]).replace("a ", "").replace("an ", "")

        question = f"Найдите ошибку: \"I saw a {thing}. {thing.capitalize()} was expensive.\""
        correct = "Нужно добавить THE перед вторым упоминанием"
        wrong_options = ["Нет ошибки", "Нужно убрать A", "Обе части правильные"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "medium",
            "explanation": f"При повторном упоминании используем THE: \"I saw a {thing}. The {thing} was expensive.\""
        }

    # ========================================
    # Методы генерации тестов
    # ========================================

    def _get_lesson_methods(self, lesson_num: int) -> List:
        """Получить методы генерации для урока"""
        lesson_methods = {
            1: [
                self.generate_lesson1_q1, self.generate_lesson1_q2,
                self.generate_lesson1_q3, self.generate_lesson1_q4,
                self.generate_lesson1_q5, self.generate_lesson1_q6
            ],
            2: [
                self.generate_lesson2_q1, self.generate_lesson2_q2,
                self.generate_lesson2_q3, self.generate_lesson2_q4,
                self.generate_lesson2_q5, self.generate_lesson2_q6,
                self.generate_lesson2_q7, self.generate_lesson2_q8
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
                self.generate_lesson5_q7, self.generate_lesson5_q8
            ],
            6: [
                self.generate_lesson6_q1, self.generate_lesson6_q2,
                self.generate_lesson6_q3, self.generate_lesson6_q4,
                self.generate_lesson6_q5, self.generate_lesson6_q6,
                self.generate_lesson6_q7, self.generate_lesson6_q8
            ],
            7: [
                self.generate_lesson7_q1, self.generate_lesson7_q2,
                self.generate_lesson7_q3, self.generate_lesson7_q4,
                self.generate_lesson7_q5, self.generate_lesson7_q6,
                self.generate_lesson7_q7, self.generate_lesson7_q8,
                self.generate_lesson7_q9, self.generate_lesson7_q10
            ]
        }
        return lesson_methods[lesson_num]

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
            lesson_num: Номер урока (1-7)
            topic_ids_sequence: [2, 3, 2, 4, ...] ← ГОТОВЫЙ список топиков
            num_questions: Количество вопросов (если None - берем все доступные)

        Returns:
            Список вопросов
        """
        methods = self._get_lesson_methods(lesson_num)

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

    def generate_full_module_test(
            self,
            topic_ids_sequence: List[int],
            num_questions: int = 56
    ) -> List[Dict]:
        """
        Генерировать полный тест по модулю
        СИНХРОННЫЙ - НЕ работает с БД!

        Args:
            topic_ids_sequence: [2, 3, 2, 4, ...] ← ГОТОВЫЙ список (56 топиков)
            num_questions: Количество вопросов

        Returns:
            Список из 56 вопросов (БЕЗ topic_name!)
        """
        all_methods = []
        for lesson_num in range(1, 8):
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

    async def get_topic_name(pool_base, topic_id: int) -> str:
        """
        Получить название топика по ID

        Returns:
            topic_name или "General" если не найдено
        """
        var_query = """
            SELECT c_topic_name 
            FROM t_lp_topics 
            WHERE c_topic_id = $1
        """
        var_Arr = await pgDB.fExec_SelectQuery_args(pool_base, var_query, [topic_id])

        if var_Arr:
            return var_Arr[0][0]

        return "General"


# Пример использования:
if __name__ == "__main__":
    generator = ArticlesQuestionGenerator(seed=42)

    # Генерация теста для урока 1 (6 вопросов)
    topic_sequence = [2, 3, 4, 5, 6, 7]
    lesson1_test = generator.generate_test_for_lesson(1, topic_sequence)

    print("=== Урок 1: Что такое артикли ===")
    for i, q in enumerate(lesson1_test, 1):
        print(f"\nВопрос {i}:")
        print(f"Тема: {generator.TOPICS[q['topic_id']]['name']}")
        print(q['question'])
        for key, value in q['options'].items():
            print(f"  {key}: {value}")
        print(f"Правильный ответ: {q['correct_answer']}")
        print(f"Объяснение: {q['explanation']}")