import os
import json
import hashlib
import random
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = "c0Cr7CY010ddee1b54438f20491db663"
CHANNEL_LINK = os.getenv("CHANNEL_LINK", "https://rubika.ir/giahanedaroi")
STATE_FILE = Path("state.json")

# هر گیاه یک لینک عکس ثابت ویکی‌مدیا دارد تا عکس اشتباه نرود
HERBS = [
    {"e": "🌿", "n": "آویشن", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/CommonThyme.jpg?width=800",
     "about": "آویشن یکی از معروف‌ترین گیاهان دارویی معطر است و از دیرباز برای مشکلات تنفسی در طب سنتی به کار می‌رود.",
     "benefits": ["کمک به تسکین سرفه و خلط‌آوری", "تقویت نسبی ایمنی در سرماخوردگی", "خاصیت ضدباکتریایی ملایم برای گلو", "عطر درمانی و باز کردن حس بویایی"],
     "harms": ["مصرف زیاد ممکن است معده را تحریک کند", "در بارداری بدون نظر پزشک توصیه نمی‌شود", "حساسیت به خانواده نعنا", "اسانس غلیظ خوراکی نیست"],
     "how": ["دم‌کرده روزی ۱ تا ۲ فنجان", "چند قطره اسانس رقیق در بخور", "با عسل برای گلودرد"]},
    {"e": "🌱", "n": "زنجبیل", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Ginger_root.jpg?width=800",
     "about": "زنجبیل ریشهٔ تند و گرمی است که برای هضم، تهوع و گرم کردن بدن در طب سنتی و آشپزی کاربرد دارد.",
     "benefits": ["کاهش حالت تهوع و تهوع سفر", "کمک به هضم و کاهش نفخ", "گرم‌کننده بدن", "بهبود گردش خون سطحی"],
     "harms": ["در زخم معده فعال ممکن است سوزش ایجاد کند", "تداخل احتمالی با رقیق‌کننده‌های خون", "مصرف خیلی زیاد باعث تپش می‌شود", "در سنگ صفرا احتیاط"],
     "how": ["چای زنجبیل تازه با عسل و لیمو", "رنده در غذا", "دمنوش قبل سفر"]},
    {"e": "🍃", "n": "نعناع", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Mentha_spicata1.jpg?width=800",
     "about": "نعناع گیاه خنک و معطری است که بیشتر برای گوارش و تازگی دهان شناخته می‌شود.",
     "benefits": ["کاهش نفخ و اسپاسم خفیف روده", "حس خنکی بعد از غذا", "کاهش موقت بوی بد دهان", "آرام‌بخش ملایم معده"],
     "harms": ["در ریفلاکس شدید گاهی علائم را بدتر می‌کند", "اسانس خالص نباید بلعیده شود", "کودکان خیلی کوچک اسانس غلیظ ممنوع", "حساسیت پوستی نادر"],
     "how": ["دم‌کرده بعد از غذا", "برگ تازه در سالاد", "استنشاق بخار ملایم"]},
    {"e": "🌼", "n": "بابونه", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Matricaria_recutita_flowers.jpg?width=800",
     "about": "بابونه گل آرامش‌بخش کلاسیک طب سنتی است و برای خواب و آرام کردن معده به کار می‌رود.",
     "benefits": ["کمک به آرامش و خواب", "تسکین التهاب خفیف معده", "آرام‌بخش اضطراب روزمره", "مفید برای پوست تحریک‌شده موضعی"],
     "harms": ["حساسیت در آلرژی به کاسنی", "خواب‌آلودگی در مصرف زیاد", "تداخل با داروهای آرام‌بخش", "در بارداری زیاده‌روی نشود"],
     "how": ["دم‌کرده شب قبل خواب", "با کمی عسل", "کمپرس خنک برای پوست"]},
    {"e": "🌰", "n": "شیرین‌بیان", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Glycyrrhiza_glabra_seeds.jpg?width=800",
     "about": "شیرین‌بیان ریشهٔ شیرین دارویی است که برای گلو و معده شهرت دارد؛ مصرفش باید محدود باشد.",
     "benefits": ["تسکین گلودرد و سرفه خشک", "آرامش مخاط معده خفیف", "طعم‌دهنده دمنوش", "کمک به سرفه خشک"],
     "harms": ["افزایش فشار خون در مصرف طولانی", "احتباس آب و افت پتاسیم", "برای فشارخونی و باردار خطرناک‌تر", "بیش از چند روز متوالی بدون پزشک نه"],
     "how": ["دم‌کرده رقیق کوتاه‌مدت", "حداکثر چند روز", "ترکیب ملایم با آویشن"]},
    {"e": "🌿", "n": "رزماری", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Rosemary_bush.jpg?width=800",
     "about": "رزماری گیاه مدیترانه‌ای معطر است برای تمرکز، گردش خون و عطر درمانی.",
     "benefits": ["کمک به هوشیاری و تمرکز", "بهبود گردش خون موضعی", "عطر درمانی", "تقویت حس شادابی"],
     "harms": ["اسانس غلیظ در بارداری و صرع ممنوع", "مصرف خوراکی خیلی زیاد تحریک‌کننده", "حساسیت پوستی ممکن", "روی زخم باز نزنید"],
     "how": ["دم‌کرده صبحگاهی رقیق", "روغن رقیق ماساژ پوست سر", "استنشاق عطر"]},
    {"e": "🍃", "n": "اسطوخودوس", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Lavandula_angustifolia_001.JPG?width=800",
     "about": "اسطوخودوس با عطر آرامش‌بخش برای استرس و خواب یکی از محبوب‌ترین گیاهان است.",
     "benefits": ["کاهش استرس و تنش", "کمک به به خواب رفتن", "تسکین سردرد تنش‌زا", "عطر آرامش‌بخش محیط"],
     "harms": ["اسانس خالص خوراکی نیست", "حساسیت پوستی در برخی", "افت فشار خفیف با مصرف زیاد", "جایگزین درمان نیست"],
     "how": ["کیسه خشک کنار بالش", "چند قطره در بخور", "آب حمام با اسانس رقیق"]},
    {"e": "🌱", "n": "زردچوبه", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Curcuma_longa_roots.jpg?width=800",
     "about": "زردچوبه ادویه طلایی ضدالتهاب است؛ کورکومین آن بیشتر مورد توجه است.",
     "benefits": ["کمک به کاهش التهاب خفیف", "پشتیبانی از مفاصل", "آنتی‌اکسیدان غذایی", "سلامت کبد در سنت گیاهی"],
     "harms": ["تداخل با ضد انعقاد", "در سنگ کیسه صفرا احتیاط", "معده را در دوز بالا اذیت می‌کند", "جذب بدون چربی و فلفل کم است"],
     "how": ["با فلفل سیاه و کمی روغن", "در غذا یا شیر طلایی", "دوز غذایی نه دارویی خودسرانه"]},
    {"e": "🌿", "n": "گزنه", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Urtica_dioica_0.7_R.jpg?width=800",
     "about": "گزنه غنی از مواد معدنی است و در طب سنتی برای خون‌سازی و پاکسازی معروف است.",
     "benefits": ["منبع گیاهی آهن", "کمک در کم‌خونی تغذیه‌ای خفیف", "ادرارآور ملایم", "تقویت مو و ناخن در سنت"],
     "harms": ["برگ تازه پوست را می‌سوزاند", "ممکن است فشار را کمی پایین بیاورد", "تداخل با ادرارآورها", "فقط برگ خشک یا پخته خوراکی"],
     "how": ["دم‌کرده برگ خشک دوره‌ای", "برگ جوان کاملاً پخته", "نه به صورت خام"]},
    {"e": "🌼", "n": "گل گاوزبان", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Borago_officinalis_001.JPG?width=800",
     "about": "گل گاوزبان در فرهنگ ایرانی نماد آرامش اعصاب است و اغلب با لیموترش مصرف می‌شود.",
     "benefits": ["آرام‌بخش ملایم اعصاب", "کمک به حس سبکی در تنش", "دمنوش عصرگاهی", "تقویت روحیه در سنت ایرانی"],
     "harms": ["مصرف طولانی بدون وقفه توصیه نمی‌شود", "بیماری کبدی: مشورت با پزشک", "در بارداری محدود", "جایگزین دارو نیست"],
     "how": ["دم‌کرده با لیموترش", "عصرها یک فنجان", "دوره‌ای نه دائمی"]},
    {"e": "🍃", "n": "پونه", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Mentha_pulegium_001.JPG?width=800",
     "about": "پونه عطر تند دارد و در آش ایرانی برای گوارش و سرماخوردگی به کار می‌رود.",
     "benefits": ["کاهش نفخ و سنگینی", "کمک در سرماخوردگی خفیف", "عطر غذا", "هضم بعد از غذای چرب"],
     "harms": ["اسانس غلیظ سمی است", "در بارداری ممنوع", "دمنوش غلیظ طولانی نه", "فقط مصرف غذایی یا دمنوش ملایم"],
     "how": ["دم‌کرده ملایم بعد از غذا", "پاشیدن خشک روی آش", "هرگز اسانس خالص"]},
    {"e": "🌱", "n": "دارچین", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Cinnamomum_verum_spices.jpg?width=800",
     "about": "دارچین ادویه گرم خوش‌عطر است که در سنت گیاهی با قند خون و گرمی بدن پیوند دارد.",
     "benefits": ["کمک به پاسخ بهتر قند خون همراه غذا", "گرم‌کننده و ضدنفخ ملایم", "طعم بدون شکر زیاد", "عطر چای و شیرینی"],
     "harms": ["کاسیا کومارین بالا دارد؛ زیاد به کبد فشار می‌آورد", "در بارداری زیاده‌روی نشود", "پودر زیاد دهان را تحریک می‌کند", "نوع سیلان در مصرف مداوم بهتر است"],
     "how": ["تکه کوچک در چای", "پودر روی جو دوسر", "نه قاشق‌های پر هر روز"]},
    {"e": "🌿", "n": "شوید", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Anethum_graveolens_002.JPG?width=800",
     "about": "شوید سبزی سفره و گیاه سنتی برای آرام کردن شکم و نفخ است.",
     "benefits": ["کاهش نفخ", "کمک به هضم غذای سنگین", "آرام‌بخش ملایم گوارش", "عطر ماست و خورشت"],
     "harms": ["دانه خیلی زیاد ممکن است حساسیت دهد", "افت فشار: احتیاط", "زیاده‌روی نکنید", "جایگزین درمان نیست"],
     "how": ["دم‌کرده تخم یا برگ بعد از غذا", "در ماست و خورشت", "دمنوش رقیق"]},
    {"e": "🌱", "n": "رازیانه", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Foeniculum_vulgare_seed.jpg?width=800",
     "about": "رازیانه طعم شیرین انیسون‌مانند دارد و برای گوارش در سنت گیاهی به کار می‌رود.",
     "benefits": ["کاهش نفخ و اسپاسم روده", "کمک به هضم", "دمنوش بعد از غذا", "طعم ملایم دمنوش"],
     "harms": ["سرطان‌های حساس به هورمون: مشورت پزشک", "دانه خیلی زیاد نه", "حساسیت نادر", "در بارداری خودسرانه نه"],
     "how": ["دم‌کرده دانه", "جویدن کمی بعد از غذا", "دمنوش رقیق"]},
    {"e": "🍃", "n": "بادرنجبویه", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Melissa_officinalis_002.JPG?width=800",
     "about": "بادرنجبویه عطر لیمویی دارد و بیشتر برای اضطراب و خواب استفاده می‌شود.",
     "benefits": ["کاهش اضطراب خفیف", "کمک به خواب آرام‌تر", "تسکین سردرد تنش‌زا", "آرام‌بخش عصبی ملایم"],
     "harms": ["تداخل احتمالی با داروهای تیروئید", "خواب‌آلودگی در دوز بالا", "کم‌کاری تیروئید: احتیاط", "جایگزین دارو نیست"],
     "how": ["دم‌کرده شب", "ترکیب با بابونه", "یک فنجان عصر"]},
    {"e": "🌼", "n": "گل محمدی", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Rosa_×_damascena.jpg?width=800",
     "about": "گل محمدی علاوه بر گلاب برای آرامش و طراوت روح و پوست در طب سنتی جایگاه دارد.",
     "benefits": ["آرام‌بخش ملایم خلق", "عطر درمانی", "گلاب برای پوست", "شربت و دمنوش سنتی"],
     "harms": ["حساسیت بویایی", "گلاب تقلبی مفید نیست", "گل خشک نامطمئن ممکن است آلوده باشد", "فقط منبع معتبر"],
     "how": ["دم‌کرده گلبرگ", "گلاب اصل", "شربت رقیق"]},
    {"e": "🌿", "n": "مرزنجوش", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Origanum_majorana_002.JPG?width=800",
     "about": "مرزنجوش گیاه معطر مدیترانه‌ای برای سرفه و آرامش تنفسی در گیاه‌درمانی است.",
     "benefits": ["کمک به راحتی تنفس در سرماخوردگی خفیف", "ضدنفخ ملایم", "عطر غذا", "دمنوش گرم زمستانی"],
     "harms": ["در بارداری زیاده‌روی نشود", "اسانس غلیظ خوراکی نیست", "حساسیت گیاهی", "دوز غذایی رعایت شود"],
     "how": ["دم‌کرده رقیق", "در غذا به مقدار ادویه", "بخور ملایم"]},
    {"e": "🌱", "n": "زیره سبز", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Cuminum_cyminum_seeds.jpg?width=800",
     "about": "زیره سبز ادویه اصلی آشپزی ایرانی است و برای نفخ و سنگینی معده شهرت دارد.",
     "benefits": ["کاهش نفخ بعد از غذا", "کمک به هضم حبوبات", "گرم‌کننده ملایم معده", "عطر خورشت"],
     "harms": ["خیلی زیاد سوزش سر دل می‌دهد", "در ریفلاکس شدید گاهی آزاردهنده", "دوز دارویی خودسرانه نه", "با آب کافی"],
     "how": ["دم‌کرده بعد از غذا", "بو داده آسیاب روی غذا", "یک فنجان دمنوش"]},
    {"e": "🍃", "n": "به‌لیمو", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Aloysia_citrodora.jpg?width=800",
     "about": "به‌لیمو عطر لیموی لطیف دارد و دمنوش محبوب عصر و آرامش است.",
     "benefits": ["کاهش تنش عصبی", "کمک به خواب سبک", "هضم ملایم", "عطر دلپذیر دمنوش"],
     "harms": ["داده ایمنی بلندمدت محدود", "حساسیت نادر", "جایگزین درمان نیست", "زیاده‌روی لازم نیست"],
     "how": ["دم‌کرده عصر یا شب", "با عسل", "یک فنجان"]},
    {"e": "🌼", "n": "گل ختمی", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Alcea_rosea1.jpg?width=800",
     "about": "گل ختمی برای نرم کردن مخاط گلو در سرفه‌های خشک سنتی معروف است.",
     "benefits": ["تسکین خشکی گلو", "کمک به سرفه خشک", "نرم‌کننده مخاط", "غرغره ملایم"],
     "harms": ["ممکن است جذب دارو را کم کند", "با فاصله از دارو مصرف شود", "کودکان فقط با پزشک", "منبع تمیز استفاده کنید"],
     "how": ["دم‌کرده یا خیساندن سرد", "غرغره ملایم", "روزانه کوتاه‌مدت"]},
    {"e": "🌱", "n": "سیاه‌دانه", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Nigella_sativa_seed.jpg?width=800",
     "about": "سیاه‌دانه در متون سنتی جایگاه ویژه‌ای دارد و برای ایمنی و التهاب به کار می‌رود.",
     "benefits": ["پشتیبانی از پاسخ ایمنی", "ضدالتهاب سنتی", "مصرف با عسل", "سلامت تنفسی در سنت"],
     "harms": ["بارداری: خودسرانه نه", "با داروهای فشار و قند مشورت", "روغن زیاد معده را اذیت می‌کند", "دوز کم کافی است"],
     "how": ["نصف قاشق چای‌خوری با عسل", "روغن به مقدار کم", "نه مشت‌مشت"]},
    {"e": "🍃", "n": "تخم کتان", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Flax_seed.jpg?width=800",
     "about": "تخم کتان منبع امگا۳ گیاهی و فیبر است و برای یبوست و قلب مطرح است.",
     "benefits": ["کمک به نظم اجابت مزاج", "فیبر مفید", "اسیدهای چرب گیاهی", "سلامت روده"],
     "harms": ["بدون آب کافی مشکل‌ساز است", "انسداد روده: ممنوع", "خام خیلی زیاد سنگین است", "با مایعات زیاد"],
     "how": ["یک قاشق خیس‌شده صبح", "پودر تازه روی ماست", "همیشه با آب زیاد"]},
    {"e": "🌿", "n": "مریم‌گلی", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Salvia_officinalis_0.JPG?width=800",
     "about": "مریم‌گلی برای غرغره گلودرد و کاهش تعریق در گیاه‌درمانی شناخته شده است.",
     "benefits": ["غرغره گلودرد", "کاهش تعریق زیاد", "عطر غذاهای گوشتی", "ضدمیکروب سنتی دهان"],
     "harms": ["مصرف خوراکی طولانی خطرناک است", "بارداری و شیردهی محدود", "صرع و فشار بالا احتیاط", "فقط کوتاه‌مدت"],
     "how": ["غرغره دم‌کرده رقیق", "خوراکی فقط کم و کوتاه", "نه هر روز ماه‌ها"]},
    {"e": "🌱", "n": "هل", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Elettaria_cardamomum_seeds.jpg?width=800",
     "about": "هل ادویه خوش‌عطر برای هضم و خوشبویی دهان در چای و شیرینی است.",
     "benefits": ["کاهش بوی بد دهان", "کمک به هضم", "عطر چای", "ضدنفخ ملایم"],
     "harms": ["سنگ صفرا: احتیاط", "خیلی زیاد سوزش می‌دهد", "حساسیت نادر", "دوز غذایی کافی است"],
     "how": ["دانه در چای", "جویدن بعد از غذا", "با دارچین در دمنوش"]},
    {"e": "🍃", "n": "چای سبز", "img": "https://commons.wikimedia.org/wiki/Special:FilePath/Green_tea_leaves.jpg?width=800",
     "about": "چای سبز نوشیدنی آنتی‌اکسیدانی با کافئین ملایم برای تمرکز و متابولیسم است.",
     "benefits": ["آنتی‌اکسیدان کاتچین", "هوشیاری ملایم", "بخشی از سبک زندگی سالم", "کمک به تمرکز"],
     "harms": ["کافئین برای بی‌خوابی‌ها مشکل است", "ناشتا گاهی سوزش معده", "تداخل جذب آهن", "عصر دیر ننوشید"],
     "how": ["آب داغ نه جوش؛ ۱–۲ فنجان", "بین وعده‌ها", "نه با غذای آهن‌دار"]},
]

STYLES = [
    "امروز دربارهٔ این گیاه بیشتر بدانیم:",
    "آشنایی دقیق‌تر با یک گیاه پرکاربرد:",
    "راهنمای کاربردی و ایمن برای مصرف:",
    "از خواص تا احتیاط‌ها در یک نگاه:",
    "نکات مهم قبل از مصرف این گیاه:",
    "مرور کوتاه آموزشی دربارهٔ این گیاه:",
    "اگر به درمان گیاهی علاقه دارید:",
    "خلاصهٔ مفید و ایمن برای استفاده روزمره:",
]

def build_post(herb, bi, hi, wi, si):
    benefits, harms = herb["benefits"], herb["harms"]
    b = benefits[bi % len(benefits)]
    h = harms[hi % len(harms)]
    w = herb["how"][wi % len(herb["how"])]
    st = STYLES[si % len(STYLES)]
    other_b = [x for i, x in enumerate(benefits) if i != bi % len(benefits)][:2]
    other_h = [x for i, x in enumerate(harms) if i != hi % len(harms)][:2]
    text = (
        f"{herb['e']} {herb['n']}\n\n{st}\n\n{herb['about']}\n\n"
        f"✅ خواص و موارد مفید:\n• {b}\n" + "".join(f"• {x}\n" for x in other_b)
        + f"\n⚠️ مضرات و احتیاط‌ها:\n• {h}\n" + "".join(f"• {x}\n" for x in other_h)
        + f"\n📌 روش مصرف پیشنهادی:\n{w}\n\n"
        f"💬 جنبهٔ آموزشی دارد و جایگزین تشخیص و درمان پزشکی نیست.\n\n"
        f"🔗 کانال گیاهان دارویی ارسباران:\n{CHANNEL_LINK}"
    )
    key = hashlib.md5(f"{herb['n']}|{bi}|{hi}|{wi}|{si}".encode()).hexdigest()[:16]
    return key, text, herb

def all_variants():
    items = []
    for herb in HERBS:
        for bi in range(len(herb["benefits"])):
            for hi in range(len(herb["harms"])):
                for wi in range(len(herb["how"])):
                    for si in range(len(STYLES)):
                        items.append(build_post(herb, bi, hi, wi, si))
    seen, unique = set(), []
    for key, text, herb in items:
        if key not in seen:
            seen.add(key)
            unique.append((key, text, herb))
    unique.sort(key=lambda x: x[0])
    return unique

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"used": [], "cycle": 1}

def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def pick_variant(variants, state):
    used = set(state.get("used", []))
    available = [v for v in variants if v[0] not in used]
    if not available:
        state["used"] = []
        state["cycle"] = state.get("cycle", 1) + 1
        available = list(variants)
        print(f"♻️ دوره جدید: cycle={state['cycle']}")
    return random.choice(available), state

def is_within_posting_hours():
    # فقط ۸ صبح تا ۲۳ (۱۱ شب) به وقت تهران — هر ساعت یک پست
    now = datetime.now(ZoneInfo("Asia/Tehran"))
    return 8 <= now.hour <= 23

def download_image(herb):
    """فقط لینک ثابت همان گیاه — عکس قاطی نمی‌شود"""
    url = herb["img"]
    path = Path(f"/tmp/herb_{hashlib.md5(herb['n'].encode()).hexdigest()[:8]}.jpg")
    try:
        r = requests.get(url, timeout=45, allow_redirects=True, headers={"User-Agent": "HerbalBot/1.0 (educational)"})
        if r.status_code == 200 and len(r.content) > 3000:
            path.write_bytes(r.content)
            return path
        print("download status", r.status_code, len(r.content))
    except Exception as e:
        print("download fail", e)
    return None

def upload_image(path: Path):
    r = requests.post(f"https://botapi.rubika.ir/v3/{TOKEN}/requestSendFile", json={"type": "Image"}, timeout=30)
    data = r.json()
    print("requestSendFile:", data)
    if not isinstance(data, dict) or data.get("status") != "OK":
        return None
    upload_url = data.get("data", {}).get("upload_url")
    if not upload_url:
        return None
    with open(path, "rb") as f:
        up = requests.post(upload_url, files={"file": (path.name, f, "image/jpeg")}, timeout=60)
    up_data = up.json()
    print("upload:", up_data)
    if isinstance(up_data, dict):
        return up_data.get("data", {}).get("file_id") or up_data.get("file_id")
    return None

def send_file(file_id, caption):
    r = requests.post(
        f"https://botapi.rubika.ir/v3/{TOKEN}/sendFile",
        json={"chat_id": CHAT_ID, "file_id": file_id, "text": caption},
        timeout=30,
    )
    return r.json()

def send_message(text):
    r = requests.post(
        f"https://botapi.rubika.ir/v3/{TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": text},
        timeout=30,
    )
    return r.json()

def main():
    if not TOKEN:
        print("❌ BOT_TOKEN نیست")
        return
    if not is_within_posting_hours():
        print("⏰ خارج از ساعت ۸ تا ۲۳ تهران — ارسال نشد")
        return

    variants = all_variants()
    state = load_state()
    (key, caption, herb), state = pick_variant(variants, state)

    print(f"واریانت یکتا: {len(variants)} | رفته: {len(state.get('used', []))} | دوره: {state.get('cycle', 1)}")
    print(f"گیاه: {herb['n']} | عکس ثابت مربوط به همین گیاه")
    print(caption[:120], "...")

    result = None
    img_path = download_image(herb)
    if img_path:
        file_id = upload_image(img_path)
        if file_id:
            result = send_file(file_id, caption)
            print("sendFile:", result)
        else:
            print("آپلود ناموفق — متنی")
            result = send_message(caption)
    else:
        print("دانلود ناموفق — متنی")
        result = send_message(caption)

    print("نتیجه:", result)
    if isinstance(result, dict) and result.get("status") == "OK":
        state.setdefault("used", []).append(key)
        save_state(state)
        print(f"✅ باقی‌مانده تقریبی این دوره: {len(variants) - len(state['used'])}")
    else:
        print("⚠️ ارسال ناموفق؛ state عوض نشد")

if __name__ == "__main__":
    main()
