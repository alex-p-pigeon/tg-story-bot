"""
Audio Generator for Verb To Be Questions
Generates audio files for all topics and lessons using ToBeQuestionGenerator
"""

import os
import shutil
from typing import List, Dict
#from gram_20_generator import ToBeQuestionGenerator


#from handlers.learnpath.services.gram_20_generator import ToBeQuestionGenerator
from handlers.learnpath.generators.factory import QuestionGeneratorFactory

import csv
#import selfFunctions as myF

# Конфигурация: какие вопросы генерировать для каждого урока
'''
#gram20:
LESSON_QUESTIONS = {
    1: ['q3', 'q5', 'q6', 'q7', 'q8'],  # 5 вопросов
    2: ['q2', 'q3', 'q5', 'q6', 'q7'],  # 5 вопросов
    3: ['q1', 'q3', 'q4', 'q6'],        # 4 вопроса
    4: ['q1', 'q4', 'q6']               # 3 вопроса
}



#gram40:
LESSON_QUESTIONS = {
    1: ['q4', 'q4', 'q4', 'q4'],        # 1x4 вопросов        !!!!!
    2: ['q6', 'q6', 'q6', 'q6'],        # 1x4 вопросов          !!!!
    3: ['q8', 'q8', 'q8', 'q8'],        # 1x4 вопроса           !!!!
    4: ['q8', 'q8', 'q8', 'q8'],        # 1x4 вопроса           !!!!
    5: [],              # 0 вопроса
    6: [],        # 0 вопроса
    7: [],    # 0 вопроса
}

#gram50:        нет различий в
LESSON_QUESTIONS = {
    1: ['q5', 'q8'],        # 2 вопросов        !!!!!
    2: [],        # 1x4 вопросов          !!!!
    3: [],        # 1x4 вопроса           !!!!
    4: ['q8'],        # 1x4 вопроса           !!!!
    5: ['q1', 'q2', 'q3', 'q4', 'q5', 'q6', 'q7', 'q8', 'q9', 'q10'],              # 0 вопроса
    6: ['q1', 'q2', 'q3', 'q4', 'q5', 'q6'],        # 0 вопроса
    7: ['q1', 'q8', 'q10'],    # 0 вопроса
}

#gram10:
LESSON_QUESTIONS = {
    #1: ['q2'],        # 4 вопросов
    2: ['q1', 'q2', 'q5', 'q7'],        # 4
    3: ['q1', 'q3', 'q5', 'q7'],        # 4
    4: ['q2', 'q3', 'q5', 'q7'],        # 4
    #5: [],              # 3 вопроса
    6: ['q1', 'q3', 'q5', 'q7', 'q9'],     # 5
}

'''
#gram30:
LESSON_QUESTIONS = {
    1: ['q2', 'q4', 'q5', 'q7'],        # 4 вопросов
    2: ['q3', 'q4', 'q5', 'q6'],        # 4 вопросов
    3: ['q5', 'q6', 'q5', 'q6'],        # 2x2 вопроса           !!!!
    4: ['q1', 'q2', 'q5', 'q7'],        # 4 вопроса
    5: ['q1', 'q2', 'q5'],              # 3 вопроса
    6: ['q3', 'q4', 'q5', 'q6'],        # 4 вопроса
    7: ['q1', 'q2', 'q3', 'q4', 'q5', 'q6'],    # 6 вопроса
    8: ['q1', 'q2', 'q4', 'q5', 'q7'],  # 5 вопроса
}

# Список топиков
TOPIC_IDS = [
    2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 18,
    20, 21, 22, 23, 24, 26, 27, 28, 29, 30, 31, 32, 33, 35,
    36, 37, 38, 39, 40
]


async def generate_all_tobe_audio_files(myF) -> Dict[str, int]:
    """
    Генерация всех аудио файлов для Verb To Be модуля
    
    Args:
        myF: модуль с функциями TTS (fGenerateVoiceParams, afTxtToOGG)
    
    Returns:
        Dict с статистикой: {'total': int, 'success': int, 'failed': int}
    """
    generator_type = 'PresentSimpleQuestionGenerator'
    filePrefix = 'gram30'
    generator = QuestionGeneratorFactory.get_generator(generator_type)
    
    # Создаем папку для аудио если не существует
    audio_dir = os.path.join(os.path.dirname(__file__), 'audio')
    os.makedirs(audio_dir, exist_ok=True)

    # Открываем CSV файл для записи соответствий файл-текст
    mapping_file = os.path.join(audio_dir, 'audio_text_mapping.csv')
    csv_file = open(mapping_file, 'w', newline='', encoding='utf-8')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['filename', 'text', 'topic_id', 'lesson', 'question_type'])  # Заголовки
    

    
    stats = {'total': 0, 'success': 0, 'failed': 0}
    
    print("🎙️ Начинаем генерацию аудио файлов для Verb To Be...")
    print(f"📊 Топиков: {len(TOPIC_IDS)}")
    print(f"📊 Уроков: 4")
    print(f"📊 Примерное количество файлов: {len(TOPIC_IDS) * 38}\n")
    
    # Проходим по каждому топику
    for topic_id in TOPIC_IDS:
        print(f"📚 Обрабатываем topic_id={topic_id}...")
        
        # Проходим по каждому уроку
        for lesson_num in [5, 6, 7, 8]:
            questions_to_generate = LESSON_QUESTIONS[lesson_num]
            
            # Проходим по каждому типу вопроса
            for q_type in questions_to_generate:
                # Генерируем 2 варианта для каждого вопроса
                for variant in [1]:     #, 2
                    stats['total'] += 1
                    
                    try:
                        # Генерируем вопрос
                        question_data = await generate_single_question(
                            generator=generator,
                            lesson_num=lesson_num,
                            q_type=q_type,
                            topic_id=topic_id
                        )
                        
                        if not question_data:
                            print(f"  ❌ Не удалось сгенерировать вопрос: less{lesson_num}_{q_type}_topic{topic_id}_v{variant}")
                            stats['failed'] += 1
                            continue
                        
                        # Получаем корректный ответ (полное предложение)
                        correct_answer = question_data['correct_answer_text']

                        # Параметры для TTS (premium)
                        arrVoiceParams = myF.fGenerateVoiceParams(isPremium=True)
                        # Генерируем аудио через TTS
                        temp_audio_file = await myF.afTxtToOGG(correct_answer, arrVoiceParams)
                        
                        if not temp_audio_file or not os.path.exists(temp_audio_file):
                            print(f"  ❌ TTS не создал файл для: {correct_answer[:30]}...")
                            stats['failed'] += 1
                            continue
                        
                        # Формируем имя файла
                        # Формат: gram20_less1_q3_topic2_v1.ogg
                        filename = f"{filePrefix}_less{lesson_num}_{q_type}_topic{topic_id}_v{variant}.ogg"
                        destination = os.path.join(audio_dir, filename)
                        
                        # Перемещаем файл в целевую директорию
                        shutil.move(temp_audio_file, destination)
                        
                        stats['success'] += 1

                        # Записываем в CSV соответствие файл-текст
                        csv_writer.writerow([
                            filename,
                            correct_answer,
                            topic_id,
                            lesson_num,
                            q_type
                        ])
                        
                        if stats['success'] % 10 == 0:
                            print(f"  ✅ Создано файлов: {stats['success']}/{stats['total']}")
                    
                    except Exception as e:
                        print(f"  ❌ Ошибка при генерации less{lesson_num}_{q_type}_topic{topic_id}_v{variant}: {e}")
                        stats['failed'] += 1
    
    # Итоговая статистика
    print("\n" + "="*60)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("="*60)
    print(f"✅ Успешно создано: {stats['success']}")
    print(f"❌ Ошибок: {stats['failed']}")
    print(f"📁 Всего обработано: {stats['total']}")
    print(f"📂 Файлы сохранены в: {audio_dir}")
    print("="*60)

    # Закрываем CSV файл
    csv_file.close()
    print(f"📄 Mapping сохранен в: {mapping_file}")

    return stats


async def generate_single_question(
        generator,  #: ToBeQuestionGenerator,
        lesson_num: int,
        q_type: str,
        topic_id: int
) -> Dict:
    """
    Генерирует один вопрос и возвращает корректный ответ
    
    Args:
        generator: экземпляр ToBeQuestionGenerator
        lesson_num: номер урока (1-4)
        q_type: тип вопроса ('q1', 'q2', ..., 'q8')
        topic_id: ID топика
    
    Returns:
        Dict с данными вопроса или None если ошибка
    """
    # Формируем имя метода: generate_lesson1_q3, generate_lesson2_q5, и т.д.
    method_name = f"generate_lesson{lesson_num}_{q_type}"
    
    # Проверяем, существует ли метод
    if not hasattr(generator, method_name):
        print(f"  ⚠️ Метод {method_name} не найден в генераторе")
        return None
    
    # Получаем метод
    method = getattr(generator, method_name)
    
    # Вызываем метод для генерации вопроса
    question_data = method(topic_id)
    
    if not question_data:
        return None
    
    # Извлекаем корректный ответ
    correct_answer_key = question_data.get('correct_answer')  # 'A', 'B', 'C', или 'D'
    options = question_data.get('options', {})
    
    if correct_answer_key not in options:
        print(f"  ⚠️ Корректный ответ '{correct_answer_key}' не найден в options")
        return None
    
    correct_answer_text = options[correct_answer_key]
    
    return {
        'question': question_data.get('question'),
        'correct_answer': correct_answer_key,
        'correct_answer_text': correct_answer_text,
        'options': options
    }


# ============================================================================
# STANDALONE ЗАПУСК (для тестирования)
# ============================================================================

if __name__ == "__main__":
    import asyncio
    
    # Mock для тестирования без реального TTS
    class MockTTS:
        def fGenerateVoiceParams(self, isPremium=True):
            return {'voice': 'test', 'rate': 1.0}
        
        async def afTxtToOGG(self, text, params):
            # Создаем временный файл для теста
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.ogg')
            temp_file.write(b'mock audio data')
            temp_file.close()
            return temp_file.name
    
    print("⚠️ ТЕСТОВЫЙ РЕЖИМ с Mock TTS")
    print("Для реального использования импортируйте настоящий модуль myF\n")
    
    mock_tts = MockTTS()
    
    # Запускаем генерацию
    asyncio.run(generate_all_tobe_audio_files(mock_tts))
