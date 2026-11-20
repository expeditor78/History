"""Собирает краткие пересказы истории России и обновляет общий офлайн-кеш."""
import json
from html import escape
from pathlib import Path

from build_rus import write_sw

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'site/russia'
TITLE = 'История России'


def label(lesson):
    return f'§ {lesson["number"]}. {lesson["title"]}'


def filename(lesson):
    return f'{int(lesson["number"].split("–")[0]):02d}.html'


def check(pair):
    question, answer = map(escape, pair)
    return f'<details><summary>Проверь себя: {question}</summary><div class="dbody"><p>{answer}</p></div></details>'


def page(title, body, lesson_id=''):
    reader = '<script defer src="../brief-nav.js"></script>' if lesson_id else ''
    return f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)}</title><link rel="stylesheet" href="../style.css"><link rel="stylesheet" href="../history.css">
<link rel="icon" href="../icon.svg" type="image/svg+xml"><link rel="manifest" href="../manifest.webmanifest">
<script src="../theme.js"></script>{reader}
<script>
if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost') && location.hostname !== 'appassets.androidplatform.net') {{
  navigator.serviceWorker.register('../sw.js').catch(() => {{}});
}}
</script></head>
<body data-history-id="{lesson_id}"><main class="russia">
{body}
</main></body></html>
'''


def index(chapters):
    links = ''.join(f'<a class="btn ghost" href="#chapter-{i}">Глава {roman}</a>'
                    for i, roman in enumerate(('I', 'II', 'III'), 1))
    body = [f'''<nav class="russia-links" aria-label="Другие разделы"><a href="../start.html">Все предметы</a> · <a href="../index.html">История Нового времени</a></nav>
<h1>{TITLE} · 7 класс</h1>
<p>Как Россия стала царством, пережила Смуту и изменилась при первых Романовых.</p>
<p>Выбери параграф. Прочитай пересказ по пунктам или целиком. Затем объясни главное своими словами и открой ответ для самопроверки.</p>
<nav class="russia-links" aria-label="Главы учебника">{links}</nav>''']
    for i, (roman, chapter) in enumerate(zip(('I', 'II', 'III'), chapters), 1):
        cards = '\n'.join(f'<a class="card" href="{filename(x)}"><span class="ct">{escape(label(x))}</span></a>'
                          for x in chapter['lessons'])
        body.append(f'''<section id="chapter-{i}">
<h2>{roman}. {escape(chapter['title'])}</h2>
<span class="history-source-note">С. {escape(chapter['pages'])} учебника</span>
<p>{escape(chapter['summary'])}</p>
{check(chapter['check'])}
<div class="grid">
{cards}
</div></section>''')
    body.append('<footer class="about">Самостоятельный краткий пересказ по учебнику В. Р. Мединского и А. В. Торкунова «История России», 7 класс. Указаны печатные страницы.</footer>')
    return page(f'{TITLE} · 7 класс', '\n'.join(body))


def render_lesson(chapter_number, lesson, prev, next_):
    title = escape(label(lesson))
    parts = '\n'.join(f'<section class="history-part"><h2 tabindex="-1">{i}. {escape(heading)}</h2><p>{escape(text)}</p></section>'
                      for i, (heading, text) in enumerate(lesson['sections'], 1))
    options = '\n'.join(f'<option value="{i}">{i + 1}. {escape(heading)}</option>'
                        for i, (heading, _) in enumerate(lesson['sections']))
    back = (f'<a href="{filename(prev)}">← § {escape(prev["number"])}</a>' if prev
            else '<a href="index.html">← Оглавление</a>')
    forward = (f'<a href="{filename(next_)}">§ {escape(next_["number"])} →</a>' if next_
               else '<a href="index.html">Оглавление →</a>')
    return page(f'{label(lesson)} — {TITLE}', f'''<nav class="russia-links" aria-label="Расположение в курсе"><a href="index.html">{TITLE}</a> · <a href="index.html#chapter-{chapter_number}">К главе</a></nav>
<h1>{title}</h1>
<p class="history-source-note">Учебник Мединского и Торкунова, с. {escape(lesson['pages'])}</p>
<div class="history-nav" id="history-nav" hidden>
<label for="history-select">Пункты учебника</label>
<select id="history-select">
{options}
</select>
<button id="history-all" type="button" aria-pressed="false">Весь пересказ</button><span id="history-counter" aria-live="polite"></span>
</div>
{parts}
<div class="history-controls" id="history-controls" hidden><button id="history-prev" type="button">← Назад</button><span id="history-step"></span><button id="history-next" type="button">Дальше →</button></div>
{check(lesson['check'])}
<nav class="pager" aria-label="Соседние параграфы">{back}{forward}</nav>''', f'russia-{filename(lesson)[:-5]}')


def main():
    chapters = [json.loads((ROOT / f'russia_src/{i}.json').read_text(encoding='utf-8')) for i in (1, 2, 3)]
    lessons = [(i, lesson) for i, chapter in enumerate(chapters, 1) for lesson in chapter['lessons']]
    coverage = []
    for _, lesson in lessons:
        bounds = list(map(int, lesson['number'].split('–')))
        coverage.extend(range(bounds[0], bounds[-1] + 1))
    if len(lessons) != 29 or coverage != list(range(1, 49)):
        raise ValueError('Ожидаются 29 уроков по §§ 1–48 в порядке учебника')
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'index.html').write_text(index(chapters), encoding='utf-8')
    for i, (chapter_number, lesson) in enumerate(lessons):
        prev = lessons[i - 1][1] if i else None
        next_ = lessons[i + 1][1] if i + 1 < len(lessons) else None
        (OUT / filename(lesson)).write_text(render_lesson(chapter_number, lesson, prev, next_), encoding='utf-8')
    write_sw()
    print(f'Собрано: {len(chapters)} главы, {len(lessons)} уроков')


if __name__ == '__main__':
    main()
