"""
Динамический генератор вопросов для финального теста SPO
Генерирует уникальные вопросы на лету без хранения в БД
"""

import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class QuestionTemplate:
    """Шаблон для генерации вопроса"""
    subjects: List[str]
    predicates: List[str]
    objects: List[str]
    topic_id: int
    topic_name: str


class SPOQuestionGenerator:
    """
    Динамический генератор вопросов по SPO структуре
    Создает уникальные вопросы для каждого теста
    """

    # Темы интересов с расширенными словарями
    TOPICS = {
        2: {
            "name": "Shopping and money",
            "subjects": ["I", "She", "He", "The customer", "My friend", "They", "We", "The buyer", "The shopper",
                         "People"],
            "predicates": ["buy", "buys", "pay", "pays", "shop", "shops", "save", "saves", "spend", "spends",
                           "purchase", "purchases", "sell", "sells", "cost", "costs"],
            "objects": ["clothes", "groceries", "money", "products", "gifts", "items", "shoes", "accessories",
                        "food", "supplies", "goods", "merchandise", "things", "equipment"]
        },
        3: {
            "name": "Weather and nature",
            "subjects": ["It", "The weather", "The sun", "Rain", "Snow", "The wind", "The storm", "The sky",
                         "Temperature", "The cloud"],
            "predicates": ["rains", "snows", "shines", "blows", "changes", "falls", "rises", "drops",
                           "improves", "worsens", "clears"],
            "objects": ["outside", "today", "often", "sometimes", "rarely", "heavily", "lightly", "gradually",
                        "suddenly", "constantly"]
        },
        4: {
            "name": "Health and medicine",
            "subjects": ["The doctor", "I", "She", "He", "The patient", "The nurse", "We", "The physician",
                         "The specialist", "They"],
            "predicates": ["examines", "examine", "take", "takes", "prescribe", "prescribes", "treat", "treats",
                           "diagnose", "diagnoses", "check", "checks", "monitor", "monitors"],
            "objects": ["patients", "medicine", "the patient", "symptoms", "health", "tests", "treatment",
                        "advice", "medication", "conditions", "diseases", "vital signs"]
        },
        5: {
            "name": "Home and daily routines",
            "subjects": ["I", "She", "He", "We", "My family", "They", "The children", "My roommate",
                         "The house", "Everyone"],
            "predicates": ["clean", "cleans", "cook", "cooks", "do", "does", "wash", "washes", "organize",
                           "organizes", "prepare", "prepares", "tidy", "tidies"],
            "objects": ["the house", "breakfast", "dishes", "laundry", "rooms", "chores", "homework", "dinner",
                        "the kitchen", "the bathroom", "the bed", "meals"]
        },
        6: {
            "name": "Transportation and directions",
            "subjects": ["I", "The bus", "She", "He", "The train", "They", "We", "The taxi", "The driver",
                         "Passengers"],
            "predicates": ["drive", "drives", "take", "takes", "arrive", "arrives", "leave", "leaves", "catch",
                           "catches", "miss", "misses", "board", "boards"],
            "objects": ["the car", "the bus", "the train", "the taxi", "directions", "the metro", "the flight",
                        "the route", "the stop", "the station"]
        },
        7: {
            "name": "Leisure and hobbies",
            "subjects": ["I", "She", "He", "We", "My friend", "They", "People", "The player", "The fan",
                         "Everyone"],
            "predicates": ["play", "plays", "watch", "watches", "read", "reads", "listen", "listens", "enjoy",
                           "enjoys", "practice", "practices", "perform", "performs"],
            "objects": ["guitar", "TV", "books", "music", "movies", "games", "sports", "hobbies", "videos",
                        "podcasts", "instruments", "activities"]
        },
        8: {
            "name": "Relationships and emotions",
            "subjects": ["I", "She", "He", "We", "My friend", "They", "People", "Everyone", "My family",
                         "The couple"],
            "predicates": ["love", "loves", "like", "likes", "miss", "misses", "trust", "trusts", "support",
                           "supports", "care", "cares", "respect", "respects"],
            "objects": ["my family", "friends", "my partner", "people", "my sister", "relationships", "emotions",
                        "feelings", "each other", "their parents"]
        },
        9: {
            "name": "Technology and gadgets",
            "subjects": ["I", "She", "He", "The developer", "We", "They", "The programmer", "The user",
                         "People", "The engineer"],
            "predicates": ["use", "uses", "develop", "develops", "test", "tests", "fix", "fixes", "install",
                           "installs", "update", "updates", "download", "downloads"],
            "objects": ["computers", "software", "apps", "the code", "programs", "devices", "technology",
                        "systems", "smartphones", "applications", "gadgets"]
        },
        11: {
            "name": "Job interviews and CVs",
            "subjects": ["I", "The candidate", "She", "He", "The applicant", "They", "We", "The interviewer",
                         "Job seekers", "Graduates"],
            "predicates": ["send", "sends", "prepare", "prepares", "write", "writes", "update", "updates",
                           "submit", "submits", "review", "reviews", "polish", "polishes"],
            "objects": ["my CV", "the resume", "applications", "documents", "the cover letter", "references",
                        "portfolios", "job applications", "credentials"]
        },
        12: {
            "name": "Meetings and negotiations",
            "subjects": ["I", "The manager", "We", "The team", "They", "She", "He", "The director",
                         "Participants", "The committee"],
            "predicates": ["schedule", "schedules", "attend", "attends", "organize", "organizes", "lead",
                           "leads", "discuss", "discusses", "chair", "chairs", "conduct", "conducts"],
            "objects": ["meetings", "the agenda", "negotiations", "proposals", "contracts", "plans", "projects",
                        "deals", "sessions", "conferences"]
        },
        13: {
            "name": "Presentations and public speaking",
            "subjects": ["I", "The speaker", "She", "He", "The presenter", "They", "We", "The expert",
                         "The lecturer", "Speakers"],
            "predicates": ["give", "gives", "prepare", "prepares", "deliver", "delivers", "practice",
                           "practices", "present", "presents", "rehearse", "rehearses"],
            "objects": ["presentations", "speeches", "slides", "reports", "the talk", "information", "data",
                        "ideas", "findings", "demonstrations"]
        },
        14: {
            "name": "Emails and business correspondence",
            "subjects": ["I", "She", "He", "The employee", "We", "They", "The assistant", "The manager",
                         "Staff", "Colleagues"],
            "predicates": ["write", "writes", "send", "sends", "read", "reads", "reply", "replies", "forward",
                           "forwards", "draft", "drafts", "compose", "composes"],
            "objects": ["emails", "messages", "letters", "reports", "correspondence", "documents", "attachments",
                        "memos", "notifications", "updates"]
        },
        15: {
            "name": "Office communication and teamwork",
            "subjects": ["I", "The team", "She", "He", "My colleague", "We", "They", "Team members",
                         "The staff", "Coworkers"],
            "predicates": ["collaborate", "collaborates", "communicate", "communicates", "share", "shares",
                           "help", "helps", "support", "supports", "coordinate", "coordinates"],
            "objects": ["ideas", "information", "tasks", "the project", "resources", "feedback", "knowledge",
                        "files", "updates", "responsibilities"]
        },
        16: {
            "name": "Project management vocabulary",
            "subjects": ["The manager", "I", "The team lead", "We", "They", "She", "He", "The coordinator",
                         "Project managers", "The director"],
            "predicates": ["manage", "manages", "plan", "plans", "track", "tracks", "coordinate", "coordinates",
                           "deliver", "delivers", "monitor", "monitors", "oversee", "oversees"],
            "objects": ["projects", "tasks", "deadlines", "resources", "the timeline", "milestones",
                        "deliverables", "goals", "budgets", "progress"]
        },
        17: {
            "name": "Customer service and support",
            "subjects": ["I", "The agent", "She", "He", "The representative", "They", "We", "The support team",
                         "Staff", "Operators"],
            "predicates": ["help", "helps", "serve", "serves", "assist", "assists", "support", "supports",
                           "resolve", "resolves", "handle", "handles", "address", "addresses"],
            "objects": ["customers", "clients", "issues", "problems", "requests", "questions", "complaints",
                        "inquiries", "concerns", "tickets"]
        },
        18: {
            "name": "Marketing and sales English",
            "subjects": ["I", "The marketer", "She", "He", "The sales team", "They", "We", "The agent",
                         "Representatives", "The company"],
            "predicates": ["sell", "sells", "promote", "promotes", "advertise", "advertises", "market",
                           "markets", "pitch", "pitches", "launch", "launches"],
            "objects": ["products", "services", "campaigns", "offers", "deals", "ideas", "solutions", "brands",
                        "merchandise", "packages"]
        },
        20: {
            "name": "At the airport and hotel",
            "subjects": ["I", "The passenger", "She", "He", "The traveler", "They", "We", "The guest",
                         "Tourists", "Visitors"],
            "predicates": ["check", "checks", "book", "books", "board", "boards", "arrive", "arrives",
                           "confirm", "confirms", "reserve", "reserves"],
            "objects": ["luggage", "tickets", "the flight", "the hotel", "reservations", "passports",
                        "boarding passes", "rooms", "baggage", "seats"]
        },
        21: {
            "name": "Sightseeing and excursions",
            "subjects": ["I", "The tourist", "She", "He", "The guide", "We", "They", "Visitors",
                         "Travelers", "The group"],
            "predicates": ["visit", "visits", "explore", "explores", "see", "sees", "tour", "tours",
                           "photograph", "photographs", "discover", "discovers"],
            "objects": ["museums", "monuments", "sights", "attractions", "places", "landmarks", "exhibitions",
                        "cities", "galleries", "ruins"]
        },
        22: {
            "name": "Emergencies abroad",
            "subjects": ["I", "The person", "She", "He", "The victim", "They", "We", "Tourists",
                         "The traveler", "Witnesses"],
            "predicates": ["call", "calls", "need", "needs", "report", "reports", "seek", "seeks", "request",
                           "requests", "contact", "contacts"],
            "objects": ["help", "the police", "an ambulance", "assistance", "emergency services", "support",
                        "the embassy", "authorities", "medical care"]
        },
        23: {
            "name": "Cultural etiquette and customs",
            "subjects": ["I", "The visitor", "She", "He", "The guest", "They", "We", "Tourists",
                         "Foreigners", "Travelers"],
            "predicates": ["respect", "respects", "follow", "follows", "learn", "learns", "observe",
                           "observes", "understand", "understands", "honor", "honors"],
            "objects": ["customs", "traditions", "etiquette", "rules", "culture", "norms", "practices",
                        "behavior", "protocols", "manners"]
        },
        24: {
            "name": "Talking about countries and nationalities",
            "subjects": ["I", "She", "He", "The person", "My friend", "They", "We", "People", "Immigrants",
                         "Expats"],
            "predicates": ["come", "comes", "visit", "visits", "live", "lives", "travel", "travels", "speak",
                           "speaks", "move", "moves"],
            "objects": ["from Russia", "to America", "in France", "English", "the language", "different countries",
                        "abroad", "overseas", "to Europe"]
        },
        26: {
            "name": "Idioms",
            "subjects": ["I", "She", "He", "People", "My friend", "They", "We", "Native speakers",
                         "Students", "Learners"],
            "predicates": ["use", "uses", "understand", "understands", "learn", "learns", "know", "knows",
                           "say", "says", "study", "studies"],
            "objects": ["idioms", "expressions", "phrases", "sayings", "proverbs", "the meaning",
                        "figurative language", "common idioms", "expressions"]
        },
        27: {
            "name": "Slang",
            "subjects": ["I", "Young people", "She", "He", "Teenagers", "They", "We", "Kids", "Friends",
                         "The youth"],
            "predicates": ["use", "uses", "speak", "speaks", "understand", "understands", "learn", "learns",
                           "hear", "hears", "pick up", "picks up"],
            "objects": ["slang", "informal words", "casual language", "colloquialisms", "street talk",
                        "modern terms", "slang words", "informal expressions"]
        },
        28: {
            "name": "Phrasal verbs",
            "subjects": ["I", "She", "He", "Students", "The learner", "They", "We", "Beginners",
                         "Language learners", "People"],
            "predicates": ["learn", "learns", "use", "uses", "practice", "practices", "study", "studies",
                           "memorize", "memorizes", "master", "masters"],
            "objects": ["phrasal verbs", "verb combinations", "expressions", "collocations", "word patterns",
                        "grammar", "verb phrases", "combinations"]
        },
        29: {
            "name": "Collocations and word patterns",
            "subjects": ["I", "She", "He", "The student", "We", "They", "Learners", "Students",
                         "Language learners", "People"],
            "predicates": ["study", "studies", "learn", "learns", "practice", "practices", "use", "uses",
                           "remember", "remembers", "memorize", "memorizes"],
            "objects": ["collocations", "word patterns", "combinations", "phrases", "vocabulary", "expressions",
                        "word pairs", "natural combinations"]
        },
        30: {
            "name": "Figurative language and metaphors",
            "subjects": ["I", "The writer", "She", "He", "The poet", "They", "We", "Authors", "Speakers",
                         "Artists"],
            "predicates": ["use", "uses", "create", "creates", "understand", "understands", "interpret",
                           "interprets", "write", "writes", "employ", "employs"],
            "objects": ["metaphors", "figurative language", "imagery", "symbols", "literary devices",
                        "comparisons", "similes", "personification"]
        },
        31: {
            "name": "Synonyms, antonyms, and nuance",
            "subjects": ["I", "The student", "She", "He", "The learner", "They", "We", "Students",
                         "Language learners", "Writers"],
            "predicates": ["learn", "learns", "study", "studies", "distinguish", "distinguishes",
                           "understand", "understands", "use", "uses", "recognize", "recognizes"],
            "objects": ["synonyms", "antonyms", "nuances", "differences", "meanings", "word choices",
                        "vocabulary", "shades of meaning"]
        },
        32: {
            "name": "Register and tone (formal vs informal)",
            "subjects": ["I", "The speaker", "She", "He", "The writer", "They", "We", "Professionals",
                         "Communicators", "Students"],
            "predicates": ["adjust", "adjusts", "change", "changes", "choose", "chooses", "use", "uses",
                           "maintain", "maintains", "adapt", "adapts"],
            "objects": ["the tone", "register", "style", "formality", "language", "expressions", "vocabulary",
                        "the level", "word choice"]
        },
        33: {
            "name": "Common grammar pitfalls",
            "subjects": ["I", "Students", "She", "He", "The learner", "They", "We", "Beginners",
                         "Language learners", "People"],
            "predicates": ["make", "makes", "avoid", "avoids", "correct", "corrects", "recognize",
                           "recognizes", "fix", "fixes", "identify", "identifies"],
            "objects": ["mistakes", "errors", "grammar pitfalls", "common problems", "wrong patterns",
                        "typical errors", "common mistakes"]
        },
        35: {
            "name": "English for IT",
            "subjects": ["I", "The programmer", "She", "He", "The IT specialist", "They", "We", "Developers",
                         "Engineers", "The team"],
            "predicates": ["write", "writes", "develop", "develops", "test", "tests", "debug", "debugs",
                           "deploy", "deploys", "maintain", "maintains"],
            "objects": ["code", "software", "applications", "programs", "scripts", "systems", "solutions",
                        "algorithms", "databases"]
        },
        36: {
            "name": "English for Finance / Accounting",
            "subjects": ["I", "The accountant", "She", "He", "The analyst", "They", "We", "The auditor",
                         "Professionals", "The CFO"],
            "predicates": ["analyze", "analyzes", "calculate", "calculates", "manage", "manages", "review",
                           "reviews", "prepare", "prepares", "audit", "audits"],
            "objects": ["finances", "budgets", "reports", "statements", "taxes", "accounts", "data",
                        "financial records", "balance sheets"]
        },
        37: {
            "name": "English for Law",
            "subjects": ["The lawyer", "I", "She", "He", "The attorney", "They", "We", "Legal professionals",
                         "The judge", "Counsel"],
            "predicates": ["review", "reviews", "draft", "drafts", "sign", "signs", "prepare", "prepares",
                           "represent", "represents", "file", "files"],
            "objects": ["contracts", "documents", "agreements", "cases", "clients", "legal papers", "clauses",
                        "lawsuits", "motions"]
        },
        38: {
            "name": "English for Medicine",
            "subjects": ["The doctor", "I", "The physician", "She", "He", "They", "We", "Medical staff",
                         "The surgeon", "Nurses"],
            "predicates": ["examine", "examines", "treat", "treats", "diagnose", "diagnoses", "prescribe",
                           "prescribes", "monitor", "monitors", "perform", "performs"],
            "objects": ["patients", "symptoms", "conditions", "diseases", "medicine", "treatments", "health",
                        "procedures", "surgeries"]
        },
        39: {
            "name": "English for Marketing and PR",
            "subjects": ["The marketer", "I", "She", "He", "The PR specialist", "They", "We", "The agency",
                         "The team", "Professionals"],
            "predicates": ["create", "creates", "manage", "manages", "run", "runs", "analyze", "analyzes",
                           "promote", "promotes", "launch", "launches"],
            "objects": ["campaigns", "content", "brands", "strategies", "media", "messages", "products",
                        "initiatives", "promotions"]
        },
        40: {
            "name": "English for HR",
            "subjects": ["The HR manager", "I", "She", "He", "The recruiter", "They", "We", "HR professionals",
                         "The department", "The team"],
            "predicates": ["hire", "hires", "interview", "interviews", "train", "trains", "manage", "manages",
                           "evaluate", "evaluates", "recruit", "recruits"],
            "objects": ["employees", "candidates", "staff", "personnel", "workers", "applicants", "teams",
                        "talent", "new hires"]
        }
    }

    # Вариативные формулировки вопросов
    QUESTION_TEMPLATES = {
        "subject": [
            "Identify the SUBJECT in this sentence: {sentence}",
            "What is the SUBJECT of this sentence? {sentence}",
            "Find the SUBJECT: {sentence}",
            "Who or what performs the action? {sentence}",
            "Which word is the SUBJECT? {sentence}"
        ],
        "predicate": [
            "Identify the PREDICATE (verb) in this sentence: {sentence}",
            "What is the PREDICATE in this sentence? {sentence}",
            "Find the PREDICATE: {sentence}",
            "Which word shows the action? {sentence}",
            "What is the verb in this sentence? {sentence}"
        ],
        "object": [
            "Identify the OBJECT in this sentence: {sentence}",
            "What is the OBJECT of this sentence? {sentence}",
            "Find the OBJECT: {sentence}",
            "What receives the action? {sentence}",
            "Which word is the OBJECT? {sentence}"
        ],
        "word_order": [
            "Choose the sentence with CORRECT word order:",
            "Which sentence has the correct SPO order?",
            "Select the grammatically correct sentence:",
            "Which sentence follows proper English word order?",
            "Identify the correctly ordered sentence:"
        ],
        "error": [
            "Which sentence is CORRECT?",
            "Find the grammatically correct sentence:",
            "Which sentence has NO errors?",
            "Select the correct sentence:",
            "Which sentence is properly structured?"
        ]
    }

    def __init__(self, seed: Optional[int] = None):
        """
        Инициализация генератора

        Args:
            seed: Seed для воспроизводимости (если нужен одинаковый тест)
        """
        self.seed = seed
        if seed is not None:
            random.seed(seed)

    def _get_sentence_parts(self, topic_id: int) -> Tuple[str, str, str]:
        """
        Получить случайные S-P-O для темы

        Returns:
            (subject, predicate, object)
        """
        topic = self.TOPICS[topic_id]
        subject = random.choice(topic["subjects"])
        predicate = random.choice(topic["predicates"])
        obj = random.choice(topic["objects"])
        return subject, predicate, obj

    def _shuffle_options(self, correct: str, wrongs: List[str]) -> Tuple[Dict[str, str], str]:
        """
        Перемешать варианты ответов

        Returns:
            (options_dict, correct_letter)
        """
        all_options = [correct] + wrongs
        random.shuffle(all_options)

        letters = ["A", "B", "C", "D"]
        options = {letter: option for letter, option in zip(letters, all_options)}
        correct_letter = [k for k, v in options.items() if v == correct][0]

        return options, correct_letter

    def generate_subject_question(self, topic_id: int) -> Dict:
        """Генерировать вопрос на определение Subject"""
        topic = self.TOPICS[topic_id]
        subject, predicate, obj = self._get_sentence_parts(topic_id)
        sentence = f"{subject} {predicate} {obj}."

        # Случайная формулировка вопроса
        question_template = random.choice(self.QUESTION_TEMPLATES["subject"])
        question_text = question_template.format(sentence=sentence)

        # Генерируем неправильные варианты
        wrong_options = [
            predicate,
            obj,
            f"{subject} {predicate}"
        ]

        options, correct_answer = self._shuffle_options(subject, wrong_options)

        return {
            "question": question_text,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "explanation": f"Subject answers WHO or WHAT performs the action. '{subject}' is the subject performing '{predicate}'."
        }

    def generate_predicate_question(self, topic_id: int) -> Dict:
        """Генерировать вопрос на определение Predicate"""
        topic = self.TOPICS[topic_id]
        subject, predicate, obj = self._get_sentence_parts(topic_id)
        sentence = f"{subject} {predicate} {obj}."

        question_template = random.choice(self.QUESTION_TEMPLATES["predicate"])
        question_text = question_template.format(sentence=sentence)

        wrong_options = [
            subject,
            obj,
            f"{subject} {predicate}"
        ]

        options, correct_answer = self._shuffle_options(predicate, wrong_options)

        return {
            "question": question_text,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "explanation": f"Predicate shows WHAT action happens. '{predicate}' is the verb showing the action."
        }

    def generate_object_question(self, topic_id: int) -> Dict:
        """Генерировать вопрос на определение Object"""
        topic = self.TOPICS[topic_id]
        subject, predicate, obj = self._get_sentence_parts(topic_id)
        sentence = f"{subject} {predicate} {obj}."

        question_template = random.choice(self.QUESTION_TEMPLATES["object"])
        question_text = question_template.format(sentence=sentence)

        wrong_options = [
            subject,
            predicate,
            f"{predicate} {obj}"
        ]

        options, correct_answer = self._shuffle_options(obj, wrong_options)

        return {
            "question": question_text,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "explanation": f"Object answers WHAT or WHO receives the action. '{obj}' receives the action of '{predicate}'."
        }

    def generate_word_order_question(self, topic_id: int) -> Dict:
        """Генерировать вопрос на правильный порядок слов"""
        topic = self.TOPICS[topic_id]
        subject, predicate, obj = self._get_sentence_parts(topic_id)
        correct = f"{subject} {predicate} {obj}"

        question_template = random.choice(self.QUESTION_TEMPLATES["word_order"])

        # Различные варианты неправильного порядка
        wrong_orders = [
            f"{obj} {predicate} {subject}",  # OPS
            f"{predicate} {subject} {obj}",  # PSO
            f"{subject} {obj} {predicate}",  # SOP
            f"{predicate} {obj} {subject}",  # POS
            f"{obj} {subject} {predicate}"  # OSP
        ]

        # Выбираем 3 случайных неправильных варианта
        wrong_options = random.sample(wrong_orders, 3)

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question_template,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "explanation": f"English follows Subject-Predicate-Object order: '{correct}'"
        }

    def generate_error_correction_question(self, topic_id: int) -> Dict:
        """Генерировать вопрос на исправление ошибок"""
        topic = self.TOPICS[topic_id]
        subject, predicate, obj = self._get_sentence_parts(topic_id)
        correct = f"{subject} {predicate} {obj}"

        question_template = random.choice(self.QUESTION_TEMPLATES["error"])

        # Типы ошибок с объяснениями
        error_types = [
            (f"{predicate} {obj}", "Missing subject: Every sentence needs a subject (who/what does the action)."),
            (f"{subject} {obj}", "Missing verb: Every sentence needs a verb (the action)."),
            (f"{obj} {subject} {predicate}", "Wrong word order: English uses Subject-Predicate-Object order."),
            (f"{subject} {predicate}", "Missing object: Transitive verbs like this need an object."),
            (f"{obj} {predicate}", "Missing subject: We need to know WHO or WHAT does the action."),
            (f"{predicate} {subject} {obj}", "Wrong word order: Subject must come before the verb."),
        ]

        # Выбираем случайный тип ошибки
        error_sentence, explanation = random.choice(error_types)

        # Создаем 2 дополнительных неправильных варианта
        additional_wrongs = [
            f"{predicate} {obj} {subject}",
            f"{obj} {predicate}",
            f"{subject} {obj}",
            f"{obj} {subject}"
        ]

        # Исключаем уже использованную ошибку и выбираем 2 новых
        available_wrongs = [w for w in additional_wrongs if w != error_sentence]
        selected_wrongs = random.sample(available_wrongs, 2)

        wrong_options = [error_sentence] + selected_wrongs

        options, correct_answer = self._shuffle_options(correct, wrong_options)

        return {
            "question": question_template,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": topic_id,
            "explanation": explanation
        }

    def generate_test_questions(self,
                                num_questions: int = 25,
                                topic_ids: Optional[List[int]] = None) -> List[Dict]:
        """
        Генерировать набор вопросов для теста

        Args:
            num_questions: Количество вопросов
            topic_ids: Список topic_id для использования (если None - используются все)

        Returns:
            Список вопросов
        """
        if topic_ids is None:
            topic_ids = list(self.TOPICS.keys())

        # Типы вопросов с их генераторами
        question_types = [
            self.generate_subject_question,
            self.generate_predicate_question,
            self.generate_object_question,
            self.generate_word_order_question,
            self.generate_error_correction_question
        ]

        questions = []

        for _ in range(num_questions):
            # Случайная тема
            topic_id = random.choice(topic_ids)

            # Случайный тип вопроса
            question_generator = random.choice(question_types)

            # Генерируем вопрос
            question = question_generator(topic_id)
            questions.append(question)

        return questions

    def generate_balanced_test(self,
                               total_questions: int = 25,
                               topic_ids: Optional[List[int]] = None) -> List[Dict]:
        """
        Генерировать сбалансированный тест (равное количество вопросов каждого типа)

        Args:
            total_questions: Общее количество вопросов (должно делиться на 5)
            topic_ids: Список topic_id для использования

        Returns:
            Список вопросов
        """
        if topic_ids is None:
            topic_ids = list(self.TOPICS.keys())

        questions_per_type = total_questions // 5
        remainder = total_questions % 5

        question_types = [
            ("subject", self.generate_subject_question),
            ("predicate", self.generate_predicate_question),
            ("object", self.generate_object_question),
            ("word_order", self.generate_word_order_question),
            ("error", self.generate_error_correction_question)
        ]

        questions = []

        for i, (type_name, generator) in enumerate(question_types):
            # Распределяем остаток вопросов
            count = questions_per_type + (1 if i < remainder else 0)

            for _ in range(count):
                topic_id = random.choice(topic_ids)
                question = generator(topic_id)
                questions.append(question)

        # Перемешиваем вопросы
        random.shuffle(questions)

        return questions


# ============================================================================
# ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("ДИНАМИЧЕСКИЙ ГЕНЕРАТОР ВОПРОСОВ SPO")
    print("=" * 80)

    # 1. Генерация теста БЕЗ seed (каждый раз новый)
    print("\n1. Генерация случайного теста (25 вопросов):")
    generator = SPOQuestionGenerator()
    questions = generator.generate_balanced_test(total_questions=25)

    print(f"✅ Сгенерировано {len(questions)} вопросов")
    print("\nПример первого вопроса:")
    print(f"Q: {questions[0]['question']}")
    print(f"Options: {questions[0]['options']}")
    print(f"Correct: {questions[0]['correct_answer']}")
    print(f"Topic ID: {questions[0]['topic_id']}")

    # 2. Генерация С seed (воспроизводимый тест)
    print("\n" + "=" * 80)
    print("2. Генерация с seed (воспроизводимый тест):")

    seed = 12345
    generator1 = SPOQuestionGenerator(seed=seed)
    test1 = generator1.generate_balanced_test(25)

    generator2 = SPOQuestionGenerator(seed=seed)
    test2 = generator2.generate_balanced_test(25)

    print(f"Тест 1, вопрос 1: {test1[0]['question'][:50]}...")
    print(f"Тест 2, вопрос 1: {test2[0]['question'][:50]}...")
    print(f"Идентичны: {test1[0] == test2[0]}")

    # 3. Генерация для конкретных тем
    print("\n" + "=" * 80)
    print("3. Генерация только для IT и Finance:")
    generator3 = SPOQuestionGenerator()
    tech_finance_test = generator3.generate_balanced_test(
        total_questions=10,
        topic_ids=[35, 36]  # IT и Finance
    )
    print(f"✅ Сгенерировано {len(tech_finance_test)} вопросов")
    print(f"Topics: {set(q['topic_id'] for q in tech_finance_test)}")

    # 4. Показать вариативность
    print("\n" + "=" * 80)
    print("4. Демонстрация вариативности (5 вопросов на Subject для topic 9):")
    generator4 = SPOQuestionGenerator()
    for i in range(5):
        q = generator4.generate_subject_question(topic_id=9)
        print(f"\nВопрос {i + 1}: {q['question'][:60]}...")
        print(f"Correct answer: {q['correct_answer']} = {q['options'][q['correct_answer']]}")