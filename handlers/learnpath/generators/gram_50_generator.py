import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from .base_generator import BaseQuestionGenerator

class SingularPluralQuestionGenerator(BaseQuestionGenerator):
    """
    Динамический генератор вопросов по теме Singular vs Plural
    Создает уникальные вопросы для каждой темы интересов
    65 типов вопросов (8+10+10+10+10+7+10 на 7 уроков)
    """

    # Темы интересов с расширенными словарями
    TOPICS = {
        2: {
            "name": "Shopping and money",
            "regular_nouns": ["product", "store", "shop", "cart", "bag", "customer", "seller", "buyer"],
            "nouns_es": ["price", "box", "purchase", "discount", "class", "business", "address"],
            "nouns_consonant_y": ["company", "category", "warranty", "delivery", "inventory", "penny"],
            "nouns_vowel_y": ["day", "way", "boy", "toy", "key"],
            "nouns_f_fe": ["shelf", "knife", "half", "loaf"],
            "nouns_f_s": ["roof", "chief", "safe", "belief"],
            "nouns_o_es": ["potato", "tomato", "hero"],
            "nouns_o_s": ["photo", "video", "kilo", "euro"],
            "irregular_plurals": {
                "man": "men", "woman": "women", "child": "children", "person": "people",
                "tooth": "teeth", "foot": "feet", "mouse": "mice"
            },
            "no_change": ["sheep", "deer", "fish"],
            "uncountable_nouns": ["money", "cash", "information", "advice", "equipment", "furniture"],
            "plural_only_nouns": ["goods", "scissors", "clothes", "earnings", "thanks"],
            "collective_nouns": ["staff", "team", "company", "family", "crowd"],
            "countable_phrases": {
                "money": "a lot of money",
                "advice": "a piece of advice",
                "information": "some information"
            }
        },
        3: {
            "name": "Weather and nature",
            "regular_nouns": ["cloud", "wind", "storm", "season", "mountain", "river", "forest", "tree"],
            "nouns_es": ["beach", "bush", "flash", "breeze", "watch"],
            "nouns_consonant_y": ["sky", "country", "city", "berry", "daisy", "lily"],
            "nouns_vowel_y": ["day", "way", "ray", "bay", "valley"],
            "nouns_f_fe": ["leaf", "wolf", "half", "life"],
            "nouns_f_s": ["cliff", "roof"],
            "nouns_o_es": ["potato", "tomato", "tornado", "volcano"],
            "nouns_o_s": ["photo", "radio", "zoo"],
            "irregular_plurals": {
                "goose": "geese", "foot": "feet", "tooth": "teeth", "mouse": "mice",
                "person": "people", "child": "children"
            },
            "no_change": ["sheep", "deer", "fish", "species", "series"],
            "uncountable_nouns": ["weather", "rain", "snow", "sunshine", "water", "air", "nature", "peace"],
            "plural_only_nouns": ["surroundings", "outskirts", "clothes", "stairs"],
            "collective_nouns": ["herd", "flock", "pack", "family", "crowd"],
            "countable_phrases": {
                "weather": "nice weather",
                "rain": "some rain",
                "advice": "a piece of advice"
            }
        },
        4: {
            "name": "Health and medicine",
            "regular_nouns": ["doctor", "patient", "hospital", "clinic", "treatment", "symptom", "medicine"],
            "nouns_es": ["illness", "diagnosis", "dose", "nurse", "virus", "stress"],
            "nouns_consonant_y": ["allergy", "injury", "pharmacy", "therapy", "remedy", "surgery"],
            "nouns_vowel_y": ["day", "way", "ray"],
            "nouns_f_fe": ["knife", "life", "half"],
            "nouns_f_s": ["chief", "belief"],
            "nouns_o_es": ["hero", "potato", "tomato"],
            "nouns_o_s": ["kilo", "photo"],
            "irregular_plurals": {
                "tooth": "teeth", "foot": "feet", "person": "people", "child": "children",
                "man": "men", "woman": "women", "mouse": "mice"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["health", "medicine", "advice", "information", "equipment", "research", "progress"],
            "plural_only_nouns": ["scissors", "glasses", "clothes", "stairs", "thanks"],
            "collective_nouns": ["staff", "team", "family", "public", "crew"],
            "countable_phrases": {
                "advice": "a piece of advice",
                "information": "some information",
                "medicine": "some medicine"
            }
        },
        5: {
            "name": "Home and daily routines",
            "regular_nouns": ["room", "bed", "table", "chair", "wall", "door", "window", "floor"],
            "nouns_es": ["dish", "glass", "brush", "box", "couch", "dress"],
            "nouns_consonant_y": ["family", "study", "laundry", "library", "balcony", "pantry"],
            "nouns_vowel_y": ["day", "key", "way", "toy", "boy"],
            "nouns_f_fe": ["knife", "shelf", "half", "loaf", "life", "wife"],
            "nouns_f_s": ["roof", "chief", "safe"],
            "nouns_o_es": ["potato", "tomato", "hero", "echo"],
            "nouns_o_s": ["photo", "video", "radio", "piano"],
            "irregular_plurals": {
                "child": "children", "person": "people", "man": "men", "woman": "women",
                "tooth": "teeth", "foot": "feet", "mouse": "mice"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["furniture", "equipment", "luggage", "water", "bread", "rice", "sugar", "advice"],
            "plural_only_nouns": ["scissors", "trousers", "jeans", "glasses", "clothes", "stairs", "goods"],
            "collective_nouns": ["family", "staff", "team", "class", "public"],
            "countable_phrases": {
                "furniture": "a piece of furniture",
                "advice": "a piece of advice",
                "bread": "a loaf of bread"
            }
        },
        6: {
            "name": "Transportation and directions",
            "regular_nouns": ["car", "bus", "train", "station", "street", "road", "driver", "passenger"],
            "nouns_es": ["bus", "pass", "address", "box", "class"],
            "nouns_consonant_y": ["city", "country", "ferry", "trolley", "subway", "runway"],
            "nouns_vowel_y": ["way", "day", "highway", "pathway", "railway"],
            "nouns_f_fe": ["half", "knife", "life"],
            "nouns_f_s": ["roof", "chief"],
            "nouns_o_es": ["hero", "potato", "tomato"],
            "nouns_o_s": ["auto", "photo", "kilo"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "foot": "feet", "tooth": "teeth", "mouse": "mice"
            },
            "no_change": ["aircraft", "spacecraft", "deer", "sheep", "fish", "series", "crossroads"],
            "uncountable_nouns": ["traffic", "luggage", "baggage", "information", "advice", "equipment", "fuel"],
            "plural_only_nouns": ["scissors", "trousers", "jeans", "glasses", "clothes", "stairs"],
            "collective_nouns": ["crew", "staff", "team", "family", "crowd", "public"],
            "countable_phrases": {
                "luggage": "a piece of luggage",
                "information": "some information",
                "advice": "a piece of advice"
            }
        },
        7: {
            "name": "Leisure and hobbies",
            "regular_nouns": ["game", "sport", "ball", "player", "fan", "team", "club", "park"],
            "nouns_es": ["class", "match", "pass", "brush", "box", "quiz"],
            "nouns_consonant_y": ["hobby", "party", "activity", "gallery", "library", "story"],
            "nouns_vowel_y": ["day", "way", "toy", "boy", "key"],
            "nouns_f_fe": ["knife", "half", "life", "shelf"],
            "nouns_f_s": ["chief", "roof", "belief"],
            "nouns_o_es": ["hero", "potato", "tomato", "echo"],
            "nouns_o_s": ["photo", "video", "piano", "solo", "studio"],
            "irregular_plurals": {
                "child": "children", "person": "people", "man": "men", "woman": "women",
                "foot": "feet", "tooth": "teeth", "mouse": "mice", "goose": "geese"
            },
            "no_change": ["sheep", "deer", "fish", "series", "species"],
            "uncountable_nouns": ["music", "art", "fun", "entertainment", "equipment", "information", "advice"],
            "plural_only_nouns": ["scissors", "glasses", "clothes", "jeans", "trousers", "thanks"],
            "collective_nouns": ["team", "family", "staff", "class", "audience", "crowd", "jury"],
            "countable_phrases": {
                "music": "some music",
                "equipment": "a piece of equipment",
                "advice": "a piece of advice"
            }
        },
        8: {
            "name": "Relationships and emotions",
            "regular_nouns": ["friend", "partner", "parent", "brother", "sister", "feeling", "emotion"],
            "nouns_es": ["wish", "kiss", "hug", "class", "stress", "boss"],
            "nouns_consonant_y": ["family", "baby", "lady", "party", "story", "memory"],
            "nouns_vowel_y": ["day", "way", "boy", "toy", "key"],
            "nouns_f_fe": ["wife", "life", "half", "knife"],
            "nouns_f_s": ["belief", "chief", "roof"],
            "nouns_o_es": ["hero", "echo"],
            "nouns_o_s": ["photo", "video"],
            "irregular_plurals": {
                "child": "children", "person": "people", "man": "men", "woman": "women",
                "tooth": "teeth", "foot": "feet", "mouse": "mice"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["love", "happiness", "sadness", "anger", "advice", "information", "support"],
            "plural_only_nouns": ["thanks", "congratulations", "clothes", "scissors", "glasses"],
            "collective_nouns": ["family", "couple", "team", "staff", "class", "public"],
            "countable_phrases": {
                "advice": "a piece of advice",
                "information": "some information",
                "love": "a lot of love"
            }
        },
        9: {
            "name": "Technology and gadgets",
            "regular_nouns": ["computer", "phone", "tablet", "screen", "keyboard", "cable", "device", "user"],
            "nouns_es": ["watch", "switch", "box", "virus", "address", "process"],
            "nouns_consonant_y": ["battery", "memory", "category", "copy", "delivery", "entry"],
            "nouns_vowel_y": ["display", "key", "way", "day"],
            "nouns_f_fe": ["knife", "half", "life"],
            "nouns_f_s": ["roof", "chief", "safe"],
            "nouns_o_es": ["hero", "echo"],
            "nouns_o_s": ["photo", "video", "kilo", "logo"],
            "irregular_plurals": {
                "mouse": "mice", "person": "people", "child": "children", "man": "men",
                "woman": "women", "foot": "feet", "tooth": "teeth"
            },
            "no_change": ["software", "hardware", "sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["information", "data", "software", "hardware", "equipment", "research", "progress"],
            "plural_only_nouns": ["scissors", "glasses", "headphones", "earphones", "goods"],
            "collective_nouns": ["staff", "team", "company", "family", "class"],
            "countable_phrases": {
                "information": "some information",
                "data": "some data",
                "software": "a piece of software"
            }
        },
        11: {
            "name": "Job interviews and CVs",
            "regular_nouns": ["interview", "job", "resume", "skill", "experience", "qualification", "position"],
            "nouns_es": ["success", "boss", "address", "process", "class", "business"],
            "nouns_consonant_y": ["company", "salary", "vacancy", "story", "duty", "responsibility"],
            "nouns_vowel_y": ["day", "way", "key"],
            "nouns_f_fe": ["life", "half", "knife"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["photo", "portfolio"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "tooth": "teeth", "foot": "feet"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["work", "experience", "advice", "information", "research", "progress", "knowledge"],
            "plural_only_nouns": ["thanks", "congratulations", "scissors", "glasses", "clothes"],
            "collective_nouns": ["staff", "team", "company", "family", "committee"],
            "countable_phrases": {
                "advice": "a piece of advice",
                "information": "some information",
                "work": "some work"
            }
        },
        12: {
            "name": "Meetings and negotiations",
            "regular_nouns": ["meeting", "agenda", "topic", "proposal", "contract", "deadline", "goal"],
            "nouns_es": ["business", "success", "process", "address", "boss", "pass"],
            "nouns_consonant_y": ["company", "strategy", "summary", "party", "policy", "priority"],
            "nouns_vowel_y": ["day", "way", "key"],
            "nouns_f_fe": ["half", "knife", "life"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero", "veto"],
            "nouns_o_s": ["memo", "portfolio"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "foot": "feet", "tooth": "teeth"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["information", "advice", "progress", "research", "work", "equipment", "furniture"],
            "plural_only_nouns": ["thanks", "scissors", "glasses", "clothes", "goods"],
            "collective_nouns": ["team", "staff", "committee", "company", "family", "board"],
            "countable_phrases": {
                "information": "some information",
                "advice": "a piece of advice",
                "progress": "some progress"
            }
        },
        13: {
            "name": "Presentations and public speaking",
            "regular_nouns": ["presentation", "speaker", "slide", "screen", "topic", "example", "point"],
            "nouns_es": ["speech", "success", "process", "class", "business", "address"],
            "nouns_consonant_y": ["story", "summary", "category", "copy", "study", "academy"],
            "nouns_vowel_y": ["way", "day", "key", "display"],
            "nouns_f_fe": ["half", "knife", "life"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero", "echo"],
            "nouns_o_s": ["photo", "video", "memo"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "foot": "feet", "tooth": "teeth"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["information", "advice", "knowledge", "research", "progress", "equipment", "work"],
            "plural_only_nouns": ["thanks", "congratulations", "scissors", "glasses", "clothes"],
            "collective_nouns": ["audience", "team", "staff", "class", "committee", "public"],
            "countable_phrases": {
                "information": "some information",
                "advice": "a piece of advice",
                "knowledge": "some knowledge"
            }
        },
        14: {
            "name": "Emails and business correspondence",
            "regular_nouns": ["email", "message", "letter", "document", "file", "sender", "recipient"],
            "nouns_es": ["address", "business", "process", "success", "boss", "pass"],
            "nouns_consonant_y": ["copy", "reply", "delivery", "company", "summary", "category"],
            "nouns_vowel_y": ["day", "way", "key"],
            "nouns_f_fe": ["half", "knife", "life"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["memo", "photo", "portfolio"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "foot": "feet", "tooth": "teeth"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["information", "advice", "correspondence", "mail", "work", "equipment", "furniture"],
            "plural_only_nouns": ["thanks", "congratulations", "scissors", "glasses", "clothes"],
            "collective_nouns": ["staff", "team", "company", "family", "committee"],
            "countable_phrases": {
                "information": "some information",
                "advice": "a piece of advice",
                "mail": "some mail"
            }
        },
        15: {
            "name": "Office communication and teamwork",
            "regular_nouns": ["colleague", "team", "project", "task", "goal", "leader", "member"],
            "nouns_es": ["success", "boss", "process", "business", "class"],
            "nouns_consonant_y": ["company", "policy", "strategy", "copy", "duty", "responsibility"],
            "nouns_vowel_y": ["day", "way", "key"],
            "nouns_f_fe": ["half", "knife", "life"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["memo", "photo"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "foot": "feet", "tooth": "teeth"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["work", "teamwork", "advice", "information", "equipment", "furniture", "progress"],
            "plural_only_nouns": ["scissors", "glasses", "clothes", "thanks", "goods"],
            "collective_nouns": ["team", "staff", "committee", "company", "family", "crew"],
            "countable_phrases": {
                "work": "some work",
                "advice": "a piece of advice",
                "information": "some information"
            }
        },
        16: {
            "name": "Project management vocabulary",
            "regular_nouns": ["project", "task", "goal", "deadline", "milestone", "resource", "manager"],
            "nouns_es": ["process", "success", "business", "boss", "address"],
            "nouns_consonant_y": ["strategy", "priority", "delivery", "company", "summary", "category"],
            "nouns_vowel_y": ["day", "way", "key"],
            "nouns_f_fe": ["half", "knife", "life"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["memo", "portfolio"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "crisis": "crises", "analysis": "analyses"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["work", "progress", "research", "information", "advice", "equipment", "furniture"],
            "plural_only_nouns": ["scissors", "glasses", "clothes", "thanks"],
            "collective_nouns": ["team", "staff", "committee", "company", "board"],
            "countable_phrases": {
                "work": "some work",
                "progress": "some progress",
                "advice": "a piece of advice"
            }
        },
        17: {
            "name": "Customer service and support",
            "regular_nouns": ["customer", "client", "request", "problem", "solution", "complaint", "service"],
            "nouns_es": ["process", "success", "address", "business", "class"],
            "nouns_consonant_y": ["company", "query", "delivery", "policy", "warranty", "category"],
            "nouns_vowel_y": ["day", "way", "key"],
            "nouns_f_fe": ["half", "knife", "life"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["photo", "video"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "foot": "feet", "tooth": "teeth"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["information", "advice", "support", "help", "work", "equipment", "furniture"],
            "plural_only_nouns": ["thanks", "scissors", "glasses", "clothes", "goods"],
            "collective_nouns": ["team", "staff", "company", "family", "public"],
            "countable_phrases": {
                "information": "some information",
                "advice": "a piece of advice",
                "support": "some support"
            }
        },
        18: {
            "name": "Marketing and sales English",
            "regular_nouns": ["product", "campaign", "brand", "customer", "target", "market", "sale"],
            "nouns_es": ["success", "process", "business", "boss", "address"],
            "nouns_consonant_y": ["company", "strategy", "category", "delivery", "copy", "story"],
            "nouns_vowel_y": ["day", "way", "key", "display"],
            "nouns_f_fe": ["half", "knife", "life"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["photo", "video", "logo", "portfolio"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "medium": "media", "analysis": "analyses"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["information", "advice", "research", "progress", "work", "equipment", "advertising"],
            "plural_only_nouns": ["goods", "scissors", "glasses", "clothes", "thanks"],
            "collective_nouns": ["team", "staff", "company", "family", "public", "audience"],
            "countable_phrases": {
                "information": "some information",
                "advice": "a piece of advice",
                "research": "some research"
            }
        },
        20: {
            "name": "At the airport and hotel",
            "regular_nouns": ["flight", "passenger", "ticket", "gate", "hotel", "room", "guest", "luggage"],
            "nouns_es": ["pass", "address", "class", "business", "process"],
            "nouns_consonant_y": ["country", "city", "entry", "delivery", "lady", "lobby"],
            "nouns_vowel_y": ["day", "way", "key", "delay"],
            "nouns_f_fe": ["knife", "half", "life"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["photo", "kilo"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "foot": "feet", "tooth": "teeth"
            },
            "no_change": ["aircraft", "sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["luggage", "baggage", "information", "advice", "equipment", "furniture", "travel"],
            "plural_only_nouns": ["scissors", "trousers", "jeans", "glasses", "clothes", "stairs"],
            "collective_nouns": ["staff", "team", "crew", "family", "public"],
            "countable_phrases": {
                "luggage": "a piece of luggage",
                "information": "some information",
                "advice": "a piece of advice"
            }
        },
        21: {
            "name": "Sightseeing and excursions",
            "regular_nouns": ["tour", "guide", "museum", "monument", "attraction", "tourist", "view"],
            "nouns_es": ["church", "beach", "address", "pass", "bus"],
            "nouns_consonant_y": ["city", "country", "gallery", "library", "story", "memory"],
            "nouns_vowel_y": ["day", "way", "bay", "valley"],
            "nouns_f_fe": ["knife", "half", "life"],
            "nouns_f_s": ["chief", "belief", "roof", "cliff"],
            "nouns_o_es": ["hero", "volcano"],
            "nouns_o_s": ["photo", "video", "zoo"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "foot": "feet", "tooth": "teeth"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["information", "advice", "luggage", "baggage", "equipment", "furniture", "scenery"],
            "plural_only_nouns": ["scissors", "trousers", "glasses", "clothes", "stairs", "surroundings"],
            "collective_nouns": ["family", "team", "staff", "crowd", "public", "audience"],
            "countable_phrases": {
                "information": "some information",
                "advice": "a piece of advice",
                "luggage": "a piece of luggage"
            }
        },
        22: {
            "name": "Emergencies abroad",
            "regular_nouns": ["emergency", "hospital", "doctor", "problem", "accident", "police", "ambulance"],
            "nouns_es": ["address", "process", "illness", "stress"],
            "nouns_consonant_y": ["injury", "embassy", "country", "city", "story", "body"],
            "nouns_vowel_y": ["day", "way", "key"],
            "nouns_f_fe": ["knife", "life", "half"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["photo"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "tooth": "teeth", "foot": "feet", "crisis": "crises"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["help", "information", "advice", "medicine", "equipment", "luggage", "baggage"],
            "plural_only_nouns": ["scissors", "glasses", "clothes", "thanks", "stairs"],
            "collective_nouns": ["police", "staff", "team", "family", "public", "crew"],
            "countable_phrases": {
                "help": "some help",
                "information": "some information",
                "advice": "a piece of advice"
            }
        },
        23: {
            "name": "Cultural etiquette and customs",
            "regular_nouns": ["custom", "tradition", "rule", "gesture", "behavior", "manner", "culture"],
            "nouns_es": ["dress", "business", "class", "process"],
            "nouns_consonant_y": ["country", "city", "ceremony", "courtesy", "lady", "story"],
            "nouns_vowel_y": ["day", "way", "key"],
            "nouns_f_fe": ["knife", "half", "life"],
            "nouns_f_s": ["belief", "chief", "roof"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["photo", "video"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "foot": "feet", "tooth": "teeth"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["information", "advice", "knowledge", "respect", "etiquette", "behavior", "culture"],
            "plural_only_nouns": ["customs", "thanks", "congratulations", "scissors", "glasses", "clothes"],
            "collective_nouns": ["family", "team", "staff", "public", "society"],
            "countable_phrases": {
                "information": "some information",
                "advice": "a piece of advice",
                "knowledge": "some knowledge"
            }
        },
        24: {
            "name": "Talking about countries and nationalities",
            "regular_nouns": ["country", "nation", "language", "culture", "border", "flag", "capital"],
            "nouns_es": ["address", "success", "class"],
            "nouns_consonant_y": ["country", "city", "embassy", "nationality", "territory", "boundary"],
            "nouns_vowel_y": ["day", "way", "key"],
            "nouns_f_fe": ["knife", "half", "life"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["photo", "video"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "foot": "feet", "tooth": "teeth"
            },
            "no_change": ["sheep", "deer", "fish", "series", "species"],
            "uncountable_nouns": ["information", "advice", "knowledge", "culture", "history", "geography", "travel"],
            "plural_only_nouns": ["scissors", "glasses", "clothes", "thanks"],
            "collective_nouns": ["nation", "people", "family", "team", "staff", "public"],
            "countable_phrases": {
                "information": "some information",
                "advice": "a piece of advice",
                "knowledge": "some knowledge"
            }
        },
        26: {
            "name": "Idioms",
            "regular_nouns": ["idiom", "phrase", "expression", "meaning", "word", "example", "context"],
            "nouns_es": ["pass", "class", "process", "success"],
            "nouns_consonant_y": ["story", "category", "dictionary", "copy", "study"],
            "nouns_vowel_y": ["way", "day", "key"],
            "nouns_f_fe": ["knife", "half", "life"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero", "echo"],
            "nouns_o_s": ["photo", "video"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "foot": "feet", "tooth": "teeth", "mouse": "mice", "goose": "geese"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["information", "advice", "knowledge", "language", "vocabulary", "slang", "jargon"],
            "plural_only_nouns": ["scissors", "glasses", "clothes", "thanks"],
            "collective_nouns": ["team", "family", "staff", "class", "public"],
            "countable_phrases": {
                "information": "some information",
                "advice": "a piece of advice",
                "knowledge": "some knowledge"
            }
        },
        27: {
            "name": "Slang",
            "regular_nouns": ["word", "phrase", "term", "expression", "meaning", "example", "speaker"],
            "nouns_es": ["pass", "class", "stress", "mess"],
            "nouns_consonant_y": ["buddy", "party", "story", "city", "country"],
            "nouns_vowel_y": ["guy", "way", "day", "boy", "key"],
            "nouns_f_fe": ["knife", "half", "life"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["photo", "video"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "foot": "feet", "tooth": "teeth", "mouse": "mice"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["slang", "language", "vocabulary", "jargon", "information", "advice", "knowledge"],
            "plural_only_nouns": ["scissors", "glasses", "clothes", "jeans", "thanks"],
            "collective_nouns": ["team", "family", "staff", "class", "public", "crowd"],
            "countable_phrases": {
                "slang": "some slang",
                "advice": "a piece of advice",
                "information": "some information"
            }
        },
        28: {
            "name": "Phrasal verbs",
            "regular_nouns": ["verb", "particle", "meaning", "example", "sentence", "context", "phrase"],
            "nouns_es": ["pass", "process", "class", "success"],
            "nouns_consonant_y": ["category", "dictionary", "study", "story", "copy"],
            "nouns_vowel_y": ["way", "day", "key"],
            "nouns_f_fe": ["knife", "half", "life"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["photo", "video"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "foot": "feet", "tooth": "teeth"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["information", "advice", "knowledge", "vocabulary", "language", "grammar"],
            "plural_only_nouns": ["scissors", "glasses", "clothes", "thanks"],
            "collective_nouns": ["team", "family", "staff", "class", "public"],
            "countable_phrases": {
                "information": "some information",
                "advice": "a piece of advice",
                "knowledge": "some knowledge"
            }
        },
        29: {
            "name": "Collocations and word patterns",
            "regular_nouns": ["pattern", "word", "phrase", "combination", "example", "meaning", "context"],
            "nouns_es": ["process", "success", "pass", "class"],
            "nouns_consonant_y": ["category", "dictionary", "study", "story", "copy"],
            "nouns_vowel_y": ["way", "day", "key"],
            "nouns_f_fe": ["knife", "half", "life"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["photo", "video"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "foot": "feet", "tooth": "teeth", "analysis": "analyses"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["information", "advice", "knowledge", "vocabulary", "language", "grammar", "usage"],
            "plural_only_nouns": ["scissors", "glasses", "clothes", "thanks"],
            "collective_nouns": ["team", "family", "staff", "class", "public"],
            "countable_phrases": {
                "information": "some information",
                "advice": "a piece of advice",
                "knowledge": "some knowledge"
            }
        },
        30: {
            "name": "Figurative language and metaphors",
            "regular_nouns": ["metaphor", "symbol", "image", "meaning", "word", "phrase", "example"],
            "nouns_es": ["pass", "class", "process", "success"],
            "nouns_consonant_y": ["story", "category", "dictionary", "copy", "library"],
            "nouns_vowel_y": ["way", "day", "key"],
            "nouns_f_fe": ["knife", "half", "life"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero", "echo"],
            "nouns_o_s": ["photo", "video"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "foot": "feet", "tooth": "teeth", "mouse": "mice", "goose": "geese"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["information", "advice", "knowledge", "language", "poetry", "literature", "imagery"],
            "plural_only_nouns": ["scissors", "glasses", "clothes", "thanks"],
            "collective_nouns": ["team", "family", "staff", "class", "audience", "public"],
            "countable_phrases": {
                "information": "some information",
                "advice": "a piece of advice",
                "knowledge": "some knowledge"
            }
        },
        31: {
            "name": "Synonyms, antonyms, and nuance",
            "regular_nouns": ["synonym", "antonym", "word", "meaning", "difference", "example", "context"],
            "nouns_es": ["pass", "class", "process", "success"],
            "nouns_consonant_y": ["category", "dictionary", "study", "story", "copy"],
            "nouns_vowel_y": ["way", "day", "key"],
            "nouns_f_fe": ["knife", "half", "life"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["photo", "video"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "foot": "feet", "tooth": "teeth", "analysis": "analyses"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["information", "advice", "knowledge", "vocabulary", "language", "grammar", "usage"],
            "plural_only_nouns": ["scissors", "glasses", "clothes", "thanks"],
            "collective_nouns": ["team", "family", "staff", "class", "public"],
            "countable_phrases": {
                "information": "some information",
                "advice": "a piece of advice",
                "knowledge": "some knowledge"
            }
        },
        32: {
            "name": "Register and tone (formal vs informal)",
            "regular_nouns": ["tone", "style", "register", "word", "phrase", "context", "example"],
            "nouns_es": ["pass", "class", "process", "address"],
            "nouns_consonant_y": ["category", "dictionary", "study", "story", "copy", "formality"],
            "nouns_vowel_y": ["way", "day", "key"],
            "nouns_f_fe": ["knife", "half", "life"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["photo", "video"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "foot": "feet", "tooth": "teeth"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["information", "advice", "knowledge", "vocabulary", "language", "grammar", "formality"],
            "plural_only_nouns": ["scissors", "glasses", "clothes", "thanks"],
            "collective_nouns": ["team", "family", "staff", "class", "public", "audience"],
            "countable_phrases": {
                "information": "some information",
                "advice": "a piece of advice",
                "knowledge": "some knowledge"
            }
        },
        33: {
            "name": "Common grammar pitfalls",
            "regular_nouns": ["mistake", "error", "rule", "example", "problem", "solution", "pattern"],
            "nouns_es": ["pass", "class", "process", "success"],
            "nouns_consonant_y": ["category", "dictionary", "study", "story", "copy", "difficulty"],
            "nouns_vowel_y": ["way", "day", "key"],
            "nouns_f_fe": ["knife", "half", "life"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["photo", "video"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "foot": "feet", "tooth": "teeth", "crisis": "crises", "analysis": "analyses"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["information", "advice", "knowledge", "grammar", "vocabulary", "language", "homework"],
            "plural_only_nouns": ["scissors", "glasses", "clothes", "thanks"],
            "collective_nouns": ["team", "family", "staff", "class", "public"],
            "countable_phrases": {
                "information": "some information",
                "advice": "a piece of advice",
                "knowledge": "some knowledge"
            }
        },
        35: {
            "name": "English for IT",
            "regular_nouns": ["server", "computer", "network", "database", "user", "program", "system"],
            "nouns_es": ["process", "virus", "address", "success", "access", "crash"],
            "nouns_consonant_y": ["memory", "battery", "category", "copy", "entry", "query"],
            "nouns_vowel_y": ["display", "key", "way", "day", "array"],
            "nouns_f_fe": ["knife", "half", "life"],
            "nouns_f_s": ["chief", "roof", "safe"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["photo", "video", "logo", "memo"],
            "irregular_plurals": {
                "mouse": "mice", "person": "people", "child": "children", "man": "men",
                "woman": "women", "medium": "media", "datum": "data", "analysis": "analyses"
            },
            "no_change": ["software", "hardware", "sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["software", "hardware", "data", "information", "equipment", "research", "progress"],
            "plural_only_nouns": ["scissors", "glasses", "headphones", "goods"],
            "collective_nouns": ["team", "staff", "company", "family", "network"],
            "countable_phrases": {
                "software": "a piece of software",
                "information": "some information",
                "data": "some data"
            }
        },
        36: {
            "name": "English for Finance / Accounting",
            "regular_nouns": ["account", "budget", "profit", "loss", "asset", "debt", "investor"],
            "nouns_es": ["business", "success", "process", "loss", "tax", "expense"],
            "nouns_consonant_y": ["company", "salary", "liability", "currency", "equity", "policy"],
            "nouns_vowel_y": ["day", "way", "key"],
            "nouns_f_fe": ["half", "knife", "life"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["portfolio", "memo"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "analysis": "analyses", "crisis": "crises", "datum": "data"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["money", "cash", "information", "advice", "research", "work", "progress", "capital"],
            "plural_only_nouns": ["earnings", "goods", "thanks", "scissors", "glasses"],
            "collective_nouns": ["staff", "team", "committee", "company", "board", "family"],
            "countable_phrases": {
                "money": "some money",
                "advice": "a piece of advice",
                "information": "some information"
            }
        },
        37: {
            "name": "English for Law",
            "regular_nouns": ["law", "court", "judge", "lawyer", "case", "contract", "client"],
            "nouns_es": ["process", "witness", "class", "address", "pass"],
            "nouns_consonant_y": ["party", "treaty", "policy", "penalty", "jury", "attorney"],
            "nouns_vowel_y": ["day", "way", "key"],
            "nouns_f_fe": ["knife", "half", "life"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["memo"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "foot": "feet", "tooth": "teeth", "crisis": "crises", "analysis": "analyses"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["evidence", "advice", "information", "research", "work", "progress", "justice"],
            "plural_only_nouns": ["scissors", "glasses", "clothes", "thanks"],
            "collective_nouns": ["jury", "staff", "team", "committee", "company", "family", "public"],
            "countable_phrases": {
                "evidence": "some evidence",
                "advice": "a piece of advice",
                "information": "some information"
            }
        },
        38: {
            "name": "English for Medicine",
            "regular_nouns": ["doctor", "patient", "hospital", "symptom", "treatment", "diagnosis", "nurse"],
            "nouns_es": ["illness", "disease", "virus", "process", "dose"],
            "nouns_consonant_y": ["injury", "allergy", "pharmacy", "therapy", "surgery", "body"],
            "nouns_vowel_y": ["day", "way", "ray"],
            "nouns_f_fe": ["knife", "life", "half"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["kilo"],
            "irregular_plurals": {
                "tooth": "teeth", "foot": "feet", "person": "people", "child": "children",
                "man": "men", "woman": "women", "mouse": "mice", "diagnosis": "diagnoses",
                "crisis": "crises", "analysis": "analyses"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["health", "medicine", "advice", "information", "equipment", "research", "progress"],
            "plural_only_nouns": ["scissors", "glasses", "clothes", "stairs", "thanks"],
            "collective_nouns": ["staff", "team", "family", "public", "crew"],
            "countable_phrases": {
                "advice": "a piece of advice",
                "information": "some information",
                "medicine": "some medicine"
            }
        },
        39: {
            "name": "English for Marketing and PR",
            "regular_nouns": ["campaign", "brand", "product", "market", "customer", "target", "strategy"],
            "nouns_es": ["success", "process", "business", "press", "class"],
            "nouns_consonant_y": ["company", "story", "category", "copy", "strategy", "agency"],
            "nouns_vowel_y": ["day", "way", "key", "display"],
            "nouns_f_fe": ["half", "knife", "life"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["photo", "video", "logo", "portfolio"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "medium": "media", "analysis": "analyses", "crisis": "crises"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["information", "advice", "research", "progress", "work", "advertising", "publicity"],
            "plural_only_nouns": ["goods", "scissors", "glasses", "clothes", "thanks"],
            "collective_nouns": ["team", "staff", "company", "family", "public", "audience"],
            "countable_phrases": {
                "information": "some information",
                "advice": "a piece of advice",
                "research": "some research"
            }
        },
        40: {
            "name": "English for HR",
            "regular_nouns": ["employee", "candidate", "position", "interview", "salary", "benefit", "recruiter"],
            "nouns_es": ["process", "success", "business", "address"],
            "nouns_consonant_y": ["company", "vacancy", "policy", "salary", "responsibility", "duty"],
            "nouns_vowel_y": ["day", "way", "key"],
            "nouns_f_fe": ["half", "knife", "life"],
            "nouns_f_s": ["chief", "belief", "roof"],
            "nouns_o_es": ["hero"],
            "nouns_o_s": ["memo", "portfolio"],
            "irregular_plurals": {
                "person": "people", "man": "men", "woman": "women", "child": "children",
                "foot": "feet", "tooth": "teeth", "crisis": "crises", "analysis": "analyses"
            },
            "no_change": ["sheep", "deer", "fish", "series"],
            "uncountable_nouns": ["work", "experience", "advice", "information", "research", "progress", "training"],
            "plural_only_nouns": ["scissors", "glasses", "clothes", "thanks", "earnings"],
            "collective_nouns": ["staff", "team", "company", "family", "committee", "board"],
            "countable_phrases": {
                "advice": "a piece of advice",
                "information": "some information",
                "work": "some work"
            }
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
    # УРОК 1: Что такое единственное и множественное число (8 вопросов)
    # ========================================

    def generate_lesson1_q1(self, topic_id: int) -> Dict:
        """L1Q1: Выберите правильный перевод (two X)"""
        topic = self.TOPICS[topic_id]
        noun = random.choice(topic["regular_nouns"])
        
        question = f"Выберите правильный перевод: 'two {noun}s'"
        correct = f"два {noun}а" if noun.endswith('r') else f"две {noun}ы"
        wrong_options = [
            f"один {noun}",
            f"{noun}",
            f"много {noun}ов"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "easy",
            "explanation": f"'Two {noun}s' означает две/два {noun}ы/а. Это множественное число."
        }

    def generate_lesson1_q2(self, topic_id: int) -> Dict:
        """L1Q2: Какое утверждение верно?"""
        question = "Какое утверждение верно?"
        correct = "В английском только две формы числа: единственное и множественное"
        wrong_options = [
            "В английском три формы числа: единственное, двойственное и множественное",
            "В английском четыре формы числа",
            "В английском число не меняется"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "easy",
            "explanation": "В английском языке существует только две формы: singular (единственное) и plural (множественное)."
        }

    def generate_lesson1_q3(self, topic_id: int) -> Dict:
        """L1Q3: Выберите правильную форму множественного числа"""
        topic = self.TOPICS[topic_id]
        noun = random.choice(topic["regular_nouns"])
        
        question = f"Выберите правильную форму множественного числа для слова '{noun}':"
        correct = f"{noun}s"
        wrong_options = [
            f"{noun}es",
            f"{noun}ies",
            f"{noun}"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "easy",
            "explanation": f"Для образования множественного числа к слову '{noun}' добавляем -s: {noun}s."
        }

    def generate_lesson1_q4(self, topic_id: int) -> Dict:
        """L1Q4: Какой артикль используется с множественным числом?"""
        question = "Какой артикль используется с множественным числом?"
        correct = "нет артикля или the"
        wrong_options = [
            "a",
            "an",
            "some обязательно"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "easy",
            "explanation": "С множественным числом используется либо нулевой артикль (нет артикля), либо определённый артикль 'the'."
        }

    def generate_lesson1_q5(self, topic_id: int) -> Dict:
        """L1Q5: Выберите правильное предложение"""
        topic = self.TOPICS[topic_id]
        noun = random.choice(topic["regular_nouns"])
        
        question = "Выберите правильное предложение:"
        correct = f"The {noun}s are here."
        wrong_options = [
            f"The {noun}s is here.",
            f"A {noun}s are here.",
            f"The {noun} are here."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "easy",
            "explanation": f"Множественное число требует глагола 'are': The {noun}s are here."
        }

    def generate_lesson1_q6(self, topic_id: int) -> Dict:
        """L1Q6: Как образуется множественное число большинства существительных?"""
        question = "Как образуется множественное число большинства существительных?"
        correct = "добавляем -s"
        wrong_options = [
            "добавляем -ed",
            "добавляем -ing",
            "меняем первую букву"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "easy",
            "explanation": "Базовое правило: существительное + S = множественное число (cat → cats)."
        }

    def generate_lesson1_q7(self, topic_id: int) -> Dict:
        """L1Q7: Выберите множественное число"""
        topic = self.TOPICS[topic_id]
        noun = random.choice(topic["regular_nouns"])
        
        question = f"Выберите множественное число: 'one {noun}'"
        correct = f"{noun}s"
        wrong_options = [
            f"{noun}",
            f"{noun}es",
            f"{noun}ies"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "easy",
            "explanation": f"Множественное число от '{noun}' образуется добавлением -s: {noun}s."
        }

    def generate_lesson1_q8(self, topic_id: int) -> Dict:
        """L1Q8: Что правильно?"""
        topic = self.TOPICS[topic_id]
        noun = random.choice(topic["regular_nouns"])
        
        question = "Что правильно?"
        correct = f"one {noun} - two {noun}s"
        wrong_options = [
            f"one {noun} - two {noun}",
            f"one {noun}s - two {noun}s",
            f"one {noun} - two {noun}es"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 1,
            "difficulty": "easy",
            "explanation": f"Единственное число: one {noun}. Множественное число: two {noun}s."
        }

    # ========================================
    # УРОК 2: Основное правило — добавление S (10 вопросов)
    # ========================================

    def generate_lesson2_q1(self, topic_id: int) -> Dict:
        """L2Q1: Выберите правильную форму множественного числа (regular)"""
        topic = self.TOPICS[topic_id]
        noun = random.choice(topic["regular_nouns"])
        
        question = f"Выберите правильную форму множественного числа: '{noun}'"
        correct = f"{noun}s"
        wrong_options = [
            f"{noun}",
            f"{noun}es",
            f"{noun}ies"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": f"К обычным существительным добавляем -s: {noun} → {noun}s."
        }

    def generate_lesson2_q2(self, topic_id: int) -> Dict:
        """L2Q2: Какое слово образует множественное число неправильно?"""
        topic = self.TOPICS[topic_id]
        noun_es = random.choice(topic["nouns_es"])
        
        question = "Какое слово образует множественное число неправильно?"
        correct = f"{noun_es}s"
        wrong_options = [
            "cats",
            "dogs",
            "phones"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": f"Правильно: {noun_es}es (после шипящих добавляем -es, а не -s)."
        }

    def generate_lesson2_q3(self, topic_id: int) -> Dict:
        """L2Q3: После каких букв добавляем -ES вместо -S?"""
        question = "После каких букв добавляем -ES вместо -S?"
        correct = "после s, ss, x, z, sh, ch"
        wrong_options = [
            "после b, d, g",
            "после всех гласных",
            "после m, n, l"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": "После шипящих и свистящих (s, ss, x, z, sh, ch) добавляем -ES."
        }

    def generate_lesson2_q4(self, topic_id: int) -> Dict:
        """L2Q4: Выберите правильную форму: 'box'"""
        question = "Выберите правильную форму: 'box'"
        correct = "boxes"
        wrong_options = [
            "boxs",
            "boxies",
            "boxess"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": "Box оканчивается на -x, поэтому добавляем -ES: boxes."
        }

    def generate_lesson2_q5(self, topic_id: int) -> Dict:
        """L2Q5: Выберите правильную форму (nouns_es)"""
        topic = self.TOPICS[topic_id]
        noun = random.choice(topic["nouns_es"])
        
        question = f"Выберите правильную форму: '{noun}'"
        
        # Определяем правильное окончание
        if noun.endswith(('s', 'ss', 'x', 'z', 'sh', 'ch')):
            correct = f"{noun}es"
        else:
            correct = f"{noun}s"
            
        wrong_options = [
            f"{noun}s" if correct.endswith('es') else f"{noun}es",
            f"{noun}ies",
            f"{noun}ess"
        ]
        
        # Убираем дубликаты
        wrong_options = [opt for opt in wrong_options if opt != correct][:3]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": f"После шипящих/свистящих добавляем -ES: {noun} → {correct}."
        }

    def generate_lesson2_q6(self, topic_id: int) -> Dict:
        """L2Q6: Как произносится окончание -s в слове 'cats'?"""
        question = "Как произносится окончание -s в слове 'cats'?"
        correct = "/s/"
        wrong_options = [
            "/z/",
            "/iz/",
            "/es/"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": "После глухих согласных (t, k, p, f) окончание -s произносится как /s/."
        }

    def generate_lesson2_q7(self, topic_id: int) -> Dict:
        """L2Q7: Как произносится окончание в слове 'dogs'?"""
        question = "Как произносится окончание в слове 'dogs'?"
        correct = "/z/"
        wrong_options = [
            "/s/",
            "/iz/",
            "не произносится"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": "После звонких согласных и гласных окончание -s произносится как /z/."
        }

    def generate_lesson2_q8(self, topic_id: int) -> Dict:
        """L2Q8: Выберите правильную форму (nouns_es 2)"""
        topic = self.TOPICS[topic_id]
        # Выбираем слово, которое точно оканчивается на шипящие
        nouns_with_sh_ch = [n for n in topic["nouns_es"] if n.endswith(('sh', 'ch', 'ss', 'x', 'z'))]
        if nouns_with_sh_ch:
            noun = random.choice(nouns_with_sh_ch)
        else:
            noun = "dish"  # fallback
        
        question = f"Выберите правильную форму: '{noun}'"
        correct = f"{noun}es"
        wrong_options = [
            f"{noun}s",
            f"{noun}ies",
            f"{noun}ess"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": f"'{noun}' оканчивается на шипящую, поэтому добавляем -ES: {noun}es."
        }

    def generate_lesson2_q9(self, topic_id: int) -> Dict:
        """L2Q9: Дополните предложение"""
        topic = self.TOPICS[topic_id]
        noun = random.choice(topic["regular_nouns"])
        
        question = f"Дополните предложение: 'I have two ___.'"
        correct = f"{noun}s"
        wrong_options = [
            f"{noun}",
            f"{noun}es",
            f"{noun}ies"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": f"'Two' требует множественного числа: two {noun}s."
        }

    def generate_lesson2_q10(self, topic_id: int) -> Dict:
        """L2Q10: Выберите правильную форму: 'watch'"""
        question = "Выберите правильную форму: 'watch'"
        correct = "watches"
        wrong_options = [
            "watchs",
            "watchies",
            "watchess"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 2,
            "difficulty": "easy",
            "explanation": "Watch оканчивается на -ch, поэтому добавляем -ES: watches."
        }

    # ========================================
    # УРОК 3: Особые правила образования множественного числа (10 вопросов)
    # ========================================

    def generate_lesson3_q1(self, topic_id: int) -> Dict:
        """L3Q1: Выберите правильную форму (consonant + Y)"""
        topic = self.TOPICS[topic_id]
        noun = random.choice(topic["nouns_consonant_y"])
        
        base = noun[:-1]  # убираем Y
        question = f"Выберите правильную форму множественного числа: '{noun}'"
        correct = f"{base}ies"
        wrong_options = [
            f"{noun}s",
            f"{noun}es",
            f"{base}yes"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": f"Согласная + Y: меняем Y на IES. {noun} → {correct}."
        }

    def generate_lesson3_q2(self, topic_id: int) -> Dict:
        """L3Q2: Что происходит со словами на согласную + Y?"""
        question = "Что происходит со словами на согласную + Y?"
        correct = "меняем Y на IES"
        wrong_options = [
            "просто добавляем -s",
            "меняем Y на S",
            "удваиваем Y"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": "Правило: согласная + Y → Y меняется на IES (city → cities)."
        }

    def generate_lesson3_q3(self, topic_id: int) -> Dict:
        """L3Q3: Выберите правильную форму: 'baby'"""
        question = "Выберите правильную форму: 'baby'"
        correct = "babies"
        wrong_options = [
            "babys",
            "babes",
            "babyies"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": "Baby: согласная (b) + Y → меняем на IES: babies."
        }

    def generate_lesson3_q4(self, topic_id: int) -> Dict:
        """L3Q4: Выберите правильную форму (vowel + Y)"""
        topic = self.TOPICS[topic_id]
        noun = random.choice(topic["nouns_vowel_y"])
        
        question = f"Выберите правильную форму: '{noun}' (гласная + Y)"
        correct = f"{noun}s"
        wrong_options = [
            f"{noun[:-1]}ies",
            f"{noun}es",
            f"{noun[:-1]}yes"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": f"Гласная + Y: просто добавляем -S. {noun} → {noun}s."
        }

    def generate_lesson3_q5(self, topic_id: int) -> Dict:
        """L3Q5: Выберите правильную форму (F/FE)"""
        topic = self.TOPICS[topic_id]
        noun = random.choice(topic["nouns_f_fe"])
        
        if noun.endswith('fe'):
            base = noun[:-2]
            correct = f"{base}ves"
        else:  # ends with 'f'
            base = noun[:-1]
            correct = f"{base}ves"
            
        question = f"Выберите правильную форму: '{noun}'"
        wrong_options = [
            f"{noun}s",
            f"{noun}es",
            f"{base}fs" if noun.endswith('f') else f"{base}fes"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": f"F/FE меняется на VES: {noun} → {correct}."
        }

    def generate_lesson3_q6(self, topic_id: int) -> Dict:
        """L3Q6: Что происходит со многими словами на F/FE?"""
        question = "Что происходит со многими словами на F/FE?"
        correct = "меняем F/FE на VES"
        wrong_options = [
            "просто добавляем -s",
            "удваиваем F",
            "убираем F"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": "Правило: многие слова на F/FE меняют F/FE на VES (knife → knives)."
        }

    def generate_lesson3_q7(self, topic_id: int) -> Dict:
        """L3Q7: Выберите правильную форму: 'leaf'"""
        question = "Выберите правильную форму: 'leaf'"
        correct = "leaves"
        wrong_options = [
            "leafs",
            "leafes",
            "leavs"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": "Leaf: F → VES, поэтому leaves."
        }

    def generate_lesson3_q8(self, topic_id: int) -> Dict:
        """L3Q8: Выберите правильную форму (O+ES)"""
        topic = self.TOPICS[topic_id]
        noun = random.choice(topic["nouns_o_es"])
        
        question = f"Выберите правильную форму: '{noun}'"
        correct = f"{noun}es"
        wrong_options = [
            f"{noun}s",
            f"{noun[:-1]}ies",
            f"{noun}ves"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": f"Согласная + O: добавляем -ES. {noun} → {noun}es."
        }

    def generate_lesson3_q9(self, topic_id: int) -> Dict:
        """L3Q9: Выберите правильную форму (O+S)"""
        topic = self.TOPICS[topic_id]
        noun = random.choice(topic["nouns_o_s"])
        
        question = f"Выберите правильную форму: '{noun}'"
        correct = f"{noun}s"
        wrong_options = [
            f"{noun}es",
            f"{noun[:-1]}ies",
            f"{noun}ves"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": f"Гласная + O или иностранные слова: добавляем -S. {noun} → {noun}s."
        }

    def generate_lesson3_q10(self, topic_id: int) -> Dict:
        """L3Q10: Выберите правильную форму: 'hero'"""
        question = "Выберите правильную форму: 'hero'"
        correct = "heroes"
        wrong_options = [
            "heros",
            "heroies",
            "heroves"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 3,
            "difficulty": "easy",
            "explanation": "Hero: согласная + O → добавляем -ES: heroes."
        }

    # ========================================
    # УРОК 4: Неправильное множественное число (10 вопросов)
    # ========================================

    def generate_lesson4_q1(self, topic_id: int) -> Dict:
        """L4Q1: Выберите правильную форму: 'man'"""
        question = "Выберите правильную форму множественного числа: 'man'"
        correct = "men"
        wrong_options = [
            "mans",
            "manes",
            "mens"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "easy",
            "explanation": "Man – неправильная форма. Множественное число: men."
        }

    def generate_lesson4_q2(self, topic_id: int) -> Dict:
        """L4Q2: Выберите правильную форму: 'woman'"""
        question = "Выберите правильную форму: 'woman'"
        correct = "women"
        wrong_options = [
            "womans",
            "womens",
            "womanes"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "easy",
            "explanation": "Woman – неправильная форма. Множественное число: women."
        }

    def generate_lesson4_q3(self, topic_id: int) -> Dict:
        """L4Q3: Выберите правильную форму: 'child'"""
        question = "Выберите правильную форму: 'child'"
        correct = "children"
        wrong_options = [
            "childs",
            "childrens",
            "childes"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "easy",
            "explanation": "Child – неправильная форма. Множественное число: children."
        }

    def generate_lesson4_q4(self, topic_id: int) -> Dict:
        """L4Q4: Выберите правильную форму: 'tooth'"""
        question = "Выберите правильную форму: 'tooth'"
        correct = "teeth"
        wrong_options = [
            "tooths",
            "toothes",
            "teeths"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "easy",
            "explanation": "Tooth – неправильная форма. Множественное число: teeth."
        }

    def generate_lesson4_q5(self, topic_id: int) -> Dict:
        """L4Q5: Выберите правильную форму: 'foot'"""
        question = "Выберите правильную форму: 'foot'"
        correct = "feet"
        wrong_options = [
            "foots",
            "footes",
            "feets"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "easy",
            "explanation": "Foot – неправильная форма. Множественное число: feet."
        }

    def generate_lesson4_q6(self, topic_id: int) -> Dict:
        """L4Q6: Выберите правильную форму: 'mouse'"""
        question = "Выберите правильную форму: 'mouse'"
        correct = "mice"
        wrong_options = [
            "mouses",
            "mices",
            "mouses"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "easy",
            "explanation": "Mouse – неправильная форма. Множественное число: mice."
        }

    def generate_lesson4_q7(self, topic_id: int) -> Dict:
        """L4Q7: Выберите правильную форму: 'person'"""
        question = "Выберите правильную форму: 'person'"
        correct = "people"
        wrong_options = [
            "persons",
            "peoples",
            "persones"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "easy",
            "explanation": "Person – неправильная форма. Множественное число: people (в обычной речи)."
        }

    def generate_lesson4_q8(self, topic_id: int) -> Dict:
        """L4Q8: Выберите правильное предложение (fish)"""
        question = "Выберите правильное предложение:"
        correct = "I caught five fish."
        wrong_options = [
            "I caught five fishes.",
            "I caught five fishs.",
            "I caught five fishies."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "easy",
            "explanation": "Для количества используем 'fish' (не меняется): five fish."
        }

    def generate_lesson4_q9(self, topic_id: int) -> Dict:
        """L4Q9: Выберите правильную форму: 'sheep'"""
        question = "Выберите правильную форму: 'sheep' (одна овца → много овец)"
        correct = "sheep"
        wrong_options = [
            "sheeps",
            "sheepes",
            "sheepies"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "easy",
            "explanation": "Sheep не меняется: one sheep → ten sheep."
        }

    def generate_lesson4_q10(self, topic_id: int) -> Dict:
        """L4Q10: Выберите правильную форму: 'deer'"""
        question = "Выберите правильную форму: 'deer' (один олень → много оленей)"
        correct = "deer"
        wrong_options = [
            "deers",
            "deeres",
            "deeries"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 4,
            "difficulty": "easy",
            "explanation": "Deer не меняется: one deer → many deer."
        }

    # ========================================
    # УРОК 5: Существительные только в единственном или множественном числе (10 вопросов)
    # ========================================

    def generate_lesson5_q1(self, topic_id: int) -> Dict:
        """L5Q1: Выберите правильное предложение (information)"""
        question = "Выберите правильное предложение:"
        correct = "I need some information."
        wrong_options = [
            "I need some informations.",
            "I need an information.",
            "I need informations."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "easy",
            "explanation": "Information – неисчисляемое существительное, всегда в единственном числе."
        }

    def generate_lesson5_q2(self, topic_id: int) -> Dict:
        """L5Q2: Выберите правильное предложение (advice)"""
        question = "Выберите правильное предложение:"
        correct = "She gave me good advice."
        wrong_options = [
            "She gave me good advices.",
            "She gave me a good advice.",
            "She gave me some advices."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "easy",
            "explanation": "Advice – неисчисляемое существительное, не имеет множественного числа."
        }

    def generate_lesson5_q3(self, topic_id: int) -> Dict:
        """L5Q3: Выберите правильное предложение (news)"""
        question = "Выберите правильное предложение:"
        correct = "The news is good."
        wrong_options = [
            "The news are good.",
            "A news is good.",
            "The newses are good."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "easy",
            "explanation": "News – единственное число, несмотря на окончание -s. Используем 'is'."
        }

    def generate_lesson5_q4(self, topic_id: int) -> Dict:
        """L5Q4: Выберите правильное предложение (trousers)"""
        question = "Выберите правильное предложение:"
        correct = "My trousers are dirty."
        wrong_options = [
            "My trousers is dirty.",
            "My trouser are dirty.",
            "A trousers is dirty."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "easy",
            "explanation": "Trousers – всегда множественное число. Используем 'are'."
        }

    def generate_lesson5_q5(self, topic_id: int) -> Dict:
        """L5Q5: Выберите правильное предложение (glasses)"""
        question = "Выберите правильное предложение:"
        correct = "Where are my glasses?"
        wrong_options = [
            "Where is my glasses?",
            "Where is my glass?",
            "Where are my glass?"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "easy",
            "explanation": "Glasses (очки) – всегда множественное число. Используем 'are'."
        }

    def generate_lesson5_q6(self, topic_id: int) -> Dict:
        """L5Q6: Как правильно посчитать 'advice'?"""
        question = "Как правильно посчитать 'advice'?"
        correct = "two pieces of advice"
        wrong_options = [
            "two advices",
            "two advice",
            "two advicees"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "easy",
            "explanation": "Неисчисляемые существительные считаем через 'piece of': two pieces of advice."
        }

    def generate_lesson5_q7(self, topic_id: int) -> Dict:
        """L5Q7: Выберите правильное предложение (mathematics)"""
        question = "Выберите правильное предложение:"
        correct = "Mathematics is difficult."
        wrong_options = [
            "Mathematics are difficult.",
            "A mathematics is difficult.",
            "Mathematicses are difficult."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "easy",
            "explanation": "Науки на -ics (mathematics, physics) – единственное число, используем 'is'."
        }

    def generate_lesson5_q8(self, topic_id: int) -> Dict:
        """L5Q8: Выберите правильное предложение (jeans)"""
        question = "Выберите правильное предложение:"
        correct = "I bought two pairs of jeans."
        wrong_options = [
            "I bought two jeans.",
            "I bought two pair of jeans.",
            "I bought two jean."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "easy",
            "explanation": "Парные предметы считаем через 'pair of': two pairs of jeans."
        }

    def generate_lesson5_q9(self, topic_id: int) -> Dict:
        """L5Q9: Выберите правильное предложение (scissors)"""
        question = "Выберите правильное предложение:"
        correct = "These scissors are sharp."
        wrong_options = [
            "These scissors is sharp.",
            "This scissors are sharp.",
            "A scissors is sharp."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "easy",
            "explanation": "Scissors (ножницы) – всегда множественное число. Используем 'are' и 'these'."
        }

    def generate_lesson5_q10(self, topic_id: int) -> Dict:
        """L5Q10: Выберите правильное предложение (furniture)"""
        topic = self.TOPICS[topic_id]
        
        question = "Выберите правильное предложение:"
        correct = "Furniture is expensive."
        wrong_options = [
            "Furniture are expensive.",
            "Furnitures are expensive.",
            "A furniture is expensive."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 5,
            "difficulty": "easy",
            "explanation": "Furniture – неисчисляемое существительное, всегда единственное число."
        }

    # ========================================
    # УРОК 6: Собирательные существительные (7 вопросов)
    # ========================================

    def generate_lesson6_q1(self, topic_id: int) -> Dict:
        """L6Q1: Выберите правильное предложение (team - американский)"""
        question = "Выберите правильное предложение (американский английский):"
        correct = "The team is playing."
        wrong_options = [
            "The team are playing.",
            "The team were playing.",
            "A team are playing."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": "В американском английском собирательные существительные используются с глаголом в единственном числе."
        }

    def generate_lesson6_q2(self, topic_id: int) -> Dict:
        """L6Q2: Выберите правильное предложение (family)"""
        question = "Выберите правильное предложение (американский английский):"
        correct = "My family is happy."
        wrong_options = [
            "My family are happy.",
            "My family were happy.",
            "A families are happy."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": "В американском английском 'family' + 'is': My family is happy."
        }

    def generate_lesson6_q3(self, topic_id: int) -> Dict:
        """L6Q3: Какое предложение правильное ВСЕГДА?"""
        question = "Какое предложение правильное ВСЕГДА (и в британском, и в американском)?"
        correct = "The police are coming."
        wrong_options = [
            "The police is coming.",
            "A police is coming.",
            "The polices are coming."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": "Police – всегда с глаголом во множественном числе: The police are."
        }

    def generate_lesson6_q4(self, topic_id: int) -> Dict:
        """L6Q4: Как правильно сказать про одного полицейского?"""
        question = "Как правильно сказать про одного полицейского?"
        correct = "a police officer"
        wrong_options = [
            "a police",
            "one police",
            "a polices"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": "Для одного полицейского говорим: a police officer / a policeman / a policewoman."
        }

    def generate_lesson6_q5(self, topic_id: int) -> Dict:
        """L6Q5: Что правильно в американском английском? (government)"""
        question = "Что правильно в американском английском?"
        correct = "The government is divided."
        wrong_options = [
            "The government are divided.",
            "A government are divided.",
            "The governments is divided."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": "В американском английском: The government is (единственное число)."
        }

    def generate_lesson6_q6(self, topic_id: int) -> Dict:
        """L6Q6: В британском английском оба варианта возможны"""
        question = "В британском английском оба варианта возможны. Какой?"
        correct = "The class is quiet / The class are quiet"
        wrong_options = [
            "The class is quiet / A class are quiet",
            "A class is quiet / The classes is quiet",
            "The class am quiet / The class is quiet"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": "В британском английском собирательные существительные могут использоваться и с 'is', и с 'are'."
        }

    def generate_lesson6_q7(self, topic_id: int) -> Dict:
        """L6Q7: Выберите собирательное существительное"""
        topic = self.TOPICS[topic_id]
        collective = random.choice(topic["collective_nouns"])
        regular = random.choice(topic["regular_nouns"])
        
        question = "Выберите собирательное существительное:"
        correct = collective
        wrong_options = [
            f"{regular}s",
            "cars",
            "houses"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 6,
            "difficulty": "easy",
            "explanation": f"'{collective}' – собирательное существительное (обозначает группу)."
        }

    # ========================================
    # УРОК 7: Типичные ошибки (10 вопросов)
    # ========================================

    def generate_lesson7_q1(self, topic_id: int) -> Dict:
        """L7Q1: Найдите ошибку (information)"""
        question = "Найдите ошибку:"
        correct = "I need informations."
        wrong_options = [
            "I need information.",
            "I need some advice.",
            "I need help."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "easy",
            "explanation": "Information – неисчисляемое, не имеет формы множественного числа. Правильно: I need information."
        }

    def generate_lesson7_q2(self, topic_id: int) -> Dict:
        """L7Q2: Найдите ошибку (women)"""
        question = "Найдите ошибку:"
        correct = "five womans"
        wrong_options = [
            "two children",
            "three men",
            "many people"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "easy",
            "explanation": "Правильно: five women (не womans). Woman → women."
        }

    def generate_lesson7_q3(self, topic_id: int) -> Dict:
        """L7Q3: Найдите ошибку (countries)"""
        question = "Найдите ошибку:"
        correct = "three countrys"
        wrong_options = [
            "many cities",
            "two babies",
            "several parties"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "easy",
            "explanation": "Правильно: three countries (не countrys). Согласная + Y → IES."
        }

    def generate_lesson7_q4(self, topic_id: int) -> Dict:
        """L7Q4: Найдите ошибку (watches)"""
        question = "Найдите ошибку:"
        correct = "four watchs"
        wrong_options = [
            "two boxes",
            "three buses",
            "many dishes"
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "easy",
            "explanation": "Правильно: four watches (не watchs). После -ch добавляем -ES."
        }

    def generate_lesson7_q5(self, topic_id: int) -> Dict:
        """L7Q5: Найдите ошибку (scissors)"""
        question = "Найдите ошибку:"
        correct = "This scissor is sharp."
        wrong_options = [
            "My trousers are dirty.",
            "Where are my glasses?",
            "My jeans are new."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "easy",
            "explanation": "Правильно: These scissors are sharp. Scissors – всегда множественное число."
        }

    def generate_lesson7_q6(self, topic_id: int) -> Dict:
        """L7Q6: Найдите ошибку (people)"""
        question = "Найдите ошибку:"
        correct = "There are five persons."
        wrong_options = [
            "There are five people.",
            "A person is waiting.",
            "Many people live here."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "easy",
            "explanation": "В обычной речи используем 'people' (не persons): There are five people."
        }

    def generate_lesson7_q7(self, topic_id: int) -> Dict:
        """L7Q7: Найдите ошибку (articles with plural)"""
        question = "Найдите ошибку:"
        correct = "I have a books."
        wrong_options = [
            "I have books.",
            "I have some books.",
            "I have many books."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "easy",
            "explanation": "Нельзя использовать артикль 'a/an' с множественным числом. Правильно: I have books / some books."
        }

    def generate_lesson7_q8(self, topic_id: int) -> Dict:
        """L7Q8: Что правильно в американском английском? (data)"""
        question = "Что правильно в американском английском?"
        correct = "The data is correct."
        wrong_options = [
            "The data are correct.",
            "A data is correct.",
            "The datas are correct."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "easy",
            "explanation": "В американском английском 'data' чаще используется как единственное число: The data is."
        }

    def generate_lesson7_q9(self, topic_id: int) -> Dict:
        """L7Q9: Найдите ошибку (fish)"""
        question = "Найдите ошибку:"
        correct = "ten fishs"
        wrong_options = [
            "five fish (количество)",
            "many fishes (виды)",
            "I caught fish."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "easy",
            "explanation": "Для количества: ten fish (не fishs). Fish не меняется."
        }

    def generate_lesson7_q10(self, topic_id: int) -> Dict:
        """L7Q10: Найдите правильное предложение"""
        question = "Найдите правильное предложение:"
        correct = "The news is good."
        wrong_options = [
            "Furnitures are expensive.",
            "I need some advices.",
            "There are good news."
        ]
        
        options, correct_answer = self._shuffle_options(correct, wrong_options)
        
        return {
            "question": question,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "lesson": 7,
            "difficulty": "easy",
            "explanation": "News – единственное число: The news is good. Остальные варианты содержат ошибки."
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
            lesson_num: Номер урока (1-7)
            topic_ids_sequence: [2, 3, 2, 4, ...]  ← ГОТОВЫЙ список топиков
            num_questions: Количество вопросов (если None, берём все доступные)

        Returns:
            Список вопросов
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
                self.generate_lesson2_q7, self.generate_lesson2_q8,
                self.generate_lesson2_q9, self.generate_lesson2_q10
            ],
            3: [
                self.generate_lesson3_q1, self.generate_lesson3_q2,
                self.generate_lesson3_q3, self.generate_lesson3_q4,
                self.generate_lesson3_q5, self.generate_lesson3_q6,
                self.generate_lesson3_q7, self.generate_lesson3_q8,
                self.generate_lesson3_q9, self.generate_lesson3_q10
            ],
            4: [
                self.generate_lesson4_q1, self.generate_lesson4_q2,
                self.generate_lesson4_q3, self.generate_lesson4_q4,
                self.generate_lesson4_q5, self.generate_lesson4_q6,
                self.generate_lesson4_q7, self.generate_lesson4_q8,
                self.generate_lesson4_q9, self.generate_lesson4_q10
            ],
            5: [
                self.generate_lesson5_q1, self.generate_lesson5_q2,
                self.generate_lesson5_q3, self.generate_lesson5_q4,
                self.generate_lesson5_q5, self.generate_lesson5_q6,
                self.generate_lesson5_q7, self.generate_lesson5_q8,
                self.generate_lesson5_q9, self.generate_lesson5_q10
            ],
            6: [
                self.generate_lesson6_q1, self.generate_lesson6_q2,
                self.generate_lesson6_q3, self.generate_lesson6_q4,
                self.generate_lesson6_q5, self.generate_lesson6_q6,
                self.generate_lesson6_q7
            ],
            7: [
                self.generate_lesson7_q1, self.generate_lesson7_q2,
                self.generate_lesson7_q3, self.generate_lesson7_q4,
                self.generate_lesson7_q5, self.generate_lesson7_q6,
                self.generate_lesson7_q7, self.generate_lesson7_q8,
                self.generate_lesson7_q9, self.generate_lesson7_q10
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
                self.generate_lesson1_q7, self.generate_lesson1_q8
            ],
            2: [
                self.generate_lesson2_q1, self.generate_lesson2_q2,
                self.generate_lesson2_q3, self.generate_lesson2_q4,
                self.generate_lesson2_q5, self.generate_lesson2_q6,
                self.generate_lesson2_q7, self.generate_lesson2_q8,
                self.generate_lesson2_q9, self.generate_lesson2_q10
            ],
            3: [
                self.generate_lesson3_q1, self.generate_lesson3_q2,
                self.generate_lesson3_q3, self.generate_lesson3_q4,
                self.generate_lesson3_q5, self.generate_lesson3_q6,
                self.generate_lesson3_q7, self.generate_lesson3_q8,
                self.generate_lesson3_q9, self.generate_lesson3_q10
            ],
            4: [
                self.generate_lesson4_q1, self.generate_lesson4_q2,
                self.generate_lesson4_q3, self.generate_lesson4_q4,
                self.generate_lesson4_q5, self.generate_lesson4_q6,
                self.generate_lesson4_q7, self.generate_lesson4_q8,
                self.generate_lesson4_q9, self.generate_lesson4_q10
            ],
            5: [
                self.generate_lesson5_q1, self.generate_lesson5_q2,
                self.generate_lesson5_q3, self.generate_lesson5_q4,
                self.generate_lesson5_q5, self.generate_lesson5_q6,
                self.generate_lesson5_q7, self.generate_lesson5_q8,
                self.generate_lesson5_q9, self.generate_lesson5_q10
            ],
            6: [
                self.generate_lesson6_q1, self.generate_lesson6_q2,
                self.generate_lesson6_q3, self.generate_lesson6_q4,
                self.generate_lesson6_q5, self.generate_lesson6_q6,
                self.generate_lesson6_q7
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

    def generate_full_module_test(
            self,
            topic_ids_sequence: List[int],
            num_questions: int = 65
    ) -> List[Dict]:
        """
        Генерировать полный тест по модулю
        СИНХРОННЫЙ - НЕ работает с БД!

        Args:
            topic_ids_sequence: [2, 3, 2, 4, ...]  ← ГОТОВЫЙ список (65 топиков)
            num_questions: Количество вопросов

        Returns:
            Список из 65 вопросов (БЕЗ topic_name!)
        """

        # Собираем все методы генерации
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
