import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from .base_generator import BaseQuestionGenerator


class ToBeQuestionGenerator(BaseQuestionGenerator):
    """
    Динамический генератор вопросов по глаголу TO BE (am/is/are)
    Создает уникальные вопросы для каждой темы интересов
    32 типа вопросов (8 на каждый из 4 уроков)
    """

    # Темы интересов с расширенными словарями
    TOPICS = {
        2: {
            "name": "Shopping and money",
            "professions": ["a customer", "a cashier", "a manager", "a seller", "a buyer", "a shopper"],
            "adjectives_state": ["tired", "busy", "ready", "free", "available"],
            "adjectives_quality": ["expensive", "cheap", "good", "new", "old", "on sale"],
            "locations_at": ["at the store", "at the mall", "at the shop", "at the market", "at the checkout"],
            "locations_in": ["in the shop", "in the mall", "in the store", "in the market"],
            "locations_on": ["on the shelf", "on sale", "on the counter"],
            "things": ["the product", "the price", "the receipt", "the card", "the cash"],
            "nationalities": ["German", "Spanish", "Italian", "French"],
            "countries": ["Germany", "Spain", "Italy", "France"],
            "cities": ["Berlin", "Madrid", "Rome", "Paris"]
        },
        3: {
            "name": "Weather and nature",
            "professions": ["a meteorologist", "a farmer", "a gardener", "a botanist"],
            "adjectives_state": ["sunny", "cloudy", "rainy", "windy", "cold", "hot", "warm"],
            "adjectives_quality": ["beautiful", "terrible", "nice", "awful", "pleasant"],
            "locations_at": ["at the park", "at the beach", "at the garden", "at the lake"],
            "locations_in": ["in the forest", "in the park", "in the garden", "in nature"],
            "locations_on": ["on the mountain", "on the hill", "on the ground"],
            "things": ["the weather", "the temperature", "the forecast", "the climate"],
            "nationalities": ["Canadian", "American", "British"],
            "countries": ["Canada", "the USA", "England"],
            "cities": ["Toronto", "New York", "London"]
        },
        4: {
            "name": "Health and medicine",
            "professions": ["a doctor", "a nurse", "a patient", "a surgeon", "a dentist", "a therapist"],
            "adjectives_state": ["sick", "healthy", "tired", "well", "ill", "fine", "better"],
            "adjectives_quality": ["serious", "minor", "chronic", "acute"],
            "locations_at": ["at the hospital", "at the clinic", "at the doctor's", "at home"],
            "locations_in": ["in the hospital", "in the clinic", "in bed", "in the ward"],
            "locations_on": ["on the bed", "on medication", "on the table"],
            "things": ["the diagnosis", "the treatment", "the medicine", "the appointment"],
            "nationalities": ["Indian", "Chinese", "Japanese"],
            "countries": ["India", "China", "Japan"],
            "cities": ["Mumbai", "Beijing", "Tokyo"]
        },
        5: {
            "name": "Home and daily routines",
            "professions": ["a homemaker", "a housekeeper", "a cleaner", "a cook"],
            "adjectives_state": ["tired", "busy", "ready", "awake", "asleep", "hungry"],
            "adjectives_quality": ["clean", "dirty", "tidy", "messy", "comfortable", "cozy"],
            "locations_at": ["at home", "at the kitchen", "at the door"],
            "locations_in": ["in the room", "in the kitchen", "in the bathroom", "in bed"],
            "locations_on": ["on the table", "on the sofa", "on the floor", "on the bed"],
            "things": ["the routine", "the schedule", "the task", "the chore"],
            "nationalities": ["Mexican", "Brazilian", "Argentinian"],
            "countries": ["Mexico", "Brazil", "Argentina"],
            "cities": ["Mexico City", "Rio de Janeiro", "Buenos Aires"]
        },
        6: {
            "name": "Transportation and directions",
            "professions": ["a driver", "a pilot", "a conductor", "a passenger"],
            "adjectives_state": ["late", "early", "on time", "ready", "lost"],
            "adjectives_quality": ["fast", "slow", "direct", "convenient"],
            "locations_at": ["at the station", "at the airport", "at the stop", "at the terminal"],
            "locations_in": ["in the car", "in the bus", "in the train", "in the taxi"],
            "locations_on": ["on the train", "on the bus", "on the plane", "on the street"],
            "things": ["the ticket", "the route", "the schedule", "the platform"],
            "nationalities": ["Dutch", "Belgian", "Swiss"],
            "countries": ["the Netherlands", "Belgium", "Switzerland"],
            "cities": ["Amsterdam", "Brussels", "Zurich"]
        },
        7: {
            "name": "Leisure and hobbies",
            "professions": ["an artist", "a musician", "a photographer", "a dancer", "a player"],
            "adjectives_state": ["excited", "bored", "interested", "enthusiastic", "passionate"],
            "adjectives_quality": ["interesting", "boring", "fun", "creative", "relaxing"],
            "locations_at": ["at the cinema", "at the concert", "at the museum", "at the gallery"],
            "locations_in": ["in the theatre", "in the cinema", "in the park", "in the club"],
            "locations_on": ["on stage", "on the team", "on vacation"],
            "things": ["the hobby", "the activity", "the event", "the show"],
            "nationalities": ["Austrian", "Swedish", "Norwegian"],
            "countries": ["Austria", "Sweden", "Norway"],
            "cities": ["Vienna", "Stockholm", "Oslo"]
        },
        8: {
            "name": "Relationships and emotions",
            "professions": ["a friend", "a partner", "a colleague", "a neighbor"],
            "adjectives_state": ["happy", "sad", "angry", "upset", "worried", "excited", "nervous"],
            "adjectives_quality": ["close", "distant", "strong", "weak", "good", "bad"],
            "locations_at": ["at the party", "at the meeting", "at home"],
            "locations_in": ["in love", "in a relationship", "in contact"],
            "locations_on": ["on good terms", "on speaking terms"],
            "things": ["the relationship", "the friendship", "the feeling", "the emotion"],
            "nationalities": ["Greek", "Turkish", "Egyptian"],
            "countries": ["Greece", "Turkey", "Egypt"],
            "cities": ["Athens", "Istanbul", "Cairo"]
        },
        9: {
            "name": "Technology and gadgets",
            "professions": ["a programmer", "an engineer", "a developer", "a technician", "an IT specialist"],
            "adjectives_state": ["online", "offline", "busy", "available", "connected"],
            "adjectives_quality": ["modern", "old", "new", "fast", "slow", "broken"],
            "locations_at": ["at the computer", "at the desk", "at work"],
            "locations_in": ["in the office", "in the lab", "in development"],
            "locations_on": ["on the desk", "on the network", "on the system"],
            "things": ["the device", "the gadget", "the software", "the application"],
            "nationalities": ["Korean", "Taiwanese", "Singaporean"],
            "countries": ["South Korea", "Taiwan", "Singapore"],
            "cities": ["Seoul", "Taipei", "Singapore"]
        },
        11: {
            "name": "Job interviews and CVs",
            "professions": ["a candidate", "an applicant", "a recruiter", "an interviewer", "a job seeker"],
            "adjectives_state": ["nervous", "confident", "ready", "prepared", "worried"],
            "adjectives_quality": ["qualified", "experienced", "suitable", "perfect", "strong"],
            "locations_at": ["at the interview", "at the office", "at the company"],
            "locations_in": ["in the interview", "in the process", "in consideration"],
            "locations_on": ["on time", "on the list", "on the phone"],
            "things": ["the CV", "the resume", "the application", "the position"],
            "nationalities": ["Polish", "Czech", "Hungarian"],
            "countries": ["Poland", "Czech Republic", "Hungary"],
            "cities": ["Warsaw", "Prague", "Budapest"]
        },
        12: {
            "name": "Meetings and negotiations",
            "professions": ["a manager", "a negotiator", "a participant", "a representative"],
            "adjectives_state": ["ready", "busy", "available", "present", "absent"],
            "adjectives_quality": ["important", "urgent", "scheduled", "productive"],
            "locations_at": ["at the meeting", "at the conference", "at the negotiation"],
            "locations_in": ["in the meeting", "in the conference room", "in discussion"],
            "locations_on": ["on the agenda", "on schedule", "on the call"],
            "things": ["the meeting", "the agenda", "the proposal", "the deal"],
            "nationalities": ["Danish", "Finnish", "Icelandic"],
            "countries": ["Denmark", "Finland", "Iceland"],
            "cities": ["Copenhagen", "Helsinki", "Reykjavik"]
        },
        13: {
            "name": "Presentations and public speaking",
            "professions": ["a speaker", "a presenter", "a lecturer", "an audience member"],
            "adjectives_state": ["nervous", "confident", "ready", "prepared", "calm"],
            "adjectives_quality": ["interesting", "boring", "clear", "engaging", "professional"],
            "locations_at": ["at the podium", "at the conference", "at the event"],
            "locations_in": ["in the hall", "in the audience", "in the presentation"],
            "locations_on": ["on stage", "on the screen", "on the slide"],
            "things": ["the presentation", "the speech", "the topic", "the slide"],
            "nationalities": ["Portuguese", "Irish", "Scottish"],
            "countries": ["Portugal", "Ireland", "Scotland"],
            "cities": ["Lisbon", "Dublin", "Edinburgh"]
        },
        14: {
            "name": "Emails and business correspondence",
            "professions": ["a correspondent", "a sender", "a recipient", "a writer"],
            "adjectives_state": ["urgent", "important", "ready", "sent", "received"],
            "adjectives_quality": ["formal", "informal", "clear", "brief", "detailed"],
            "locations_at": ["at the desk", "at work", "at the office"],
            "locations_in": ["in the inbox", "in the draft", "in the folder"],
            "locations_on": ["on the computer", "on the screen", "on the list"],
            "things": ["the email", "the message", "the letter", "the reply"],
            "nationalities": ["Romanian", "Bulgarian", "Croatian"],
            "countries": ["Romania", "Bulgaria", "Croatia"],
            "cities": ["Bucharest", "Sofia", "Zagreb"]
        },
        15: {
            "name": "Office communication and teamwork",
            "professions": ["a colleague", "a team member", "a supervisor", "a coordinator"],
            "adjectives_state": ["busy", "available", "free", "cooperative", "helpful"],
            "adjectives_quality": ["productive", "efficient", "collaborative", "supportive"],
            "locations_at": ["at the office", "at the desk", "at the meeting"],
            "locations_in": ["in the office", "in the team", "in the department"],
            "locations_on": ["on the team", "on the project", "on the call"],
            "things": ["the project", "the task", "the deadline", "the report"],
            "nationalities": ["Australian", "New Zealander", "Canadian"],
            "countries": ["Australia", "New Zealand", "Canada"],
            "cities": ["Sydney", "Auckland", "Toronto"]
        },
        16: {
            "name": "Project management vocabulary",
            "professions": ["a project manager", "a coordinator", "a team leader", "a stakeholder"],
            "adjectives_state": ["on track", "delayed", "complete", "ongoing", "finished"],
            "adjectives_quality": ["critical", "important", "urgent", "successful"],
            "locations_at": ["at the meeting", "at the checkpoint", "at the milestone"],
            "locations_in": ["in progress", "in development", "in the pipeline"],
            "locations_on": ["on schedule", "on budget", "on track"],
            "things": ["the project", "the milestone", "the deliverable", "the timeline"],
            "nationalities": ["South African", "Nigerian", "Kenyan"],
            "countries": ["South Africa", "Nigeria", "Kenya"],
            "cities": ["Cape Town", "Lagos", "Nairobi"]
        },
        17: {
            "name": "Customer service and support",
            "professions": ["a representative", "a support agent", "a customer", "a client"],
            "adjectives_state": ["available", "busy", "helpful", "patient", "frustrated"],
            "adjectives_quality": ["excellent", "poor", "professional", "friendly", "quick"],
            "locations_at": ["at the desk", "at the phone", "at the counter"],
            "locations_in": ["in contact", "in the call", "in the queue"],
            "locations_on": ["on the phone", "on the line", "on hold"],
            "things": ["the issue", "the complaint", "the request", "the solution"],
            "nationalities": ["Malaysian", "Thai", "Vietnamese"],
            "countries": ["Malaysia", "Thailand", "Vietnam"],
            "cities": ["Kuala Lumpur", "Bangkok", "Hanoi"]
        },
        18: {
            "name": "Marketing and sales English",
            "professions": ["a marketer", "a salesperson", "a sales manager", "a customer"],
            "adjectives_state": ["successful", "active", "aggressive", "persuasive"],
            "adjectives_quality": ["effective", "attractive", "competitive", "profitable"],
            "locations_at": ["at the market", "at the campaign", "at the store"],
            "locations_in": ["in the campaign", "in the market", "in sales"],
            "locations_on": ["on the market", "on sale", "on promotion"],
            "things": ["the campaign", "the product", "the strategy", "the target"],
            "nationalities": ["Chilean", "Peruvian", "Colombian"],
            "countries": ["Chile", "Peru", "Colombia"],
            "cities": ["Santiago", "Lima", "Bogota"]
        },
        20: {
            "name": "At the airport and hotel",
            "professions": ["a passenger", "a guest", "a receptionist", "a flight attendant"],
            "adjectives_state": ["late", "early", "ready", "tired", "lost"],
            "adjectives_quality": ["comfortable", "convenient", "expensive", "cheap"],
            "locations_at": ["at the airport", "at the hotel", "at the gate", "at the desk"],
            "locations_in": ["in the hotel", "in the room", "in the lobby"],
            "locations_on": ["on the flight", "on the plane", "on the floor"],
            "things": ["the flight", "the reservation", "the room", "the luggage"],
            "nationalities": ["Filipino", "Indonesian", "Cambodian"],
            "countries": ["the Philippines", "Indonesia", "Cambodia"],
            "cities": ["Manila", "Jakarta", "Phnom Penh"]
        },
        21: {
            "name": "Sightseeing and excursions",
            "professions": ["a tourist", "a guide", "a traveler", "a visitor"],
            "adjectives_state": ["excited", "tired", "interested", "lost", "amazed"],
            "adjectives_quality": ["beautiful", "interesting", "historic", "famous"],
            "locations_at": ["at the museum", "at the monument", "at the site"],
            "locations_in": ["in the city", "in the museum", "in the gallery"],
            "locations_on": ["on the tour", "on the excursion", "on the trip"],
            "things": ["the tour", "the guide", "the attraction", "the landmark"],
            "nationalities": ["Moroccan", "Tunisian", "Algerian"],
            "countries": ["Morocco", "Tunisia", "Algeria"],
            "cities": ["Marrakech", "Tunis", "Algiers"]
        },
        22: {
            "name": "Emergencies abroad",
            "professions": ["a traveler", "a victim", "an officer", "a helper"],
            "adjectives_state": ["worried", "scared", "lost", "hurt", "safe"],
            "adjectives_quality": ["serious", "urgent", "dangerous", "safe"],
            "locations_at": ["at the embassy", "at the police station", "at the hospital"],
            "locations_in": ["in trouble", "in danger", "in the hospital"],
            "locations_on": ["on the phone", "on the street"],
            "things": ["the emergency", "the problem", "the situation", "the help"],
            "nationalities": ["Israeli", "Lebanese", "Jordanian"],
            "countries": ["Israel", "Lebanon", "Jordan"],
            "cities": ["Tel Aviv", "Beirut", "Amman"]
        },
        23: {
            "name": "Cultural etiquette and customs",
            "professions": ["a visitor", "a local", "a guest", "a host"],
            "adjectives_state": ["respectful", "polite", "curious", "confused"],
            "adjectives_quality": ["traditional", "modern", "acceptable", "taboo"],
            "locations_at": ["at the ceremony", "at the event", "at the gathering"],
            "locations_in": ["in the culture", "in the tradition", "in the country"],
            "locations_on": ["on the occasion", "on the holiday"],
            "things": ["the custom", "the tradition", "the etiquette", "the rule"],
            "nationalities": ["Saudi", "Emirati", "Qatari"],
            "countries": ["Saudi Arabia", "the UAE", "Qatar"],
            "cities": ["Riyadh", "Dubai", "Doha"]
        },
        24: {
            "name": "Talking about countries and nationalities",
            "professions": ["a citizen", "a resident", "a native", "an immigrant"],
            "adjectives_state": ["foreign", "local", "native", "international"],
            "adjectives_quality": ["diverse", "multicultural", "unique", "traditional"],
            "locations_at": ["at the border", "at the embassy", "at the consulate"],
            "locations_in": ["in the country", "in the city", "in the region"],
            "locations_on": ["on the continent", "on the map"],
            "things": ["the nationality", "the passport", "the country", "the culture"],
            "nationalities": ["Argentinian", "Uruguayan", "Paraguayan"],
            "countries": ["Argentina", "Uruguay", "Paraguay"],
            "cities": ["Buenos Aires", "Montevideo", "Asuncion"]
        },
        26: {
            "name": "Idioms",
            "professions": ["a speaker", "a learner", "a teacher", "a student"],
            "adjectives_state": ["confused", "clear", "fluent", "advanced"],
            "adjectives_quality": ["idiomatic", "natural", "common", "rare"],
            "locations_at": ["at the lesson", "at the class", "at the course"],
            "locations_in": ["in the context", "in the conversation", "in use"],
            "locations_on": ["on the tip of the tongue", "on the same page"],
            "things": ["the idiom", "the expression", "the phrase", "the meaning"],
            "nationalities": ["Cuban", "Jamaican", "Dominican"],
            "countries": ["Cuba", "Jamaica", "the Dominican Republic"],
            "cities": ["Havana", "Kingston", "Santo Domingo"]
        },
        27: {
            "name": "Slang",
            "professions": ["a native speaker", "a learner", "a teenager", "a young person"],
            "adjectives_state": ["cool", "trendy", "outdated", "modern"],
            "adjectives_quality": ["informal", "casual", "colloquial", "vulgar"],
            "locations_at": ["at the party", "at the club", "at the street"],
            "locations_in": ["in the conversation", "in the culture", "in use"],
            "locations_on": ["on the street", "on social media"],
            "things": ["the slang", "the expression", "the word", "the term"],
            "nationalities": ["Guatemalan", "Honduran", "Salvadoran"],
            "countries": ["Guatemala", "Honduras", "El Salvador"],
            "cities": ["Guatemala City", "Tegucigalpa", "San Salvador"]
        },
        28: {
            "name": "Phrasal verbs",
            "professions": ["a student", "a teacher", "a learner", "a speaker"],
            "adjectives_state": ["common", "difficult", "easy", "confusing"],
            "adjectives_quality": ["separable", "inseparable", "idiomatic", "literal"],
            "locations_at": ["at the lesson", "at the course", "at the class"],
            "locations_in": ["in the sentence", "in use", "in context"],
            "locations_on": ["on the list", "on the page"],
            "things": ["the phrasal verb", "the particle", "the meaning", "the usage"],
            "nationalities": ["Ecuadorian", "Bolivian", "Venezuelan"],
            "countries": ["Ecuador", "Bolivia", "Venezuela"],
            "cities": ["Quito", "La Paz", "Caracas"]
        },
        29: {
            "name": "Collocations and word patterns",
            "professions": ["a linguist", "a teacher", "a learner", "a writer"],
            "adjectives_state": ["natural", "unnatural", "correct", "incorrect"],
            "adjectives_quality": ["common", "rare", "strong", "weak"],
            "locations_at": ["at the lesson", "at the university", "at the course"],
            "locations_in": ["in the language", "in the text", "in the pattern"],
            "locations_on": ["on the list", "on the paper"],
            "things": ["the collocation", "the pattern", "the combination", "the phrase"],
            "nationalities": ["Costa Rican", "Panamanian", "Nicaraguan"],
            "countries": ["Costa Rica", "Panama", "Nicaragua"],
            "cities": ["San Jose", "Panama City", "Managua"]
        },
        30: {
            "name": "Figurative language and metaphors",
            "professions": ["a writer", "a poet", "a speaker", "a reader"],
            "adjectives_state": ["creative", "imaginative", "literal", "figurative"],
            "adjectives_quality": ["poetic", "vivid", "subtle", "obvious"],
            "locations_at": ["at the reading", "at the lecture", "at the class"],
            "locations_in": ["in the text", "in the literature", "in the language"],
            "locations_on": ["on the page", "on the line"],
            "things": ["the metaphor", "the simile", "the image", "the expression"],
            "nationalities": ["Senegalian", "Ghanaian", "Ivorian"],
            "countries": ["Senegal", "Ghana", "Ivory Coast"],
            "cities": ["Dakar", "Accra", "Abidjan"]
        },
        31: {
            "name": "Synonyms, antonyms, and nuance",
            "professions": ["a student", "a teacher", "a writer", "a translator"],
            "adjectives_state": ["similar", "different", "opposite", "exact"],
            "adjectives_quality": ["subtle", "obvious", "important", "slight"],
            "locations_at": ["at the lesson", "at the class", "at the dictionary"],
            "locations_in": ["in the meaning", "in the context", "in the nuance"],
            "locations_on": ["on the list", "on the page"],
            "things": ["the synonym", "the antonym", "the nuance", "the difference"],
            "nationalities": ["Ethiopian", "Ugandan", "Tanzanian"],
            "countries": ["Ethiopia", "Uganda", "Tanzania"],
            "cities": ["Addis Ababa", "Kampala", "Dar es Salaam"]
        },
        32: {
            "name": "Register and tone (formal vs informal)",
            "professions": ["a speaker", "a writer", "a communicator", "a professional"],
            "adjectives_state": ["formal", "informal", "casual", "professional"],
            "adjectives_quality": ["appropriate", "inappropriate", "polite", "rude"],
            "locations_at": ["at the meeting", "at the party", "at the office"],
            "locations_in": ["in the context", "in the situation", "in the conversation"],
            "locations_on": ["on the occasion", "on the phone"],
            "things": ["the register", "the tone", "the style", "the language"],
            "nationalities": ["Zimbabwean", "Zambian", "Malawian"],
            "countries": ["Zimbabwe", "Zambia", "Malawi"],
            "cities": ["Harare", "Lusaka", "Lilongwe"]
        },
        33: {
            "name": "Common grammar pitfalls",
            "professions": ["a student", "a learner", "a teacher", "a speaker"],
            "adjectives_state": ["correct", "incorrect", "confused", "clear"],
            "adjectives_quality": ["common", "frequent", "typical", "rare"],
            "locations_at": ["at the lesson", "at the test", "at the exam"],
            "locations_in": ["in the sentence", "in the grammar", "in the mistake"],
            "locations_on": ["on the test", "on the paper"],
            "things": ["the mistake", "the error", "the pitfall", "the problem"],
            "nationalities": ["Mongolian", "Nepalese", "Bhutanese"],
            "countries": ["Mongolia", "Nepal", "Bhutan"],
            "cities": ["Ulaanbaatar", "Kathmandu", "Thimphu"]
        },
        35: {
            "name": "English for IT",
            "professions": ["a developer", "a programmer", "an engineer", "a tester", "an IT specialist"],
            "adjectives_state": ["online", "offline", "active", "inactive", "deployed"],
            "adjectives_quality": ["functional", "broken", "stable", "buggy", "optimized"],
            "locations_at": ["at the computer", "at the server", "at the workstation"],
            "locations_in": ["in the code", "in the system", "in production"],
            "locations_on": ["on the server", "on the cloud", "on the network"],
            "things": ["the code", "the bug", "the feature", "the update"],
            "nationalities": ["Estonian", "Latvian", "Lithuanian"],
            "countries": ["Estonia", "Latvia", "Lithuania"],
            "cities": ["Tallinn", "Riga", "Vilnius"]
        },
        36: {
            "name": "English for Finance / Accounting",
            "professions": ["an accountant", "a financial analyst", "an auditor", "a banker"],
            "adjectives_state": ["profitable", "unprofitable", "balanced", "overdue"],
            "adjectives_quality": ["fiscal", "financial", "accurate", "detailed"],
            "locations_at": ["at the bank", "at the office", "at the meeting"],
            "locations_in": ["in the budget", "in the account", "in the statement"],
            "locations_on": ["on the balance sheet", "on the report"],
            "things": ["the budget", "the account", "the invoice", "the transaction"],
            "nationalities": ["Luxembourgish", "Maltese", "Cypriot"],
            "countries": ["Luxembourg", "Malta", "Cyprus"],
            "cities": ["Luxembourg City", "Valletta", "Nicosia"]
        },
        37: {
            "name": "English for Law",
            "professions": ["a lawyer", "an attorney", "a judge", "a legal advisor"],
            "adjectives_state": ["legal", "illegal", "guilty", "innocent", "liable"],
            "adjectives_quality": ["legal", "valid", "binding", "enforceable"],
            "locations_at": ["at the court", "at the office", "at the hearing"],
            "locations_in": ["in the court", "in the contract", "in the case"],
            "locations_on": ["on trial", "on the record"],
            "things": ["the case", "the contract", "the law", "the clause"],
            "nationalities": ["Slovenian", "Slovak", "Serbian"],
            "countries": ["Slovenia", "Slovakia", "Serbia"],
            "cities": ["Ljubljana", "Bratislava", "Belgrade"]
        },
        38: {
            "name": "English for Medicine",
            "professions": ["a doctor", "a surgeon", "a physician", "a nurse", "a medical student"],
            "adjectives_state": ["critical", "stable", "recovering", "ill", "healthy"],
            "adjectives_quality": ["medical", "clinical", "chronic", "acute"],
            "locations_at": ["at the hospital", "at the clinic", "at the surgery"],
            "locations_in": ["in the hospital", "in the ward", "in surgery"],
            "locations_on": ["on duty", "on call", "on medication"],
            "things": ["the patient", "the diagnosis", "the treatment", "the procedure"],
            "nationalities": ["Georgian", "Armenian", "Azerbaijani"],
            "countries": ["Georgia", "Armenia", "Azerbaijan"],
            "cities": ["Tbilisi", "Yerevan", "Baku"]
        },
        39: {
            "name": "English for Marketing and PR",
            "professions": ["a marketer", "a PR specialist", "a brand manager", "a copywriter"],
            "adjectives_state": ["viral", "trending", "successful", "effective"],
            "adjectives_quality": ["creative", "engaging", "persuasive", "innovative"],
            "locations_at": ["at the campaign", "at the launch", "at the event"],
            "locations_in": ["in the campaign", "in the market", "in the media"],
            "locations_on": ["on social media", "on the market", "on air"],
            "things": ["the campaign", "the brand", "the strategy", "the message"],
            "nationalities": ["Kazakh", "Uzbek", "Turkmen"],
            "countries": ["Kazakhstan", "Uzbekistan", "Turkmenistan"],
            "cities": ["Almaty", "Tashkent", "Ashgabat"]
        },
        40: {
            "name": "English for HR",
            "professions": ["an HR manager", "a recruiter", "an HR specialist", "a talent scout"],
            "adjectives_state": ["hired", "fired", "employed", "unemployed", "available"],
            "adjectives_quality": ["qualified", "experienced", "suitable", "promising"],
            "locations_at": ["at the office", "at the interview", "at the training"],
            "locations_in": ["in the department", "in the position", "in the company"],
            "locations_on": ["on probation", "on the team", "on leave"],
            "things": ["the candidate", "the employee", "the position", "the vacancy"],
            "nationalities": ["Afghan", "Pakistani", "Bangladeshi"],
            "countries": ["Afghanistan", "Pakistan", "Bangladesh"],
            "cities": ["Kabul", "Karachi", "Dhaka"]
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
    # УРОК 1: Утвердительные предложения
    # ========================================

    def generate_lesson1_q1(self, topic_id: int) -> Dict:
        """L1Q1: I _____ a student (простой выбор формы)"""
        topic = self.TOPICS[topic_id]
        profession = random.choice(topic["professions"])

        question = f"Выберите правильную форму глагола:\nI _____ {profession}."
        correct = "am"
        wrong_options = ["is", "are", "be"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "easy",
            "explanation": f"'I' always takes 'am'. The correct sentence is: I am {profession}."
        }

    def generate_lesson1_q2(self, topic_id: int) -> Dict:
        """L1Q2: She _____ a doctor (простой выбор формы)"""
        topic = self.TOPICS[topic_id]
        profession = random.choice(topic["professions"])

        question = f"Выберите правильную форму глагола:\nShe _____ {profession}."
        correct = "is"
        wrong_options = ["am", "are", "be"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "easy",
            "explanation": f"'She' (third person singular) takes 'is'. The correct sentence is: She is {profession}."
        }

    def generate_lesson1_q3(self, topic_id: int) -> Dict:
        """L1Q3: Исправление ошибки I student -> I am a student"""
        topic = self.TOPICS[topic_id]
        profession = random.choice(topic["professions"]).replace("a ", "")

        question = "Найдите правильное предложение:"
        correct = f"I am a {profession}."
        wrong_options = [
            f"I {profession}.",
            f"I is a {profession}.",
            f"I a am {profession}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "medium",
            "explanation": "In English, the verb 'to be' is always required. The correct structure is: I am + a/an + profession."
        }

    def generate_lesson1_q4(self, topic_id: int) -> Dict:
        """L1Q4: They _____ from Spain (множественное число)"""
        topic = self.TOPICS[topic_id]
        country = random.choice(topic["countries"])

        question = f"Выберите правильную форму:\nThey _____ from {country}."
        correct = "are"
        wrong_options = ["is", "am", "be"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "medium",
            "explanation": f"'They' (plural) takes 'are'. The correct sentence is: They are from {country}."
        }

    def generate_lesson1_q5(self, topic_id: int) -> Dict:
        """L1Q5: Перевод 'Он инженер'"""
        topic = self.TOPICS[topic_id]
        profession = random.choice(topic["professions"]).replace("a ", "")

        # Определяем артикль
        article = "an" if profession[0].lower() in "aeiou" else "a"

        question = f"Как правильно сказать \"Он {profession}\"?"
        correct = f"He is {article} {profession}."
        wrong_options = [
            f"He {profession}.",
            f"He is {profession}.",
            f"He {article} {profession}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "medium",
            "explanation": f"We need 'He is' + article + profession. The correct sentence is: He is {article} {profession}."
        }

    def generate_lesson1_q6(self, topic_id: int) -> Dict:
        """L1Q6: Артикль перед профессией"""
        topic = self.TOPICS[topic_id]
        profession = random.choice(topic["professions"]).replace("a ", "")

        question = "Какое предложение составлено правильно?"
        correct = f"She is a {profession}."
        wrong_options = [
            f"She is {profession}.",
            f"She a is {profession}.",
            f"She {profession} is."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "hard",
            "explanation": "Professions require an article (a/an) in English. The correct form is: She is a + profession."
        }

    def generate_lesson1_q7(self, topic_id: int) -> Dict:
        """L1Q7: Ловушка I am work vs I work"""
        topic = self.TOPICS[topic_id]
        city = random.choice(topic["cities"])

        question = "Какое предложение правильное?"
        correct = f"I work in {city}."
        wrong_options = [
            f"I am work in {city}.",
            f"I am a work in {city}.",
            f"I is work in {city}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "hard",
            "explanation": "'Work' is a verb, not used with 'to be'. Use: I work (not 'I am work')."
        }

    def generate_lesson1_q8(self, topic_id: int) -> Dict:
        """L1Q8: Сокращение I am -> I'm"""
        topic = self.TOPICS[topic_id]
        city = random.choice(topic["cities"])

        question = f"Выберите правильное сокращение:\n\"I am from {city}.\""
        correct = f"I'm from {city}."
        wrong_options = [
            f"I from {city}.",
            f"Im from {city}.",
            f"I'am from {city}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "hard",
            "explanation": "The correct contraction is 'I'm' (with apostrophe). I am = I'm."
        }

    # ========================================
    # УРОК 2: Отрицания и местоположение
    # ========================================

    def generate_lesson2_q1(self, topic_id: int) -> Dict:
        """L2Q1: I _____ tired (отрицание)"""
        topic = self.TOPICS[topic_id]
        adjective = random.choice(topic["adjectives_state"])

        question = f"Выберите правильную отрицательную форму:\nI _____ {adjective}."
        correct = "am not"
        wrong_options = ["is not", "not am", "amn't"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": f"'I' takes 'am not' for negative. The correct sentence is: I am not {adjective}."
        }

    def generate_lesson2_q2(self, topic_id: int) -> Dict:
        """L2Q2: Сокращение She is not -> She isn't"""
        topic = self.TOPICS[topic_id]
        profession = random.choice(topic["professions"])

        question = f"Выберите правильное сокращение:\n\"She is not {profession}.\""
        correct = f"She isn't {profession}."
        wrong_options = [
            f"She'sn't {profession}.",
            f"She amn't {profession}.",
            f"She not {profession}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": "The correct contraction is 'isn't'. She is not = She isn't."
        }

    def generate_lesson2_q3(self, topic_id: int) -> Dict:
        """L2Q3: Предлог AT (at home)"""
        topic = self.TOPICS[topic_id]
        location_at = random.choice(topic["locations_at"])

        question = f"Как правильно сказать \"Я {location_at.replace('at the ', 'в ').replace('at ', 'дома' if 'home' in location_at else 'на ')}\"?"
        correct = f"I'm {location_at}."

        # Создаем неправильные варианты с in/on
        location_word = location_at.replace("at ", "")
        wrong_options = [
            f"I {location_at}.",
            f"I'm in {location_word}.",
            f"I'm on {location_word}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "medium",
            "explanation": f"Use 'at' for specific locations/points. The correct form is: I'm {location_at}."
        }

    def generate_lesson2_q4(self, topic_id: int) -> Dict:
        """L2Q4: Предлог IN (in Tokyo)"""
        topic = self.TOPICS[topic_id]
        city = random.choice(topic["cities"])

        question = f"Выберите правильный вариант:\nShe _____ in {city}."
        correct = "is"
        wrong_options = ["at", "on", "am"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "medium",
            "explanation": f"Use 'is' with 'She' and 'in' for cities. The correct sentence is: She is in {city}."
        }

    def generate_lesson2_q5(self, topic_id: int) -> Dict:
        """L2Q5: Предлог ON (on the table)"""
        topic = self.TOPICS[topic_id]
        location_on = random.choice(topic["locations_on"])
        thing = random.choice(topic["things"])

        question = f"Как правильно сказать \"{thing.replace('the ', '').capitalize()} на {location_on.replace('on the ', '')}\"?"
        correct = f"{thing.capitalize()} is {location_on}."

        location_word = location_on.replace("on ", "")
        wrong_options = [
            f"{thing.capitalize()} is in {location_word}.",
            f"{thing.capitalize()} is at {location_word}.",
            f"{thing.capitalize()} at {location_on}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "medium",
            "explanation": f"Use 'on' for surfaces. The correct sentence is: {thing.capitalize()} is {location_on}."
        }

    def generate_lesson2_q6(self, topic_id: int) -> Dict:
        """L2Q6: Двойное отрицание"""
        topic = self.TOPICS[topic_id]
        profession = random.choice(topic["professions"])

        question = "Какое предложение правильное?"
        correct = f"I'm not {profession}."
        wrong_options = [
            f"I am not no {profession}.",
            f"I amn't {profession}.",
            f"I not am {profession}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "hard",
            "explanation": "English doesn't use double negatives. Use only one negative: I'm not + profession."
        }

    def generate_lesson2_q7(self, topic_id: int) -> Dict:
        """L2Q7: Отрицание + место"""
        topic = self.TOPICS[topic_id]
        location_in = random.choice(topic["locations_in"])

        question = f"Выберите правильный перевод \"Его нет {location_in.replace('in the ', 'в ')}\"."
        correct = f"He isn't {location_in}."
        wrong_options = [
            f"He not {location_in}.",
            f"He isn't in {location_in.replace('in the ', '')}.",
            f"He not is {location_in}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "hard",
            "explanation": f"The correct negative form is: He isn't {location_in}."
        }

    def generate_lesson2_q8(self, topic_id: int) -> Dict:
        """L2Q8: Порядок слов в отрицании"""
        topic = self.TOPICS[topic_id]
        adjective = random.choice(topic["adjectives_state"])

        question = "Найдите ошибку:"
        options_list = [
            "I'm not tired.",
            f"She not is {adjective}.",
            "They aren't busy.",
            "We aren't late."
        ]

        correct = options_list[1]  # Неправильное предложение
        options = {"A": options_list[0], "B": options_list[1], "C": options_list[2], "D": options_list[3]}
        correct_answer = "B"

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "hard",
            "explanation": f"'She not is' is incorrect. The correct order is: She is not / She isn't {adjective}."
        }

    # ========================================
    # УРОК 3: Вопросы и ответы
    # ========================================

    def generate_lesson3_q1(self, topic_id: int) -> Dict:
        """L3Q1: Общий вопрос Are you a student?"""
        topic = self.TOPICS[topic_id]
        profession = random.choice(topic["professions"])

        question = f"Как правильно задать вопрос?\n\"You are {profession}.\""
        correct = f"Are you {profession}?"
        wrong_options = [
            f"You are {profession}?",
            f"Is you {profession}?",
            f"You {profession} are?"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": f"To form a question, put 'are' before 'you'. The correct question is: Are you {profession}?"
        }

    def generate_lesson3_q2(self, topic_id: int) -> Dict:
        """L3Q2: Краткий ответ Yes, I am"""
        topic = self.TOPICS[topic_id]
        adjective = random.choice(topic["adjectives_state"])

        question = f"Выберите правильный краткий ответ:\n\"Are you {adjective}?\" — \"Yes, _____\""
        correct = "I am."
        wrong_options = ["I'm.", "I is.", "I are."]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": "In positive short answers, don't use contractions. The correct answer is: Yes, I am."
        }

    def generate_lesson3_q3(self, topic_id: int) -> Dict:
        """L3Q3: Инверсия She is at home -> Is she at home?"""
        topic = self.TOPICS[topic_id]
        location_at = random.choice(topic["locations_at"])

        question = f"Преобразуйте в вопрос:\n\"She is {location_at}.\""
        correct = f"Is she {location_at}?"
        wrong_options = [
            f"She is {location_at}?",
            f"Are she {location_at}?",
            f"She {location_at} is?"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "medium",
            "explanation": f"Put 'is' before 'she' to form a question. The correct question is: Is she {location_at}?"
        }

    def generate_lesson3_q4(self, topic_id: int) -> Dict:
        """L3Q4: Where вопрос"""
        topic = self.TOPICS[topic_id]

        question = "Как правильно спросить \"Где ты?\""
        correct = "Where are you?"
        wrong_options = [
            "Where you are?",
            "Where is you?",
            "You where are?"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "medium",
            "explanation": "The correct word order for questions is: Where + are + you?"
        }

    def generate_lesson3_q5(self, topic_id: int) -> Dict:
        """L3Q5: Отрицательный краткий ответ"""
        topic = self.TOPICS[topic_id]
        profession = random.choice(topic["professions"])

        question = f"Выберите правильный краткий ответ:\n\"Is he {profession}?\" — \"No, _____\""
        correct = "he isn't."
        wrong_options = ["he not.", "he amn't.", "he aren't."]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "medium",
            "explanation": "The correct negative short answer is: No, he isn't."
        }

    def generate_lesson3_q6(self, topic_id: int) -> Dict:
        """L3Q6: Who вопрос"""
        topic = self.TOPICS[topic_id]

        question = "Как правильно спросить \"Кто это?\""
        correct = "Who is that?"
        wrong_options = [
            "Who are that?",
            "Who that is?",
            "That who is?"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "hard",
            "explanation": "The correct question form is: Who is that?"
        }

    def generate_lesson3_q7(self, topic_id: int) -> Dict:
        """L3Q7: Ловушка с сокращением Yes, they're"""
        topic = self.TOPICS[topic_id]
        profession = random.choice(topic["professions"]).replace("a ", "")

        question = f"Какой ответ НЕПРАВИЛЬНЫЙ?\n\"Are they {profession}s?\""

        options_list = [
            "Yes, they are.",
            "No, they aren't.",
            "Yes, they're.",  # Неправильный
            "No, they're not."
        ]

        correct = "Yes, they're."
        options = {"A": options_list[0], "B": options_list[1], "C": options_list[2], "D": options_list[3]}
        correct_answer = "C"

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "hard",
            "explanation": "In positive short answers, don't use contractions. 'Yes, they're' is incorrect. Use: Yes, they are."
        }

    def generate_lesson3_q8(self, topic_id: int) -> Dict:
        """L3Q8: How вопрос"""
        topic = self.TOPICS[topic_id]

        question = "Выберите правильный вопрос:"
        correct = "How are you?"
        wrong_options = [
            "How you are?",
            "How is you?",
            "You how are?"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "hard",
            "explanation": "The correct question form is: How are you?"
        }

    # ========================================
    # УРОК 4: Практика и ситуации
    # ========================================

    def generate_lesson4_q1(self, topic_id: int) -> Dict:
        """L4Q1: Знакомство I'm Maria"""
        topic = self.TOPICS[topic_id]

        names = ["Maria", "John", "Sarah", "David", "Emma", "Michael"]
        name = random.choice(names)

        question = "Как правильно представиться?"
        correct = f"I'm {name}."
        wrong_options = [
            f"I {name}.",
            f"I is {name}.",
            f"I am from {name}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "easy",
            "explanation": f"To introduce yourself, use: I'm + name. The correct form is: I'm {name}."
        }

    def generate_lesson4_q2(self, topic_id: int) -> Dict:
        """L4Q2: В аэропорту Where is gate 5?"""
        topic = self.TOPICS[topic_id]

        gates = ["5", "12", "A3", "B7", "15"]
        gate = random.choice(gates)

        question = f"Выберите правильный вариант для ситуации в аэропорту:\n\"Where _____ gate {gate}?\""
        correct = "is"
        wrong_options = ["am", "are", "be"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "medium",
            "explanation": f"'Gate' is singular, so use 'is'. The correct question is: Where is gate {gate}?"
        }

    def generate_lesson4_q3(self, topic_id: int) -> Dict:
        """L4Q3: Диалог Are you free tomorrow?"""
        topic = self.TOPICS[topic_id]

        question = "Заполните пропуск в диалоге:\nA: \"_____ you free tomorrow?\"\nB: \"Yes, I am.\""
        correct = "Are"
        wrong_options = ["Is", "Am", "Be"]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "medium",
            "explanation": "To ask a question with 'you', use 'Are'. The correct question is: Are you free tomorrow?"
        }

    def generate_lesson4_q4(self, topic_id: int) -> Dict:
        """L4Q4: На работе I'm not in the office"""
        topic = self.TOPICS[topic_id]
        location_in = random.choice(topic["locations_in"])

        question = f"Как правильно сказать \"Меня нет {location_in.replace('in the ', 'в ')}\"?"
        correct = f"I'm not {location_in}."
        wrong_options = [
            f"I not {location_in}.",
            f"I'm not in {location_in.replace('in the ', '')}.",
            f"I not am {location_in}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "medium",
            "explanation": f"The correct negative form is: I'm not {location_in}."
        }

    def generate_lesson4_q5(self, topic_id: int) -> Dict:
        """L4Q5: Трансформация She is busy"""
        topic = self.TOPICS[topic_id]
        adjective = random.choice(topic["adjectives_state"])

        question = f"Преобразуйте в отрицание и вопрос:\n\"She is {adjective}.\""
        correct = f"She isn't {adjective}. / Is she {adjective}?"
        wrong_options = [
            f"She not is {adjective}. / She is {adjective}?",
            f"She amn't {adjective}. / Are she {adjective}?",
            f"She not {adjective}. / Is {adjective} she?"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "hard",
            "explanation": f"Negative: She isn't {adjective}. Question: Is she {adjective}?"
        }

    def generate_lesson4_q6(self, topic_id: int) -> Dict:
        """L4Q6: О семье My parents are in Spain"""
        topic = self.TOPICS[topic_id]
        country = random.choice(topic["countries"])

        question = f"Выберите правильное предложение о семье:"
        correct = f"My parents are in {country}."
        wrong_options = [
            f"My parents is in {country}.",
            f"My parents am in {country}.",
            f"My parents in {country}."
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "hard",
            "explanation": f"'Parents' is plural, so use 'are'. The correct sentence is: My parents are in {country}."
        }

    def generate_lesson4_q7(self, topic_id: int) -> Dict:
        """L4Q7: Диалог Is this your first day? / Yes, it is"""
        topic = self.TOPICS[topic_id]

        question = "Заполните диалог правильно:\nA: \"_____ this your first day?\"\nB: \"Yes, it _____.\""
        correct = "Is / is"
        wrong_options = [
            "Are / are",
            "Is / are",
            "Are / is"
        ]

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "hard",
            "explanation": "'This' is singular, so use 'is' for both question and answer. Correct: Is this...? / Yes, it is."
        }

    def generate_lesson4_q8(self, topic_id: int) -> Dict:
        """L4Q8: Все формы - найти ошибку"""
        topic = self.TOPICS[topic_id]
        country = random.choice(topic["countries"])

        question = "Какое предложение составлено НЕПРАВИЛЬНО?"

        options_list = [
            "I'm not sure.",
            "Are you ready?",
            "She's a teacher.",
            f"They is from {country}."  # Неправильное
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
            "explanation": f"'They' is plural, so use 'are' (not 'is'). The correct sentence is: They are from {country}."
        }

    # ========================================
    # Методы генерации тестов
    # ========================================

    def generate_test_for_lesson(
            self,
            lesson_num: int,
            topic_ids_sequence: List[int],  # ✅ Получаем готовый список!
            num_questions: int = 8
    ) -> List[Dict]:
        """
        Генерировать тест для урока
        СИНХРОННЫЙ - НЕ работает с БД!

        Args:
            lesson_num: Номер урока (1-4)
            topic_ids_sequence: [2, 3, 2, 4, ...]  ← ГОТОВЫЙ список топиков
            num_questions: Количество вопросов

        Returns:
            [
                {
                    'question': str,
                    'options': {...},
                    'correct_answer': str,
                    'explanation': str,
                    'topic_id': int,  # ← Есть
                    # 'topic_name': НЕТ! Добавится снаружи
                    'lesson': int
                },
                ...
            ]
        """

        # Методы генерации для урока
        lesson_methods = {
            1: [
                self.generate_lesson1_q1, self.generate_lesson1_q2,
                self.generate_lesson1_q3, self.generate_lesson1_q4,
                self.generate_lesson1_q5, self.generate_lesson1_q6,
                self.generate_lesson1_q7, self.generate_lesson1_q8
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
            ]
        }

        methods = lesson_methods[lesson_num]
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
                self.generate_lesson1_q7, self.generate_lesson1_q8
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
            ]
        }
        return lesson_methods[lesson_num]

    def generate_full_module_test(
            self,
            topic_ids_sequence: List[int],  # ✅ Получаем готовый список!
            num_questions: int = 32
    ) -> List[Dict]:
        """
        Генерировать полный тест по модулю
        СИНХРОННЫЙ - НЕ работает с БД!

        Args:
            topic_ids_sequence: [2, 3, 2, 4, ...]  ← ГОТОВЫЙ список (32 топика)
            num_questions: Количество вопросов

        Returns:
            Список из 32 вопросов (БЕЗ topic_name!)
        """

        # Собираем все методы генерации
        all_methods = []
        for lesson_num in range(1, 5):
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
'''
if __name__ == "__main__":
    # Создаем генератор
    generator = ToBeQuestionGenerator(seed=42)

    # Пример 1: Генерируем вопросы для Урока 1 (Shopping and money)
    print("=" * 60)
    print("УРОК 1: Утвердительные предложения")
    print("Тема: Shopping and money")
    print("=" * 60)

    lesson1_questions = generator.generate_test_for_lesson(
        lesson_num=1,
        topic_id=2,  # Shopping and money
        num_questions=8
    )

    for i, q in enumerate(lesson1_questions, 1):
        print(f"\nВопрос {i}:")
        print(q["question"])
        for letter, option in q["options"].items():
            print(f"{letter}) {option}")
        print(f"Правильный ответ: {q['correct_answer']}")
        print(f"Объяснение: {q['explanation']}")

    # Пример 2: Генерируем полный тест по модулю (32 вопроса)
    print("\n" + "=" * 60)
    print("ПОЛНЫЙ МОДУЛЬ (32 вопроса)")
    print("Тема: Technology and gadgets")
    print("=" * 60)

    full_test = generator.generate_full_module_test(topic_id=9)  # Technology

    print(f"\nВсего вопросов сгенерировано: {len(full_test)}")
    print(f"Уроков: 4")
    print(f"Вопросов на урок: 8")

    # Показываем первый вопрос из каждого урока
    for lesson in [1, 2, 3, 4]:
        lesson_qs = [q for q in full_test if q["lesson"] == lesson]
        if lesson_qs:
            print(f"\n--- Урок {lesson} (пример) ---")
            q = lesson_qs[0]
            print(f"Вопрос: {q['question']}")
            print(f"Правильный ответ: {q['correct_answer']}")
'''