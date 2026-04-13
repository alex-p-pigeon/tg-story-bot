import asyncio
import asyncpg
from datetime import datetime, date, timezone, timedelta
import logging
from config_reader import config

logger = logging.getLogger(__name__)
'''
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
'''

async def fPool_Init(toggleDB = 1):
    print('toggleDB', toggleDB)
    if toggleDB == 1:
        host = 'localhost'
        port = config.DB_PORT.get_secret_value()
        user = config.DB_USER.get_secret_value()
        password = config.DB_PASSWORD.get_secret_value()
    else:       #direct prod connection (for newsppr generation script
        host = config.PROD_DB_HOST.get_secret_value()
        port = config.PROD_DB_PORT.get_secret_value()
        user = config.PROD_DB_USER.get_secret_value()
        password = config.PROD_DB_PASSWORD.get_secret_value()
    database = config.DB_NAME.get_secret_value()
    pool_base = await asyncpg.create_pool(
        user=user,
        password=password,
        database=database,
        host=host,
        port=port,
        min_size=1,  # Minimum number of connections in the pool
        max_size=100,  # Maximum number of connections in the pool
        timeout = 10.0
    )
    if pool_base: print(f'0| pool for {database} created succesfully')


    database = config.DBLOG_NAME.get_secret_value()
    pool_log = await asyncpg.create_pool(
        user=user,
        password=password,
        database=database,
        host=host,
        port=port,
        min_size=1,  # Minimum number of connections in the pool
        max_size=100,  # Maximum number of connections in the pool
        timeout=10.0
    )
    if pool_log: print(f'1| pool for {database} created succesfully')
    return [pool_base, pool_log]

async def fExec_SelectQuery(pool, query):
    try:
        async with pool.acquire(timeout=5.0) as connection:
            async with connection.transaction():
                records = await connection.fetch(query, timeout=10.0)
                result = [tuple(record) for record in records]
                return result
    except Exception as e:
        logging.error(f"An error occurred while executing the query: {e}")
        return None
    
async def fExec_SelectQuery_args(pool, query, *args):
    try:
        async with pool.acquire(timeout=5.0) as connection:
            async with connection.transaction():
                if args:
                    records = await connection.fetch(query, *args, timeout=10.0)
                else:
                    records = await connection.fetch(query, timeout=10.0)
                result = [tuple(record) for record in records]
                return result
    except Exception as e:
        logging.error(f"An error occurred while executing the query: {e}")
        logging.error(f"Query: {query}")
        logging.error(f"Args: {args}")
        return None

async def fExec_UpdateQuery_args(pool, query, *args):
    try:
        async with pool.acquire(timeout=5.0) as connection:
            async with connection.transaction():
                await connection.execute(query, *args)
    except Exception as e:
        logging.error(f"An error occurred while executing the query: {e}")
        logging.error(f"        ---->query is: {query}")


async def fExec_TransactionQueries(pool, queries_with_args: list):
    """
    Выполняет несколько запросов в одной транзакции, каждый со своими параметрами.

    Args:
        pool: Connection pool
        queries_with_args: Список кортежей (query, *args) или просто запросов
            Примеры:
            [("SELECT * FROM table WHERE id = $1", 123)]
            [("DELETE FROM table WHERE id = $1", 456), ("UPDATE other SET x = $1", 789)]
    """
    try:
        async with pool.acquire(timeout=5.0) as connection:
            async with connection.transaction():
                for item in queries_with_args:
                    if isinstance(item, tuple):
                        query = item[0]
                        args = item[1:] if len(item) > 1 else ()
                        await connection.execute(query, *args)
                    else:
                        # Если передана просто строка запроса без параметров
                        await connection.execute(item)
    except Exception as e:
        logging.error(f"An error occurred while executing transaction: {e}")
        logging.error(f"        ---->queries_with_args: {queries_with_args}")
        raise

async def fFetch_InsertQuery_args(pool, query, *args):
    try:
        async with pool.acquire(timeout=5.0) as connection:
            async with connection.transaction():
                # Use fetchrow() to get the returned row (e.g. after RETURNING c_id)
                row = await connection.fetchrow(query, *args)
                return row  # Can be None if no RETURNING clause or no row
    except Exception as e:
        logging.error(f"An error occurred while executing the query: {e}")
        logging.error(f"        ---->query is: {query}")
        return None

async def fExec_UpdateQuery(pool, query):
    try:
        async with pool.acquire(timeout=5.0) as connection:
            async with connection.transaction():
                await connection.execute(query)
    except Exception as e:
        logging.error(f"An error occurred while executing the query: {e}")

async def fExec_UpdateArrQuery(pool, arrQuery):
    try:
        async with pool.acquire(timeout=5.0) as connection:
            async with connection.transaction():
                for query in arrQuery:
                    await connection.execute(query)
    except Exception as e:
        logging.error(f"An error occurred while executing the queries: {e}")


async def fExec_LogQuery(pool, userID, txtLog, logType=2):
    #INSERT INTO t_log (c_log_user_id, c_log_txt, c_log_date, c_log_type) VALUES ({userID}, '{txtLog}', CURRENT_TIMESTAMP, {logType})
    query = """
        INSERT INTO t_log (c_log_user_id, c_log_txt, c_log_date, c_log_type) VALUES ($1, $2, CURRENT_TIMESTAMP, $3)
    """

    try:
        async with pool.acquire(timeout=5.0) as connection:
            async with connection.transaction():
                await connection.execute(query, userID, txtLog, logType)
    except Exception as e:
        logging.error(f"An error occurred while executing the query: {e}")

async def fExec_LogQuery_test(pool, userID, txtLog, c_log2, c_log3, c_log4, logType=2):
    query = """
        INSERT INTO t_log (c_log_user_id, c_log_txt, c_log2, c_log3, c_log4, c_log_date, c_log_type) 
        VALUES ($1, $2, $3, $4, $5, CURRENT_TIMESTAMP, $6)
    """

    try:
        async with pool.acquire(timeout=5.0) as connection:
            async with connection.transaction():
                await connection.execute(query, userID, txtLog, c_log2, c_log3, c_log4, logType)
    except Exception as e:
        logging.error(f"An error occurred while executing the query: {e}")

async def fPool_Close(pool):
    await pool.close()
