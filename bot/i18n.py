"""Interface texts in every supported language.

Answers to questions come from the LLM in the user's language, so only
buttons and service messages live here.
"""

DEFAULT_LANG = "en"

# code -> (button label, language name for the LLM prompt)
LANGUAGES = {
    "en": ("🇬🇧 English", "English"),
    "ru": ("🇷🇺 Русский", "Russian"),
    "zh": ("🇨🇳 中文", "Simplified Chinese"),
    "ar": ("🇸🇦 العربية", "Arabic"),
    "fr": ("🇫🇷 Français", "French"),
    "es": ("🇪🇸 Español", "Spanish"),
    "hi": ("🇮🇳 हिन्दी", "Hindi"),
    "fa": ("🇮🇷 فارسی", "Persian (Farsi)"),
    "tr": ("🇹🇷 Türkçe", "Turkish"),
}

TOPICS = ["sim", "transport", "documents", "medicine", "money", "emergency"]

TOPIC_EMOJI = {
    "sim": "📱",
    "transport": "🚇",
    "documents": "📄",
    "medicine": "💊",
    "money": "💳",
    "emergency": "🆘",
}

# What the bot asks the LLM when a topic button is pressed.
TOPIC_QUESTIONS = {
    "sim": "How can a foreigner get a SIM card in Moscow? Which operators, where to buy, "
           "what documents are needed, approximate prices, and how registration works now.",
    "transport": "How does public transport work in Moscow for a newcomer? Where and how to get "
                 "a Troika card or other transport card, current fares, how to pay, useful apps.",
    "documents": "What documents and registrations does a foreign student or tourist need after "
                 "arriving in Moscow (migration registration, migration card, deadlines), and where to do it?",
    "medicine": "How can a foreigner in Moscow get medical help: pharmacies, buying medicine, "
                "private and public clinics, medical insurance, what to do if you get sick?",
    "money": "How can a foreigner handle money in Moscow: foreign bank cards, cash, currency "
             "exchange, opening a Russian bank account, paying by phone?",
    "emergency": "What emergency phone numbers and steps should a foreigner in Moscow know "
                 "(police, ambulance, fire, single emergency number, lost passport, embassy)?",
}

PLACE_CATEGORIES = ["pharmacy", "metro", "mobile", "atm", "hospital"]

PLACE_EMOJI = {
    "pharmacy": "💊",
    "metro": "🚇",
    "mobile": "📱",
    "atm": "🏧",
    "hospital": "🏥",
}

T = {
    "en": {
        "welcome": "👋 Hi! I'm Help in Moscow, your assistant for life in Moscow.\n\n"
                   "Pick a topic below or just ask me anything in your own words.",
        "choose_language": "Please choose your language:",
        "language_selected": "Language selected: English",
        "help": "Ask me anything about life in Moscow: transport, SIM cards, documents, "
                "medicine, money. Send your location to find places nearby.\n\n"
                "/chooselanguage - change language",
        "sim": "SIM card", "transport": "Transport", "documents": "Documents",
        "medicine": "Medicine", "money": "Money & banks", "emergency": "Emergency",
        "nearby": "📍 Nearby", "language": "🌍 Choose language",
        "send_location": "📍 Send my location",
        "nearby_ask": "Send me your location and I'll find places nearby.",
        "nearby_choose": "What are you looking for?",
        "pharmacy": "Pharmacy", "metro": "Metro", "mobile": "Phone & SIM shop",
        "atm": "ATM", "hospital": "Hospital / clinic",
        "nearby_none": "I couldn't find anything like that within 1.5 km.",
        "nearby_title": "Nearest places:",
        "location_again": "Please send your location again.",
        "thinking": "🔎 Looking it up…",
        "limit_user": "You've reached today's limit of questions. Please try again tomorrow.",
        "limit_global": "The bot is very busy today. Please try again tomorrow.",
        "error": "Something went wrong. Please try again a bit later.",
        "open_map": "map",
        "open_on_map": "🗺 Open on the map",
        "nearby_map": "Here is a map search around you:",
    },
    "ru": {
        "welcome": "👋 Привет! Я Help in Moscow, помогаю освоиться в Москве.\n\n"
                   "Выбери тему ниже или просто задай вопрос своими словами.",
        "choose_language": "Выберите язык:",
        "language_selected": "Выбран язык: русский",
        "help": "Спрашивай что угодно о жизни в Москве: транспорт, SIM-карты, документы, "
                "медицина, деньги. Отправь геолокацию, чтобы найти места рядом.\n\n"
                "/chooselanguage - сменить язык",
        "sim": "SIM-карта", "transport": "Транспорт", "documents": "Документы",
        "medicine": "Медицина", "money": "Деньги и банки", "emergency": "Экстренная помощь",
        "nearby": "📍 Рядом со мной", "language": "🌍 Сменить язык",
        "send_location": "📍 Отправить геолокацию",
        "nearby_ask": "Отправь свою геолокацию, и я найду места поблизости.",
        "nearby_choose": "Что ищем?",
        "pharmacy": "Аптека", "metro": "Метро", "mobile": "Салон связи",
        "atm": "Банкомат", "hospital": "Больница / клиника",
        "nearby_none": "В радиусе 1,5 км ничего такого не нашлось.",
        "nearby_title": "Ближайшие места:",
        "location_again": "Отправь геолокацию ещё раз, пожалуйста.",
        "thinking": "🔎 Ищу информацию…",
        "limit_user": "На сегодня лимит вопросов исчерпан. Попробуй завтра.",
        "limit_global": "Сегодня бот очень загружен. Попробуй завтра.",
        "error": "Что-то пошло не так. Попробуй чуть позже.",
        "open_map": "карта",
        "open_on_map": "🗺 Открыть на карте",
        "nearby_map": "Вот поиск на карте рядом с тобой:",
    },
    "zh": {
        "welcome": "👋 你好！我是 Help in Moscow，帮助你在莫斯科生活的助手。\n\n"
                   "请选择下面的主题，或直接用你自己的话提问。",
        "choose_language": "请选择语言：",
        "language_selected": "已选择语言：中文",
        "help": "你可以问我任何关于莫斯科生活的问题：交通、SIM卡、证件、医疗、钱。"
                "发送你的位置，我可以帮你找附近的地方。\n\n"
                "/chooselanguage - 更换语言",
        "sim": "SIM卡", "transport": "交通", "documents": "证件",
        "medicine": "医疗", "money": "钱和银行", "emergency": "紧急情况",
        "nearby": "📍 附近", "language": "🌍 选择语言",
        "send_location": "📍 发送我的位置",
        "nearby_ask": "请发送你的位置，我来帮你找附近的地方。",
        "nearby_choose": "你在找什么？",
        "pharmacy": "药店", "metro": "地铁", "mobile": "手机/SIM卡店",
        "atm": "ATM取款机", "hospital": "医院/诊所",
        "nearby_none": "在1.5公里内没有找到相关地点。",
        "nearby_title": "最近的地方：",
        "location_again": "请重新发送你的位置。",
        "thinking": "🔎 正在查找…",
        "limit_user": "你今天的提问次数已用完，请明天再试。",
        "limit_global": "今天机器人非常繁忙，请明天再试。",
        "error": "出了点问题，请稍后再试。",
        "open_map": "地图",
        "open_on_map": "🗺 在地图上打开",
        "nearby_map": "这是你附近的地图搜索：",
    },
    "ar": {
        "welcome": "👋 مرحبًا! أنا Help in Moscow، مساعدك للحياة في موسكو.\n\n"
                   "اختر موضوعًا من الأسفل أو اسألني أي سؤال بكلماتك.",
        "choose_language": "يرجى اختيار اللغة:",
        "language_selected": "تم اختيار اللغة: العربية",
        "help": "اسألني عن أي شيء يخص الحياة في موسكو: المواصلات، شرائح الاتصال، الوثائق، "
                "الطب، المال. أرسل موقعك لأجد لك الأماكن القريبة.\n\n"
                "/chooselanguage - تغيير اللغة",
        "sim": "شريحة الاتصال", "transport": "المواصلات", "documents": "الوثائق",
        "medicine": "الطب", "money": "المال والبنوك", "emergency": "الطوارئ",
        "nearby": "📍 بالقرب مني", "language": "🌍 اختيار اللغة",
        "send_location": "📍 إرسال موقعي",
        "nearby_ask": "أرسل لي موقعك وسأجد لك الأماكن القريبة.",
        "nearby_choose": "عمّ تبحث؟",
        "pharmacy": "صيدلية", "metro": "مترو", "mobile": "متجر هواتف وشرائح",
        "atm": "صراف آلي", "hospital": "مستشفى / عيادة",
        "nearby_none": "لم أجد شيئًا من هذا النوع ضمن 1.5 كم.",
        "nearby_title": "أقرب الأماكن:",
        "location_again": "يرجى إرسال موقعك مرة أخرى.",
        "thinking": "🔎 أبحث عن المعلومات…",
        "limit_user": "لقد وصلت إلى الحد اليومي للأسئلة. حاول مرة أخرى غدًا.",
        "limit_global": "البوت مشغول جدًا اليوم. حاول مرة أخرى غدًا.",
        "error": "حدث خطأ ما. حاول مرة أخرى بعد قليل.",
        "open_map": "الخريطة",
        "open_on_map": "🗺 افتح على الخريطة",
        "nearby_map": "إليك البحث على الخريطة بالقرب منك:",
    },
    "fr": {
        "welcome": "👋 Bonjour ! Je suis Help in Moscow, ton assistant pour la vie à Moscou.\n\n"
                   "Choisis un thème ci-dessous ou pose-moi simplement ta question.",
        "choose_language": "Veuillez choisir votre langue :",
        "language_selected": "Langue choisie : français",
        "help": "Pose-moi n'importe quelle question sur la vie à Moscou : transports, carte SIM, "
                "documents, santé, argent. Envoie ta position pour trouver des lieux à proximité.\n\n"
                "/chooselanguage - changer de langue",
        "sim": "Carte SIM", "transport": "Transports", "documents": "Documents",
        "medicine": "Santé", "money": "Argent et banques", "emergency": "Urgences",
        "nearby": "📍 À proximité", "language": "🌍 Choisir la langue",
        "send_location": "📍 Envoyer ma position",
        "nearby_ask": "Envoie-moi ta position et je trouverai des lieux à proximité.",
        "nearby_choose": "Que cherches-tu ?",
        "pharmacy": "Pharmacie", "metro": "Métro", "mobile": "Boutique téléphone/SIM",
        "atm": "Distributeur", "hospital": "Hôpital / clinique",
        "nearby_none": "Je n'ai rien trouvé de ce type à moins de 1,5 km.",
        "nearby_title": "Lieux les plus proches :",
        "location_again": "Envoie à nouveau ta position, s'il te plaît.",
        "thinking": "🔎 Je cherche…",
        "limit_user": "Tu as atteint la limite de questions pour aujourd'hui. Réessaie demain.",
        "limit_global": "Le bot est très sollicité aujourd'hui. Réessaie demain.",
        "error": "Une erreur s'est produite. Réessaie un peu plus tard.",
        "open_map": "carte",
        "open_on_map": "🗺 Ouvrir sur la carte",
        "nearby_map": "Voici une recherche sur la carte autour de toi :",
    },
    "es": {
        "welcome": "👋 ¡Hola! Soy Help in Moscow, tu asistente para la vida en Moscú.\n\n"
                   "Elige un tema abajo o simplemente hazme una pregunta con tus palabras.",
        "choose_language": "Por favor, elige tu idioma:",
        "language_selected": "Idioma seleccionado: español",
        "help": "Pregúntame lo que quieras sobre la vida en Moscú: transporte, tarjetas SIM, "
                "documentos, salud, dinero. Envía tu ubicación para encontrar lugares cercanos.\n\n"
                "/chooselanguage - cambiar idioma",
        "sim": "Tarjeta SIM", "transport": "Transporte", "documents": "Documentos",
        "medicine": "Salud", "money": "Dinero y bancos", "emergency": "Emergencias",
        "nearby": "📍 Cerca de mí", "language": "🌍 Elegir idioma",
        "send_location": "📍 Enviar mi ubicación",
        "nearby_ask": "Envíame tu ubicación y encontraré lugares cercanos.",
        "nearby_choose": "¿Qué buscas?",
        "pharmacy": "Farmacia", "metro": "Metro", "mobile": "Tienda de móviles/SIM",
        "atm": "Cajero automático", "hospital": "Hospital / clínica",
        "nearby_none": "No encontré nada de ese tipo en 1,5 km.",
        "nearby_title": "Lugares más cercanos:",
        "location_again": "Por favor, envía tu ubicación otra vez.",
        "thinking": "🔎 Buscando…",
        "limit_user": "Has alcanzado el límite de preguntas de hoy. Inténtalo mañana.",
        "limit_global": "El bot está muy ocupado hoy. Inténtalo mañana.",
        "error": "Algo salió mal. Inténtalo un poco más tarde.",
        "open_map": "mapa",
        "open_on_map": "🗺 Abrir en el mapa",
        "nearby_map": "Aquí tienes una búsqueda en el mapa cerca de ti:",
    },
    "hi": {
        "welcome": "👋 नमस्ते! मैं Help in Moscow हूँ, मॉस्को में जीवन के लिए आपका सहायक।\n\n"
                   "नीचे कोई विषय चुनें या बस अपने शब्दों में सवाल पूछें।",
        "choose_language": "कृपया अपनी भाषा चुनें:",
        "language_selected": "चुनी गई भाषा: हिन्दी",
        "help": "मॉस्को में जीवन के बारे में कुछ भी पूछें: परिवहन, सिम कार्ड, दस्तावेज़, "
                "दवा, पैसा। पास की जगहें ढूँढने के लिए अपनी लोकेशन भेजें।\n\n"
                "/chooselanguage - भाषा बदलें",
        "sim": "सिम कार्ड", "transport": "परिवहन", "documents": "दस्तावेज़",
        "medicine": "दवा और इलाज", "money": "पैसा और बैंक", "emergency": "आपातकाल",
        "nearby": "📍 मेरे पास", "language": "🌍 भाषा चुनें",
        "send_location": "📍 मेरी लोकेशन भेजें",
        "nearby_ask": "अपनी लोकेशन भेजें, मैं पास की जगहें ढूँढ दूँगा।",
        "nearby_choose": "आप क्या ढूँढ रहे हैं?",
        "pharmacy": "दवा की दुकान", "metro": "मेट्रो", "mobile": "मोबाइल/सिम की दुकान",
        "atm": "एटीएम", "hospital": "अस्पताल / क्लिनिक",
        "nearby_none": "1.5 किमी के अंदर ऐसा कुछ नहीं मिला।",
        "nearby_title": "सबसे पास की जगहें:",
        "location_again": "कृपया अपनी लोकेशन फिर से भेजें।",
        "thinking": "🔎 जानकारी ढूँढ रहा हूँ…",
        "limit_user": "आज के सवालों की सीमा पूरी हो गई। कृपया कल फिर कोशिश करें।",
        "limit_global": "आज बॉट बहुत व्यस्त है। कृपया कल फिर कोशिश करें।",
        "error": "कुछ गड़बड़ हो गई। कृपया थोड़ी देर बाद फिर कोशिश करें।",
        "open_map": "नक्शा",
        "open_on_map": "🗺 नक्शे पर खोलें",
        "nearby_map": "यह आपके आस-पास नक्शे पर खोज है:",
    },
    "fa": {
        "welcome": "👋 سلام! من Help in Moscow هستم، دستیار شما برای زندگی در مسکو.\n\n"
                   "یکی از موضوع‌های زیر را انتخاب کنید یا سؤال خود را با کلمات خودتان بپرسید.",
        "choose_language": "لطفاً زبان خود را انتخاب کنید:",
        "language_selected": "زبان انتخاب‌شده: فارسی",
        "help": "هر سؤالی درباره زندگی در مسکو دارید بپرسید: حمل‌ونقل، سیم‌کارت، مدارک، "
                "پزشکی، پول. برای پیدا کردن مکان‌های نزدیک، موقعیت خود را بفرستید.\n\n"
                "/chooselanguage - تغییر زبان",
        "sim": "سیم‌کارت", "transport": "حمل‌ونقل", "documents": "مدارک",
        "medicine": "پزشکی", "money": "پول و بانک", "emergency": "اورژانس",
        "nearby": "📍 نزدیک من", "language": "🌍 انتخاب زبان",
        "send_location": "📍 ارسال موقعیت من",
        "nearby_ask": "موقعیت خود را بفرستید تا مکان‌های نزدیک را پیدا کنم.",
        "nearby_choose": "دنبال چه چیزی هستید؟",
        "pharmacy": "داروخانه", "metro": "مترو", "mobile": "فروشگاه موبایل و سیم‌کارت",
        "atm": "خودپرداز", "hospital": "بیمارستان / کلینیک",
        "nearby_none": "در شعاع ۱٫۵ کیلومتر چیزی پیدا نشد.",
        "nearby_title": "نزدیک‌ترین مکان‌ها:",
        "location_again": "لطفاً دوباره موقعیت خود را بفرستید.",
        "thinking": "🔎 در حال جستجو…",
        "limit_user": "سقف سؤال‌های امروز شما پر شده است. لطفاً فردا دوباره امتحان کنید.",
        "limit_global": "ربات امروز خیلی شلوغ است. لطفاً فردا دوباره امتحان کنید.",
        "error": "مشکلی پیش آمد. لطفاً کمی بعد دوباره امتحان کنید.",
        "open_map": "نقشه",
        "open_on_map": "🗺 باز کردن روی نقشه",
        "nearby_map": "این جستجو روی نقشه در نزدیکی شماست:",
    },
    "tr": {
        "welcome": "👋 Merhaba! Ben Help in Moscow, Moskova'daki hayatın için asistanınım.\n\n"
                   "Aşağıdan bir konu seç ya da sorunu kendi kelimelerinle sor.",
        "choose_language": "Lütfen dilinizi seçin:",
        "language_selected": "Seçilen dil: Türkçe",
        "help": "Moskova'daki hayatla ilgili her şeyi sorabilirsin: ulaşım, SIM kart, belgeler, "
                "sağlık, para. Yakındaki yerleri bulmak için konumunu gönder.\n\n"
                "/chooselanguage - dili değiştir",
        "sim": "SIM kart", "transport": "Ulaşım", "documents": "Belgeler",
        "medicine": "Sağlık", "money": "Para ve bankalar", "emergency": "Acil durum",
        "nearby": "📍 Yakınımda", "language": "🌍 Dil seç",
        "send_location": "📍 Konumumu gönder",
        "nearby_ask": "Konumunu gönder, yakındaki yerleri bulayım.",
        "nearby_choose": "Ne arıyorsun?",
        "pharmacy": "Eczane", "metro": "Metro", "mobile": "Telefon/SIM mağazası",
        "atm": "ATM", "hospital": "Hastane / klinik",
        "nearby_none": "1,5 km içinde böyle bir yer bulamadım.",
        "nearby_title": "En yakın yerler:",
        "location_again": "Lütfen konumunu tekrar gönder.",
        "thinking": "🔎 Araştırıyorum…",
        "limit_user": "Bugünkü soru limitine ulaştın. Lütfen yarın tekrar dene.",
        "limit_global": "Bot bugün çok yoğun. Lütfen yarın tekrar dene.",
        "error": "Bir şeyler ters gitti. Lütfen biraz sonra tekrar dene.",
        "open_map": "harita",
        "open_on_map": "🗺 Haritada aç",
        "nearby_map": "Yakınındaki harita araması:",
    },
}


def t(lang: str, key: str) -> str:
    return T.get(lang, T[DEFAULT_LANG]).get(key) or T[DEFAULT_LANG][key]


def topic_label(lang: str, topic: str) -> str:
    return f"{TOPIC_EMOJI[topic]} {t(lang, topic)}"


def place_label(lang: str, category: str) -> str:
    return f"{PLACE_EMOJI[category]} {t(lang, category)}"


def language_name(lang: str) -> str:
    return LANGUAGES.get(lang, LANGUAGES[DEFAULT_LANG])[1]


def all_labels(key_fn) -> dict[str, str]:
    """Map every translated button label back to its key, for all languages."""
    result = {}
    for lang in LANGUAGES:
        for label, key in key_fn(lang):
            result[label] = key
    return result
