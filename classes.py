import asyncio
import nltk
from nltk.corpus import wordnet, cmudict
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
import language_tool_python
from spellchecker import SpellChecker
import spacy
import gender_guesser.detector as gender

cmu_dict = cmudict.dict()

from aiogram import BaseMiddleware, types
from aiogram.types import TelegramObject
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.enums import ParseMode


from typing import Callable, Dict, Any, Awaitable, Optional
from datetime import datetime, date

import logging
import selfFunctions as myF

logger = logging.getLogger(__name__)

'''
class FreeActionCounter:
    """
    Class to track daily free actions for users in a Telegram bot.

    Usage:
    1. Initialize once when bot starts: counter = FreeActionCounter(pool, daily_limit=6)
    2. Use in handlers: is_valid = await counter.check_and_increment(user_id)
    """

    def __init__(self, pool, daily_limit: int = 6, table_name: str = "t_user"):
        """
        Initialize the counter.

        Args:
            pool: Database connection pool
            daily_limit: Maximum free actions per day
            table_name: Name of the user table
        """
        self.pool = pool
        self.daily_limit = daily_limit
        self.table_name = table_name
        self._cache: Dict[int, Dict] = {}  # In-memory cache for performance

    async def check_and_increment(self, user_id: int) -> bool:
        """
        Check if user can perform action and increment counter if valid.

        Args:
            user_id: Telegram user ID

        Returns:
            bool: True if action is allowed, False if limit exceeded
        """
        try:
            current_date = date.today()

            # Get current counter from database
            current_count = await self._get_daily_count(user_id, current_date)

            # Check if limit exceeded
            if current_count >= self.daily_limit:
                return False

            # Increment counter
            await self._increment_counter(user_id, current_date, current_count + 1)

            # Update cache
            self._cache[user_id] = {
                'date': current_date,
                'count': current_count + 1
            }

            return True

        except Exception as e:
            logging.error(f"Error in check_and_increment for user {user_id}: {e}")
            return False

    async def get_remaining_actions(self, user_id: int) -> int:
        """
        Get remaining free actions for user today.

        Args:
            user_id: Telegram user ID

        Returns:
            int: Number of remaining free actions
        """
        try:
            current_date = date.today()
            current_count = await self._get_daily_count(user_id, current_date)
            return max(0, self.daily_limit - current_count)
        except Exception as e:
            logging.error(f"Error getting remaining actions for user {user_id}: {e}")
            return 0

    async def reset_user_counter(self, user_id: int) -> bool:
        """
        Reset user's daily counter (admin function).

        Args:
            user_id: Telegram user ID

        Returns:
            bool: True if reset successful
        """
        try:
            current_date = date.today()
            await self._set_counter(user_id, current_date, 0)

            # Clear cache
            if user_id in self._cache:
                del self._cache[user_id]

            return True
        except Exception as e:
            logging.error(f"Error resetting counter for user {user_id}: {e}")
            return False

    async def _get_daily_count(self, user_id: int, current_date: date) -> int:
        """Get current daily count for user."""

        # Check cache first
        if user_id in self._cache:
            cached_data = self._cache[user_id]
            if cached_data['date'] == current_date:
                return cached_data['count']

        # Query database
        query = f"""
            SELECT c_free_actions_count, c_free_actions_date 
            FROM {self.table_name} 
            WHERE c_user_id = $1
        """

        async with self.pool.acquire() as connection:
            result = await connection.fetchrow(query, user_id)

            if not result:
                # User not found, create entry
                await self._create_user_entry(user_id)
                return 0

            db_date = result['c_free_actions_date']
            db_count = result['c_free_actions_count'] or 0

            # If date is different, reset counter
            if not db_date or db_date != current_date:
                await self._set_counter(user_id, current_date, 0)
                return 0

            return db_count

    async def _increment_counter(self, user_id: int, current_date: date, new_count: int):
        """Increment the counter in database."""
        query = f"""
            UPDATE {self.table_name} 
            SET c_free_actions_count = $1, c_free_actions_date = $2 
            WHERE c_user_id = $3
        """

        async with self.pool.acquire() as connection:
            await connection.execute(query, new_count, current_date, user_id)

    async def _set_counter(self, user_id: int, current_date: date, count: int):
        """Set the counter to specific value."""
        query = f"""
            UPDATE {self.table_name} 
            SET c_free_actions_count = $1, c_free_actions_date = $2 
            WHERE c_user_id = $3
        """

        async with self.pool.acquire() as connection:
            await connection.execute(query, count, current_date, user_id)

    async def _create_user_entry(self, user_id: int):
        """Create user entry if doesn't exist."""
        current_date = date.today()
        query = f"""
            INSERT INTO {self.table_name} (c_user_id, c_free_actions_count, c_free_actions_date)
            VALUES ($1, 0, $2)
            ON CONFLICT (c_user_id) DO NOTHING
        """

        async with self.pool.acquire() as connection:
            await connection.execute(query, user_id, current_date)
'''


class FreeActionCounter:
    """
    Class to track daily free actions for users in a Telegram bot.

    Usage:
    1. Initialize once when bot starts: counter = FreeActionCounter(pool, daily_limit=6)
    2. Use in handlers: is_valid = await counter.check_and_increment(user_id)
    """

    def __init__(self, pool, daily_limit: int = 100, table_name: str = "t_user"):
        """
        Initialize the counter.

        Args:
            pool: Database connection pool
            daily_limit: Maximum free actions per day
            table_name: Name of the user table
        """
        self.pool = pool
        self.daily_limit = daily_limit
        self.table_name = table_name
        self._cache: Dict[int, Dict] = {}  # In-memory cache for performance

    async def check_and_increment(self, user_id: int) -> bool:
        """
        Check if user can perform action and increment counter if valid.
        Users with active subscriptions (status 1-2) bypass the limit.

        Args:
            user_id: Telegram user ID

        Returns:
            bool: True if action is allowed, False if limit exceeded
        """
        try:
            # First check subscription status
            has_active_subscription = await self._has_active_subscription(user_id)

            # Users with active subscription bypass free action limits
            if has_active_subscription:
                return True

            current_date = date.today()

            # Get current counter from database
            current_count = await self._get_daily_count(user_id, current_date)

            # Check if limit exceeded
            if current_count >= self.daily_limit:
                return False

            # Increment counter
            await self._increment_counter(user_id, current_date, current_count + 1)

            # Update cache
            self._cache[user_id] = {
                'date': current_date,
                'count': current_count + 1
            }

            return True

        except Exception as e:
            logging.error(f"Error in check_and_increment for user {user_id}: {e}")
            return False

    async def get_remaining_actions(self, user_id: int) -> int:
        """
        Get remaining free actions for user today.
        Users with active subscriptions have unlimited actions.

        Args:
            user_id: Telegram user ID

        Returns:
            int: Number of remaining free actions (-1 for unlimited/subscribed users)
        """
        try:
            # Check subscription status first
            has_active_subscription = await self._has_active_subscription(user_id)

            # Users with active subscription have unlimited actions
            if has_active_subscription:
                return -1  # -1 indicates unlimited

            current_date = date.today()
            current_count = await self._get_daily_count(user_id, current_date)
            return max(0, self.daily_limit - current_count)
        except Exception as e:
            logging.error(f"Error getting remaining actions for user {user_id}: {e}")
            return 0

    async def reset_user_counter(self, user_id: int) -> bool:
        """
        Reset user's daily counter (admin function).

        Args:
            user_id: Telegram user ID

        Returns:
            bool: True if reset successful
        """
        try:
            current_date = date.today()
            await self._set_counter(user_id, current_date, 0)

            # Clear cache
            if user_id in self._cache:
                del self._cache[user_id]

            return True
        except Exception as e:
            logging.error(f"Error resetting counter for user {user_id}: {e}")
            return False

    async def _get_daily_count(self, user_id: int, current_date: date) -> int:
        """Get current daily count for user."""

        # Check cache first
        if user_id in self._cache:
            cached_data = self._cache[user_id]
            if cached_data['date'] == current_date:
                return cached_data['count']

        # Query database
        query = f"""
            SELECT c_free_actions_count, c_free_actions_date 
            FROM {self.table_name} 
            WHERE c_user_id = $1
        """

        async with self.pool.acquire() as connection:
            result = await connection.fetchrow(query, user_id)

            if not result:
                # User not found, create entry
                await self._create_user_entry(user_id)
                return 0

            db_date = result['c_free_actions_date']
            db_count = result['c_free_actions_count'] or 0

            # If date is different, reset counter
            if not db_date or db_date != current_date:
                await self._set_counter(user_id, current_date, 0)
                return 0

            return db_count

    async def _increment_counter(self, user_id: int, current_date: date, new_count: int):
        """Increment the counter in database."""
        query = f"""
            UPDATE {self.table_name} 
            SET c_free_actions_count = $1, c_free_actions_date = $2 
            WHERE c_user_id = $3
        """

        async with self.pool.acquire() as connection:
            await connection.execute(query, new_count, current_date, user_id)

    async def _set_counter(self, user_id: int, current_date: date, count: int):
        """Set the counter to specific value."""
        query = f"""
            UPDATE {self.table_name} 
            SET c_free_actions_count = $1, c_free_actions_date = $2 
            WHERE c_user_id = $3
        """

        async with self.pool.acquire() as connection:
            await connection.execute(query, count, current_date, user_id)

    async def _create_user_entry(self, user_id: int):
        """Create user entry if doesn't exist."""
        current_date = date.today()
        query = f"""
            INSERT INTO {self.table_name} (c_user_id, c_free_actions_count, c_free_actions_date)
            VALUES ($1, 0, $2)
            ON CONFLICT (c_user_id) DO NOTHING
        """

        async with self.pool.acquire() as connection:
            await connection.execute(query, user_id, current_date)

    async def _has_active_subscription(self, user_id: int) -> bool:
        """
        Check if user has active subscription.

        Args:
            user_id: Telegram user ID

        Returns:
            bool: True if user has active subscription (status 1-2), False otherwise
        """
        try:
            query = f"""
                SELECT c_subscription_status 
                FROM {self.table_name} 
                WHERE c_user_id = $1
            """

            async with self.pool.acquire() as connection:
                result = await connection.fetchrow(query, user_id)

                if not result:
                    # User not found, create entry and return False (no subscription)
                    await self._create_user_entry(user_id)
                    return False

                subscription_status = result['c_subscription_status']

                # Check if subscription is active (status 1 or 2)
                if subscription_status is not None and 0 < subscription_status < 3:
                    return True

                return False

        except Exception as e:
            logging.error(f"Error checking subscription status for user {user_id}: {e}")
            return False  # Default to no subscription on error

    async def get_user_status(self, user_id: int) -> dict:
        """
        Get comprehensive user status including subscription and remaining actions.

        Args:
            user_id: Telegram user ID

        Returns:
            dict: User status information
        """
        try:
            has_subscription = await self._has_active_subscription(user_id)
            remaining_actions = await self.get_remaining_actions(user_id)

            if has_subscription:
                return {
                    'has_subscription': True,
                    'remaining_actions': -1,  # Unlimited
                    'daily_limit': self.daily_limit,
                    'status': 'premium'
                }
            else:
                current_date = date.today()
                used_actions = await self._get_daily_count(user_id, current_date)

                return {
                    'has_subscription': False,
                    'remaining_actions': remaining_actions,
                    'used_actions': used_actions,
                    'daily_limit': self.daily_limit,
                    'status': 'free'
                }

        except Exception as e:
            logging.error(f"Error getting user status for user {user_id}: {e}")
            return {
                'has_subscription': False,
                'remaining_actions': 0,
                'daily_limit': self.daily_limit,
                'status': 'error'
            }

    async def is_action_allowed(self, user_id: int) -> bool:
        """
        Simple check if user can perform action without incrementing counter.
        Useful for UI decisions.

        Args:
            user_id: Telegram user ID

        Returns:
            bool: True if action would be allowed
        """
        try:
            # Check subscription status first
            has_active_subscription = await self._has_active_subscription(user_id)

            if has_active_subscription:
                return True

            current_date = date.today()
            current_count = await self._get_daily_count(user_id, current_date)

            return current_count < self.daily_limit

        except Exception as e:
            logging.error(f"Error in is_action_allowed for user {user_id}: {e}")
            return False



class AsyncNLPTools:
    def __init__(self):
        self._initialized = False
        self._init_task = None

    async def initialize(self):
        if not self._initialized:
            # Run heavy initialization in thread pool
            loop = asyncio.get_event_loop()

            # Download NLTK data and initialize tools
            await loop.run_in_executor(None, self._download_nltk_data)

            # Initialize and warm up LanguageTool
            self.tool = await loop.run_in_executor(
                None, self._init_and_warmup_tool
            )

            self.spell = await loop.run_in_executor(
                None, SpellChecker
            )
            self.nlp = await loop.run_in_executor(
                None, lambda: spacy.load("en_core_web_sm")
            )

            # Initialize gender detector
            self.gender_detector = await loop.run_in_executor(
                None, gender.Detector
            )

            # Initialize NLTK components
            self.lemmatizer = WordNetLemmatizer()
            self.wordnet = wordnet  # Reference to wordnet module
            self.pos_tag = pos_tag  # Reference to pos_tag function

            # Initialize CMU dictionary
            await loop.run_in_executor(None, self._init_cmu_dict)

            # Warm up NLTK components
            await loop.run_in_executor(None, self._warmup_nltk)

            # Warm up gender detector
            await loop.run_in_executor(None, self._warmup_gender_detector)

            self._initialized = True

    def _download_nltk_data(self):
        """Download required NLTK data"""
        try:
            nltk.download('wordnet', quiet=True)
            nltk.download('omw-1.4', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            nltk.download('averaged_perceptron_tagger_eng', quiet=True)
            nltk.download('cmudict', quiet=True)
        except Exception as e:
            print(f"Error downloading NLTK data: {e}")

    def _init_cmu_dict(self):
        """Initialize CMU Pronouncing Dictionary"""
        try:
            from nltk.corpus import cmudict
            self.cmu_dict = cmudict.dict()
            print("CMU Dictionary initialized successfully")
        except Exception as e:
            print(f"Error initializing CMU dictionary: {e}")
            self.cmu_dict = {}  # Fallback to empty dict

    def _init_and_warmup_tool(self):
        """Initialize LanguageTool and perform warm-up check"""
        tool = language_tool_python.LanguageTool('en-US', language_tool_download_version='6.4')
        # Warm-up call
        _ = tool.check("This is a warm-up sentence")
        return tool

    def _warmup_nltk(self):
        """Warm up NLTK components"""
        try:
            # Forces POS tagger to load
            pos_tag(["test"])
            # Forces WordNet to load
            _ = wordnet.synsets("test")
            # Warm up lemmatizer
            self.lemmatizer.lemmatize("running", pos='v')
            # Test CMU dictionary access
            if hasattr(self, 'cmu_dict') and self.cmu_dict:
                _ = self.cmu_dict.get("test", [])
        except Exception as e:
            print(f"Error warming up NLTK: {e}")

    def _warmup_gender_detector(self):
        """Warm up gender detector"""
        try:
            # Test gender detection with common names
            _ = self.gender_detector.get_gender("John")
            _ = self.gender_detector.get_gender("Mary")
            print("Gender detector initialized and warmed up successfully")
        except Exception as e:
            print(f"Error warming up gender detector: {e}")

    async def get_tools(self):
        if not self._initialized:
            await self.initialize()
        return self


class LogonStatusMiddleware(BaseMiddleware):
    def __init__(self, db_pool):
        super().__init__()
        self.db_pool_base, self.db_pool_log = db_pool

    async def __call__(self, handler, event, data: dict):
        # Depending on the type of event (message or callback),
        # call the appropriate pre-processing method

        # print(event.message)
        if event.message is not None:
            await self.on_pre_process_message(event.message, data)
        elif event.callback_query is not None:
            await self.on_pre_process_callback_query(event.callback_query, data)
        # Call the next handler
        return await handler(event, data)

    async def on_pre_process_message(self, message: types.Message, data: dict):
        user_id = message.chat.id
        # Determine action type

        isValid = True
        if message.text and message.text.startswith('/'):
            action = 'command'
            v_comment = message.text
            if v_comment.startswith('/start'): isValid = False
        elif message.text:
            action = 'text_message'
            v_comment = message.text
        elif message.voice:
            action = 'voice_message'
            v_file_size = message.voice.file_size
            v_file_length = message.voice.duration
            v_comment = f"{v_file_size} - {v_file_length}"
        else:
            action = 'unknown_action'
            v_comment = ''
        if isValid: await self.update_logon_status(user_id, action, v_comment)

    async def on_pre_process_callback_query(self, callback_query: types.CallbackQuery, data: dict):
        user_id = callback_query.message.chat.id
        action = 'button_click'
        v_comment = callback_query.data
        await self.update_logon_status(user_id, action, v_comment)

    async def update_logon_status(self, user_id: int, action: str, v_comment: str):

        async with self.db_pool_base.acquire(timeout=5.0) as connection:
            var_query = """
                INSERT INTO t_user_status (c_user_id, c_last_active, c_type, c_text)
                VALUES ($1, CURRENT_TIMESTAMP, $2, $3)
                ON CONFLICT (c_user_id)
                DO UPDATE SET
                    c_last_active = CURRENT_TIMESTAMP,
                    c_type = EXCLUDED.c_type,
                    c_text = EXCLUDED.c_text;
            """
            await connection.execute(var_query, user_id, action, v_comment)

        async with self.db_pool_log.acquire(timeout=5.0) as connection:
            var_query = """
                INSERT INTO t_log (c_log_user_id, c_log_txt, c_log_date, c_log_type, c_log2) 
                VALUES ($1, $2, CURRENT_TIMESTAMP, $3, $4)
            """
            await connection.execute(var_query, user_id, v_comment, 5, action)

            '''
            var_query = """
                UPDATE t_user_status
                SET c_last_active = CURRENT_TIMESTAMP, c_type = $1, c_text = $2
                WHERE c_user_id = $3;
            """
            await connection.execute(var_query, action, v_comment, user_id)

            var_query = """
                INSERT INTO t_user_status (c_user_id, c_last_active, c_type, c_text)
                SELECT $3, CURRENT_TIMESTAMP, $1, $2
                WHERE NOT EXISTS (SELECT 1 FROM t_user_status WHERE c_user_id = $3);
            """
            await connection.execute(var_query, action, v_comment, user_id)
            '''


class ConnPoolMiddleware(BaseMiddleware):
    def __init__(self, pool):
        self.pool = pool

    async def __call__(self, handler, event, data: dict):
        data['pool'] = self.pool
        return await handler(event, data)


class DispatcherMiddleware(BaseMiddleware):
    def __init__(self, dp):
        self.dp = dp

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # Inject dispatcher into handler data
        data["dp"] = self.dp
        return await handler(event, data)


# Separate Free Action Middleware (if you prefer separation of concerns)
class FreeActionMiddleware(BaseMiddleware):
    """Dedicated middleware for free action checking."""

    def __init__(self, db_pool):
        super().__init__()
        self.db_pool = db_pool

        # Configure which actions require free action checking
        self.free_action_callbacks = {
            'w_repeatNext', 'newsppr_st2:mov:'
        }

        self.excluded_callbacks = {
            'start', 'help', 'settings', 'profile', 'subscribe',
            'payment_', 'cancel', 'back', 'menu', 'nav_'
        }

    async def __call__(self, handler, event, data: dict):
        free_counter = data.get('dispatcher').workflow_data.get('free_counter')

        if not free_counter:
            return await handler(event, data)

        user_id = None
        should_check = False

        # Check messages
        if event.message:
            user_id = event.message.chat.id
            should_check = await self._should_check_message(event.message)

        # Check callbacks
        elif event.callback_query:
            user_id = event.callback_query.message.chat.id
            should_check = self._should_check_callback(event.callback_query.data)

        # Perform free action check
        if should_check and user_id:
            is_allowed = await free_counter.check_and_increment(user_id)
            if not is_allowed:
                await self._handle_limit_exceeded(event, free_counter, data)
                return  # Stop processing

        return await handler(event, data)

    def _should_check_callback(self, callback_data: str) -> bool:
        """Check if callback requires free action."""
        if not callback_data:
            return False

        # Skip excluded
        for excluded in self.excluded_callbacks:
            if callback_data.startswith(excluded):
                return False

        # Check patterns
        for pattern in self.free_action_callbacks:
            if pattern.endswith('_') and callback_data.startswith(pattern):
                return True
            elif callback_data == pattern:
                return True

        return False

    async def _should_check_message(self, message: types.Message) -> bool:
        """Check if message requires free action."""
        if message.text and message.text.startswith('/'):
            excluded_commands = ['/start', '/settings', '/menu']
            return not any(message.text.startswith(cmd) for cmd in excluded_commands)

        return bool(message.text or message.voice)

    async def _handle_limit_exceeded(self, event, free_counter, data):
        """Handle limit exceeded for both messages and callbacks."""
        if event.message:
            await self._send_limit_message(free_counter, event.message, data)
        elif event.callback_query:
            await self._send_limit_message(free_counter, event.callback_query.message, data)
            #await self._send_limit_callback(event.callback_query, free_counter)

    async def _send_limit_message(self, free_counter, message_obj, data):     #message: types.Message,        =None, callback_obj=None
        vUserID = message_obj.chat.id
        user_status = await free_counter.get_user_status(vUserID)
        bot = message_obj.bot
        state = data.get('state')

        if user_status['has_subscription']:
            # This shouldn't happen, but just in case
            return

        #remaining = await free_counter.get_remaining_actions(message.chat.id)
        str_Msg = (
            f'🚫 <b>Вы временно исчерпали лимит запросов!</b>\n\n'
            f'🌱 Предлагаем оформить <b>безлимитную подписку!</b>\n'
        )

        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('tariff'), callback_data="vA_st5_2"))

        msg = await message_obj.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        await myF.fSubMsgDel(state, self.db_pool, vUserID, message_obj.message_id, msg.message_id, bot, 2)

    async def _send_limit_callback(self, callback: types.CallbackQuery, free_counter):
        vUserID = callback.message.chat.id
        user_status = await free_counter.get_user_status(vUserID)
        bot = callback.message.bot

        if user_status['has_subscription']:
            # This shouldn't happen, but just in case
            return

        #await callback.answer("Daily limit exceeded! Subscribe for unlimited access!", show_alert=True)
        str_Msg = (
            f'🚫 <b>Вы временно исчерпали лимит запросов!</b>\n\n'
            f'🌱 Предлагаем оформить <b>безлимитную подписку!</b>\n'
        )

        builder = InlineKeyboardBuilder()
        builder.add(types.InlineKeyboardButton(text=myF.fCSS('tariff'), callback_data="vA_st5_2"))

        msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)
        await myF.fSubMsgDel(state, self.db_pool, vUserID, callback.message.message_id, msg.message_id, bot, 2)



