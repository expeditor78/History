import json, re, html, os, shutil

RAW = 'raw'
OUT = 'site'
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT + '/p')

def inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<i>\1</i>', t)
    t = re.sub(r'&lt;br ?/?&gt;', '<br>', t)
    t = re.sub(r'&lt;(/?)(b|i|u)&gt;', r'<\1\2>', t)
    t = t.replace('\\', '')
    return t

def dedent(lines):
    return [l[1:] if l.startswith('\t') else l for l in lines]

def parse(lines):
    """returns list of blocks"""
    blocks = []
    i = 0
    while i < len(lines):
        l = lines[i]
        s = l.strip()
        if not s:
            i += 1; continue
        m = re.match(r'<callout icon="([^"]*)"', s)
        if m:
            j = i + 1; inner = []
            while not lines[j].strip().startswith('</callout>'):
                inner.append(lines[j]); j += 1
            blocks.append(('callout', m.group(1), parse(dedent(inner))))
            i = j + 1; continue
        if s.startswith('<details'):
            summ = re.search(r'<summary>(.*?)</summary>', lines[i + 1]).group(1)
            j = i + 2; inner = []
            while not lines[j].strip().startswith('</details>'):
                inner.append(lines[j]); j += 1
            blocks.append(('details', summ, parse(dedent(inner))))
            i = j + 1; continue
        if s.startswith('<table'):
            header = 'header-row="true"' in s
            j = i + 1; rows = []; cur = None
            while not lines[j].strip().startswith('</table>'):
                t = lines[j].strip()
                if t == '<tr>': cur = []
                elif t == '</tr>': rows.append(cur)
                else:
                    mm = re.match(r'<td>(.*)</td>$', t)
                    if mm: cur.append(mm.group(1))
                j += 1
            blocks.append(('table', header, rows))
            i = j + 1; continue
        m = re.match(r'(#{1,4}) (.*)', s)
        if m:
            blocks.append(('h', len(m.group(1)), m.group(2))); i += 1; continue
        if re.match(r'\d+\. ', s):
            items = []
            while i < len(lines) and re.match(r'\d+\. ', lines[i].strip()):
                items.append(re.sub(r'^\d+\. ', '', lines[i].strip())); i += 1
            blocks.append(('ol', items)); continue
        if s.startswith('- '):
            items = []
            while i < len(lines) and lines[i].strip().startswith('- '):
                items.append(lines[i].strip()[2:]); i += 1
            blocks.append(('ul', items)); continue
        blocks.append(('p', s)); i += 1
    return blocks

def render(blocks, ctx=None):
    out = []
    k = 0
    while k < len(blocks):
        b = blocks[k]
        t = b[0]
        if t == 'h':
            lvl = min(b[1] + 1, 4) if b[1] >= 2 else 2
            if b[1] == 2: lvl = 2
            txt = b[2]
            out.append(f'<h{lvl}>{inline(txt)}</h{lvl}>')
            if 'Мини-тест' in txt and k + 1 < len(blocks) and blocks[k + 1][0] == 'ol':
                ans = None
                if k + 2 < len(blocks) and blocks[k + 2][0] == 'details':
                    ans = blocks[k + 2][2]
                out.append(quiz(blocks[k + 1][1], ans))
                k += 3 if ans is not None else 2
                continue
        elif t == 'p':
            out.append(f'<p>{inline(b[1])}</p>')
        elif t == 'callout':
            out.append(f'<aside class="callout"><span class="ico">{b[1]}</span><div>{render(b[2])}</div></aside>')
        elif t == 'details':
            out.append(f'<details><summary>{inline(b[1])}</summary><div class="dbody">{render(b[2])}</div></details>')
        elif t == 'ul':
            out.append('<ul>' + ''.join(f'<li>{inline(x)}</li>' for x in b[1]) + '</ul>')
        elif t == 'ol':
            out.append('<ol>' + ''.join(f'<li>{inline(x)}</li>' for x in b[1]) + '</ol>')
        elif t == 'table':
            rows = b[2]; h = ''
            body = rows
            if b[1] and rows:
                h = '<thead><tr>' + ''.join(f'<th>{inline(c)}</th>' for c in rows[0]) + '</tr></thead>'
                body = rows[1:]
            bd = ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in body)
            out.append(f'<div class="tw"><table>{h}<tbody>{bd}</tbody></table></div>')
        k += 1
    return '\n'.join(out)

def quiz(items, ans_blocks):
    answers = {}
    full = {}
    if ans_blocks:
        for blk in ans_blocks:
            if blk[0] == 'ol':
                # numbering is lost by parse; rebuild order
                for n, it in enumerate(blk[1], 1):
                    full[n] = it
                    m = re.match(r'([А-Г])\b', it)
                    if m: answers[n] = m.group(1)
    h = ['<div class="quiz" data-total="%d">' % len(items)]
    for n, it in enumerate(items, 1):
        m = re.search(r'\s(?=А\) )', it)
        opts = []
        stem = it
        if m:
            stem = it[:m.start()]
            for o in it[m.start():].strip().split(' · '):
                mm = re.match(r'([А-Г])\)\s*(.*)', o.strip())
                if mm: opts.append(mm.groups())
        a = answers.get(n, '')
        expl = full.get(n, '')
        if len(opts) >= 2 and a:
            h.append(f'<div class="q" data-a="{a}"><p class="qt"><span class="qn">{n}</span>{inline(stem)}</p><div class="opts">')
            for L, tx in opts:
                h.append(f'<button class="opt" data-l="{L}"><b>{L}</b>{inline(tx)}</button>')
            h.append(f'</div><p class="expl" hidden>{inline(expl)}</p></div>')
        else:
            h.append(f'<div class="q open"><p class="qt"><span class="qn">{n}</span>{inline(stem)}</p>'
                     f'<button class="show">Показать ответ</button><p class="expl" hidden>{inline(expl)}</p></div>')
    h.append('<div class="score" aria-live="polite"></div></div>')
    return '\n'.join(h)

def txt(v):
    if isinstance(v, dict):
        if 'select' in v: return v['select']['name']
        for k in ('title', 'rich_text'):
            if k in v: return ''.join(x.get('plain_text', '') for x in v[k])
    return v

def load(n):
    d = json.load(open(f'{RAW}/p{n}.json'))
    md = d['markdown']['markdown']
    props = d['page'].get('properties', {})
    icon = d['page'].get('icon') or {}
    if isinstance(icon, dict): icon = icon.get('emoji', '')
    return md, props, icon

CH = ['I. Великие географические открытия', 'II. Европа в XVI–XVII вв.', 'III. Азия и Африка']
chcol = ['#2783DE', '#46A171', '#D5803B']
paras = []
for n in range(32, 53):
    md, props, icon = load(n)
    paras.append(dict(n=n, num=len(paras) + 1, title=txt(props.get('Параграф') or props.get('title')), ch=txt(props.get('Глава')), icon=icon, md=md))
for i, p in enumerate(paras):
    p['file'] = f"{p['num']:02d}.html"

def nav(active=''):
    h = ['<nav class="side" id="side"><a class="brand" href="{R}index.html">🧭 История Нового времени<small>7 класс</small></a>',
         '<div class="prog"><div class="bar"><i id="gbar"></i></div><span id="gtxt">0 из 21</span></div>',
         '<a class="nl %s" href="{R}how.html">⏱️ Как заниматься</a>' % ('on' if active == 'how' else ''),
         '<a class="nl %s" href="{R}timeline.html">🗓️ Лента времени</a>' % ('on' if active == 'tl' else '')]
    for ci, c in enumerate(CH):
        h.append(f'<div class="chh" style="--c:{chcol[ci]}">{c}</div>')
        for p in paras:
            if p['ch'] == c:
                h.append(f'<a class="nl {"on" if active == p["file"] else ""}" data-p="{p["num"]}" href="{{R}}p/{p["file"]}"><span class="dot"></span>{html.escape(p["title"])}</a>')
    h.append('</nav>')
    return '\n'.join(h)

def page(title, body, active='', root='', extra=''):
    nv = nav(active).replace('{R}', root)
    return f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} — История Нового времени, 7 класс</title><link rel="stylesheet" href="{root}style.css"><link rel="stylesheet" href="{root}video.css"></head>
<body><header class="top"><button id="menu" aria-label="Меню">☰</button><span>История Нового времени · 7 класс</span></header>
{nv}<main>{body}</main><script src="{root}app.js" defer></script></body></html>'''

# Видеоразборы: № страницы -> (id ролика на YouTube, длительность). Канал Tatiana Themis, серия «История Нового времени 7 / Мединский».
VIDEOS = {
    1: ('ISlQzbwqXHg', '19:45'),
    2: ('wo59YKor-AE', '20:31'),
    3: ('-3OXpYC13w4', '28:22'),
    4: ('jAWJPzGAEw0', '21:51'),
    5: ('7qENzDfLRf0', '23:23'),
    6: ('0-XWz2pn1FI', '21:54'),
    7: ('ZkX6b6oPIvM', '19:16'),
    8: ('2GJ6BqdvDpU', '16:03'),
    9: ('jyqb3gc5hYQ', '17:24'),
    10: ('Xuesbuv0WyM', '15:50'),
    11: ('TbUq1jnH8S4', '21:20'),
    12: ('0-NkuYcP7zU', '20:02'),
    13: ('PvU415Sj464', '22:08'),
    14: ('utScbaZw6jA', '26:20'),
    15: ('JzGoDqhh5xY', '19:20'),
    16: ('THpKSNjSIgI', '19:20'),
    17: ('k-9y_Wklnas', '21:45'),
    18: ('0UH2FBSgaTk', '19:39'),
    19: ('HSh9Yx7bYis', '12:38'),
    20: ('OTqONm6hPB8', '21:50'),
    21: ('hrqxQNeJDOA', '12:03'),
}

def video(n):
    if n not in VIDEOS: return ''
    vid, d = VIDEOS[n]
    return (f'<section class="vid"><h2>🎬 Видеоразбор параграфа <small>{d}</small></h2>'
            f'<div class="vframe"><iframe src="https://www.youtube-nocookie.com/embed/{vid}?rel=0" title="Видеоразбор параграфа" loading="lazy" '
            f'allow="accelerometer; encrypted-media; picture-in-picture; fullscreen" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>'
            f'<p class="vmeta">Не открывается? <a href="https://www.youtube.com/watch?v={vid}" target="_blank" rel="noopener">Смотреть на YouTube ↗</a></p></section>')

# paragraph pages
for i, p in enumerate(paras):
    body_md = render(parse(p['md'].split('\n')))
    pv = paras[i - 1] if i else None
    nx = paras[i + 1] if i + 1 < len(paras) else None
    ci = CH.index(p['ch'])
    body = f'''<div class="crumb" style="--c:{chcol[ci]}">{p['ch']}</div><h1><span class="big">{p['icon']}</span>{html.escape(p['title'])}</h1>
<div class="status" data-p="{p['num']}"><span>Статус:</span><button class="st" id="st">Не начато</button><span class="hint">нажмите, чтобы сменить</span></div>
{video(p['num'])}
{body_md}
<div class="pager">{'<a href="'+pv['file']+'">← '+html.escape(pv['title'])+'</a>' if pv else '<span></span>'}{'<a href="'+nx['file']+'">'+html.escape(nx['title'])+' →</a>' if nx else '<a href="../index.html">К оглавлению →</a>'}</div>'''
    open(f"{OUT}/p/{p['file']}", 'w').write(page(p['title'], body, p['file'], '../'))

# static pages
for n, fn, key, ttl in [(11, 'how.html', 'how', 'Как заниматься'), (12, 'timeline.html', 'tl', 'Лента времени')]:
    md, props, icon = load(n)
    body = f'<h1><span class="big">{icon}</span>{html.escape(txt(props.get("title")) or ttl)}</h1>' + render(parse(md.split('\n')))
    open(f'{OUT}/{fn}', 'w').write(page(ttl, body, key, ''))

# index
cards = []
for ci, c in enumerate(CH):
    cards.append(f'<h2 class="chtitle" style="--c:{chcol[ci]}">{c}</h2><div class="grid">')
    for p in paras:
        if p['ch'] == c:
            cards.append(f'<a class="card" data-p="{p["num"]}" href="p/{p["file"]}"><span class="ci">{p["icon"]}</span><span class="ct">{html.escape(p["title"])}</span><span class="badge">Не начато</span></a>')
    cards.append('</div>')
home = f'''<h1>История Нового времени, 7 класс — по-человечески</h1>
<p class="lead">Шпаргалки по учебнику Мединского и Чубарьяна (конец XV–XVII в.). У каждого параграфа: сюжет в 30 секунд, даты-якоря, термины простыми словами, «кто есть кто», разбор по пунктам и интерактивный тест. Прогресс сохраняется в браузере.</p>
<aside class="callout"><span class="ico">💡</span><div><p>Цикл на параграф: <b>трейлер → чтение → объясни вслух → проверь себя → повтори через 3 дня и 2 недели</b>. Начните со страницы <a href="how.html">«Как заниматься»</a>.</p></div></aside>
<div class="hero"><div><b id="hnum">0</b><span>усвоено из 21</span></div><div class="bar big"><i id="hbar"></i></div></div>
<div class="quick"><a class="btn" id="cont" href="p/01.html">Продолжить →</a><a class="btn ghost" href="timeline.html">Лента времени</a><a class="btn ghost" href="how.html">Как заниматься</a></div>
{''.join(cards)}'''
open(f'{OUT}/index.html', 'w').write(page('Оглавление', home, '', ''))

open(f'{OUT}/.nojekyll', 'w').write('')
for f in os.listdir('dist_src'):
    if f != 'video.js': shutil.copy('dist_src/' + f, OUT + '/' + f)
print('built', len(paras))
