from typing import Dict, Any
from enum import Enum

class Language(Enum):
    ENGLISH = "en"
    RUSSIAN = "ru"
    UZBEK = "uz"
    UKRAINIAN = "uk"

# Language names for display
LANGUAGE_NAMES = {
    Language.ENGLISH: "🇺🇸 English",
    Language.RUSSIAN: "🇷🇺 Русский",
    Language.UZBEK: "🇺🇿 O'zbek",
    Language.UKRAINIAN: "🇺🇦 Українська"
}

# Language flags for buttons
LANGUAGE_FLAGS = {
    Language.ENGLISH: "🇺🇸",
    Language.RUSSIAN: "🇷🇺",
    Language.UZBEK: "🇺🇿",
    Language.UKRAINIAN: "🇺🇦"
}

# Translations
TRANSLATIONS = {
    Language.ENGLISH: {
        "welcome": """
🎨 Welcome to the Image Colorization Bot!

I can help you colorize black and white images using AI.

How to use:
1. Send me a black and white image
2. I'll process it and return a colorized version

Commands:
/start - Show this message
/help - Get help
/about - About this bot
/stats - Your statistics
/language - Change language

Just send me an image to get started! 📸
        """,
        "help": """
🆘 Help - Image Colorization Bot

This bot uses AI to colorize black and white images.

How to use:
1. Send a black and white image (JPG, PNG, etc.)
2. Wait for processing (may take a few seconds)
3. Receive your colorized image!

Tips for best results:
• Use clear, high-quality black and white images
• Avoid very small or blurry images
• The bot works best with photos of people, objects, and scenes

Commands:
/start - Welcome message
/help - This help message
/about - About the bot
/stats - Your statistics
/language - Change language

Just send me an image to start colorizing! 🎨
        """,
        "about": """
🤖 About Image Colorization Bot

This bot uses a Caffe-based deep learning model to automatically colorize black and white images.

Features:
• AI-powered colorization
• Support for various image formats
• High-quality results
• Easy to use
• User statistics tracking
• Multi-language support

The bot processes your images locally and returns colorized versions using advanced machine learning techniques.

Made with ❤️ for bringing old photos to life!
        """,
        "stats": """
📊 Your Statistics

👤 User Info:
• Username: @{username}
• Name: {first_name} {last_name}
• Member since: {created_at}

📈 Activity:
• Total requests: {total_requests}
• Images processed: {total_images_processed}
• Last activity: {last_activity}

🎨 Keep sending images to increase your stats!
        """,
        "admin_stats": """
📊 Admin Statistics (Last 30 days)

👥 Users:
• Total users: {total_users}
• Active users: {active_users}

📈 Requests:
• Total requests: {total_requests}
• Successful: {successful_requests}
• Failed: {failed_requests}
• Success rate: {success_rate:.1f}%

⏱️ Performance:
• Average processing time: {average_processing_time:.2f}s

🏆 Top Users:
{top_users}
        """,
        "language_selection": "🌍 Please select your language:",
        "language_changed": "✅ Language changed to {language}!",
        "processing": "🎨 Processing your image... This may take a few seconds.",
        "colorized_result": "🎨 Here's your colorized image! The AI has added realistic colors to your black and white photo.",
        "rate_limit": "⏰ Rate limit exceeded. You can make {limit} requests per hour. Please try again later.",
        "invalid_image": "❌ {error_message}",
        "processing_error": "❌ Sorry, I encountered an error while processing your image. Please make sure you sent a valid black and white image and try again.",
        "send_image": "📸 Please send me a black and white image to colorize!\n\nUse /help to see all available commands.",
        "stats_unavailable": "❌ Statistics are not available at the moment.",
        "admin_denied": "❌ Access denied. This command is for administrators only.",
        "error_occurred": "❌ An unexpected error occurred. Please try again later.",
        "stats_error": "❌ Error retrieving statistics.",
        "admin_stats_error": "❌ Error retrieving admin statistics."
    },
    
    Language.RUSSIAN: {
        "welcome": """
🎨 Добро пожаловать в бот для раскрашивания изображений!

Я могу помочь вам раскрасить черно-белые изображения с помощью ИИ.

Как использовать:
1. Отправьте мне черно-белое изображение
2. Я обработаю его и верну раскрашенную версию

Команды:
/start - Показать это сообщение
/help - Получить помощь
/about - О боте
/stats - Ваша статистика
/language - Изменить язык

Просто отправьте мне изображение, чтобы начать! 📸
        """,
        "help": """
🆘 Помощь - Бот для раскрашивания изображений

Этот бот использует ИИ для раскрашивания черно-белых изображений.

Как использовать:
1. Отправьте черно-белое изображение (JPG, PNG и т.д.)
2. Дождитесь обработки (может занять несколько секунд)
3. Получите раскрашенное изображение!

Советы для лучших результатов:
• Используйте четкие, качественные черно-белые изображения
• Избегайте очень маленьких или размытых изображений
• Бот лучше всего работает с фотографиями людей, объектов и сцен

Команды:
/start - Приветственное сообщение
/help - Это сообщение помощи
/about - О боте
/stats - Ваша статистика
/language - Изменить язык

Просто отправьте мне изображение, чтобы начать раскрашивать! 🎨
        """,
        "about": """
🤖 О боте для раскрашивания изображений

Этот бот использует модель глубокого обучения на основе Caffe для автоматического раскрашивания черно-белых изображений.

Возможности:
• Раскрашивание с помощью ИИ
• Поддержка различных форматов изображений
• Высокое качество результатов
• Простота использования
• Отслеживание статистики пользователей
• Многоязычная поддержка

Бот обрабатывает ваши изображения локально и возвращает раскрашенные версии, используя передовые методы машинного обучения.

Сделано с ❤️ для оживления старых фотографий!
        """,
        "stats": """
📊 Ваша статистика

👤 Информация о пользователе:
• Имя пользователя: @{username}
• Имя: {first_name} {last_name}
• Участник с: {created_at}

📈 Активность:
• Всего запросов: {total_requests}
• Обработано изображений: {total_images_processed}
• Последняя активность: {last_activity}

🎨 Продолжайте отправлять изображения, чтобы увеличить статистику!
        """,
        "admin_stats": """
📊 Статистика администратора (Последние 30 дней)

👥 Пользователи:
• Всего пользователей: {total_users}
• Активных пользователей: {active_users}

📈 Запросы:
• Всего запросов: {total_requests}
• Успешных: {successful_requests}
• Неудачных: {failed_requests}
• Процент успеха: {success_rate:.1f}%

⏱️ Производительность:
• Среднее время обработки: {average_processing_time:.2f}с

🏆 Топ пользователи:
{top_users}
        """,
        "language_selection": "🌍 Пожалуйста, выберите ваш язык:",
        "language_changed": "✅ Язык изменен на {language}!",
        "processing": "🎨 Обрабатываю ваше изображение... Это может занять несколько секунд.",
        "colorized_result": "🎨 Вот ваше раскрашенное изображение! ИИ добавил реалистичные цвета к вашей черно-белой фотографии.",
        "rate_limit": "⏰ Превышен лимит запросов. Вы можете сделать {limit} запросов в час. Попробуйте позже.",
        "invalid_image": "❌ {error_message}",
        "processing_error": "❌ Извините, я столкнулся с ошибкой при обработке вашего изображения. Убедитесь, что вы отправили корректное черно-белое изображение и попробуйте снова.",
        "send_image": "📸 Пожалуйста, отправьте мне черно-белое изображение для раскрашивания!\n\nИспользуйте /help для просмотра всех доступных команд.",
        "stats_unavailable": "❌ Статистика недоступна в данный момент.",
        "admin_denied": "❌ Доступ запрещен. Эта команда только для администраторов.",
        "error_occurred": "❌ Произошла неожиданная ошибка. Попробуйте позже.",
        "stats_error": "❌ Ошибка получения статистики.",
        "admin_stats_error": "❌ Ошибка получения статистики администратора."
    },
    
    Language.UZBEK: {
        "welcome": """
🎨 Rasm ranglashtirish botiga xush kelibsiz!

Men sizga AI yordamida qora-oq rasmlarni ranglashtirishda yordam bera olaman.

Qanday foydalanish:
1. Menga qora-oq rasm yuboring
2. Men uni qayta ishlab, rangli versiyasini qaytaraman

Buyruqlar:
/start - Bu xabarni ko'rsatish
/help - Yordam olish
/about - Bot haqida
/stats - Sizning statistikangiz
/language - Tilni o'zgartirish

Boshlash uchun menga rasm yuboring! 📸
        """,
        "help": """
🆘 Yordam - Rasm ranglashtirish boti

Bu bot qora-oq rasmlarni ranglashtirish uchun AI dan foydalanadi.

Qanday foydalanish:
1. Qora-oq rasm yuboring (JPG, PNG va boshqalar)
2. Qayta ishlashni kuting (bir necha soniya vaqt olishi mumkin)
3. Rangli rasmni oling!

Yaxshi natijalar uchun maslahatlar:
• Aniq, yuqori sifatli qora-oq rasmlardan foydalaning
• Juda kichik yoki xiralangan rasmlardan qoching
• Bot odamlar, narsalar va manzaralar fotosuratlari bilan eng yaxshi ishlaydi

Buyruqlar:
/start - Xush kelibsiz xabari
/help - Bu yordam xabari
/about - Bot haqida
/stats - Sizning statistikangiz
/language - Tilni o'zgartirish

Ranglashtirishni boshlash uchun menga rasm yuboring! 🎨
        """,
        "about": """
🤖 Rasm ranglashtirish boti haqida

Bu bot qora-oq rasmlarni avtomatik ranglashtirish uchun Caffe asosidagi chuqur o'rganish modelidan foydalanadi.

Xususiyatlar:
• AI yordamida ranglashtirish
• Turli rasm formatlarini qo'llab-quvvatlash
• Yuqori sifatli natijalar
• Oson foydalanish
• Foydalanuvchi statistikasini kuzatish
• Ko'p tilli qo'llab-quvvatlash

Bot sizning rasmlaringizni mahalliy ravishda qayta ishlaydi va ilg'or mashina o'rganish texnikalaridan foydalangan holda rangli versiyalarni qaytaradi.

Eski fotosuratlarni jonlantirish uchun ❤️ bilan yaratilgan!
        """,
        "stats": """
📊 Sizning statistikangiz

👤 Foydalanuvchi ma'lumotlari:
• Foydalanuvchi nomi: @{username}
• Ism: {first_name} {last_name}
• A'zo bo'lgan vaqt: {created_at}

📈 Faoliyat:
• Jami so'rovlar: {total_requests}
• Qayta ishlangan rasmlar: {total_images_processed}
• So'nggi faoliyat: {last_activity}

🎨 Statistikangizni oshirish uchun rasmlar yuborishda davom eting!
        """,
        "admin_stats": """
📊 Administrator statistikasi (So'nggi 30 kun)

👥 Foydalanuvchilar:
• Jami foydalanuvchilar: {total_users}
• Faol foydalanuvchilar: {active_users}

📈 So'rovlar:
• Jami so'rovlar: {total_requests}
• Muvaffaqiyatli: {successful_requests}
• Muvaffaqiyatsiz: {failed_requests}
• Muvaffaqiyat darajasi: {success_rate:.1f}%

⏱️ Ishlash:
• O'rtacha qayta ishlash vaqti: {average_processing_time:.2f}s

🏆 Eng faol foydalanuvchilar:
{top_users}
        """,
        "language_selection": "🌍 Iltimos, tilingizni tanlang:",
        "language_changed": "✅ Til {language} ga o'zgartirildi!",
        "processing": "🎨 Rasmingizni qayta ishlayapman... Bu bir necha soniya vaqt olishi mumkin.",
        "colorized_result": "🎨 Mana sizning rangli rasmingiz! AI sizning qora-oq fotosuratingizga realistik ranglar qo'shdi.",
        "rate_limit": "⏰ So'rovlar chegarasi oshirildi. Siz soatiga {limit} ta so'rov yuborishingiz mumkin. Keyinroq urinib ko'ring.",
        "invalid_image": "❌ {error_message}",
        "processing_error": "❌ Kechirasiz, rasmingizni qayta ishlashda xatolik yuz berdi. Iltimos, to'g'ri qora-oq rasm yuborganingizga ishonch hosil qiling va qayta urinib ko'ring.",
        "send_image": "📸 Iltimos, ranglashtirish uchun menga qora-oq rasm yuboring!\n\nBarcha mavjud buyruqlarni ko'rish uchun /help dan foydalaning.",
        "stats_unavailable": "❌ Hozircha statistika mavjud emas.",
        "admin_denied": "❌ Kirish rad etildi. Bu buyruq faqat administratorlar uchun.",
        "error_occurred": "❌ Kutilmagan xatolik yuz berdi. Keyinroq urinib ko'ring.",
        "stats_error": "❌ Statistikani olishda xatolik.",
        "admin_stats_error": "❌ Administrator statistikasini olishda xatolik."
    },
    
    Language.UKRAINIAN: {
        "welcome": """
🎨 Ласкаво просимо до бота для розфарбовування зображень!

Я можу допомогти вам розфарбувати чорно-білі зображення за допомогою ШІ.

Як використовувати:
1. Надішліть мені чорно-біле зображення
2. Я оброблю його і поверну розфарбовану версію

Команди:
/start - Показати це повідомлення
/help - Отримати допомогу
/about - Про бота
/stats - Ваша статистика
/language - Змінити мову

Просто надішліть мені зображення, щоб почати! 📸
        """,
        "help": """
🆘 Допомога - Бот для розфарбовування зображень

Цей бот використовує ШІ для розфарбовування чорно-білих зображень.

Як використовувати:
1. Надішліть чорно-біле зображення (JPG, PNG тощо)
2. Дочекайтеся обробки (може зайняти кілька секунд)
3. Отримайте розфарбоване зображення!

Поради для кращих результатів:
• Використовуйте чіткі, високоякісні чорно-білі зображення
• Уникайте дуже маленьких або розмитих зображень
• Бот найкраще працює з фотографіями людей, об'єктів і сцен

Команди:
/start - Привітальне повідомлення
/help - Це повідомлення допомоги
/about - Про бота
/stats - Ваша статистика
/language - Змінити мову

Просто надішліть мені зображення, щоб почати розфарбовувати! 🎨
        """,
        "about": """
🤖 Про бота для розфарбовування зображень

Цей бот використовує модель глибокого навчання на основі Caffe для автоматичного розфарбовування чорно-білих зображень.

Можливості:
• Розфарбовування за допомогою ШІ
• Підтримка різних форматів зображень
• Висока якість результатів
• Простота використання
• Відстеження статистики користувачів
• Багатомовна підтримка

Бот обробляє ваші зображення локально і повертає розфарбовані версії, використовуючи передові методи машинного навчання.

Зроблено з ❤️ для оживлення старих фотографій!
        """,
        "stats": """
📊 Ваша статистика

👤 Інформація про користувача:
• Ім'я користувача: @{username}
• Ім'я: {first_name} {last_name}
• Учасник з: {created_at}

📈 Активність:
• Всього запитів: {total_requests}
• Оброблено зображень: {total_images_processed}
• Остання активність: {last_activity}

🎨 Продовжуйте надсилати зображення, щоб збільшити статистику!
        """,
        "admin_stats": """
📊 Статистика адміністратора (Останні 30 днів)

👥 Користувачі:
• Всього користувачів: {total_users}
• Активних користувачів: {active_users}

📈 Запити:
• Всього запитів: {total_requests}
• Успішних: {successful_requests}
• Невдалих: {failed_requests}
• Відсоток успіху: {success_rate:.1f}%

⏱️ Продуктивність:
• Середній час обробки: {average_processing_time:.2f}с

🏆 Топ користувачі:
{top_users}
        """,
        "language_selection": "🌍 Будь ласка, оберіть вашу мову:",
        "language_changed": "✅ Мову змінено на {language}!",
        "processing": "🎨 Обробляю ваше зображення... Це може зайняти кілька секунд.",
        "colorized_result": "🎨 Ось ваше розфарбоване зображення! ШІ додав реалістичні кольори до вашої чорно-білої фотографії.",
        "rate_limit": "⏰ Перевищено ліміт запитів. Ви можете зробити {limit} запитів на годину. Спробуйте пізніше.",
        "invalid_image": "❌ {error_message}",
        "processing_error": "❌ Вибачте, я зіткнувся з помилкою при обробці вашого зображення. Переконайтеся, що ви надіслали коректне чорно-біле зображення і спробуйте знову.",
        "send_image": "📸 Будь ласка, надішліть мені чорно-біле зображення для розфарбовування!\n\nВикористовуйте /help для перегляду всіх доступних команд.",
        "stats_unavailable": "❌ Статистика недоступна на даний момент.",
        "admin_denied": "❌ Доступ заборонено. Ця команда тільки для адміністраторів.",
        "error_occurred": "❌ Сталася неочікувана помилка. Спробуйте пізніше.",
        "stats_error": "❌ Помилка отримання статистики.",
        "admin_stats_error": "❌ Помилка отримання статистики адміністратора."
    }
}

def get_translation(language: Language, key: str, **kwargs) -> str:
    """Get translation for a specific language and key"""
    if language not in TRANSLATIONS:
        language = Language.ENGLISH
    
    if key not in TRANSLATIONS[language]:
        # Fallback to English if key not found
        if key in TRANSLATIONS[Language.ENGLISH]:
            return TRANSLATIONS[Language.ENGLISH][key].format(**kwargs)
        return f"Translation not found: {key}"
    
    return TRANSLATIONS[language][key].format(**kwargs)

def get_language_from_code(code: str) -> Language:
    """Get Language enum from language code"""
    for lang in Language:
        if lang.value == code:
            return lang
    return Language.ENGLISH

def get_supported_languages() -> list:
    """Get list of supported languages"""
    return list(Language)



