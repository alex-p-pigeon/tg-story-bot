"""
Централизованные SQL запросы для LearnPath модуля
"""


class LearnPathQueries:
    """Константы SQL запросов"""

    # ==================== USER CURRICULUM ====================

    GET_USER_LEARNPATH = """
        SELECT 
            uc.c_topic_id, 
            uc.c_status, 
            uc.c_progress_percent,
            uc.c_order_in_program,
            t.c_topic_name_ru,
            t.c_estimated_hours
        FROM t_lp_module_user uc
        JOIN t_lp_topics t ON uc.c_topic_id = t.c_topic_id
        WHERE uc.c_user_id = {user_id}
        ORDER BY uc.c_order_in_program
    """

    HAS_LEARNPATH = """
        SELECT COUNT(*) 
        FROM t_lp_module_user 
        WHERE c_user_id = {user_id}
    """

    CREATE_LEARNPATH_TOPIC = """
        INSERT INTO t_lp_module_user 
        (c_user_id, c_topic_id, c_status, c_order_in_program, c_progress_percent)
        VALUES ({user_id}, {topic_id}, 'not_started', {order}, 0)
        ON CONFLICT (c_user_id, c_topic_id) DO NOTHING
    """

    ACTIVATE_FIRST_TOPIC = """
        UPDATE t_lp_module_user 
        SET c_status = 'in_progress', c_start_date = CURRENT_TIMESTAMP
        WHERE c_user_id = {user_id} AND c_topic_id = {topic_id}
    """

    DELETE_USER_LEARNPATH = """
        DELETE FROM t_lp_module_user WHERE c_user_id = {user_id}
    """

    GET_CURRENT_TOPIC = """
        SELECT c_topic_id
        FROM t_lp_module_user
        WHERE c_user_id = {user_id} AND c_status = 'in_progress'
        ORDER BY c_order_in_program
        LIMIT 1
    """

    COMPLETE_TOPIC = """
        UPDATE t_lp_module_user 
        SET 
            c_status = 'completed',
            c_completion_date = CURRENT_TIMESTAMP,
            c_progress_percent = 100
        WHERE c_user_id = {user_id} AND c_topic_id = {topic_id}
    """

    # ==================== TOPICS ====================

    GET_TOPICS_BY_LEVEL = """
        SELECT c_topic_id, c_topic_name, c_topic_name_ru, c_description, c_category
        FROM t_lp_topics
        WHERE c_eng_level <= {level}
        ORDER BY c_order_priority
    """

    GET_ESSENTIAL_TOPICS = """
        SELECT c_topic_id 
        FROM t_lp_topics
        WHERE c_eng_level = {level} 
            AND c_category = 'essential'
        ORDER BY c_order_priority
    """

    GET_TOPIC_INFO = """
        SELECT 
            c_topic_name,
            c_topic_name_ru,
            c_description,
            c_estimated_hours,
            c_eng_level,
            c_category
        FROM t_lp_topics
        WHERE c_topic_id = {topic_id}
    """

    # ==================== MODULES ====================

    GET_MODULE = """
        SELECT 
            m.c_module_name,
            m.c_content_type,
            m.c_content,
            m.c_topic_id
        FROM t_lp_module m
        WHERE m.c_module_id = {module_id}
    """

    GET_TOPIC_MODULES = """
        SELECT 
            m.c_module_id,
            m.c_module_name,
            m.c_content_type,
            m.c_estimated_minutes,
            COALESCE(ump.c_status, 'not_started') as status
        FROM t_lp_module m
        LEFT JOIN t_lp_user_module_progress ump 
            ON m.c_module_id = ump.c_module_id AND ump.c_user_id = {user_id}
        WHERE m.c_topic_id = {topic_id}
        ORDER BY m.c_module_order
    """

    GET_NEXT_MODULE = """
        SELECT m.c_module_id
        FROM t_lp_module m
        LEFT JOIN t_lp_user_module_progress ump 
            ON m.c_module_id = ump.c_module_id AND ump.c_user_id = {user_id}
        WHERE m.c_topic_id = {topic_id}
            AND COALESCE(ump.c_status, 'not_started') != 'completed'
        ORDER BY m.c_module_order
        LIMIT 1
    """

    # ==================== PROGRESS ====================

    UPDATE_MODULE_PROGRESS = """
        INSERT INTO t_lp_user_module_progress 
        (c_user_id, c_module_id, c_status, c_attempts, c_score)
        VALUES ({user_id}, {module_id}, '{status}', 1, {score})
        ON CONFLICT (c_user_id, c_module_id) 
        DO UPDATE SET 
            c_status = '{status}',
            c_attempts = t_lp_user_module_progress.c_attempts + 1,
            c_score = {score},
            c_completed_at = {completed_at}
    """

    UPDATE_TOPIC_PROGRESS = """
        UPDATE t_lp_module_user 
        SET c_progress_percent = {progress}
        WHERE c_user_id = {user_id} AND c_topic_id = {topic_id}
    """

    GET_TOPIC_PROGRESS = """
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN COALESCE(ump.c_status, 'not_started') = 'completed' THEN 1 ELSE 0 END) as completed
        FROM t_lp_module m
        LEFT JOIN t_lp_user_module_progress ump 
            ON m.c_module_id = ump.c_module_id AND ump.c_user_id = {user_id}
        WHERE m.c_topic_id = {topic_id}
    """

    # ==================== TESTS ====================

    GET_RANDOM_QUESTION = """
        SELECT c_question_id, c_question_text, c_question_data 
        FROM t_lp_init_assess_questions 
        WHERE c_eng_level = {level} 
            AND c_question_type = 'multiple_choice'
        ORDER BY RANDOM() 
        LIMIT 1
    """

    GET_TOPIC_TEST_QUESTIONS = """
        SELECT c_question_id, c_question_text, c_question_data
        FROM t_lp_init_assess_questions
        WHERE c_topic_id = {topic_id}
        ORDER BY RANDOM()
        LIMIT {limit}
    """

    SAVE_TEST_RESULT = """
        INSERT INTO t_lp_init_assess_user_results 
        (c_user_id, c_topic_id, c_test_type, c_score, c_max_score, c_passed, c_test_data)
        VALUES ({user_id}, {topic_id}, '{test_type}', {score}, {max_score}, {passed}, '{test_data}')
    """

    # ==================== INTERESTS ====================

    SAVE_INTEREST = """
        INSERT INTO t_lp_topics_user (c_user_id, c_topic_id, c_priority)
        VALUES ({user_id}, {topic_id}, {priority})
        ON CONFLICT (c_user_id, c_topic_id) 
        DO UPDATE SET c_priority = {priority}, c_date_set = CURRENT_TIMESTAMP
    """

    GET_USER_INTERESTS = """
        SELECT c_topic_id, c_priority 
        FROM t_lp_topics_user 
        WHERE c_user_id = {user_id} AND c_priority >= 3
        ORDER BY c_priority DESC, c_date_set DESC
    """

    DELETE_USER_INTERESTS = """
        DELETE FROM t_lp_topics_user WHERE c_user_id = {user_id}
    """

    # ==================== STATISTICS ====================

    GET_TOPIC_STATS = """
        SELECT 
            COUNT(*) as total_topics,
            SUM(CASE WHEN c_status = 'completed' THEN 1 ELSE 0 END) as completed_topics,
            SUM(CASE WHEN c_status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
            AVG(c_progress_percent) as avg_progress
        FROM t_lp_module_user
        WHERE c_user_id = {user_id}
    """

    GET_TEST_STATS = """
        SELECT 
            COUNT(*) as total_tests,
            AVG(c_score / c_max_score * 100) as avg_score,
            SUM(CASE WHEN c_passed THEN 1 ELSE 0 END) as passed_tests
        FROM t_lp_init_assess_user_results
        WHERE c_user_id = {user_id}
    """

    GET_TIME_STATS = """
        SELECT SUM(c_time_spent_minutes)
        FROM t_lp_user_module_progress
        WHERE c_user_id = {user_id}
    """