from datetime import datetime, date, timezone, timedelta

print("import Start:", datetime.now().time().strftime("%H:%M:%S"))
from telethon import TelegramClient, events, errors
from telethon.tl.custom import Button
from telethon.tl.types import InputPeerUser
from telethon.errors import UserIsBlockedError
import time
import asyncio
import re
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.state import StatesGroup, State
import redis.asyncio as aioredis  # This provides async Redis support
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
import sys, os
import random
import json
import pickle

# import random

# import aioredis
import pytz
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

# custom functions
import fpgDB as pgDB
import selfFunctions as myF
import rmndr_msg as myRemn
from config_reader import config
from states import myState

print("import End:", datetime.now().time().strftime("%H:%M:%S"))


#class myState(StatesGroup):
#    reminder = State()
#    words = State()


api_id = config.TG_API_ID.get_secret_value()
api_hash = config.TG_API_HASH.get_secret_value()
bot_token = config.bot_token.get_secret_value()



bot_id = int(bot_token.split(":")[0])

bot = TelegramClient('reminder', api_id, api_hash, timeout=20).start(bot_token=bot_token)


class ReminderType(Enum):
    NEWS_ARTICLE = 1
    QUIZ_SLANG = 2
    WORD_REPEAT = 3
    SPEAKING_PRACTICE = 4
    ACTIVITY_CHECK = 5  # NEW - первичная проверка активности
    ACTIVITY_RECHECK = 6  # NEW - повторная проверка через месяц
    # GRAMMAR_EXERCISE = 5
    # VOCABULARY_REVIEW = 6


@dataclass
class ReminderConfig:
    reminder_type: ReminderType
    local_time: str  # Format: "HH:MM"
    title: str
    description: str
    is_active: bool = True


@dataclass
class UserReminder:
    user_id: int
    reminder_type: ReminderType
    scheduled_time: datetime
    timezone: str
    last_sent: Optional[datetime] = None


class EnhancedReminderSystem:
    def __init__(self, pool, storage, bot):
        self.pool = pool
        self.storage = storage
        self.bot = bot

        # Centralized reminder configuration
        self.reminder_configs: Dict[ReminderType, ReminderConfig] = {
            ReminderType.NEWS_ARTICLE: ReminderConfig(
                ReminderType.NEWS_ARTICLE,
                "08:00",
                "📰 Morning News",
                "Start your day with fresh news articles!",
                is_active=False
            ),
            ReminderType.QUIZ_SLANG: ReminderConfig(
                ReminderType.QUIZ_SLANG,        #AJRM
                "09:00",
                "🧠 Midday Quiz",
                "Test your knowledge with today's quiz!"
            ),
            ReminderType.WORD_REPEAT: ReminderConfig(
                ReminderType.WORD_REPEAT,
                "18:00",
                "📚 Evening Word Practice",
                "Review and practice your vocabulary!",
                is_active=False
            ),
            ReminderType.SPEAKING_PRACTICE: ReminderConfig(
                ReminderType.SPEAKING_PRACTICE,
                "21:00",
                "🗣️ Speaking Practice",
                "Time to practice your speaking skills!",
                is_active=False
            ),
            ReminderType.ACTIVITY_CHECK: ReminderConfig(
                ReminderType.ACTIVITY_CHECK,
                "07:00",  # Проверка активности в 7:00
                "👋 Activity Check",
                "Check user activity and send re-engagement message",
                is_active=False
            ),
            ReminderType.ACTIVITY_RECHECK: ReminderConfig(
                ReminderType.ACTIVITY_RECHECK,
                "07:00",  # Повторная проверка в 7:00
                "👋 Activity Re-check",
                "Re-check user activity after timeout",
                is_active=False
            ),
        }

    async def get_inactive_users(self) -> List[Tuple[int, str, datetime]]:
        """
        Получить пользователей, неактивных последние 2 дня с подпиской = 3

        Returns:
            List[Tuple[user_id, timezone, last_active]]
        """
        pool_base, _ = self.pool

        query = """
        SELECT 
            t1.c_user_id,
            COALESCE(t2.c_timezone::text, '180') as timezone,
            t3.c_last_active
        FROM t_user t1
        LEFT JOIN t_user_paramssingle t2 ON t1.c_user_id = t2.c_ups_user_id
        INNER JOIN t_user_status t3 ON t1.c_user_id = t3.c_user_id
        WHERE 
            t1.c_subscription_status = 3
            AND t3.c_last_active < NOW() - INTERVAL '2 days'
        ORDER BY t1.c_user_id;
        """

        return await pgDB.fExec_SelectQuery(pool_base, query)

    async def get_timeout_users_for_recheck(self) -> List[Tuple[int, str, datetime]]:
        """
        Получить пользователей в статусе timeout (9),
        у которых прошло 28 дней (месяц - 2 дня) с момента установки статуса

        Returns:
            List[Tuple[user_id, timezone, timeout_date]]
        """
        pool_base, _ = self.pool

        query = """
        SELECT 
            t1.c_user_id,
            COALESCE(t2.c_timezone::text, '180') as timezone,
            t1.c_subscription_date
        FROM t_user t1
        LEFT JOIN t_user_paramssingle t2 ON t1.c_user_id = t2.c_ups_user_id
        WHERE 
            t1.c_subscription_status = 9
            AND t1.c_subscription_date < NOW() - INTERVAL '28 days'
        ORDER BY t1.c_user_id;
        """

        return await pgDB.fExec_SelectQuery(pool_base, query)

    async def update_user_subscription_status(self, user_id: int, new_status: int) -> bool:
        """
        Обновить статус подписки пользователя

        Args:
            user_id: ID пользователя
            new_status: Новый статус (9 - timeout, 3 - active, 0 - paused)

        Returns:
            bool: Успешность операции
        """
        pool_base, _ = self.pool

        query = """
        UPDATE t_user 
        SET 
            c_subscription_status = $1,
            c_subscription_date = NOW()
        WHERE c_user_id = $2
        RETURNING c_user_id;
        """

        try:
            result = await pgDB.fExec_UpdateQuery(pool_base, query, new_status, user_id)
            return result is not None
        except Exception as e:
            print(f"Failed to update subscription status for user {user_id}: {e}")
            return False

    async def was_activity_check_sent_today(self, user_id: int, check_type: str = "initial") -> bool:
        """
        Проверить, отправлялось ли сообщение о проверке активности сегодня

        Args:
            check_type: "initial" для первичной проверки, "recheck" для повторной
        """
        redis_key = f"activity_check_sent:{check_type}:{user_id}:{datetime.utcnow().strftime('%Y-%m-%d')}"

        try:
            redis_client = self.storage.redis
            result = await redis_client.get(redis_key)
            return result is not None
        except:
            return False

    async def mark_activity_check_as_sent(self, user_id: int, check_type: str = "initial"):
        """
        Отметить, что сообщение о проверке активности отправлено

        Args:
            check_type: "initial" для первичной проверки, "recheck" для повторной
        """
        redis_key = f"activity_check_sent:{check_type}:{user_id}:{datetime.utcnow().strftime('%Y-%m-%d')}"

        try:
            redis_client = self.storage.redis
            # Хранить 25 часов для гарантии
            await redis_client.setex(redis_key, 90000, "sent")
        except Exception as e:
            print(f"Failed to mark activity check as sent: {e}")

    async def send_activity_check_reminder(self, user_id: int) -> bool:
        """
        Отправить ПЕРВИЧНОЕ сообщение о проверке активности неактивному пользователю
        """
        try:
            user_entity = await self.bot.get_entity(user_id)

            vAddress = myF.get_address2user(user_entity.first_name)

            str_Msg = (
                f"👋 <b>{vAddress}</b>\n\n"
                f"Мы заметили, что вы не пользовались ботом последние пару дней.\n\n"
                f"🤔 <b>Если вам по-прежнему актуальны наши уведомления</b> - "
                f"нажмите кнопку <b>\"Продолжить\"</b> ниже.\n\n"
                f"😴 <b>Если уведомления сейчас неактуальны</b> - мы не хотим вас спамить! "
                f"Нажмите <b>\"Приостановить\"</b>, и мы временно прекратим отправку.\n\n"
                f"💡 Вы всегда сможете вернуться к обучению позже через меню бота."
            )

            buttonArr = [
                [Button.inline('✅ Продолжить', b"activity_continue")],
                #[Button.inline('⏸️ Приостановить', b"activity_pause")],
                [Button.inline(myF.fCSS('menu'), b"menu")]
            ]

            sent_message = await self.bot.send_message(
                user_entity,
                str_Msg,
                buttons=buttonArr,
                parse_mode='html'
            )

            # Обновляем статус на "timeout" (9)
            success = await self.update_user_subscription_status(user_id, 9)

            if success:
                await self.mark_activity_check_as_sent(user_id, "initial")
                await self.log_reminder_sent(
                    user_id,
                    ReminderType.ACTIVITY_CHECK,
                    "Initial activity check sent, status set to 9 (timeout)"
                )
                print(f"✅ Sent initial activity check to user {user_id}, status -> 9")
                return True
            else:
                print(f"❌ Failed to update status for user {user_id}")
                return False

        except Exception as e:
            print(f"❌ Failed to send activity check to user {user_id}: {e}")
            await self.log_reminder_sent(
                user_id,
                ReminderType.ACTIVITY_CHECK,
                f"Failed: {str(e)}"
            )
            return False

    async def send_activity_recheck_reminder(self, user_id: int) -> bool:
        """
        Отправить ПОВТОРНОЕ сообщение о проверке активности
        (через месяц-2 дня после timeout)
        """
        try:
            user_entity = await self.bot.get_entity(user_id)

            vAddress = myF.get_address2user(user_entity.first_name)

            str_Msg = (
                f"👋 <b>{vAddress} Привет! Давно не виделись.</b>\n\n"
                f"🌟 Мы скучали! Как насчет того, чтобы вернуться к изучению английского?\n\n"
                f"📚 <b>Получится продолжить обучение?</b>\n"
                f"За это время у нас появились новые статьи, квизы и упражнения!\n\n"
                f"Нажмите <b>\"Продолжить\"</b>, чтобы возобновить уведомления, "
                f"или <b>\"Приостановить\"</b>, если сейчас не подходящее время.\n\n"
                f"💪 Мы верим в вас!"
            )

            buttonArr = [
                [Button.inline('✅ Продолжить', b"activity_continue")],
                [Button.inline('⏸️ Приостановить', b"activity_pause")],
                [Button.inline(myF.fCSS('menu'), b"menu")]
            ]

            sent_message = await self.bot.send_message(
                user_entity,
                str_Msg,
                buttons=buttonArr,
                parse_mode='html'
            )

            # Статус остается 9, просто отправляем повторное напоминание
            await self.mark_activity_check_as_sent(user_id, "recheck")
            await self.log_reminder_sent(
                user_id,
                ReminderType.ACTIVITY_RECHECK,
                "Recheck activity reminder sent (28 days after timeout)"
            )
            print(f"✅ Sent recheck activity reminder to user {user_id}")
            return True

        except Exception as e:
            print(f"❌ Failed to send recheck reminder to user {user_id}: {e}")
            await self.log_reminder_sent(
                user_id,
                ReminderType.ACTIVITY_RECHECK,
                f"Failed: {str(e)}"
            )
            return False

    async def should_send_activity_check(self, user_id: int, user_timezone: str) -> bool:
        """
        Проверить, нужно ли отправлять проверку активности этому пользователю
        в текущее время (7:00 по местному времени)

        Args:
            user_id: ID пользователя
            user_timezone: Часовой пояс пользователя (минуты)

        Returns:
            bool: True если нужно отправить сообщение
        """
        # Получаем конфигурацию для activity check
        config = self.reminder_configs[ReminderType.ACTIVITY_CHECK]

        # Рассчитываем время отправки (7:00 по местному времени)
        try:
            minutes_offset = int(user_timezone)
            tz = pytz.FixedOffset(minutes_offset)
        except:
            tz = pytz.FixedOffset(180)  # UTC+3 по умолчанию

        # Текущее время пользователя
        user_now = datetime.now(tz)

        # Целевое время отправки (7:00)
        hour, minute = map(int, config.local_time.split(':'))
        target_time = user_now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # Проверяем, находимся ли мы в окне ±10 минут от 7:00
        time_diff = (user_now - target_time).total_seconds()

        # В пределах окна отправки?
        if -600 <= time_diff <= 600:
            # Уже отправляли сегодня?
            return not await self.was_activity_check_sent_today(user_id, "initial")

        return False

    async def should_send_activity_recheck(self, user_id: int, user_timezone: str) -> bool:
        """
        Проверить, нужно ли отправлять повторную проверку активности
        в текущее время (7:00 по местному времени)
        """
        config = self.reminder_configs[ReminderType.ACTIVITY_RECHECK]

        try:
            minutes_offset = int(user_timezone)
            tz = pytz.FixedOffset(minutes_offset)
        except:
            tz = pytz.FixedOffset(180)

        user_now = datetime.now(tz)
        hour, minute = map(int, config.local_time.split(':'))
        target_time = user_now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        time_diff = (user_now - target_time).total_seconds()

        if -600 <= time_diff <= 600:
            return not await self.was_activity_check_sent_today(user_id, "recheck")

        return False

    async def process_activity_checks(self):
        """
        Обработать ПЕРВИЧНЫЕ проверки активности
        Вызывается в основном цикле напоминаний
        """
        print(f"🔍 Checking for inactive users (initial check) at {datetime.utcnow()}")

        try:
            # Получаем список неактивных пользователей
            inactive_users = await self.get_inactive_users()

            if not inactive_users:
                print("ℹ️ No inactive users found for initial check")
                return

            print(f"📋 Found {len(inactive_users)} potentially inactive users")

            # Проверяем каждого пользователя
            sent_count = 0
            for user_id, timezone, last_active in inactive_users:
                # Проверяем, нужно ли отправлять сейчас (7:00 по местному времени)
                if await self.should_send_activity_check(user_id, timezone):
                    success = await self.send_activity_check_reminder(user_id)
                    if success:
                        sent_count += 1
                    await asyncio.sleep(0.5)  # Небольшая задержка между отправками

            if sent_count > 0:
                print(f"✅ Sent {sent_count} initial activity check messages")

        except Exception as e:
            print(f"❌ Error in initial activity check process: {e}")

    async def process_activity_rechecks(self):
        """
        Обработать ПОВТОРНЫЕ проверки активности
        (для пользователей в timeout более 28 дней)
        """
        print(f"🔍 Checking for timeout users (recheck) at {datetime.utcnow()}")

        try:
            # Получаем пользователей в timeout более 28 дней
            timeout_users = await self.get_timeout_users_for_recheck()

            if not timeout_users:
                print("ℹ️ No timeout users found for recheck")
                return

            print(f"📋 Found {len(timeout_users)} timeout users for recheck")

            # Проверяем каждого пользователя
            sent_count = 0
            for user_id, timezone, timeout_date in timeout_users:
                # Проверяем, нужно ли отправлять сейчас (7:00 по местному времени)
                if await self.should_send_activity_recheck(user_id, timezone):
                    success = await self.send_activity_recheck_reminder(user_id)
                    if success:
                        sent_count += 1
                    await asyncio.sleep(0.5)

            if sent_count > 0:
                print(f"✅ Sent {sent_count} recheck activity messages")

        except Exception as e:
            print(f"❌ Error in recheck activity process: {e}")

    async def get_users_with_timezones(self) -> List[Tuple[int, str]]:
        """Get all active users with their timezones, excluding recently active users"""
        pool_base, _ = self.pool
        #AJRM
        query = """
        SELECT DISTINCT 
            t1.c_user_id,
            COALESCE(t2.c_timezone::text, '180') as timezone
        FROM t_user t1
        LEFT JOIN t_user_paramssingle t2 ON t1.c_user_id = t2.c_ups_user_id 
        LEFT JOIN t_user_status t3 ON t1.c_user_id = t3.c_user_id
        WHERE 
            t1.c_subscription_status IN (1, 2, 3)
            AND (t3.c_last_active IS NULL OR t3.c_last_active < NOW() - INTERVAL '15 minutes') 
            AND t1.c_segment IS NOT NULL AND t1.c_segment NOT IN ('speakpal', 'befstories') 
        ORDER BY t1.c_user_id;
        """
        #AND t1.c_user_id = 372671079

        return await pgDB.fExec_SelectQuery(pool_base, query)

    def calculate_user_reminder_times(self, user_timezone: str) -> List[UserReminder]:
        """Calculate reminder times for a user based on their timezone"""
        user_reminders = []
        current_utc = datetime.utcnow()

        try:
            # Convert minutes offset string to integer, then to pytz timezone
            minutes_offset = int(user_timezone)
            tz = pytz.FixedOffset(minutes_offset)
            #print('try tz - ', tz)
        except:
            # tz = pytz.UTC  # Fallback to UTC if timezone is invalid
            # Fallback to UTC+3 if timezone is invalid
            tz = pytz.FixedOffset(180)  # UTC+3
            #print('except tz - ', tz)

        for reminder_type, config in self.reminder_configs.items():
            if not config.is_active:
                continue

            # Parse local time
            hour, minute = map(int, config.local_time.split(':'))

            # Create today's reminder time in user's timezone
            user_now = datetime.now(tz)
            reminder_local = user_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            #print('Create today reminder time in user timezone| user_now - ', user_now, ' | reminder_local - ', reminder_local)

            # If reminder time has passed today, schedule for tomorrow
            if reminder_local <= user_now:
                reminder_local += timedelta(days=1)

            # Convert to UTC for storage/comparison
            reminder_utc = reminder_local.utctimetuple()
            reminder_utc_dt = datetime(*reminder_utc[:6])

            user_reminders.append(UserReminder(
                user_id=0,  # Will be set later
                reminder_type=reminder_type,
                scheduled_time=reminder_utc_dt,
                timezone=user_timezone
            ))

        return user_reminders

    async def get_due_reminders(self) -> List[UserReminder]:
        """Get all reminders that are due to be sent"""
        users_with_timezones = await self.get_users_with_timezones()
        #print('users_with_timezones - ', users_with_timezones)
        due_reminders = []
        current_utc = datetime.utcnow()

        for user_id, timezone in users_with_timezones:
            user_reminders = self.calculate_user_reminder_times(timezone)
            #print('user_reminders - ', user_reminders)

            for reminder in user_reminders:
                reminder.user_id = user_id

                # Check if reminder is due (within the last 10 minutes to current time)
                time_diff = (current_utc - reminder.scheduled_time).total_seconds()
                #print('user_id - ', user_id, ' | reminder - ', reminder, ' |time_diff - ', time_diff)

                # Reminder is due if it's between -600 seconds (10 min future) and 600 seconds (10 min past)
                if -600 <= time_diff <= 600:
                    #print(user_id, 'success')
                    # Check if we haven't sent this reminder today
                    if not await self.was_reminder_sent_today(user_id, reminder.reminder_type):
                        due_reminders.append(reminder)

        return due_reminders

    async def was_reminder_sent_today(self, user_id: int, reminder_type: ReminderType) -> bool:
        """Check if a specific reminder was already sent today"""
        redis_key = f"reminder_sent:{user_id}:{reminder_type.value}:{datetime.utcnow().strftime('%Y-%m-%d')}"

        try:
            redis_client = self.storage.redis
            result = await redis_client.get(redis_key)
            return result is not None
        except:
            return False

    async def mark_reminder_as_sent(self, user_id: int, reminder_type: ReminderType):
        """Mark a reminder as sent for today"""
        redis_key = f"reminder_sent:{user_id}:{reminder_type.value}:{datetime.utcnow().strftime('%Y-%m-%d')}"

        try:
            redis_client = self.storage.redis
            # Set with expiration of 25 hours to ensure cleanup
            await redis_client.setex(redis_key, 90000, "sent")  # 25 hours
        except Exception as e:
            print(f"Failed to mark reminder as sent: {e}")

    async def clear_reminder_storage(self):
        """Clear all reminder-related keys from Redis storage (for testing purposes)"""
        try:
            redis_client = self.storage.redis

            # Find all keys that match the reminder pattern
            arr_pattern = ["reminder_sent:*", "daily_news_data:*", "daily_quiz_data:*"]
            for pattern in arr_pattern:
                keys = await redis_client.keys(pattern)

                if keys:
                    # Delete all matching keys
                    deleted_count = await redis_client.delete(*keys)
                    print(f"Cleared {deleted_count} reminder keys from Redis storage for {pattern}")
                else:
                    print(f"No reminder keys found to clear for {pattern}")

        except Exception as e:
            print(f"Failed to clear reminder storage: {e}")

    async def send_news_reminder(self, user_id: int):
        """Send news article reminder using cached data"""
        try:
            user_entity = await self.bot.get_entity(user_id)

            # Remove previous keyboard
            await myF.fRemoveReplyKB(use_telethon=True, bot=self.bot, chat_id=user_id)

            # Get cached news data instead of querying database
            cached_news = await self.get_cached_news_data()
            if not cached_news:
                print(f"❌ No cached news data available for user {user_id}")
                return False

            var_Arr = cached_news['var_Arr']
            isNext = cached_news['isNext']
            vLevel = cached_news['vLevel']
            vOffset = cached_news['vOffset']

            if not var_Arr:
                return False

            # Format the message
            vTitle = var_Arr[0][0]
            vSummary = var_Arr[0][2]
            vEmoji = var_Arr[0][3]
            vDate = var_Arr[0][4]
            vTitle_ru = var_Arr[0][5]

            vAddress = myF.get_address2user(user_entity.first_name)
            str_Msg = (
                f"<b>{vAddress} Let’s have some reading practice</b>\n"
                f"Here’s an article for you to explore:\n\n"
                f'{vEmoji} <b>{vTitle}</b>\n{vSummary}\n\n'
                f"Tap the button below to start reading!"
            )

            buttonArr = [
                [Button.inline('Read more ❱❱', b"newsppr_st2_1")],
                [Button.inline(myF.fCSS('menu'), b"menu")]
            ]

            sent_message = await self.bot.send_message(
                user_entity,
                str_Msg,
                buttons=buttonArr,
                parse_mode='html'
            )
            #await myF.fSubMsgDel(None, self.pool, user_id, '', sent_message.id, bot, 3, vClient=1)  # очистка предыдущих

            # Get FSM state and data
            key = StorageKey(bot_id=bot_id, chat_id=user_id, user_id=user_id)
            state = FSMContext(storage=self.storage, key=key)

            await state.update_data(arrNewsTitle=var_Arr)
            await state.update_data(vLevel=vLevel)
            await state.update_data(vOffset=vOffset)

            await self.log_reminder_sent(user_id, ReminderType.NEWS_ARTICLE, "News reminder sent")
            return True

        except Exception as e:
            print(f"Failed to send news reminder to user {user_id}: {e}")
            return False

    # NEW METHOD: Cache news data in Redis
    async def cache_daily_news_data(self) -> bool:
        """Cache news data in Redis for the day to avoid repeated DB calls"""
        today = datetime.utcnow().strftime('%Y-%m-%d')
        redis_key = f"daily_news_data:{today}"

        try:
            redis_client = self.storage.redis

            # Check if news data already exists in cache
            cached_data = await redis_client.get(redis_key)
            if cached_data:
                print("📰 News data already cached for today")
                return True

            # Fetch news data from database
            pool_base, _ = self.pool
            vOffset = 0
            vLevel = 3

            var_Arr, isNext = await myF.fGetNewsQuery(pool_base, vLevel, vOffset, s_reminder = 2)       #LingoMojo
            #var_Arr, isNext = await myF.fGetNewsQuery(pool_base, vLevel, vOffset, s_reminder = 3)      #speakpal

            if not var_Arr:
                print("❌ No news data available")
                return False

            # get article ID and set c_reminder to 1 (status is used)
            await myF.set_news_reminded(pool_base, int(var_Arr[0][1]))      #LingoMojo
            #await myF.set_news_reminded_sp(pool_base, int(var_Arr[0][1]))       #speakpal

            # Prepare data for caching
            news_cache_data = {
                'var_Arr': var_Arr,
                'isNext': isNext,
                'vLevel': vLevel,
                'vOffset': vOffset,
                'cached_at': datetime.utcnow().isoformat()
            }

            # Cache the data (expire at end of day + 1 hour buffer)
            # Calculate seconds until tomorrow + 1 hour
            tomorrow = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1, hours=1)
            seconds_until_expire = int((tomorrow - datetime.utcnow()).total_seconds())

            # Store as JSON string
            await redis_client.setex(
                redis_key,
                seconds_until_expire,
                json.dumps(news_cache_data, default=str)
            )

            print(f"📰 Cached news data for {today}, expires in {seconds_until_expire} seconds")
            return True

        except Exception as e:
            print(f"❌ Failed to cache news data: {e}")
            return False

    # NEW METHOD: Get cached news data
    async def get_cached_news_data(self) -> Optional[Dict]:
        """Retrieve cached news data from Redis"""
        today = datetime.utcnow().strftime('%Y-%m-%d')
        redis_key = f"daily_news_data:{today}"

        try:
            redis_client = self.storage.redis
            cached_data = await redis_client.get(redis_key)

            if cached_data:
                return json.loads(cached_data)
            else:
                print("📰 No cached news data found")
                return None

        except Exception as e:
            print(f"❌ Failed to retrieve cached news data: {e}")
            return None

    async def send_quiz_reminder(self, user_id: int):
        """Send quiz reminder using cached data"""
        try:
            user_entity = await self.bot.get_entity(user_id)
            #print('user_entity - ', user_entity)

            # Get cached quiz data instead of querying database
            cached_quiz = await self.get_cached_quiz_data()
            if not cached_quiz:
                print(f"❌ No cached quiz data available for user {user_id}")
                return False

            arrRes = cached_quiz['arrRes']
            if not arrRes:
                return False

            vExample = arrRes[0]
            vTopic = arrRes[5]
            vObj = arrRes[6]
            optionTrue = arrRes[1]


            # Prepare quiz options
            numTrue = random.choice([1, 2, 3, 4])

            #print(f'-----------------------numTrue - {numTrue}')
            arrOptions = [arrRes[2], arrRes[3], arrRes[4]]
            random.shuffle(arrOptions)
            #print(f'-----------------------arrOptions bef - {arrOptions}')
            arrOptions.insert(numTrue-1, optionTrue)
            #print(f'-----------------------arrOptions aft - {arrOptions}')

            # Generate quiz buttons
            quiz_labels = [f'quiz_{i}{"t" if i == numTrue else "f"}' for i in range(1, 5)]
            option_labels = ['🅐', '🅑', '🅒', '🅓']
            #print(f'-----------------------quiz_labels - {quiz_labels}')

            buttons = [
                Button.inline(option_labels[i], quiz_labels[i].encode())
                for i in range(4)
            ]
            buttonArr = [buttons[:2], buttons[2:]]

            vAddress = myF.get_address2user(user_entity.first_name)

            #AJRM
            str_Msg = (
                f'{vAddress} Let’s have {vTopic} quiz\n\n'
                f'<b>🧐  What does this expression mean?</b>\n'
                f'💬 {vObj}\n\n'
                f'<b>📖 Example:</b> <i>{vExample}</i>\n\n'
                f'<b>Choose your answer:</b>\n'
                f'🅐 {arrOptions[0]}\n'
                f'🅑 {arrOptions[1]}\n'
                f'🅒 {arrOptions[2]}\n'
                f'🅓 {arrOptions[3]}'
            )

            sent_message = await self.bot.send_message(
                user_entity,
                str_Msg,
                buttons=buttonArr,
                parse_mode='html'
            )

            #await myF.fSubMsgDel(None, self.pool, user_id, '', sent_message.id, bot, 3, vClient=1)  # очистка предыдущих
            await self.log_reminder_sent(user_id, ReminderType.QUIZ_SLANG, "Quiz reminder sent")
            return True

        except Exception as e:
            print(f"Failed to send quiz reminder to user {user_id}: {e}")
            return False

    # NEW METHOD: Cache quiz data in Redis
    async def cache_daily_quiz_data(self) -> bool:
        """Cache quiz data in Redis for the day"""
        today = datetime.utcnow().strftime('%Y-%m-%d')
        redis_key = f"daily_quiz_data:{today}"

        try:
            redis_client = self.storage.redis

            # Check if quiz data already exists in cache
            cached_data = await redis_client.get(redis_key)
            if cached_data:
                print("🧠 Quiz data already cached for today")
                return True

            # Fetch quiz data from database
            vDate = datetime.now().strftime('%y%m%d')
            arrRes = await myF.getRmndrPost(vDate, self.pool)

            if not arrRes:
                print("❌ No quiz data available")
                return False

            # Prepare data for caching
            quiz_cache_data = {
                'arrRes': arrRes,
                'cached_at': datetime.utcnow().isoformat()
            }

            # Calculate seconds until tomorrow + 1 hour
            tomorrow = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1, hours=1)
            seconds_until_expire = int((tomorrow - datetime.utcnow()).total_seconds())

            # Store as JSON string
            await redis_client.setex(
                redis_key,
                seconds_until_expire,
                json.dumps(quiz_cache_data, default=str)
            )

            print(f"🧠 Cached quiz data for {today}")
            return True

        except Exception as e:
            print(f"❌ Failed to cache quiz data: {e}")
            return False

    # NEW METHOD: Get cached quiz data
    async def get_cached_quiz_data(self) -> Optional[Dict]:
        """Retrieve cached quiz data from Redis"""
        today = datetime.utcnow().strftime('%Y-%m-%d')
        redis_key = f"daily_quiz_data:{today}"

        try:
            redis_client = self.storage.redis
            cached_data = await redis_client.get(redis_key)

            if cached_data:
                return json.loads(cached_data)
            else:
                print("🧠 No cached quiz data found")
                return None

        except Exception as e:
            print(f"❌ Failed to retrieve cached quiz data: {e}")
            return None




    async def send_word_repeat_reminder(self, user_id: int):
        """Send word repetition reminder"""
        #build a sentence
        try:
            pool_base, _ = self.pool
            # Set FSM state
            key = StorageKey(bot_id=bot_id, chat_id=user_id, user_id=user_id)
            state = FSMContext(storage=self.storage, key=key)
            await state.set_state(myState.words)

            user_entity = await self.bot.get_entity(user_id)
            print('user_entity - ', user_entity)
            # get 4 words
            v_words = await myF.fGetLearnWords(user_id, pool_base, 4)
            print('v_words - ', v_words)
            vAddress = myF.get_address2user(user_entity.first_name)
            str_Msg = (
                f"{vAddress} Let's play a 🧱 Build-a-Sentence game!\n\n"
                f'Придумайте предложение или короткую историю из 4х изучаемых слов:\n'
                f'<b>{v_words}</b>\n\n'
                f'P.S. запишите голосовое или введите с клавиатуры текстом \n👇'
            )

            #builder.add(types.InlineKeyboardButton(text=myF.fCSS('menu'), callback_data="menu"))

            # send a message
            #msg = await callback.message.answer(str_Msg, reply_markup=builder.as_markup(), parse_mode=ParseMode.HTML)



            buttonArr = [
                #[Button.inline(myF.fCSS('bas'), b"w_bas")],
                [Button.inline(myF.fCSS('menu'), b"menu")]
            ]



            sent_message = await self.bot.send_message(
                user_entity,
                str_Msg,
                buttons=buttonArr,
                parse_mode='html'
            )
            #await myF.fSubMsgDel(None, self.pool, user_id, '', sent_message.id, bot, 3, vClient=1)  # очистка предыдущих
            # Get FSM state and data
            key = StorageKey(bot_id=bot_id, chat_id=user_id, user_id=user_id)
            state = FSMContext(storage=self.storage, key=key)
            await state.update_data(bas_words=v_words)
            await self.log_reminder_sent(user_id, ReminderType.WORD_REPEAT, "Word practice reminder sent")
            return True

        except Exception as e:
            print(f"Failed to send word reminder to user {user_id}: {e}")
            return False

    async def send_speaking_reminder(self, user_id: int):
        """Send speaking practice reminder"""
        try:
            user_entity = await self.bot.get_entity(user_id)

            buttonArr = [
                [Button.inline(myF.fCSS('speak'), b"speak")],
                [Button.inline(myF.fCSS('menu'), b"menu")]
            ]

            vAddress = myF.get_address2user(user_entity.first_name)
            message = (
                f"🗣️ <b>{vAddress} Time for Speaking Practice!</b>\n\n"
                "Build confidence and fluency through regular speaking exercises.\n"
                "💪 Build speaking confidence\n"
                "🗣️ Improve fluency\n\n"
                "Tap the button below and have a talk \n👇"
            )

            sent_message = await self.bot.send_message(
                user_entity,
                message,
                buttons=buttonArr,
                parse_mode='html'
            )
            # await myF.fSubMsgDel(None, self.pool, user_id, '', sent_message.id, bot, 3, vClient=1)  # очистка предыдущих
            await self.log_reminder_sent(user_id, ReminderType.SPEAKING_PRACTICE, "Speaking reminder sent")
            return True

        except Exception as e:
            print(f"Failed to send speaking reminder to user {user_id}: {e}")
            return False

    async def log_reminder_sent(self, user_id: int, reminder_type: ReminderType, message: str):
        """Log reminder activity"""
        try:
            _, pool_log = self.pool
            await pgDB.fExec_LogQuery(pool_log, user_id, f"Reminder|{reminder_type}|{message}", 1)
        except Exception as e:
            print(f"Failed to log reminder: {e}")

    async def process_reminder(self, reminder: UserReminder) -> bool:
        """Process a single reminder"""
        success = False

        try:
            # Set FSM state
            key = StorageKey(bot_id=bot_id, chat_id=reminder.user_id, user_id=reminder.user_id)
            state = FSMContext(storage=self.storage, key=key)
            await state.set_state(myState.reminder)

            # Send appropriate reminder based on type
            if reminder.reminder_type == ReminderType.NEWS_ARTICLE:
                success = await self.send_news_reminder(reminder.user_id)
            elif reminder.reminder_type == ReminderType.QUIZ_SLANG:
                success = await self.send_quiz_reminder(reminder.user_id)
            elif reminder.reminder_type == ReminderType.WORD_REPEAT:
                success = await self.send_word_repeat_reminder(reminder.user_id)
            elif reminder.reminder_type == ReminderType.SPEAKING_PRACTICE:
                success = await self.send_speaking_reminder(reminder.user_id)

            if success:
                await self.mark_reminder_as_sent(reminder.user_id, reminder.reminder_type)
                print(f"✅ Sent {reminder.reminder_type} reminder to user {reminder.user_id}")

        except Exception as e:
            print(f"❌ Failed to process reminder for user {reminder.user_id}: {e}")
            await self.log_reminder_sent(reminder.user_id, reminder.reminder_type, f"Failed: {str(e)}")

        return success

    # UPDATED METHOD: Cache data before processing reminders
    async def run_reminder_cycle(self):
        """Main reminder processing cycle with data caching optimization"""
        print(f"🔄 Checking for due reminders at {datetime.utcnow()}")

        try:
            # 1. Обрабатываем первичные проверки активности
            #await self.process_activity_checks()

            # 2. Обрабатываем повторные проверки активности
            #await self.process_activity_rechecks()

            # 3. Обрабатываем обычные напоминания
            due_reminders = await self.get_due_reminders()

            if not due_reminders:
                print("ℹ️ No reminders due at this time")
                return

            print(f"📨 Found {len(due_reminders)} due reminders")

            # Pre-cache data for reminder types that will be sent
            reminder_types_needed = set(r.reminder_type for r in due_reminders)

            cache_tasks = []
            if ReminderType.NEWS_ARTICLE in reminder_types_needed:
                cache_tasks.append(self.cache_daily_news_data())
            if ReminderType.QUIZ_SLANG in reminder_types_needed:
                cache_tasks.append(self.cache_daily_quiz_data())

            # Execute caching tasks concurrently
            if cache_tasks:
                print("📋 Pre-caching daily data...")
                await asyncio.gather(*cache_tasks, return_exceptions=True)

            # Process reminders with small delays to avoid overwhelming
            for reminder in due_reminders:
                await self.process_reminder(reminder)
                await asyncio.sleep(0.5)  # Small delay between reminders

        except Exception as e:
            print(f"❌ Error in reminder cycle: {e}")


async def main():
    try:
        # Initialize the pool outside the loop
        pool = await pgDB.fPool_Init()

        redis_client = aioredis.from_url("redis://localhost:6379")
        storage = RedisStorage(redis_client)

        # Initialize enhanced reminder system
        # --------------------
        reminder_system = EnhancedReminderSystem(pool, storage, bot)

        print("🚀 Enhanced reminder system started")
        print("⏰ Configured reminder times:")
        for reminder_type, config in reminder_system.reminder_configs.items():
            print(f"   {reminder_type} | {config.local_time} - {config.title}")
        #await reminder_system.clear_reminder_storage()     #for testing purposes        AJRM
        # --------------------
        while True:
            try:
                await reminder_system.run_reminder_cycle()
                await asyncio.sleep(60)  # Check every minute

            except ConnectionError as e:
                print(f"🔌 Connection error, retrying... {e}")
                await asyncio.sleep(10)
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                await asyncio.sleep(10)

    except Exception as init_error:
        print(f"💥 Failed to initialize: {init_error}")
    finally:
        if 'pool' in locals() and pool is not None:
            await pool.close()
            print("🔒 Database pool closed.")


with bot as bot_client:
    bot.loop.run_until_complete(main())