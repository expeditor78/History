# История Нового времени, 7 класс — по-человечески

Статический сайт для занятий: 21 шпаргалка, интерактивные тесты, лента времени, видеоразбор к каждому параграфу, прогресс в браузере.

- Сайт — папка `site/` (открыть `site/index.html`).
- Видео — словарь `VIDEOS` в `build.py` (ролики YouTube встраиваются в страницы при сборке).
- Пересборка из выгрузки Notion: `python3 build.py` (файлы из `dist_src/` копируются в `site/` автоматически).
- Деплой: GitHub Pages, воркфлоу `.github/workflows/pages.yml`.

## Android-приложение

Папка `android/` — оболочка на WebView, которая берёт сайт из `site/` и работает без интернета (кроме видео).

- Сборка в GitHub: Actions → **Build Android APK** → Run workflow; готовый `app-debug.apk` будет в Artifacts.
- Локально: `cd android && gradle assembleDebug` (JDK 17, Android SDK 34).
- После изменения сайта пересоберите APK, чтобы обновить содержимое.

Если сайт открывается по своему домену с заголовком Content-Security-Policy, добавьте `frame-src https://www.youtube-nocookie.com`, иначе видео будут заблокированы.
