"""Render concise textbook-ordered retellings; keep full versions in the source archive."""
from pathlib import Path
from bs4 import BeautifulSoup
import json,re,html,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
def inline(t):return re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',html.escape(t))
def label(o):return '§ '+o['number']+'. '+o['title']
def fix_names(s,lessons):
 changed=False
 for a in s.select('a.nl[data-p]'):
  id=str(a['data-p']).zfill(2)
  if id not in lessons:continue
  want=label(lessons[id]);got=a.get_text(' ',strip=True)
  if got!=want:
   dot=a.select_one('.dot');dot=dot.extract() if dot else None;a.clear()
   if dot:a.append(dot)
   a.append(want);changed=True
 for c in s.select('.card[data-p]'):
  id=str(c['data-p']).zfill(2);t=c.select_one('.ct')
  if id in lessons and t and t.get_text()!=label(lessons[id]):t.string=label(lessons[id]);changed=True
 for a in s.select('.pager a'):
  m=re.search(r'(?:^|/)p/(\d+)\.html$',a.get('href','')) or re.search(r'^(\d+)\.html$',a.get('href',''))
  if not m:continue
  id=m[1].zfill(2)
  if id not in lessons:continue
  old=a.get_text(' ',strip=True);new=('← '+label(lessons[id])) if old.startswith('←') else label(lessons[id])+' →'
  if new!=old:a.string=new;changed=True
 return changed

def render_brief(o,root=ROOT,lessons=None):
 id=o['id'];path=root/f'site/p/{id}.html';s=BeautifulSoup(path.read_text(),'html.parser');main=s.select_one('main');assert main,id
 keep={}
 for name,sel in [('crumb','.crumb'),('h1','h1'),('status','.status'),('quiz','.quiz'),('video','.vid'),('pager','.pager'),('footer','footer')]:
  node=main.select_one(sel);keep[name]=node.extract() if node else None
 assert all(keep[k] for k in ['h1','status','pager','footer']),id
 main.clear()
 h1=keep['h1'];icon=h1.select_one('.big');icon=icon.extract() if icon else None;h1.clear()
 if icon:h1.append(icon)
 h1.append(label(o))
 if s.title:s.title.string=label(o)+' · История · 7 класс'
 for k in ['crumb','h1','status']:
  if keep[k]:main.append(keep[k])
 nav='<div class="history-nav" id="history-nav"><label for="history-select">Пункты учебника</label><select id="history-select">'+''.join(f'<option value="{i}">{x["number"]}. {html.escape(x["title"])}</option>' for i,x in enumerate(o['sections']))+'</select><button id="history-all" type="button" aria-pressed="false">Весь пересказ</button><span id="history-counter" aria-live="polite"></span></div>'
 main.append(BeautifulSoup('<p class="hint">Краткий пересказ</p>'+nav,'html.parser'))
 url=o['source']['url']
 for i,sec in enumerate(o['sections']):
  body='';pages=[]
  for block in sec['blocks']:
   if block['kind']=='p':body+='<p>'+inline(block['text'])+'</p>';pages+=block['pages']
   else:
    body+='<ul>'+''.join('<li>'+inline(b['text'])+'</li>' for b in block['items'])+'</ul>'
    pages += [n for b in block['items'] for n in b['pages']]
  pages=sorted(set(pages));refs=', '.join(map(str,pages))
  body+='<p class="history-refs"><a href="'+html.escape(url)+'#page='+str(pages[0]-1)+'" target="_blank" rel="noopener">Учебник, с. '+refs+'</a></p>'
  main.append(BeautifulSoup(f'<section class="history-part brief-part" id="history-part-{i}" data-book-number="{sec["number"]}"><h2 tabindex="-1">{sec["number"]}. {inline(sec["title"])}</h2>{body}</section>','html.parser'))
 main.append(BeautifulSoup('<div class="history-controls" id="history-controls" hidden><button id="history-prev" type="button">← Назад</button><span id="history-step"></span><button id="history-next" type="button">Дальше →</button></div>','html.parser'))
 # Existing quizzes remain separate, collapsed and explicitly about the full textbook.
 if keep['quiz']:
  d=BeautifulSoup('<details class="brief-test"><summary>Тест по полному параграфу учебника</summary><div class="dbody"></div></details>','html.parser');d.select_one('.dbody').append(keep['quiz']);main.append(d)
 if keep['video']:
  d=BeautifulSoup('<details><summary>Видео</summary><div class="dbody"></div></details>','html.parser');d.select_one('.dbody').append(keep['video']);main.append(d)
 main.append(BeautifulSoup('<p class="history-source-note">Краткий пересказ по <a href="'+html.escape(url)+'#page='+str(o['source']['pdf_start'])+'" target="_blank" rel="noopener">учебнику: '+html.escape(label(o))+', с. '+str(o['source']['printed_start'])+'–'+str(o['source']['printed_end'])+'</a>.</p>','html.parser'))
 main.append(keep['pager']);main.append(keep['footer'])
 # Remove obsolete lesson-specific navigation; the main app and its learner records remain.
 for script in list(s.find_all('script')):
  src=script.get('src','')
  if src in ['../history-nav.js','../brief-nav.js'] or (not src and 'p11-part' in script.get_text()):script.decompose()
 if not s.head.find('script',src='../theme.js'):s.head.insert(2,s.new_tag('script',src='../theme.js'))
 if not s.head.find('link',href='../history.css'):s.head.append(s.new_tag('link',rel='stylesheet',href='../history.css'))
 s.body['data-history-id']=id;s.body['data-brief-revision']=hashlib.sha256(json.dumps(o,ensure_ascii=False,sort_keys=True).encode()).hexdigest()[:12]
 s.body.append(s.new_tag('script',src='../brief-nav.js',defer=True))
 if lessons:fix_names(s,lessons)
 out=str(s);assert '\ufffd' not in out,(id,'replacement character remains');path.write_text(out)
 return {'id':id,'parts':len(o['sections']),'bytes':path.stat().st_size}

def update_cache(root=ROOT):
 sw=root/'site/sw.js';text=sw.read_text();m=re.search(r'const FILES = (\[.*?\]);',text);assert m
 files=json.loads(m[1])
 for f in ['./history.css','./brief-nav.js']:
  if f not in files:files.append(f)
 for f in files:assert (root/'site'/f.lstrip('./')).exists(),f
 text=text[:m.start(1)]+json.dumps(files,ensure_ascii=False)+text[m.end(1):]
 h=hashlib.sha256()
 for f in sorted((root/'site').rglob('*')):
  if f.is_file() and f!=sw:h.update(str(f.relative_to(root/'site')).encode());h.update(f.read_bytes())
 version='hist7-'+h.hexdigest()[:12];text=re.sub(r"const V = '[^']+';",f"const V = '{version}';",text,count=1);sw.write_text(text);return version

def sync_hints(root):
 replacements={
 'index.html':{
 'Шпаргалки по учебнику Мединского и Чубарьяна (конец XV–XVII в.). У каждого параграфа: сюжет в 30 секунд, даты-якоря, термины простыми словами, «кто есть кто», разбор по пунктам и интерактивный тест. Прогресс сохраняется в браузере.':'Краткие пересказы по учебнику Мединского и Чубарьяна (конец XV–XVII в.). Названия параграфов и пунктов — как в учебнике. Читай по пунктам или открой весь пересказ. Тест по полному параграфу учебника находится в сворачиваемом блоке. Прогресс сохраняется в браузере.',
 'трейлер → чтение → объясни вслух → проверь себя → повтори через 3 дня и 2 недели':'краткий пересказ → учебник → объясни вслух → проверь себя → повтори'
 },
 'how.html':{
 'трейлер → чтение → объяснение → проверка → повторение':'краткий пересказ → учебник → объяснение → проверка → повторение',
 '1. Трейлер':'1. Знакомство с темой',
 'Читаем шпаргалку параграфа (сюжет в 30 секунд + даты-якоря). Смотрим карту. В учебнике читаем только вопрос в начале и блок «Подведём итоги» в конце.':'Читаем краткий пересказ по пунктам учебника. Смотрим карту. Затем открываем соответствующий параграф учебника, его главный вопрос и итог.',
 'Блок «Проверь себя» из шпаргалки без подсказок. Ошибки — в «Повторить».':'Открываем сворачиваемый блок «Тест по полному параграфу учебника» и отвечаем без подсказок. Этот тест охватывает больше деталей, чем краткий пересказ. Непонятное сверяем с учебником; при необходимости меняем статус на «Повторить».',
 'вопросы из «Проверь себя» ещё раз через 3 дня и через 2 недели (по 3–5 минут). Это даёт больше, чем час зубрёжки накануне контрольной.':'возвращаемся к вопросам учебника через 3 дня и через 2 недели, пробуем ответить своими словами.',
 'Любое событие в истории — звено в цепочке. Если сын может достроить цепочку, даты вспоминаются сами. Пример: пушки → рыцари не нужны → нужны наёмные армии → нужны деньги → власть у банкиров → деньги на экспедиции → Великие географические открытия.':'Для главного события назови причину, действие и результат. Например, в §12: война с шотландцами потребовала денег → Карл I созвал парламент → депутаты потребовали изменить управление.',
 'В шпаргалках у каждой даты есть своя зацепка.':'Выбирайте только важные даты из текущего параграфа.',
 'Учебник интегрирует всеобщую и российскую историю. В каждой шпаргалке есть блок «Что в это время в России» — события, которые сын уже знает из 6–7 классов, становятся мостиком.':'Если в параграфе есть связь с российской историей, найдите её в учебнике и сопоставьте события по времени.'
 }}
 for name,pairs in replacements.items():
  p=root/'site'/name;text=p.read_text()
  for old,new in pairs.items():
   assert text.count(old)<=1,(name,old)
   text=text.replace(old,new)
  p.write_text(text)

def render_all(inputs,root=ROOT):
 lessons={}
 for f in inputs:
  o=json.loads(Path(f).read_text());lessons[o['id']]=o
 results=[render_brief(o,root,lessons) for o in lessons.values()]
 for f in (root/'site').rglob('*.html'):
  if 'rus' in f.relative_to(root/'site').parts:continue
  s=BeautifulSoup(f.read_text(),'html.parser')
  if fix_names(s,lessons):f.write_text(str(s))
 sync_hints(root)
 return results
if __name__=='__main__':
 inputs=sys.argv[1:] or sorted((ROOT/'history_src/briefs').glob('*.json'))
 assert inputs,'No brief JSON inputs'
 for row in render_all(inputs):print(json.dumps(row,ensure_ascii=False))
 print('Cache:',update_cache())
