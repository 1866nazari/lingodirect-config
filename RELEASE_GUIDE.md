راهنمای انتشار نسخه جدید LingoDirect
این راهنما مسیر کامل انتشار نسخه جدید، از تغییر نسخه در پروژه اندروید تا انتشار APK و به‌روزرسانی update.json را مشخص می‌کند.

۱. تعیین نسخه جدید
در فایل app/build.gradle مقدار نسخه را افزایش دهید:

gradle
defaultConfig {
    versionCode 8
    versionName "1.0.8"
}
versionCode: عدد صحیح و همیشه صعودی است. سیستم به‌روزرسانی نسخه‌ها را با این عدد مقایسه می‌کند.
versionName: نام نمایشی نسخه برای کاربر است.
نمونه ترتیب صحیح:

versionCode: 6 → 7 → 8
versionName: 1.0.6 → 1.0.7 → 1.0.8
هیچ‌گاه برای نسخه جدید، versionCode قبلی را تکرار نکنید.

۲. ساخت APK نسخه Release
در Android Studio مسیر زیر را اجرا کنید:

Build
→ Generate Signed Bundle / APK
→ APK
→ Next
→ release
→ Create
تمام نسخه‌های تولیدی باید با همان Release Keystore نسخه‌های قبلی امضا شوند. تغییر Keystore باعث می‌شود نسخه جدید روی نسخه قبلی نصب نشود.

فایل خروجی را به این الگو نام‌گذاری کنید:

LingoDirect-1.0.8.apk
در این مرحله از APK ساخته‌شده توسط دکمه Run استفاده نکنید، چون آن APK معمولاً با کلید Debug امضا شده است.

۳. بررسی APK قبل از انتشار
قبل از بارگذاری، این موارد را بررسی کنید:

فایل APK از نوع release باشد.
فایل با Release Keystore همیشگی امضا شده باشد.
versionCode و versionName صحیح باشند.
فایل روی نسخه Release قبلی قابل نصب باشد.
نام فایل دقیقاً با نامی که در لینک دانلود استفاده می‌شود مطابقت داشته باشد.

۴. ساخت GitHub Release
آدرس Releases را باز کنید:

https://github.com/1866nazari/lingodirect-config/releases

سپس مراحل زیر را انجام دهید:

روی Draft a new release بزنید.
در Select tag تگ نسخه جدید را بسازید:

v1.0.8
عنوان Release را وارد کنید:

LingoDirect 1.0.8
توضیحات دوزبانه را وارد کنید:

LingoDirect version 1.0.8

- بهبود پایداری و عملکرد برنامه
- رفع خطاهای گزارش‌شده

- Improved application stability and performance
- Fixed reported issues

فایل زیر را به قسمت Attach binaries اضافه کنید:

LingoDirect-1.0.8.apk

گزینه زیر را فعال نگه دارید:

Set as the latest release
روی Publish release بزنید.

۵. بررسی لینک دانلود APK
پس از انتشار، لینک مستقیم باید از الگوی زیر پیروی کند:

https://github.com/1866nazari/lingodirect-config/releases/download/v1.0.8/LingoDirect-1.0.8.apk
قبل از تغییر update.json، لینک را در مرورگر باز کنید و مطمئن شوید دانلود APK واقعاً شروع می‌شود.

نام تگ و نام فایل به حروف بزرگ و کوچک حساس هستند و باید دقیقاً مطابق Release باشند.

۶. به‌روزرسانی update.json
فایل زیر را ویرایش کنید:

D:\Android\Projects\lingodirect-config\update.json
مقادیر نسخه، لینک APK، هش و توضیحات را تغییر دهید:


{
  "latest_version_name": "1.0.8",
  "latest_version_code": 8,
  "force_update": false,
  "apk_url": "https://github.com/1866nazari/lingodirect-config/releases/download/v1.0.8/LingoDirect-1.0.8.apk",
  "apk_sha256": "bdd21c64941b07bbab58f51f3e013296d88d95a3ac99660d89c346ee3a3d4aa1",

  "title_fa": "نسخه جدید LingoDirect آماده است",
  "title_en": "A new version of LingoDirect is available",

  "message_fa": "نسخه جدید LingoDirect شامل بهبود عملکرد و رفع برخی خطاها است.",
  "message_en": "The new version of LingoDirect includes performance improvements and bug fixes.",

  "release_notes_fa": [
    "بهبود پایداری و عملکرد برنامه",
    "رفع خطاهای گزارش‌شده"
  ],
  "release_notes_en": [
    "Improved application stability and performance",
    "Fixed reported issues"
  ],

  "positive_button_fa": "به‌روزرسانی",
  "positive_button_en": "Update"
}

سیاست Force Update

برای آپدیت معمولی:
"force_update": false

برای آپدیت اجباری:
"force_update": true

از true فقط برای نسخه‌های ضروری مانند اصلاح امنیتی، خرابی جدی یا ناسازگاری نسخه قبلی استفاده کنید. بهتر است انتشار اولیه همیشه با false انجام و ابتدا روند دانلود و نصب آزمایش شود.

۷. ثبت update.json در Git
یک CMD جدید باز کرده و دستورات زیر را به‌ترتیب اجرا کنید:

cd /d D:\Android\Projects\lingodirect-config
git status
git add update.json
git status
git commit -m "Prepare update manifest for LingoDirect 1.0.8"
git push origin clean-history

قبل از git add، خروجی git status را بررسی کنید تا فایل ناخواسته‌ای وارد Commit نشود.

۸. بررسی GitHub Pages
پس از Push، آدرس زیر را در مرورگر باز کنید:

https://1866nazari.github.io/lingodirect-config/update.json

بررسی کنید که مقادیر زیر مربوط به نسخه جدید باشند:

latest_version_name = 1.0.8
latest_version_code = 8
force_update = false
"apk_url": "https://github.com/1866nazari/lingodirect-config/releases/download/v1.0.8/LingoDirect-1.0.8.apk",
"apk_sha256": "bdd21c64941b07bbab58f51f3e013296d88d95a3ac99660d89c346ee3a3d4aa1",

اگر نسخه قدیمی نمایش داده شد، چند دقیقه صبر کنید یا آدرس را با پارامتر موقت باز کنید:

https://1866nazari.github.io/lingodirect-config/update.json?t=1008
پارامتر t فقط برای دور زدن Cache مرورگر است و نباید در کد اپ ثبت شود.

۹. تست نهایی به‌روزرسانی
برای آزمایش واقعی:

نسخه Release قبلی، مثلاً 1.0.7، را روی گوشی نصب کنید.
اپ را از Android Studio با Run نصب نکنید.
نسخه قبلی را روی گوشی باز کنید.
نمایش دیالوگ دوزبانه به‌روزرسانی را بررسی کنید.
دانلود APK را آغاز کنید.
موفقیت اعتبارسنجی SHA-256 را بررسی کنید.
نصب نسخه جدید روی نسخه قبلی را انجام دهید.
پس از نصب، نسخه نمایش‌داده‌شده در About را بررسی کنید.
داده‌ها و تنظیمات قبلی برنامه را بررسی کنید.
اپ را دوباره اجرا و مطمئن شوید دیگر دیالوگ همان نسخه نمایش داده نمی‌شود.

برای مشاهده Logcat نسخه Release لازم نیست اپ را با Android Studio اجرا کنید. گوشی را متصل کرده، اپ را دستی باز کنید و اجرا کنید.

قاعده حیاتی انتشار:
ابتدا APK نهایی را بسازید و GitHub Release را منتشر کنید؛
فقط بعد از اطمینان از صحت لینک دانلود و SHA-256، فایل update.json را به نسخه جدید تغییر دهید.
چون به‌محض انتشار update.json، کاربران نسخه قبلی اعلان به‌روزرسانی را دریافت می‌کنند.

