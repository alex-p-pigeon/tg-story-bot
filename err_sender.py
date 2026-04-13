

import fpgDB as pgDB

import logging
logger = logging.getLogger(__name__)



async def err_sender(bot, pool_log, user_id, err_msg):

    supportID = 6894355153

    # Ограничиваем длину сообщения
    str_Msg = f"{user_id}|\n{err_msg}"
    if len(str_Msg) > 1200:
        str_Msg = str_Msg[:1197] + "..."

    try:
        await bot.send_message(
            chat_id=supportID,
            text=str_Msg,
            parse_mode='HTML'
        )

        await pgDB.fExec_LogQuery(pool_log, user_id, err_msg)
    except Exception as e:
        logger.info(f"An unexpected error occurred: {e}")