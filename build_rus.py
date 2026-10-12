# -*- coding: utf-8 -*-
"""Сборка раздела «Русский язык» в site/rus/ (исходники — rus_src/).
Запуск: python3 build_rus.py  — пересобирает только site/rus/ и обновляет site/sw.js.
Вызывается также из build.py."""
import os, sys, json, html, shutil, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'rus_src')
OUT = os.path.join(HERE, 'site')
sys.path.insert(0, SRC)
import content1, content2, content3

TOPICS = content1.TOPICS + content2.TOPICS
LET = 'АБВГД'
ABOUT = ('<footer class="about">💡 Идея и составление: <b>Алексей</b> · '
         '<a href="https://github.com/expeditor78" target="_blank" rel="noopener">GitHub: expeditor78</a></footer>')

def esc(t): return html.escape(t, quote=False)

def nav(active):
    h = [f'<nav class="side" id="side" data-total="{len(TOPICS)}"><a class="brand" href="index.html">📝 Русский язык<small>7 класс</small></a>',
         '<a class="nl" href="../index.html">← История Нового времени</a>',
         f'<div class="prog"><div class="bar"><i id="gbar"></i></div><span id="gtxt">0 из {len(TOPICS)}</span></div>']
    for f, t in [('practice.html', '🧪 Практикум'), ('test.html', '✅ Итоговый тест'), ('cheat.html', '📋 Шпаргалка и термины')]:
        h.append(f'<a class="nl {"on" if active == f else ""}" href="{f}">{t}</a>')
    h.append('<div class="chh" style="--c:#2783DE">Темы</div>')
    for t in TOPICS:
        f = t['slug'] + '.html'
        h.append(f'<a class="nl {"on" if active == f else ""}" data-t="{t["slug"]}" href="{f}"><span class="dot"></span>{t["icon"]} {esc(t["title"])}</a>')
    h.append('</nav>')
    return '\n'.join(h)

def page(title, body, active):
    return f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} — Русский язык, 7 класс</title><link rel="stylesheet" href="../style.css"><link rel="stylesheet" href="rus.css"><link rel="manifest" href="../manifest.webmanifest"><meta name="theme-color" content="#2783DE"><link rel="icon" href="../icon.svg" type="image/svg+xml"></head>
<body><header class="top"><button id="menu" aria-label="Меню">☰</button><span>Русский язык · 7 класс</span></header>
{nav(active)}<main>{body}{ABOUT}</main><script src="rus.js" defer></script></body></html>'''

def quiz(qid, items, tags=None):
    h = [f'<div class="rq" data-id="{qid}">']
    for n, q in enumerate(items, 1):
        tag = f'<span class="tag">{esc(tags[n-1])}</span>' if tags else ''
        h.append(f'<div class="q" data-a="{q["a"]}">{tag}<p class="qt"><span class="qn">{n}</span>{esc(q["q"])}</p><div class="opts">')
        for i, o in enumerate(q['o']):
            h.append(f'<button class="opt" data-i="{i}"><b>{LET[i]}</b>{esc(o)}</button>')
        h.append(f'</div><p class="expl" hidden>{esc(q["e"])}</p></div>')
    h.append('<div class="score" aria-live="polite"></div></div>')
    return '\n'.join(h)

def build():
    out = os.path.join(OUT, 'rus')
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    for f in ('rus.css', 'rus.js'):
        shutil.copy(os.path.join(SRC, f), os.path.join(out, f))
    order = [t['slug'] for t in TOPICS]

    # страницы тем
    for i, t in enumerate(TOPICS):
        secs = ''.join(f'<h2>{esc(h)}</h2>{b}' for h, b in t['sections'])
        pv = TOPICS[i - 1] if i else None
        nx = TOPICS[i + 1] if i + 1 < len(TOPICS) else None
        pager = ('<div class="pager">' +
                 (f'<a href="{pv["slug"]}.html">← {esc(pv["title"])}</a>' if pv else '<span></span>') +
                 (f'<a href="{nx["slug"]}.html">{esc(nx["title"])} →</a>' if nx else '<a href="practice.html">К практикуму →</a>') + '</div>')
        body = (f'<div class="crumb" style="--c:#2783DE">Русский язык, 7 класс</div>'
                f'<h1><span class="big">{t["icon"]}</span>{esc(t["title"])}</h1><p class="lead">{esc(t["lead"])}</p>'
                f'<div class="status" data-t="{t["slug"]}"><span>Статус:</span><button class="st" id="st">Не начато</button><span class="hint">нажмите, чтобы сменить</span></div>'
                f'{secs}<h2>Проверь себя</h2>{quiz(t["slug"], t["quiz"])}{pager}')
        open(f'{out}/{t["slug"]}.html', 'w', encoding='utf-8').write(page(t['title'], body, t['slug'] + '.html'))

    # практикум
    tree = json.dumps(dict(steps=[[q, h, list(r)] for q, h, r in content3.TREE], end=list(content3.TREE_END)), ensure_ascii=False)
    punct = ''.join(
        f'<div class="pz"><p class="qt"><span class="qn">{n}</span>{esc(s)}</p><button class="show rev">Показать ответ</button>'
        f'<div class="expl" hidden><b>{esc(ans)}</b><br>{esc(why)}</div></div>'
        for n, (s, ans, why) in enumerate(content3.PUNCT, 1))
    errs = ''
    for n, (txt, items, fixed) in enumerate(content3.ERRORS, 1):
        li = ''.join(f'<li><s>{esc(a)}</s> → <b>{esc(b)}</b>. {esc(c)}</li>' for a, b, c in items)
        errs += (f'<div class="pz"><p class="qt"><span class="qn">{n}</span>{esc(txt)}</p><button class="show rev">Показать ошибки</button>'
                 f'<div class="expl" hidden><ul>{li}</ul><p><b>Исправлено:</b> {esc(fixed)}</p></div></div>')
    errs = errs.replace('Показать ошибки', 'Показать ответ')
    orth = [dict(q=f'Где верно поставлено ударение в слове «{w}»?', o=o, a=a, e=e) for w, o, a, e in content3.ORTHO]
    body = f'''<h1><span class="big">🧪</span>Практикум</h1>
<p class="lead">Задания на самопроверку: сначала выполните самостоятельно, затем сверьтесь с ответом.</p>
<h2>Н или НН: алгоритм</h2>
<p>Ответьте на вопросы по порядку — алгоритм подскажет, сколько букв Н писать в причастии или отглагольном прилагательном.</p>
<div class="tree" id="tree"></div><script type="application/json" id="tree-data">{tree}</script>
<h2>Расставьте знаки препинания</h2>
<p>Спишите предложение и расставьте запятые, где они нужны. В некоторых предложениях запятые не нужны.</p>{punct}
<h2>Найдите ошибки</h2>
<p>В каждом тексте — ошибки, изученные в этом разделе. Найдите их и исправьте.</p>{errs}
<h2>Ударения</h2>{quiz('ortho', orth)}'''
    open(f'{out}/practice.html', 'w', encoding='utf-8').write(page('Практикум', body, 'practice.html'))

    # итоговый тест
    allq, tags = [], []
    for t in TOPICS:
        for q in t['quiz']:
            allq.append(q); tags.append(t['title'])
    body = (f'<h1><span class="big">✅</span>Итоговый тест</h1>'
            f'<p class="lead">{len(allq)} вопросов по всем темам. После каждого ответа появляется пояснение.</p>{quiz("final", allq, tags)}')
    open(f'{out}/test.html', 'w', encoding='utf-8').write(page('Итоговый тест', body, 'test.html'))

    # шпаргалка и термины
    gl = content1.T(*[[f'<b>{esc(a)}</b>', esc(b), c] for a, b, c in content3.GLOSSARY], head=['Термин', 'Значение', 'Пример'])
    body = (f'<div class="cheat"><h1><span class="big">📋</span>Шпаргалка и термины</h1>'
            f'<p class="lead">Краткая сводка правил. Страницу удобно распечатать.</p>{content3.CHEAT}<h2>Термины</h2>{gl}</div>')
    open(f'{out}/cheat.html', 'w', encoding='utf-8').write(page('Шпаргалка и термины', body, 'cheat.html'))

    # главная раздела
    cards = ''.join(f'<a class="card" data-t="{t["slug"]}" href="{t["slug"]}.html"><span class="ci">{t["icon"]}</span><span class="ct">{esc(t["title"])}</span><span class="badge">Не начато</span></a>' for t in TOPICS)
    body = f'''<h1>Русский язык, 7 класс — коротко и по делу</h1>
<p class="lead">Опорные конспекты по темам 7 класса: причастие, деепричастие, наречие, категория состояния, служебные части речи и междометие. В каждой теме — правило, примеры, типичные ошибки и тест.</p>
<aside class="callout"><span class="ico">💡</span><div><p>Порядок работы: <b>прочитать правило → разобрать примеры → пройти тест темы → выполнить задания практикума</b>. Конспекты дополняют учебник, а не заменяют его.</p></div></aside>
<div class="hero"><div><b id="hnum">0</b><span>тем усвоено из <span id="htot">{len(TOPICS)}</span></span></div><div class="bar big"><i id="hbar"></i></div></div>
<div class="quick"><a class="btn" href="{TOPICS[0]["slug"]}.html">Начать →</a><a class="btn ghost" href="practice.html">Практикум</a><a class="btn ghost" href="test.html">Итоговый тест</a><a class="btn ghost" href="cheat.html">Шпаргалка</a><a class="btn ghost" href="../index.html">← История</a></div>
<h2 class="chtitle" style="--c:#2783DE">Темы</h2><div class="grid">{cards}</div>'''
    open(f'{out}/index.html', 'w', encoding='utf-8').write(page('Оглавление', body, ''))

def write_sw():
    """Пересобирает site/sw.js: офлайн-кэш всех файлов сайта."""
    files, h = ['./'], hashlib.sha1()
    for root_, _, names in sorted(os.walk(OUT)):
        for nm in sorted(names):
            if nm in ('sw.js', '.nojekyll'): continue
            fp = os.path.join(root_, nm)
            files.append('./' + os.path.relpath(fp, OUT).replace(os.sep, '/'))
            h.update(open(fp, 'rb').read())
    SW = """const V = 'hist7-%s';
const FILES = %s;
self.addEventListener('install', e => e.waitUntil(caches.open(V).then(c => c.addAll(FILES)).then(() => self.skipWaiting())));
self.addEventListener('activate', e => e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith('hist7-') && k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener('fetch', e => {
  const r = e.request;
  if (r.method !== 'GET' || new URL(r.url).origin !== location.origin) return;
  e.respondWith(caches.match(r, {ignoreSearch: true}).then(hit => hit || fetch(r)));
});
""" % (h.hexdigest()[:10], json.dumps(files))
    open(os.path.join(OUT, 'sw.js'), 'w').write(SW)

if __name__ == '__main__':
    build()
    write_sw()
    print('rus built:', len(TOPICS), 'topics')
