import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from .base_generator import BaseQuestionGenerator


class PresentSimpleQuestionGenerator(BaseQuestionGenerator):
    """
    Динамический генератор вопросов по Present Simple
    Создает уникальные вопросы для каждой темы интересов
    67 вопросов (9 уроков)
    """

    # Темы интересов с расширенными словарями
    TOPICS = {
        2: {
            "name": "Shopping and money",
            "professions": ["a customer", "a cashier", "a sales manager", "a shop assistant", "a buyer"],
            "verbs": ["shop", "buy", "sell", "pay", "spend", "save", "cost", "return"],
            "objects": ["money", "products", "clothes", "receipts", "discounts", "prices"],
            "locations_at": ["at the store", "at the mall", "at the shop", "at the market", "at the checkout"],
            "locations_in": ["in the shop", "in the mall", "in the store", "in the market"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every day", "on weekends", "twice a week", "every month"],
            "things": ["the product", "the price", "the receipt", "the card", "the discount"],
            "adjectives_quality": ["expensive", "cheap", "good", "affordable", "on sale"],
            "nationalities": ["German", "Spanish", "Italian", "French"],
            "countries": ["Germany", "Spain", "Italy", "France"],
            "cities": ["Berlin", "Madrid", "Rome", "Paris"]
        },
        3: {
            "name": "Weather and nature",
            "professions": ["a meteorologist", "a farmer", "a gardener", "a park ranger"],
            "verbs": ["rain", "snow", "shine", "blow", "freeze", "melt", "grow", "bloom"],
            "objects": ["plants", "flowers", "trees", "crops", "forecasts", "temperatures"],
            "locations_at": ["at the park", "at the beach", "at the garden", "at the lake"],
            "locations_in": ["in the forest", "in the park", "in the garden", "in nature"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every spring", "in summer", "during winter", "every season"],
            "things": ["the weather", "the temperature", "the forecast", "the climate"],
            "adjectives_quality": ["sunny", "cloudy", "rainy", "windy", "beautiful"],
            "nationalities": ["Canadian", "American", "British", "Australian"],
            "countries": ["Canada", "the USA", "England", "Australia"],
            "cities": ["Toronto", "New York", "London", "Sydney"]
        },
        4: {
            "name": "Health and medicine",
            "professions": ["a doctor", "a nurse", "a patient", "a pharmacist", "a dentist"],
            "verbs": ["exercise", "sleep", "eat", "rest", "feel", "hurt", "cure", "treat"],
            "objects": ["medicines", "vitamins", "appointments", "symptoms", "treatments"],
            "locations_at": ["at the hospital", "at the clinic", "at the doctor's", "at the pharmacy"],
            "locations_in": ["in the hospital", "in the clinic", "in the waiting room"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every day", "twice a day", "once a week", "every morning"],
            "things": ["the medicine", "the appointment", "the prescription", "health"],
            "adjectives_quality": ["healthy", "sick", "tired", "painful", "strong"],
            "nationalities": ["Swiss", "Swedish", "Norwegian", "Danish"],
            "countries": ["Switzerland", "Sweden", "Norway", "Denmark"],
            "cities": ["Zurich", "Stockholm", "Oslo", "Copenhagen"]
        },
        5: {
            "name": "Home and daily routines",
            "professions": ["a housewife", "a homeowner", "a tenant", "a cleaner"],
            "verbs": ["wake up", "cook", "clean", "wash", "sleep", "relax", "watch", "live"],
            "objects": ["dishes", "laundry", "furniture", "meals", "housework"],
            "locations_at": ["at home", "at the kitchen", "at the bedroom"],
            "locations_in": ["in the house", "in the kitchen", "in the living room", "in the bedroom"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every morning", "every evening", "on weekdays", "on weekends"],
            "things": ["the routine", "the housework", "breakfast", "dinner"],
            "adjectives_quality": ["clean", "comfortable", "cozy", "modern", "spacious"],
            "nationalities": ["Dutch", "Belgian", "Austrian", "Polish"],
            "countries": ["the Netherlands", "Belgium", "Austria", "Poland"],
            "cities": ["Amsterdam", "Brussels", "Vienna", "Warsaw"]
        },
        6: {
            "name": "Transportation and directions",
            "professions": ["a driver", "a pilot", "a bus driver", "a taxi driver"],
            "verbs": ["drive", "walk", "fly", "travel", "arrive", "depart", "catch", "miss"],
            "objects": ["tickets", "routes", "schedules", "maps", "directions"],
            "locations_at": ["at the station", "at the airport", "at the stop", "at the terminal"],
            "locations_in": ["in the car", "in the bus", "in the train", "in the city"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every day", "on weekdays", "twice a day", "every morning"],
            "things": ["the bus", "the train", "the route", "the schedule"],
            "adjectives_quality": ["fast", "slow", "convenient", "direct", "delayed"],
            "nationalities": ["Japanese", "Chinese", "Korean", "Indian"],
            "countries": ["Japan", "China", "Korea", "India"],
            "cities": ["Tokyo", "Beijing", "Seoul", "Mumbai"]
        },
        7: {
            "name": "Leisure and hobbies",
            "professions": ["a photographer", "a musician", "an artist", "a dancer"],
            "verbs": ["play", "read", "paint", "dance", "sing", "collect", "draw", "photograph"],
            "objects": ["books", "music", "pictures", "collections", "instruments"],
            "locations_at": ["at the gym", "at the club", "at the studio", "at the gallery"],
            "locations_in": ["in the park", "in the cinema", "in the theater", "in the museum"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every weekend", "on Saturdays", "twice a week", "every evening"],
            "things": ["the hobby", "the activity", "free time", "entertainment"],
            "adjectives_quality": ["interesting", "boring", "exciting", "relaxing", "creative"],
            "nationalities": ["Brazilian", "Argentinian", "Mexican", "Colombian"],
            "countries": ["Brazil", "Argentina", "Mexico", "Colombia"],
            "cities": ["Rio de Janeiro", "Buenos Aires", "Mexico City", "Bogota"]
        },
        8: {
            "name": "Relationships and emotions",
            "professions": ["a friend", "a colleague", "a partner", "a family member"],
            "verbs": ["love", "like", "hate", "trust", "understand", "support", "care", "miss"],
            "objects": ["friends", "family", "relationships", "emotions", "feelings"],
            "locations_at": ["at parties", "at meetings", "at gatherings"],
            "locations_in": ["in relationships", "in friendships", "in the family"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every day", "all the time", "on holidays", "every week"],
            "things": ["the relationship", "the friendship", "love", "trust"],
            "adjectives_quality": ["happy", "sad", "angry", "worried", "excited"],
            "nationalities": ["Greek", "Turkish", "Egyptian", "Lebanese"],
            "countries": ["Greece", "Turkey", "Egypt", "Lebanon"],
            "cities": ["Athens", "Istanbul", "Cairo", "Beirut"]
        },
        9: {
            "name": "Technology and gadgets",
            "professions": ["a programmer", "an IT specialist", "a tech support worker", "a gamer"],
            "verbs": ["use", "work", "charge", "connect", "download", "upload", "install", "update"],
            "objects": ["devices", "apps", "programs", "files", "updates", "passwords"],
            "locations_at": ["at the computer", "at the desk"],
            "locations_in": ["in the office", "in the cloud", "in the system"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every day", "all the time", "twice a day", "every hour"],
            "things": ["the device", "the app", "the program", "technology"],
            "adjectives_quality": ["new", "old", "fast", "slow", "modern"],
            "nationalities": ["Russian", "Ukrainian", "Estonian", "Latvian"],
            "countries": ["Russia", "Ukraine", "Estonia", "Latvia"],
            "cities": ["Moscow", "Kyiv", "Tallinn", "Riga"]
        },
        11: {
            "name": "Job interviews and CVs",
            "professions": ["a candidate", "an applicant", "a recruiter", "an interviewer"],
            "verbs": ["apply", "interview", "hire", "prepare", "answer", "ask", "present", "qualify"],
            "objects": ["CVs", "resumes", "applications", "interviews", "questions"],
            "locations_at": ["at the interview", "at the office", "at the company"],
            "locations_in": ["in the office", "in the interview room", "in HR"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every week", "every month", "regularly", "annually"],
            "things": ["the CV", "the interview", "the position", "the application"],
            "adjectives_quality": ["qualified", "experienced", "suitable", "professional", "confident"],
            "nationalities": ["Singaporean", "Malaysian", "Thai", "Vietnamese"],
            "countries": ["Singapore", "Malaysia", "Thailand", "Vietnam"],
            "cities": ["Singapore", "Kuala Lumpur", "Bangkok", "Hanoi"]
        },
        12: {
            "name": "Meetings and negotiations",
            "professions": ["a manager", "a negotiator", "a director", "a participant"],
            "verbs": ["meet", "discuss", "negotiate", "agree", "present", "propose", "decide", "conclude"],
            "objects": ["meetings", "agendas", "proposals", "agreements", "decisions"],
            "locations_at": ["at the meeting", "at the conference", "at the table"],
            "locations_in": ["in the meeting room", "in the office", "in negotiations"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every week", "on Mondays", "twice a month", "regularly"],
            "things": ["the meeting", "the agenda", "the proposal", "the deal"],
            "adjectives_quality": ["successful", "productive", "important", "difficult", "final"],
            "nationalities": ["Israeli", "Saudi", "Emirati", "Qatari"],
            "countries": ["Israel", "Saudi Arabia", "the UAE", "Qatar"],
            "cities": ["Tel Aviv", "Riyadh", "Dubai", "Doha"]
        },
        13: {
            "name": "Presentations and public speaking",
            "professions": ["a presenter", "a speaker", "a lecturer", "an instructor"],
            "verbs": ["present", "speak", "explain", "demonstrate", "show", "introduce", "conclude", "summarize"],
            "objects": ["presentations", "slides", "speeches", "topics", "audiences"],
            "locations_at": ["at the conference", "at the event", "at the stage"],
            "locations_in": ["in the hall", "in the auditorium", "in front of people"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every month", "regularly", "at conferences", "annually"],
            "things": ["the presentation", "the speech", "the topic", "the audience"],
            "adjectives_quality": ["clear", "interesting", "boring", "professional", "engaging"],
            "nationalities": ["Irish", "Scottish", "Welsh", "English"],
            "countries": ["Ireland", "Scotland", "Wales", "England"],
            "cities": ["Dublin", "Edinburgh", "Cardiff", "London"]
        },
        14: {
            "name": "Emails and business correspondence",
            "professions": ["a correspondent", "an assistant", "a secretary", "a manager"],
            "verbs": ["write", "send", "receive", "reply", "forward", "attach", "check", "read"],
            "objects": ["emails", "messages", "letters", "attachments", "replies"],
            "locations_at": ["at the desk", "at work"],
            "locations_in": ["in the inbox", "in the office", "in correspondence"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every day", "every morning", "regularly", "constantly"],
            "things": ["the email", "the message", "the letter", "correspondence"],
            "adjectives_quality": ["formal", "informal", "urgent", "important", "professional"],
            "nationalities": ["New Zealand", "Fijian", "Samoan", "Australian"],
            "countries": ["New Zealand", "Fiji", "Samoa", "Australia"],
            "cities": ["Auckland", "Suva", "Apia", "Melbourne"]
        },
        15: {
            "name": "Office communication and teamwork",
            "professions": ["a team member", "a colleague", "a coordinator", "a team leader"],
            "verbs": ["work", "collaborate", "cooperate", "communicate", "help", "support", "share", "contribute"],
            "objects": ["tasks", "projects", "ideas", "information", "resources"],
            "locations_at": ["at the office", "at work", "at meetings"],
            "locations_in": ["in the team", "in the office", "in the department"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every day", "regularly", "constantly", "all the time"],
            "things": ["the team", "the project", "teamwork", "collaboration"],
            "adjectives_quality": ["productive", "efficient", "cooperative", "friendly", "professional"],
            "nationalities": ["Czech", "Slovak", "Hungarian", "Romanian"],
            "countries": ["the Czech Republic", "Slovakia", "Hungary", "Romania"],
            "cities": ["Prague", "Bratislava", "Budapest", "Bucharest"]
        },
        16: {
            "name": "Project management vocabulary",
            "professions": ["a project manager", "a team lead", "a coordinator", "a planner"],
            "verbs": ["plan", "organize", "manage", "coordinate", "monitor", "control", "complete", "deliver"],
            "objects": ["projects", "tasks", "deadlines", "milestones", "deliverables"],
            "locations_at": ["at work", "at the office", "at meetings"],
            "locations_in": ["in the project", "in the team", "in management"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every week", "regularly", "on schedule", "monthly"],
            "things": ["the project", "the deadline", "the task", "the milestone"],
            "adjectives_quality": ["important", "urgent", "complex", "successful", "challenging"],
            "nationalities": ["Finnish", "Icelandic", "Portuguese", "Croatian"],
            "countries": ["Finland", "Iceland", "Portugal", "Croatia"],
            "cities": ["Helsinki", "Reykjavik", "Lisbon", "Zagreb"]
        },
        17: {
            "name": "Customer service and support",
            "professions": ["a customer service agent", "a support specialist", "a representative", "a consultant"],
            "verbs": ["help", "assist", "solve", "answer", "respond", "support", "handle", "resolve"],
            "objects": ["customers", "issues", "complaints", "requests", "questions"],
            "locations_at": ["at the call center", "at the desk", "at work"],
            "locations_in": ["in the office", "in customer service", "in support"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every day", "all day", "constantly", "regularly"],
            "things": ["the customer", "the issue", "the solution", "service"],
            "adjectives_quality": ["helpful", "patient", "professional", "polite", "efficient"],
            "nationalities": ["Chilean", "Peruvian", "Bolivian", "Ecuadorian"],
            "countries": ["Chile", "Peru", "Bolivia", "Ecuador"],
            "cities": ["Santiago", "Lima", "La Paz", "Quito"]
        },
        18: {
            "name": "Marketing and sales English",
            "professions": ["a marketer", "a sales manager", "a sales representative", "a promoter"],
            "verbs": ["sell", "promote", "advertise", "market", "attract", "convince", "pitch", "close"],
            "objects": ["products", "services", "campaigns", "clients", "deals"],
            "locations_at": ["at the market", "at events", "at presentations"],
            "locations_in": ["in sales", "in marketing", "in the field"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every quarter", "monthly", "regularly", "constantly"],
            "things": ["the product", "the campaign", "the sale", "the market"],
            "adjectives_quality": ["successful", "effective", "profitable", "competitive", "innovative"],
            "nationalities": ["South African", "Kenyan", "Nigerian", "Ghanaian"],
            "countries": ["South Africa", "Kenya", "Nigeria", "Ghana"],
            "cities": ["Cape Town", "Nairobi", "Lagos", "Accra"]
        },
        20: {
            "name": "At the airport and hotel",
            "professions": ["a traveler", "a tourist", "a guest", "a receptionist"],
            "verbs": ["check in", "book", "reserve", "stay", "travel", "fly", "arrive", "depart"],
            "objects": ["tickets", "reservations", "luggage", "rooms", "flights"],
            "locations_at": ["at the airport", "at the hotel", "at reception", "at the gate"],
            "locations_in": ["in the hotel", "in the room", "in the airport", "in the lobby"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every trip", "on vacation", "annually", "regularly"],
            "things": ["the flight", "the room", "the reservation", "the ticket"],
            "adjectives_quality": ["comfortable", "convenient", "expensive", "luxurious", "modern"],
            "nationalities": ["Moroccan", "Tunisian", "Algerian", "Libyan"],
            "countries": ["Morocco", "Tunisia", "Algeria", "Libya"],
            "cities": ["Marrakech", "Tunis", "Algiers", "Tripoli"]
        },
        21: {
            "name": "Sightseeing and excursions",
            "professions": ["a tourist", "a guide", "a traveler", "an explorer"],
            "verbs": ["visit", "explore", "see", "tour", "photograph", "discover", "walk", "enjoy"],
            "objects": ["monuments", "museums", "attractions", "sights", "landmarks"],
            "locations_at": ["at the museum", "at the monument", "at attractions"],
            "locations_in": ["in the city", "in museums", "in historic sites"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["on vacation", "every trip", "on weekends", "annually"],
            "things": ["the attraction", "the museum", "the tour", "the sight"],
            "adjectives_quality": ["beautiful", "historic", "famous", "impressive", "ancient"],
            "nationalities": ["Cambodian", "Laotian", "Burmese", "Indonesian"],
            "countries": ["Cambodia", "Laos", "Myanmar", "Indonesia"],
            "cities": ["Phnom Penh", "Vientiane", "Yangon", "Jakarta"]
        },
        22: {
            "name": "Emergencies abroad",
            "professions": ["a traveler", "a tourist", "an emergency contact", "a helper"],
            "verbs": ["help", "call", "contact", "report", "need", "lose", "find", "solve"],
            "objects": ["documents", "phones", "money", "assistance", "emergencies"],
            "locations_at": ["at the embassy", "at the police station", "at the hospital"],
            "locations_in": ["in trouble", "in an emergency", "in a foreign country"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["in emergencies", "when needed", "immediately", "quickly"],
            "things": ["the problem", "the emergency", "help", "assistance"],
            "adjectives_quality": ["urgent", "serious", "important", "necessary", "immediate"],
            "nationalities": ["Georgian", "Armenian", "Azerbaijani", "Kazakh"],
            "countries": ["Georgia", "Armenia", "Azerbaijan", "Kazakhstan"],
            "cities": ["Tbilisi", "Yerevan", "Baku", "Almaty"]
        },
        23: {
            "name": "Cultural etiquette and customs",
            "professions": ["a visitor", "a guest", "a foreigner", "a local"],
            "verbs": ["respect", "follow", "understand", "observe", "practice", "learn", "adapt", "behave"],
            "objects": ["customs", "traditions", "rules", "etiquette", "culture"],
            "locations_at": ["at events", "at ceremonies", "at gatherings"],
            "locations_in": ["in the country", "in society", "in different cultures"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["in different countries", "abroad", "everywhere", "always"],
            "things": ["the custom", "the tradition", "etiquette", "culture"],
            "adjectives_quality": ["important", "different", "respectful", "traditional", "local"],
            "nationalities": ["Sri Lankan", "Nepali", "Bhutanese", "Mongolian"],
            "countries": ["Sri Lanka", "Nepal", "Bhutan", "Mongolia"],
            "cities": ["Colombo", "Kathmandu", "Thimphu", "Ulaanbaatar"]
        },
        24: {
            "name": "Talking about countries and nationalities",
            "professions": ["a citizen", "a resident", "a native", "an immigrant"],
            "verbs": ["live", "come from", "speak", "belong", "visit", "move", "stay", "travel"],
            "objects": ["languages", "countries", "cultures", "nationalities", "origins"],
            "locations_at": ["at home", "at the border"],
            "locations_in": ["in the country", "in the city", "in different places"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["all the time", "permanently", "temporarily", "now"],
            "things": ["the country", "the nationality", "the language", "the culture"],
            "adjectives_quality": ["native", "foreign", "local", "international", "multicultural"],
            "nationalities": ["Uzbek", "Tajik", "Kyrgyz", "Turkmen"],
            "countries": ["Uzbekistan", "Tajikistan", "Kyrgyzstan", "Turkmenistan"],
            "cities": ["Tashkent", "Dushanbe", "Bishkek", "Ashgabat"]
        },
        26: {
            "name": "Idioms",
            "professions": ["a native speaker", "a language learner", "a teacher", "a translator"],
            "verbs": ["use", "understand", "learn", "mean", "express", "say", "explain", "sound"],
            "objects": ["idioms", "expressions", "meanings", "phrases", "language"],
            "locations_at": ["at school", "at work", "at conversations"],
            "locations_in": ["in English", "in conversations", "in speech"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every day", "in conversations", "regularly", "commonly"],
            "things": ["the idiom", "the expression", "the meaning", "the phrase"],
            "adjectives_quality": ["common", "useful", "confusing", "interesting", "typical"],
            "idioms": [
                "cost an arm and a leg", "break the ice", "piece of cake",
                "hit the nail on the head", "let the cat out of the bag", "spill the beans",
                "under the weather", "once in a blue moon", "break a leg",
                "bite the bullet", "cut corners", "get cold feet"
            ],
            "nationalities": ["American", "British", "Australian", "Canadian"],
            "countries": ["the USA", "the UK", "Australia", "Canada"],
            "cities": ["New York", "London", "Sydney", "Toronto"]
        },
        27: {
            "name": "Slang",
            "professions": ["a teenager", "a young person", "a native speaker", "a friend"],
            "verbs": ["say", "use", "talk", "chat", "speak", "sound", "call", "mean"],
            "objects": ["slang words", "expressions", "phrases", "terms", "language"],
            "locations_at": ["at parties", "at school", "at hangouts"],
            "locations_in": ["in conversations", "in casual speech", "in chats"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every day", "all the time", "constantly", "nowadays"],
            "things": ["the slang", "the word", "the expression", "the term"],
            "adjectives_quality": ["cool", "informal", "casual", "modern", "popular"],
            "slang": [
                "chill", "hang out", "catch up", "hit up", "freak out",
                "zonked", "bummed", "psyched", "bail", "ditch",
                "ace", "bomb", "sweet", "legit", "sick"
            ],
            "nationalities": ["American", "British", "Australian", "Irish"],
            "countries": ["the USA", "the UK", "Australia", "Ireland"],
            "cities": ["Los Angeles", "Manchester", "Melbourne", "Dublin"]
        },
        28: {
            "name": "Phrasal verbs",
            "professions": ["a student", "a learner", "a teacher", "a speaker"],
            "verbs": ["use", "understand", "learn", "practice", "know", "study", "remember", "apply"],
            "objects": ["phrasal verbs", "meanings", "particles", "combinations", "usage"],
            "locations_at": ["at lessons", "at school", "at work"],
            "locations_in": ["in English", "in sentences", "in conversations"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every day", "in speech", "regularly", "constantly"],
            "things": ["the phrasal verb", "the meaning", "the particle", "usage"],
            "adjectives_quality": ["common", "difficult", "important", "useful", "tricky"],
            "phrasal_verbs": [
                "give up", "put off", "turn down", "look after", "take off",
                "get up", "wake up", "go out", "come back", "set up",
                "work out", "figure out", "find out", "carry on", "break down"
            ],
            "nationalities": ["English", "American", "Scottish", "Welsh"],
            "countries": ["England", "the USA", "Scotland", "Wales"],
            "cities": ["Oxford", "Boston", "Glasgow", "Cardiff"]
        },
        29: {
            "name": "Collocations and word patterns",
            "professions": ["a linguist", "a teacher", "a learner", "a writer"],
            "verbs": ["use", "combine", "form", "create", "make", "sound", "say", "write"],
            "objects": ["collocations", "combinations", "patterns", "words", "phrases"],
            "locations_at": ["at work", "at school", "at writing"],
            "locations_in": ["in English", "in texts", "in speech"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every day", "regularly", "in writing", "in speech"],
            "things": ["the collocation", "the pattern", "the combination", "the phrase"],
            "adjectives_quality": ["natural", "correct", "common", "typical", "proper"],
            "nationalities": ["Canadian", "New Zealand", "South African", "Irish"],
            "countries": ["Canada", "New Zealand", "South Africa", "Ireland"],
            "cities": ["Vancouver", "Wellington", "Johannesburg", "Cork"]
        },
        30: {
            "name": "Figurative language and metaphors",
            "professions": ["a poet", "a writer", "an author", "a speaker"],
            "verbs": ["use", "create", "understand", "interpret", "mean", "express", "write", "speak"],
            "objects": ["metaphors", "images", "meanings", "comparisons", "expressions"],
            "locations_at": ["at readings", "at performances"],
            "locations_in": ["in literature", "in poetry", "in speech"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["in writing", "in speech", "regularly", "commonly"],
            "things": ["the metaphor", "the image", "the meaning", "the comparison"],
            "adjectives_quality": ["beautiful", "powerful", "creative", "poetic", "expressive"],
            "nationalities": ["British", "Irish", "American", "Canadian"],
            "countries": ["Britain", "Ireland", "the USA", "Canada"],
            "cities": ["London", "Dublin", "Chicago", "Montreal"]
        },
        31: {
            "name": "Synonyms, antonyms, and nuance",
            "professions": ["a lexicographer", "a teacher", "a student", "a translator"],
            "verbs": ["mean", "differ", "understand", "use", "distinguish", "know", "learn", "choose"],
            "objects": ["synonyms", "antonyms", "meanings", "differences", "nuances"],
            "locations_at": ["at lessons", "at work"],
            "locations_in": ["in the dictionary", "in usage", "in context"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every day", "in writing", "in speech", "constantly"],
            "things": ["the word", "the meaning", "the synonym", "the antonym"],
            "adjectives_quality": ["similar", "different", "opposite", "precise", "subtle"],
            "nationalities": ["European", "Asian", "African", "American"],
            "countries": ["Europe", "Asia", "Africa", "America"],
            "cities": ["Paris", "Tokyo", "Cairo", "New York"]
        },
        32: {
            "name": "Register and tone (formal vs informal)",
            "professions": ["a professional", "a colleague", "a friend", "a student"],
            "verbs": ["speak", "write", "use", "sound", "communicate", "express", "talk", "address"],
            "objects": ["language", "tone", "style", "register", "words"],
            "locations_at": ["at work", "at meetings", "at parties"],
            "locations_in": ["in emails", "in conversations", "in presentations"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["at work", "with friends", "in formal situations", "casually"],
            "things": ["the tone", "the register", "the style", "formality"],
            "adjectives_quality": ["formal", "informal", "casual", "professional", "polite"],
            "nationalities": ["British", "American", "Australian", "Canadian"],
            "countries": ["Britain", "the USA", "Australia", "Canada"],
            "cities": ["London", "Washington", "Canberra", "Ottawa"]
        },
        33: {
            "name": "Common grammar pitfalls",
            "professions": ["a student", "a learner", "a teacher", "a proofreader"],
            "verbs": ["make", "correct", "avoid", "learn", "understand", "fix", "notice", "check"],
            "objects": ["mistakes", "errors", "grammar", "rules", "corrections"],
            "locations_at": ["at school", "at lessons", "at exams"],
            "locations_in": ["in writing", "in speech", "in texts"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every day", "in learning", "regularly", "constantly"],
            "things": ["the mistake", "the error", "the rule", "grammar"],
            "adjectives_quality": ["common", "typical", "frequent", "serious", "simple"],
            "nationalities": ["International", "Global", "Universal", "Worldwide"],
            "countries": ["many countries", "all countries", "different countries", "various countries"],
            "cities": ["major cities", "big cities", "different cities", "various cities"]
        },
        35: {
            "name": "English for IT",
            "professions": ["a developer", "a programmer", "a QA engineer", "a system administrator"],
            "verbs": ["code", "test", "debug", "deploy", "develop", "program", "update", "fix"],
            "objects": ["code", "bugs", "features", "applications", "systems", "databases"],
            "locations_at": ["at the office", "at the desk", "at work"],
            "locations_in": ["in the system", "in the code", "in development"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every day", "daily", "regularly", "constantly"],
            "things": ["the code", "the bug", "the system", "the application"],
            "adjectives_quality": ["efficient", "functional", "stable", "scalable", "secure"],
            "nationalities": ["American", "Indian", "Chinese", "German"],
            "countries": ["the USA", "India", "China", "Germany"],
            "cities": ["Silicon Valley", "Bangalore", "Shenzhen", "Berlin"]
        },
        36: {
            "name": "English for Finance / Accounting",
            "professions": ["an accountant", "a financial analyst", "an auditor", "a CFO"],
            "verbs": ["calculate", "audit", "report", "analyze", "budget", "invest", "forecast", "reconcile"],
            "objects": ["accounts", "reports", "budgets", "statements", "taxes", "revenues"],
            "locations_at": ["at the office", "at meetings", "at audits"],
            "locations_in": ["in accounting", "in finance", "in the department"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every quarter", "monthly", "annually", "regularly"],
            "things": ["the budget", "the report", "the statement", "the account"],
            "adjectives_quality": ["accurate", "detailed", "financial", "fiscal", "profitable"],
            "nationalities": ["American", "British", "Swiss", "Japanese"],
            "countries": ["the USA", "the UK", "Switzerland", "Japan"],
            "cities": ["New York", "London", "Zurich", "Tokyo"]
        },
        37: {
            "name": "English for Law",
            "professions": ["a lawyer", "an attorney", "a judge", "a legal consultant"],
            "verbs": ["represent", "defend", "prosecute", "advise", "argue", "interpret", "draft", "negotiate"],
            "objects": ["cases", "contracts", "laws", "clients", "documents", "agreements"],
            "locations_at": ["at court", "at the office", "at hearings"],
            "locations_in": ["in court", "in the legal system", "in law"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every day", "regularly", "in court", "frequently"],
            "things": ["the case", "the law", "the contract", "the client"],
            "adjectives_quality": ["legal", "lawful", "binding", "valid", "enforceable"],
            "nationalities": ["American", "British", "Canadian", "Australian"],
            "countries": ["the USA", "the UK", "Canada", "Australia"],
            "cities": ["Washington", "London", "Ottawa", "Sydney"]
        },
        38: {
            "name": "English for Medicine",
            "professions": ["a doctor", "a surgeon", "a nurse", "a medical researcher"],
            "verbs": ["treat", "diagnose", "examine", "prescribe", "operate", "cure", "prevent", "monitor"],
            "objects": ["patients", "symptoms", "diseases", "medications", "treatments", "diagnoses"],
            "locations_at": ["at the hospital", "at the clinic", "at surgeries"],
            "locations_in": ["in the hospital", "in medicine", "in the operating room"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every day", "daily", "regularly", "constantly"],
            "things": ["the patient", "the treatment", "the diagnosis", "the medication"],
            "adjectives_quality": ["medical", "clinical", "healthy", "serious", "critical"],
            "nationalities": ["American", "British", "German", "French"],
            "countries": ["the USA", "the UK", "Germany", "France"],
            "cities": ["Boston", "London", "Munich", "Paris"]
        },
        39: {
            "name": "English for Marketing and PR",
            "professions": ["a PR specialist", "a marketing manager", "a brand manager", "a communications director"],
            "verbs": ["promote", "brand", "communicate", "advertise", "launch", "position", "target", "engage"],
            "objects": ["campaigns", "brands", "messages", "audiences", "content", "strategies"],
            "locations_at": ["at agencies", "at events", "at launches"],
            "locations_in": ["in marketing", "in PR", "in communications"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every campaign", "regularly", "constantly", "frequently"],
            "things": ["the campaign", "the brand", "the message", "the audience"],
            "adjectives_quality": ["effective", "creative", "strategic", "innovative", "viral"],
            "nationalities": ["American", "British", "French", "Japanese"],
            "countries": ["the USA", "the UK", "France", "Japan"],
            "cities": ["New York", "London", "Paris", "Tokyo"]
        },
        40: {
            "name": "English for HR",
            "professions": ["an HR manager", "a recruiter", "an HR specialist", "a talent acquisition specialist"],
            "verbs": ["hire", "recruit", "interview", "train", "evaluate", "manage", "develop", "retain"],
            "objects": ["employees", "candidates", "positions", "interviews", "training", "performance"],
            "locations_at": ["at the office", "at interviews", "at training sessions"],
            "locations_in": ["in HR", "in the department", "in recruitment"],
            "frequency_adverbs": ["always", "usually", "often", "sometimes", "rarely", "never"],
            "time_markers": ["every week", "regularly", "monthly", "constantly"],
            "things": ["the candidate", "the employee", "the position", "the interview"],
            "adjectives_quality": ["qualified", "experienced", "suitable", "talented", "professional"],
            "nationalities": ["American", "British", "German", "Dutch"],
            "countries": ["the USA", "the UK", "Germany", "the Netherlands"],
            "cities": ["Chicago", "Manchester", "Frankfurt", "Amsterdam"]
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
    # УРОК 1: Что такое Present Simple и когда его используют (7 вопросов)
    # ========================================

    def generate_lesson1_q1(self, topic_id: int) -> Dict:
        """L1Q1: Когда НЕ используется Present Simple (регулярность/сейчас)"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["verbs"])

        question = "В каком случае мы НЕ используем Present Simple?"
        correct = "Для описания действия, которое происходит прямо сейчас в момент речи"
        wrong_options = [
            "Для описания регулярных действий и привычек",
            "Для описания общих фактов и истин",
            "Для описания расписаний и графиков"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "easy",
            "explanation": "Present Simple используется для регулярных действий, фактов и расписаний, но НЕ для действий в момент речи."
        }

    def generate_lesson1_q2(self, topic_id: int) -> Dict:
        """L1Q2: Определение общего факта"""
        topic = self.TOPICS[topic_id]
        thing = random.choice(topic["things"])

        question = "Какое предложение описывает общий факт?"
        
        # Для разных топиков делаем разные факты
        if topic_id in [3]:  # Weather
            correct = "The Sun rises in the east."
            wrongs = [
                "I am reading a book now.",
                "She is working at the moment.",
                "They are having dinner."
            ]
        elif topic_id in [4, 38]:  # Health/Medicine
            correct = "Water boils at 100 degrees Celsius."
            wrongs = [
                "The patient is sleeping now.",
                "She is feeling better today.",
                "They are waiting for results."
            ]
        else:
            correct = f"{thing.capitalize()} is important."
            wrongs = [
                "I am working now.",
                "She is studying at the moment.",
                "They are meeting today."
            ]

        options, correct_answer = self._shuffle_options(correct, wrongs)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "easy",
            "explanation": "Общие факты и истины выражаются в Present Simple."
        }

    def generate_lesson1_q3(self, topic_id: int) -> Dict:
        """L1Q3: Слово-маркер Present Simple"""
        topic = self.TOPICS[topic_id]

        question = "Какое слово-маркер чаще всего указывает на Present Simple?"
        correct = "every day"
        wrong_options = ["now", "at the moment", "currently"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "easy",
            "explanation": "'Every day' указывает на регулярное действие, что характерно для Present Simple."
        }

    def generate_lesson1_q4(self, topic_id: int) -> Dict:
        """L1Q4: Выбор правильного использования Present Simple с расписанием"""
        topic = self.TOPICS[topic_id]
        
        if topic_id in [6, 20]:  # Transportation, Airport
            subject = "The train"
            action = "leaves"
            time = "at 8 AM"
        elif topic_id in [7, 21]:  # Leisure, Sightseeing
            subject = "The movie"
            action = "starts"
            time = "at 7 PM"
        else:
            subject = "The store"
            action = "opens"
            time = "at 9 AM"

        question = f"Выберите правильное предложение с расписанием:"
        correct = f"{subject} {action} {time}."
        wrong_options = [
            f"{subject} is {action.rstrip('s')}ing {time}.",
            f"{subject} {action.rstrip('s')} {time}.",
            f"{subject} {action}ing {time}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "medium",
            "explanation": f"Расписания выражаются в Present Simple: {subject} {action} {time}"
        }

    def generate_lesson1_q5(self, topic_id: int) -> Dict:
        """L1Q5: Постоянная ситуация"""
        topic = self.TOPICS[topic_id]
        city = random.choice(topic["cities"])
        profession = random.choice(topic["professions"])

        question = "Какое предложение описывает постоянную ситуацию?"
        correct = f"I live in {city}."
        wrong_options = [
            f"I am living in {city} this month.",
            "I will live there.",
            "I lived there before."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "medium",
            "explanation": f"Постоянные ситуации (где живешь, работаешь) описываются в Present Simple."
        }

    def generate_lesson1_q6(self, topic_id: int) -> Dict:
        """L1Q6: Слово-маркер НЕ для Present Simple"""
        topic = self.TOPICS[topic_id]

        question = "С каким словом-маркером НЕ используется Present Simple?"
        correct = "right now"
        wrong_options = ["always", "usually", "sometimes"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "medium",
            "explanation": "'Right now' указывает на действие в момент речи, поэтому используется Present Continuous."
        }

    def generate_lesson1_q7(self, topic_id: int) -> Dict:
        """L1Q7: Привычка с маркером времени"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["verbs"])
        obj = random.choice(topic["objects"])
        time_marker = random.choice(topic["time_markers"])

        question = "Какое предложение правильно описывает привычку?"
        correct = f"She {verb}s {obj} {time_marker}."
        wrong_options = [
            f"She is {verb}ing {obj} {time_marker}.",
            f"She {verb} {obj} now.",
            f"She {verb}ed {obj} yesterday."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "hard",
            "explanation": f"Регулярные действия с маркерами времени ('{time_marker}') используют Present Simple."
        }

    # ========================================
    # УРОК 2: Утвердительные предложения в Present Simple (6 вопросов)
    # ========================================

    def generate_lesson2_q1(self, topic_id: int) -> Dict:
        """L2Q1: Простой выбор формы глагола для I"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["verbs"])
        location = random.choice(topic["locations_in"])

        question = f"Выберите правильную форму глагола:\nI _____ {location}."
        correct = verb
        wrong_options = [f"{verb}s", f"{verb}ing", f"am {verb}"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": f"С 'I' используется базовая форма глагола: I {verb}."
        }

    def generate_lesson2_q2(self, topic_id: int) -> Dict:
        """L2Q2: Выбор формы для We/They"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["verbs"])
        obj = random.choice(topic["objects"])
        subject = random.choice(["We", "They"])

        question = f"Выберите правильную форму глагола:\n{subject} _____ {obj}."
        correct = verb
        wrong_options = [f"{verb}s", f"{verb}ing", f"are {verb}"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": f"С '{subject}' используется базовая форма глагола: {subject} {verb}."
        }

    def generate_lesson2_q3(self, topic_id: int) -> Dict:
        """L2Q3: Правильное утвердительное предложение"""
        topic = self.TOPICS[topic_id]
        city = random.choice(topic["cities"])
        profession = random.choice(topic["professions"])

        question = "Выберите правильное утвердительное предложение:"
        correct = f"Maria lives in {city}."
        wrong_options = [
            f"Maria live in {city}.",
            f"Maria living in {city}.",
            f"Maria is live in {city}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "medium",
            "explanation": f"Для третьего лица единственного числа добавляем -s: Maria lives."
        }

    def generate_lesson2_q4(self, topic_id: int) -> Dict:
        """L2Q4: Предложение о привычке"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["verbs"])
        obj = random.choice(topic["objects"])
        time_marker = random.choice(topic["time_markers"])

        question = f"Выберите правильное предложение о привычке:"
        correct = f"I {verb} {obj} {time_marker}."
        wrong_options = [
            f"I {verb}s {obj} {time_marker}.",
            f"I am {verb} {obj} {time_marker}.",
            f"I {verb}ing {obj} {time_marker}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "medium",
            "explanation": f"Регулярные действия в Present Simple: I {verb} {obj} {time_marker}."
        }

    def generate_lesson2_q5(self, topic_id: int) -> Dict:
        """L2Q5: Общий факт с They"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["verbs"])
        
        if topic_id == 3:  # Weather
            subject = "Birds"
            verb_used = "fly"
        elif topic_id == 4:  # Health
            subject = "Doctors"
            verb_used = "help"
        else:
            subject = "People"
            verb_used = verb

        question = "Выберите правильное предложение с общим фактом:"
        correct = f"{subject} {verb_used}."
        wrong_options = [
            f"{subject} {verb_used}s.",
            f"{subject} {verb_used}ing.",
            f"{subject} is {verb_used}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "medium",
            "explanation": f"Общие факты во множественном числе: {subject} {verb_used}."
        }

    def generate_lesson2_q6(self, topic_id: int) -> Dict:
        """L2Q6: Сложное утверждение с профессией"""
        topic = self.TOPICS[topic_id]
        profession = random.choice(topic["professions"])
        location = random.choice(topic["locations_at"])

        question = f"Выберите правильное предложение:"
        correct = f"My brother works as {profession}."
        wrong_options = [
            f"My brother work as {profession}.",
            f"My brother working as {profession}.",
            f"My brother is work as {profession}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "hard",
            "explanation": "'My brother' (he) требует окончания -s: works."
        }

    # ========================================
    # УРОК 3: Третье лицо единственного числа (He/She/It + S) (8 вопросов)
    # ========================================

    def generate_lesson3_q1(self, topic_id: int) -> Dict:
        """L3Q1: Простое добавление -s"""
        topic = self.TOPICS[topic_id]
        verb = random.choice([v for v in topic["verbs"] if not v.endswith(('s', 'sh', 'ch', 'x', 'o', 'y'))])
        obj = random.choice(topic["objects"])

        question = f"Выберите правильную форму глагола:\nShe _____ {obj}."
        
        # Проверяем, что глагол не исключение
        if verb == "have":
            correct = "has"
        else:
            correct = f"{verb}s"
        
        wrong_options = [verb, f"{verb}es", f"{verb}ing"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": f"Для he/she/it добавляем -s: She {correct}."
        }

    def generate_lesson3_q2(self, topic_id: int) -> Dict:
        """L3Q2: Глаголы на -s, -sh, -ch, -x, -o → -es"""
        topic = self.TOPICS[topic_id]
        
        # Выбираем глаголы, которые требуют -es
        es_verbs = {
            "watch": "watches", "go": "goes", "do": "does",
            "teach": "teaches", "fix": "fixes", "wash": "washes"
        }
        
        # Ищем подходящий глагол из топика
        verb = None
        for v in topic["verbs"]:
            if v in es_verbs:
                verb = v
                break
        
        # Если не нашли, используем стандартные
        if not verb:
            verb = random.choice(["watch", "go"])
        
        correct_form = es_verbs.get(verb, f"{verb}es")

        question = f"Выберите правильную форму глагола:\nHe _____ ."
        correct = correct_form
        wrong_options = [f"{verb}s", verb, f"{verb}ing"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "medium",
            "explanation": f"Глаголы на -s, -sh, -ch, -x, -o принимают окончание -es: {correct}."
        }

    def generate_lesson3_q3(self, topic_id: int) -> Dict:
        """L3Q3: Согласная + Y → IES"""
        topic = self.TOPICS[topic_id]
        
        # Глаголы на согласную + y
        y_verbs = {"study": "studies", "try": "tries", "fly": "flies", "carry": "carries"}
        
        verb = None
        for v in topic["verbs"]:
            if v in y_verbs:
                verb = v
                break
        
        if not verb:
            verb = "study"
        
        correct_form = y_verbs.get(verb, f"{verb[:-1]}ies")

        question = f"Выберите правильную форму глагола:\nShe _____ hard."
        correct = correct_form
        wrong_options = [f"{verb}s", verb, f"{verb}es"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "medium",
            "explanation": f"Глаголы на согласную + y: y → ies. {verb} → {correct}."
        }

    def generate_lesson3_q4(self, topic_id: int) -> Dict:
        """L3Q4: Исключение HAVE → HAS"""
        topic = self.TOPICS[topic_id]
        obj = random.choice(topic["objects"])

        question = f"Выберите правильную форму глагола:\nShe _____ {obj}."
        correct = "has"
        wrong_options = ["have", "haves", "having"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": "HAVE — исключение! Для he/she/it используется HAS."
        }

    def generate_lesson3_q5(self, topic_id: int) -> Dict:
        """L3Q5: Предложение с животным/предметом (It)"""
        topic = self.TOPICS[topic_id]
        
        if topic_id == 3:  # Weather
            subject = "The sun"
            verb = "shines"
        elif topic_id == 9:  # Technology
            subject = "This computer"
            verb = "works"
        else:
            subject = "It"
            verb = f"{random.choice(topic['verbs'])}s"

        question = f"Выберите правильное предложение:"
        correct = f"{subject} {verb} very well."
        wrong_options = [
            f"{subject} {verb[:-1]} very well.",
            f"{subject} {verb}ing very well.",
            f"{subject} are {verb[:-1]} very well."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "medium",
            "explanation": f"'It' (третье лицо) требует -s: {subject} {verb}."
        }

    def generate_lesson3_q6(self, topic_id: int) -> Dict:
        """L3Q6: С наречием частоты"""
        topic = self.TOPICS[topic_id]
        adverb = random.choice(topic["frequency_adverbs"])
        location = random.choice(topic["locations_at"])

        question = f"Выберите правильное предложение:"
        correct = f"He {adverb} arrives {location} on time."
        wrong_options = [
            f"He {adverb} arrive {location} on time.",
            f"He {adverb} arriving {location} on time.",
            f"He {adverb} is arrive {location} on time."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "medium",
            "explanation": f"С he/she/it глагол принимает -s даже с наречием: He {adverb} arrives."
        }

    def generate_lesson3_q7(self, topic_id: int) -> Dict:
        """L3Q7: Правило для гласная + Y"""
        topic = self.TOPICS[topic_id]
        
        # Глаголы на гласную + y (просто +s)
        vowel_y_verbs = {"play": "plays", "say": "says", "buy": "buys", "pay": "pays"}
        
        verb = None
        for v in topic["verbs"]:
            if v in vowel_y_verbs:
                verb = v
                break
        
        if not verb:
            verb = "play"
        
        correct_form = vowel_y_verbs.get(verb, f"{verb}s")

        question = f"Выберите правильную форму глагола:\nShe _____ ."
        correct = correct_form
        wrong_options = [f"{verb[:-1]}ies", verb, f"{verb}es"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "hard",
            "explanation": f"Гласная + y: просто добавляем -s. {verb} → {correct}."
        }

    def generate_lesson3_q8(self, topic_id: int) -> Dict:
        """L3Q8: Найти ошибку в третьем лице"""
        topic = self.TOPICS[topic_id]
        city = random.choice(topic["cities"])
        profession = random.choice(topic["professions"])

        question = "Какое предложение содержит ОШИБКУ?"
        
        options_list = [
            f"Anna works as {profession}.",
            f"Tom lives in {city}.",
            "My friend speaks well.",
            f"Sarah teach students."  # Ошибка!
        ]

        correct = options_list[3]
        options = {"A": options_list[0], "B": options_list[1], "C": options_list[2], "D": options_list[3]}
        correct_answer = "D"

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "hard",
            "explanation": "Sarah (she) требует окончания -s: Sarah teaches."
        }

    # ========================================
    # УРОК 4: Отрицательные предложения (7 вопросов)
    # ========================================

    def generate_lesson4_q1(self, topic_id: int) -> Dict:
        """L4Q1: Простое отрицание с don't"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["verbs"])
        time_marker = random.choice(topic["time_markers"])

        question = f"Выберите правильное отрицательное предложение:"
        correct = f"I don't {verb} {time_marker}."
        wrong_options = [
            f"I not {verb} {time_marker}.",
            f"I doesn't {verb} {time_marker}.",
            f"I don't {verb}s {time_marker}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "easy",
            "explanation": f"С I используется don't + базовая форма глагола: I don't {verb}."
        }

    def generate_lesson4_q2(self, topic_id: int) -> Dict:
        """L4Q2: Выбор doesn't для he/she/it"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["verbs"])
        time_marker = random.choice(topic["time_markers"])

        question = f"Выберите правильное отрицательное предложение:"
        correct = f"He doesn't {verb} {time_marker}."
        wrong_options = [
            f"He don't {verb} {time_marker}.",
            f"He doesn't {verb}s {time_marker}.",
            f"He not {verb} {time_marker}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "easy",
            "explanation": f"С he/she/it используется doesn't + базовая форма: He doesn't {verb}."
        }

    def generate_lesson4_q3(self, topic_id: int) -> Dict:
        """L4Q3: Форма глагола после doesn't"""
        topic = self.TOPICS[topic_id]
        obj = random.choice(topic["objects"])

        question = "Какая форма глагола используется после don't/doesn't?"
        correct = "инфинитив без to (базовая форма)"
        wrong_options = [
            "глагол с окончанием -s",
            "глагол с окончанием -ing",
            "глагол с окончанием -ed"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "medium",
            "explanation": "После don't/doesn't всегда используется базовая форма глагола без окончаний."
        }

    def generate_lesson4_q4(self, topic_id: int) -> Dict:
        """L4Q4: Найти ошибку - неправильный вспомогательный глагол"""
        topic = self.TOPICS[topic_id]
        obj = random.choice(topic["objects"])

        question = "Найдите ошибку в предложении: 'She don't like coffee.'"
        correct = "нужно 'doesn't' вместо 'don't'"
        wrong_options = [
            "нужно 'likes' вместо 'like'",
            "нужно убрать 'don't'",
            "ошибок нет"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "medium",
            "explanation": "She (третье лицо) требует doesn't, а не don't."
        }

    def generate_lesson4_q5(self, topic_id: int) -> Dict:
        """L4Q5: Отрицание с They"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["verbs"])

        question = f"Выберите правильное предложение:"
        correct = f"They don't {verb}."
        wrong_options = [
            f"They doesn't {verb}.",
            f"They don't {verb}s.",
            f"They doesn't {verb}s."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "medium",
            "explanation": f"They (множественное число) использует don't: They don't {verb}."
        }

    def generate_lesson4_q6(self, topic_id: int) -> Dict:
        """L4Q6: Ошибка - сохранение -s после doesn't"""
        topic = self.TOPICS[topic_id]
        location = random.choice(topic["locations_at"])

        question = "Какое предложение содержит ОШИБКУ?"
        
        options_list = [
            "I don't speak French.",
            "He doesn't work here.",
            "We don't live in London.",
            "She doesn't works here."  # Ошибка!
        ]

        correct = options_list[3]
        options = {"A": options_list[0], "B": options_list[1], "C": options_list[2], "D": options_list[3]}
        correct_answer = "D"

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "hard",
            "explanation": "После doesn't глагол БЕЗ -s: She doesn't work (не works)."
        }

    def generate_lesson4_q7(self, topic_id: int) -> Dict:
        """L4Q7: Сложное отрицание с профессией"""
        topic = self.TOPICS[topic_id]
        profession = random.choice(topic["professions"])
        city = random.choice(topic["cities"])

        question = f"Выберите правильное отрицательное предложение:"
        correct = f"Maria doesn't live in {city}."
        wrong_options = [
            f"Maria don't live in {city}.",
            f"Maria doesn't lives in {city}.",
            f"Maria not live in {city}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "hard",
            "explanation": f"Maria (she) требует doesn't + базовую форму: doesn't live."
        }

    # ========================================
    # УРОК 5: Общие вопросы (Yes/No Questions) (7 вопросов)
    # ========================================

    def generate_lesson5_q1(self, topic_id: int) -> Dict:
        """L5Q1: Простой вопрос с Do"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["verbs"])
        nationality = random.choice(topic["nationalities"])

        question = f"Выберите правильный вопрос:"
        correct = f"Do you {verb}?"
        wrong_options = [
            f"Does you {verb}?",
            f"Are you {verb}?",
            f"You {verb}?"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "easy",
            "explanation": f"С you используется Do + базовая форма: Do you {verb}?"
        }

    def generate_lesson5_q2(self, topic_id: int) -> Dict:
        """L5Q2: Вопрос с Does"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["verbs"])
        location = random.choice(topic["locations_in"])

        question = f"Выберите правильный вопрос:"
        correct = f"Does he {verb} {location}?"
        wrong_options = [
            f"Do he {verb} {location}?",
            f"Does he {verb}s {location}?",
            f"Is he {verb} {location}?"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "easy",
            "explanation": f"С he используется Does + базовая форма: Does he {verb}?"
        }

    def generate_lesson5_q3(self, topic_id: int) -> Dict:
        """L5Q3: Краткий положительный ответ"""
        topic = self.TOPICS[topic_id]

        question = "Какой краткий ответ правильный на вопрос 'Do you work here?'"
        correct = "Yes, I do."
        wrong_options = [
            "Yes, I work.",
            "Yes, I am.",
            "Yes, I does."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "medium",
            "explanation": "Краткий ответ использует do/does: Yes, I do."
        }

    def generate_lesson5_q4(self, topic_id: int) -> Dict:
        """L5Q4: Краткий отрицательный ответ"""
        topic = self.TOPICS[topic_id]

        question = "Какой краткий отрицательный ответ на вопрос 'Does he play tennis?'"
        correct = "No, he doesn't."
        wrong_options = [
            "No, he don't.",
            "No, he isn't.",
            "No, he not."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "medium",
            "explanation": "Для he/she/it отрицательный краткий ответ: No, he doesn't."
        }

    def generate_lesson5_q5(self, topic_id: int) -> Dict:
        """L5Q5: Вопрос с They"""
        topic = self.TOPICS[topic_id]
        city = random.choice(topic["cities"])

        question = f"Выберите правильный вопрос:"
        correct = f"Do they live in {city}?"
        wrong_options = [
            f"Does they live in {city}?",
            f"Do they lives in {city}?",
            f"Are they live in {city}?"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "medium",
            "explanation": f"They (множественное число) использует Do: Do they live?"
        }

    def generate_lesson5_q6(self, topic_id: int) -> Dict:
        """L5Q6: Найти ошибку в вопросе"""
        topic = self.TOPICS[topic_id]

        question = "Какой вопрос содержит ОШИБКУ?"
        
        options_list = [
            "Do you speak English?",
            "Does she like coffee?",
            "Does it rains often?",  # Ошибка!
            "Do they work here?"
        ]

        correct = options_list[2]
        options = {"A": options_list[0], "B": options_list[1], "C": options_list[2], "D": options_list[3]}
        correct_answer = "C"

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "hard",
            "explanation": "После does глагол БЕЗ -s: Does it rain (не rains)?"
        }

    def generate_lesson5_q7(self, topic_id: int) -> Dict:
        """L5Q7: Диалог - вопрос и ответ"""
        topic = self.TOPICS[topic_id]
        profession = random.choice(topic["professions"])
        location = random.choice(topic["locations_at"])

        question = f"Выберите правильный диалог:"
        correct = f"A: Does Sarah work {location}? B: Yes, she does."
        wrong_options = [
            f"A: Does Sarah works {location}? B: Yes, she does.",
            f"A: Does Sarah work {location}? B: Yes, she do.",
            f"A: Do Sarah work {location}? B: Yes, she does."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "hard",
            "explanation": "Правильная форма: Does Sarah work? Yes, she does."
        }

    # ========================================
    # УРОК 6: Специальные вопросы (Wh-Questions) (8 вопросов)
    # ========================================

    def generate_lesson6_q1(self, topic_id: int) -> Dict:
        """L6Q1: Where вопрос"""
        topic = self.TOPICS[topic_id]

        question = f"Выберите правильный вопрос:"
        correct = "Where do you live?"
        wrong_options = [
            "Where you live?",
            "Where does you live?",
            "Where are you live?"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": "Where + do/does + подлежащее + глагол: Where do you live?"
        }

    def generate_lesson6_q2(self, topic_id: int) -> Dict:
        """L6Q2: What вопрос"""
        topic = self.TOPICS[topic_id]

        question = "Выберите правильный вопрос о профессии:"
        correct = "What do you do?"
        wrong_options = [
            "What you do?",
            "What does you do?",
            "What are you do?"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": "'What do you do?' — стандартный вопрос о профессии."
        }

    def generate_lesson6_q3(self, topic_id: int) -> Dict:
        """L6Q3: When вопрос"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["verbs"])

        question = f"Выберите правильный вопрос:"
        correct = f"When do you {verb}?"
        wrong_options = [
            f"When you {verb}?",
            f"When does you {verb}?",
            f"When are you {verb}?"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "medium",
            "explanation": f"When + do + you + глагол: When do you {verb}?"
        }

    def generate_lesson6_q4(self, topic_id: int) -> Dict:
        """L6Q4: Why вопрос с he/she"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["verbs"])

        question = f"Выберите правильный вопрос:"
        correct = f"Why does he {verb}?"
        wrong_options = [
            f"Why do he {verb}?",
            f"Why does he {verb}s?",
            f"Why he {verb}s?"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "medium",
            "explanation": f"Why + does + he + базовая форма: Why does he {verb}?"
        }

    def generate_lesson6_q5(self, topic_id: int) -> Dict:
        """L6Q5: How often вопрос"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["verbs"])

        question = f"Выберите правильный вопрос о частоте:"
        correct = f"How often do you {verb}?"
        wrong_options = [
            f"How often you {verb}?",
            f"How often does you {verb}?",
            f"How often are you {verb}?"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "medium",
            "explanation": f"How often + do/does + подлежащее + глагол."
        }

    def generate_lesson6_q6(self, topic_id: int) -> Dict:
        """L6Q6: Who как подлежащее (без do/does)"""
        topic = self.TOPICS[topic_id]
        city = random.choice(topic["cities"])

        question = f"Выберите правильный вопрос:"
        correct = f"Who lives in {city}?"
        wrong_options = [
            f"Who do live in {city}?",
            f"Who does lives in {city}?",
            f"Who live in {city}?"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "hard",
            "explanation": "Когда Who — подлежащее, НЕ используем do/does: Who lives?"
        }

    def generate_lesson6_q7(self, topic_id: int) -> Dict:
        """L6Q7: Найти ошибку в Wh-вопросе"""
        topic = self.TOPICS[topic_id]

        question = "Какой вопрос содержит ОШИБКУ?"
        
        options_list = [
            "What do you do?",
            "Where does she live?",
            "When do they arrive?",
            "Why does they work here?"  # Ошибка!
        ]

        correct = options_list[3]
        options = {"A": options_list[0], "B": options_list[1], "C": options_list[2], "D": options_list[3]}
        correct_answer = "D"

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "hard",
            "explanation": "They (множественное число) требует do, а не does: Why do they work?"
        }

    def generate_lesson6_q8(self, topic_id: int) -> Dict:
        """L6Q8: Who teaches (подлежащее)"""
        topic = self.TOPICS[topic_id]

        question = "Выберите правильный вопрос:"
        correct = "Who teaches this class?"
        wrong_options = [
            "Who do teach this class?",
            "Who does teach this class?",
            "Who teach this class?"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "hard",
            "explanation": "Who как подлежащее: глагол с -s, без do/does. Who teaches?"
        }

    # ========================================
    # УРОК 7: Глаголы-исключения и особые случаи (7 вопросов)
    # ========================================

    def generate_lesson7_q1(self, topic_id: int) -> Dict:
        """L7Q1: Глагол TO BE не использует do/does"""
        topic = self.TOPICS[topic_id]
        profession = random.choice(topic["professions"])

        question = "Какой вопрос правильный с глаголом TO BE?"
        correct = f"Are you {profession}?"
        wrong_options = [
            f"Do you are {profession}?",
            f"Does you are {profession}?",
            f"Do you be {profession}?"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "easy",
            "explanation": "TO BE не использует do/does. Правильно: Are you...?"
        }

    def generate_lesson7_q2(self, topic_id: int) -> Dict:
        """L7Q2: Отрицание с TO BE"""
        topic = self.TOPICS[topic_id]
        nationality = random.choice(topic["nationalities"])

        question = "Какое отрицание правильное с глаголом TO BE?"
        correct = f"I am not {nationality}."
        wrong_options = [
            f"I don't am {nationality}.",
            f"I doesn't be {nationality}.",
            f"I not am {nationality}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "easy",
            "explanation": "TO BE: отрицание am not/is not/are not (без do/does)."
        }

    def generate_lesson7_q3(self, topic_id: int) -> Dict:
        """L7Q3: HAVE с do/does (современный английский)"""
        topic = self.TOPICS[topic_id]
        obj = random.choice(topic["objects"])

        question = "Какая форма используется в современном английском?"
        correct = f"Do you have {obj}?"
        wrong_options = [
            f"Have you {obj}?",
            f"Does you have {obj}?",
            f"Are you have {obj}?"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "medium",
            "explanation": "В современном английском HAVE используется с do/does: Do you have?"
        }

    def generate_lesson7_q4(self, topic_id: int) -> Dict:
        """L7Q4: Модальный глагол CAN без -s"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["verbs"])

        question = "Выберите правильное предложение с модальным глаголом:"
        correct = f"He can {verb}."
        wrong_options = [
            f"He cans {verb}.",
            f"He can {verb}s.",
            f"He can to {verb}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "medium",
            "explanation": "Модальные глаголы НЕ добавляют -s: He can (не cans)."
        }

    def generate_lesson7_q5(self, topic_id: int) -> Dict:
        """L7Q5: Вопрос с CAN без do/does"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["verbs"])

        question = "Выберите правильный вопрос с модальным глаголом:"
        correct = f"Can you {verb}?"
        wrong_options = [
            f"Do you can {verb}?",
            f"Does you can {verb}?",
            f"Are you can {verb}?"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "medium",
            "explanation": "Модальные глаголы НЕ используют do/does: Can you...?"
        }

    def generate_lesson7_q6(self, topic_id: int) -> Dict:
        """L7Q6: Отрицание с HAVE"""
        topic = self.TOPICS[topic_id]
        obj = random.choice(topic["objects"])

        question = "Какое предложение правильное?"
        correct = f"She doesn't have {obj}."
        wrong_options = [
            f"She doesn't has {obj}.",
            f"She don't have {obj}.",
            f"She hasn't {obj}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "hard",
            "explanation": "HAVE в отрицании: doesn't have (базовая форма после doesn't)."
        }

    def generate_lesson7_q7(self, topic_id: int) -> Dict:
        """L7Q7: Найти ошибку с особыми глаголами"""
        topic = self.TOPICS[topic_id]

        question = "Какое предложение содержит ОШИБКУ?"
        
        options_list = [
            "I am a teacher.",
            "Can he swim?",
            "Do you have a car?",
            "Does he can drive?"  # Ошибка!
        ]

        correct = options_list[3]
        options = {"A": options_list[0], "B": options_list[1], "C": options_list[2], "D": options_list[3]}
        correct_answer = "D"

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "hard",
            "explanation": "Модальные глаголы НЕ используют does: Can he drive? (не Does he can)"
        }

    # ========================================
    # УРОК 8: Наречия частоты (Frequency Adverbs) (7 вопросов)
    # ========================================

    def generate_lesson8_q1(self, topic_id: int) -> Dict:
        """L8Q1: Место наречия ПЕРЕД глаголом"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["verbs"])
        obj = random.choice(topic["objects"])

        question = f"Выберите правильное предложение:"
        correct = f"I always {verb} {obj}."
        wrong_options = [
            f"I {verb} always {obj}.",
            f"Always I {verb} {obj}.",
            f"I {verb} {obj} always."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 8,
            "difficulty": "easy",
            "explanation": f"Наречие частоты ставится ПЕРЕД основным глаголом: I always {verb}."
        }

    def generate_lesson8_q2(self, topic_id: int) -> Dict:
        """L8Q2: Наречие ПОСЛЕ глагола TO BE"""
        topic = self.TOPICS[topic_id]
        adjective = random.choice(topic["adjectives_quality"])

        question = f"Выберите правильное предложение с глаголом TO BE:"
        correct = f"She is usually {adjective}."
        wrong_options = [
            f"She usually is {adjective}.",
            f"Usually she is {adjective}.",
            f"She is {adjective} usually."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 8,
            "difficulty": "easy",
            "explanation": "Наречие частоты ставится ПОСЛЕ глагола TO BE: is usually."
        }

    def generate_lesson8_q3(self, topic_id: int) -> Dict:
        """L8Q3: Наречие always (100%)"""
        topic = self.TOPICS[topic_id]

        question = "Какое наречие означает 100% частоту?"
        correct = "always"
        wrong_options = ["usually", "often", "sometimes"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 8,
            "difficulty": "easy",
            "explanation": "'Always' означает всегда (100% частоту)."
        }

    def generate_lesson8_q4(self, topic_id: int) -> Dict:
        """L8Q4: Наречие never (0%)"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["verbs"])

        question = "Выберите правильное предложение с 'never':"
        correct = f"I never {verb}."
        wrong_options = [
            f"I don't never {verb}.",
            f"I never don't {verb}.",
            f"I not never {verb}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 8,
            "difficulty": "medium",
            "explanation": "Never уже содержит отрицание, don't не нужен: I never..."
        }

    def generate_lesson8_q5(self, topic_id: int) -> Dict:
        """L8Q5: Порядок слов с наречием"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["verbs"])
        location = random.choice(topic["locations_at"])

        question = f"Выберите правильное предложение:"
        correct = f"They often {verb} {location}."
        wrong_options = [
            f"They {verb} often {location}.",
            f"Often they {verb} {location}.",
            f"They {verb} {location} often."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 8,
            "difficulty": "medium",
            "explanation": f"Наречие перед глаголом: They often {verb}."
        }

    def generate_lesson8_q6(self, topic_id: int) -> Dict:
        """L8Q6: Найти ошибку с наречием"""
        topic = self.TOPICS[topic_id]

        question = "Какое предложение содержит ОШИБКУ?"
        
        options_list = [
            "She always arrives on time.",
            "I usually drink coffee.",
            "I drink always tea.",  # Ошибка!
            "They often visit us."
        ]

        correct = options_list[2]
        options = {"A": options_list[0], "B": options_list[1], "C": options_list[2], "D": options_list[3]}
        correct_answer = "C"

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 8,
            "difficulty": "hard",
            "explanation": "Наречие ставится ПЕРЕД глаголом: I always drink (не drink always)."
        }

    def generate_lesson8_q7(self, topic_id: int) -> Dict:
        """L8Q7: Сложное предложение с наречием и he/she"""
        topic = self.TOPICS[topic_id]
        verb = random.choice(topic["verbs"])
        time_marker = random.choice(topic["time_markers"])

        question = f"Выберите правильное предложение:"
        correct = f"He sometimes {verb}s {time_marker}."
        wrong_options = [
            f"He sometimes {verb} {time_marker}.",
            f"He {verb}s sometimes {time_marker}.",
            f"Sometimes he {verb} {time_marker}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 8,
            "difficulty": "hard",
            "explanation": f"He + наречие + глагол с -s: He sometimes {verb}s."
        }

    # ========================================
    # УРОК 9: Типичные ошибки (8 вопросов)
    # ========================================

    def generate_lesson9_q1(self, topic_id: int) -> Dict:
        """L9Q1: Ошибка - забыли добавить -s"""
        topic = self.TOPICS[topic_id]
        city = random.choice(topic["cities"])

        question = "Найдите ошибку: 'He work in Berlin.'"
        correct = "нужно 'works' вместо 'work'"
        wrong_options = [
            "нужно 'is working' вместо 'work'",
            "нужно 'does work' вместо 'work'",
            "ошибок нет"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 9,
            "difficulty": "easy",
            "explanation": "He/she/it требует окончания -s: He works."
        }

    def generate_lesson9_q2(self, topic_id: int) -> Dict:
        """L9Q2: Ошибка - -s после doesn't"""
        topic = self.TOPICS[topic_id]

        question = "Какое предложение содержит ОШИБКУ?"
        
        options_list = [
            "I always drink coffee.",
            "She doesn't work here.",
            "He doesn't works here.",  # Ошибка!
            "Do you speak English?"
        ]

        correct = options_list[2]
        options = {"A": options_list[0], "B": options_list[1], "C": options_list[2], "D": options_list[3]}
        correct_answer = "C"

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 9,
            "difficulty": "easy",
            "explanation": "После doesn't глагол БЕЗ -s: He doesn't work (не works)."
        }

    def generate_lesson9_q3(self, topic_id: int) -> Dict:
        """L9Q3: Ошибка - do/does с TO BE"""
        topic = self.TOPICS[topic_id]
        profession = random.choice(topic["professions"])

        question = "Найдите ошибку: 'Do you are a student?'"
        correct = "нужно 'Are you' вместо 'Do you are'"
        wrong_options = [
            "нужно 'Does' вместо 'Do'",
            "нужно убрать 'a'",
            "ошибок нет"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 9,
            "difficulty": "medium",
            "explanation": "TO BE не использует do/does: Are you? (не Do you are)"
        }

    def generate_lesson9_q4(self, topic_id: int) -> Dict:
        """L9Q4: Ошибка - неправильное окончание -y"""
        topic = self.TOPICS[topic_id]

        question = "Какое предложение правильное?"
        correct = "He studies English."
        wrong_options = [
            "He studys English.",
            "He studyes English.",
            "He study English."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 9,
            "difficulty": "medium",
            "explanation": "Согласная + y → -ies: study → studies."
        }

    def generate_lesson9_q5(self, topic_id: int) -> Dict:
        """L9Q5: Ошибка - гласная + y"""
        topic = self.TOPICS[topic_id]

        question = "Найдите ошибку: 'She plaies tennis.'"
        correct = "нужно 'plays' вместо 'plaies'"
        wrong_options = [
            "нужно 'play' вместо 'plaies'",
            "нужно 'playing' вместо 'plaies'",
            "ошибок нет"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 9,
            "difficulty": "medium",
            "explanation": "Гласная + y: просто -s. play → plays (не plaies)."
        }

    def generate_lesson9_q6(self, topic_id: int) -> Dict:
        """L9Q6: Ошибка - место наречия"""
        topic = self.TOPICS[topic_id]

        question = "Какое предложение правильное?"
        correct = "I always drink coffee."
        wrong_options = [
            "I drink always coffee.",
            "Always I drink coffee.",
            "I coffee always drink."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 9,
            "difficulty": "hard",
            "explanation": "Наречие перед глаголом: I always drink."
        }

    def generate_lesson9_q7(self, topic_id: int) -> Dict:
        """L9Q7: Ошибка - двойное отрицание"""
        topic = self.TOPICS[topic_id]

        question = "Найдите ошибку: 'I don't never go there.'"
        correct = "нужно убрать 'don't' или 'never'"
        wrong_options = [
            "нужно 'doesn't' вместо 'don't'",
            "нужно 'not' вместо 'don't'",
            "ошибок нет"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 9,
            "difficulty": "hard",
            "explanation": "Never уже содержит отрицание: I never go ИЛИ I don't go."
        }

    def generate_lesson9_q8(self, topic_id: int) -> Dict:
        """L9Q8: Комплексная ошибка - все формы"""
        topic = self.TOPICS[topic_id]
        country = random.choice(topic["countries"])

        question = "Какое предложение составлено НЕПРАВИЛЬНО?"
        
        options_list = [
            "I don't work on Sundays.",
            "Are you ready?",
            "She teaches students.",
            f"They is from {country}."  # Ошибка!
        ]

        correct = options_list[3]
        options = {"A": options_list[0], "B": options_list[1], "C": options_list[2], "D": options_list[3]}
        correct_answer = "D"

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 9,
            "difficulty": "hard",
            "explanation": f"They (множественное число) требует 'are': They are from {country}."
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
            lesson_num: Номер урока (1-9)
            topic_ids_sequence: [2, 3, 2, 4, ...]  ← ГОТОВЫЙ список топиков
            num_questions: Количество вопросов (None = все вопросы урока)

        Returns:
            [
                {
                    'question': str,
                    'options': {...},
                    'correct_answer': str,
                    'explanation': str,
                    'topic_id': int,
                    'lesson': int,
                    'difficulty': str
                },
                ...
            ]
        """

        # Методы генерации для урока
        lesson_methods = {
            1: [  # 7 вопросов
                self.generate_lesson1_q1, self.generate_lesson1_q2,
                self.generate_lesson1_q3, self.generate_lesson1_q4,
                self.generate_lesson1_q5, self.generate_lesson1_q6,
                self.generate_lesson1_q7
            ],
            2: [  # 6 вопросов
                self.generate_lesson2_q1, self.generate_lesson2_q2,
                self.generate_lesson2_q3, self.generate_lesson2_q4,
                self.generate_lesson2_q5, self.generate_lesson2_q6
            ],
            3: [  # 8 вопросов
                self.generate_lesson3_q1, self.generate_lesson3_q2,
                self.generate_lesson3_q3, self.generate_lesson3_q4,
                self.generate_lesson3_q5, self.generate_lesson3_q6,
                self.generate_lesson3_q7, self.generate_lesson3_q8
            ],
            4: [  # 7 вопросов
                self.generate_lesson4_q1, self.generate_lesson4_q2,
                self.generate_lesson4_q3, self.generate_lesson4_q4,
                self.generate_lesson4_q5, self.generate_lesson4_q6,
                self.generate_lesson4_q7
            ],
            5: [  # 7 вопросов
                self.generate_lesson5_q1, self.generate_lesson5_q2,
                self.generate_lesson5_q3, self.generate_lesson5_q4,
                self.generate_lesson5_q5, self.generate_lesson5_q6,
                self.generate_lesson5_q7
            ],
            6: [  # 8 вопросов
                self.generate_lesson6_q1, self.generate_lesson6_q2,
                self.generate_lesson6_q3, self.generate_lesson6_q4,
                self.generate_lesson6_q5, self.generate_lesson6_q6,
                self.generate_lesson6_q7, self.generate_lesson6_q8
            ],
            7: [  # 7 вопросов
                self.generate_lesson7_q1, self.generate_lesson7_q2,
                self.generate_lesson7_q3, self.generate_lesson7_q4,
                self.generate_lesson7_q5, self.generate_lesson7_q6,
                self.generate_lesson7_q7
            ],
            8: [  # 7 вопросов
                self.generate_lesson8_q1, self.generate_lesson8_q2,
                self.generate_lesson8_q3, self.generate_lesson8_q4,
                self.generate_lesson8_q5, self.generate_lesson8_q6,
                self.generate_lesson8_q7
            ],
            9: [  # 8 вопросов
                self.generate_lesson9_q1, self.generate_lesson9_q2,
                self.generate_lesson9_q3, self.generate_lesson9_q4,
                self.generate_lesson9_q5, self.generate_lesson9_q6,
                self.generate_lesson9_q7, self.generate_lesson9_q8
            ]
        }

        methods = lesson_methods[lesson_num]
        
        # Если num_questions не указано, используем все вопросы урока
        if num_questions is None:
            num_questions = len(methods)
        
        num = min(num_questions, len(methods), len(topic_ids_sequence))

        questions = []

        # ✅ Чистая логика - просто генерируем вопросы
        for i in range(num):
            topic_id = topic_ids_sequence[i]
            question = methods[i](topic_id)
            question['topic_id'] = topic_id
            questions.append(question)

        return questions

    # ========================================
    # ВСПОМОГАТЕЛЬНЫЙ МЕТОД
    # ========================================

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
                self.generate_lesson2_q5, self.generate_lesson2_q6
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
                self.generate_lesson4_q7
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
                self.generate_lesson6_q7, self.generate_lesson6_q8
            ],
            7: [
                self.generate_lesson7_q1, self.generate_lesson7_q2,
                self.generate_lesson7_q3, self.generate_lesson7_q4,
                self.generate_lesson7_q5, self.generate_lesson7_q6,
                self.generate_lesson7_q7
            ],
            8: [
                self.generate_lesson8_q1, self.generate_lesson8_q2,
                self.generate_lesson8_q3, self.generate_lesson8_q4,
                self.generate_lesson8_q5, self.generate_lesson8_q6,
                self.generate_lesson8_q7
            ],
            9: [
                self.generate_lesson9_q1, self.generate_lesson9_q2,
                self.generate_lesson9_q3, self.generate_lesson9_q4,
                self.generate_lesson9_q5, self.generate_lesson9_q6,
                self.generate_lesson9_q7, self.generate_lesson9_q8
            ]
        }
        return lesson_methods[lesson_num]

    def generate_full_module_test(
            self,
            topic_ids_sequence: List[int],
            num_questions: int = 67
    ) -> List[Dict]:
        """
        Генерировать полный тест по модулю
        СИНХРОННЫЙ - НЕ работает с БД!

        Args:
            topic_ids_sequence: [2, 3, 2, 4, ...]  ← ГОТОВЫЙ список (67 топиков)
            num_questions: Количество вопросов (по умолчанию 67)

        Returns:
            Список из 67 вопросов (БЕЗ topic_name!)
        """

        # Собираем все методы генерации
        all_methods = []
        for lesson_num in range(1, 10):  # 9 уроков
            all_methods.extend(self._get_lesson_methods(lesson_num))

        # Перемешиваем для разнообразия
        random.shuffle(all_methods)

        all_questions = []

        # ✅ Чистая логика - просто генерируем вопросы
        for i in range(min(num_questions, len(all_methods), len(topic_ids_sequence))):
            topic_id = topic_ids_sequence[i]
            method = all_methods[i]

            question = method(topic_id)
            question['topic_id'] = topic_id
            all_questions.append(question)

        return all_questions

    @staticmethod
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


# ========================================
# Пример использования
# ========================================

if __name__ == "__main__":
    # Создаем генератор
    generator = PresentSimpleQuestionGenerator(seed=42)

    # Пример: генерация теста для урока 1 (7 вопросов)
    print("=" * 80)
    print("LESSON 1 TEST - Что такое Present Simple")
    print("=" * 80)
    
    # Топики для 7 вопросов
    topic_sequence_lesson1 = [2, 3, 4, 5, 6, 7, 8]
    
    test_lesson1 = generator.generate_test_for_lesson(
        lesson_num=1,
        topic_ids_sequence=topic_sequence_lesson1
    )
    
    for i, q in enumerate(test_lesson1, 1):
        print(f"\nВопрос {i} (Topic: {generator.TOPICS[q['topic_id']]['name']}, Difficulty: {q['difficulty']})")
        print(f"Q: {q['question']}")
        for letter, option in sorted(q['options'].items()):
            marker = "✓" if letter == q['correct_answer'] else " "
            print(f"  {marker} {letter}) {option}")
        print(f"Explanation: {q['explanation']}")

    # Пример: генерация полного теста (67 вопросов)
    print("\n" + "=" * 80)
    print("FULL MODULE TEST - Present Simple (67 questions)")
    print("=" * 80)
    
    # Случайная последовательность топиков для 67 вопросов
    import random
    all_topic_ids = list(generator.TOPICS.keys())
    topic_sequence_full = [random.choice(all_topic_ids) for _ in range(67)]
    
    full_test = generator.generate_full_module_test(
        topic_ids_sequence=topic_sequence_full
    )
    
    print(f"\nСгенерировано {len(full_test)} вопросов")
    print(f"Распределение по сложности:")
    difficulties = {}
    for q in full_test:
        diff = q['difficulty']
        difficulties[diff] = difficulties.get(diff, 0) + 1
    
    for diff, count in sorted(difficulties.items()):
        print(f"  {diff}: {count} вопросов")
    
    print(f"\nПервые 3 вопроса:")
    for i, q in enumerate(full_test[:3], 1):
        print(f"\n{i}. {q['question'][:50]}...")
        print(f"   Topic: {generator.TOPICS[q['topic_id']]['name']}")
        print(f"   Lesson: {q['lesson']}, Difficulty: {q['difficulty']}")

