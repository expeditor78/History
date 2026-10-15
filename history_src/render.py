"""Render only explicitly supplied, reviewed lessons. Never removes site/ or changes §11."""
from pathlib import Path
from bs4 import BeautifulSoup
import json,re,html,hashlib,sys,random
ROOT=Path(__file__).resolve().parents[1]
def inline(t):
 t=html.escape(t)
 t=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',t)
 return t

def reader_limits(t):
 # Keep source uncertainty; omit time-bound author workflow notes from the lesson.
 t=re.sub(r'(?:^|(?<=\.)\s+)(?:Это исправлен|Это точечно уточн[её]н|Исправленная версия|Доработано как|[vV]\d+ исправ|Новые мостики).*$', '',t)
 t=re.sub(r';\s*[vV]\d+ ещё.*$', '.',t)
 t=t.replace('; самостоятельная проверка автора не является внешним аудитом или проверкой усвоения','')
 assert not re.search(r'\b[vV]\d+\b|\ufffd',t), 'Unremoved author workflow note'
 return t.strip()

def render_lesson(o,root=ROOT):
 id=o['id'];assert id!='11', '§11 is protected'
 path=root/f'site/p/{id}.html';soup=BeautifulSoup(path.read_text(),'html.parser');main=soup.select_one('main')
 video=main.select_one('.vid');video=video.extract() if video else None
 pager=main.select_one('.pager').extract();footer=main.select_one('footer').extract();status=main.select_one('.status')
 for n in list(status.next_siblings):n.extract()
 url=o['source']['url']
 def refs(pages):
  ps=sorted(set(pages));label=', '.join(map(str,ps))
  return f'<span class="history-refs"> <a href="{html.escape(url)}#page={ps[0]-1}" target="_blank" rel="noopener" title="Учебник, с. {label}" aria-label="Источник: учебник, страницы {label}">с. {label}</a></span>'
 def para(b):return '<p>'+inline(b['text'])+refs(b['pages'])+'</p>'
 main.append(BeautifulSoup('<aside class="callout"><div><p><strong>Главный вопрос:</strong> '+inline(o['main_question'])+refs([o['source']['printed_start']])+'</p></div></aside>'+''.join(para(b) for b in o['intro']),'html.parser'))
 parts=[]
 for sec in o['sections']:parts.append((sec['title'],''.join(para(b) for b in sec['paragraphs'])))
 parts.append(('Ответ на главный вопрос',''.join(para(b) for b in o['conclusion'])))
 if o['optional']:
  text=''.join('<details><summary>'+inline(s['title'])+'</summary><div class="dbody">'+''.join(para(b) for b in s['paragraphs'])+'</div></details>' for s in o['optional'])
  parts.append(('Дополнительно — после первого чтения',text))
 if o['reports']:
  text='<p class="hint">Это короткие пересказы для устного ответа, а не замена объяснению. Каждый рассчитан примерно на минуту; время зависит от темпа речи.</p>'
  text+=''.join('<details><summary>'+inline(s['title'])+'</summary><div class="dbody"><p>'+inline(s['text'])+refs(s['pages'])+'</p></div></details>' for s in o['reports'])
  parts.append(('Короткие доклады по пунктам учебника',text))
 text='<h3>Ответь своими словами</h3><ol>'+''.join('<li>'+inline(q['question'])+'</li>' for q in o['understanding'])+'</ol>'
 text+='<details><summary>Смысл ответов — после своей попытки</summary><div class="dbody"><ol>'+''.join('<li>'+inline(q['answer'])+refs(q['pages'])+'</li>' for q in o['understanding'])+'</ol></div></details>'
 text+='<h3>Мини-тест с объяснениями</h3><div class="quiz" data-total="'+str(len(o['quiz']))+'">'
 labels='АБВГ'
 for i,q in enumerate(o['quiz']):
  # Stable pseudorandom order, not a predictable cyclic answer pattern.
  options=q['options'];order=list(range(len(options)))
  seed=hashlib.sha256(json.dumps([id,q],ensure_ascii=False,sort_keys=True).encode()).hexdigest()
  random.Random(seed).shuffle(order)
  rot=[options[j] for j in order];correct=order.index(q['correct'])
  text+=f'<div class="q" data-a="{labels[correct]}"><p class="qt"><span class="qn">{i+1}</span>'+inline(q['question'])+'</p><div class="opts">'
  text+=''.join(f'<button class="opt" data-l="{labels[j]}"><b>{labels[j]}</b>'+inline(op)+'</button>' for j,op in enumerate(rot))
  text+='</div><p class="expl" hidden>'+inline(q['explanation'])+refs(q['pages'])+'</p></div>'
 text+='<div class="score" aria-live="polite"></div></div>';parts.append(('Проверь понимание',text))
 nav='<div class="history-nav" id="history-nav"><label for="history-select">Содержание параграфа</label><select id="history-select">'+''.join(f'<option value="{i}">{html.escape(t)}</option>' for i,(t,b) in enumerate(parts))+'</select><button id="history-all" type="button" aria-pressed="false">Вся тема</button><span id="history-counter" aria-live="polite"></span></div>'
 main.append(BeautifulSoup(nav,'html.parser'))
 for i,(title,body) in enumerate(parts):main.append(BeautifulSoup(f'<section class="history-part" id="history-part-{i}"><h2 tabindex="-1">{inline(title)}</h2>{body}</section>','html.parser'))
 main.append(BeautifulSoup('<div class="history-controls" id="history-controls" hidden><button id="history-prev" type="button">← Назад</button><span id="history-step"></span><button id="history-next" type="button">Дальше →</button></div><p class="history-source-note">Источник: <a href="'+html.escape(url)+'#page='+str(o['source']['pdf_start'])+'" target="_blank" rel="noopener">учебник, с. '+str(o['source']['printed_start'])+'–'+str(o['source']['printed_end'])+'</a>. '+inline(reader_limits(o['limitations']))+'</p>','html.parser'))
 if video:
  d=BeautifulSoup('<details><summary>Дополнительное видео</summary><div class="dbody"></div></details>','html.parser');d.select_one('.dbody').append(video);main.append(d)
 main.append(pager);main.append(footer)
 # Preserve app/status/menu; add shared navigation and early theme, each exactly once.
 if not soup.head.find('script',src='../theme.js'):soup.head.insert(2,soup.new_tag('script',src='../theme.js'))
 if not soup.head.find('link',href='../history.css'):soup.head.append(soup.new_tag('link',rel='stylesheet',href='../history.css'))
 for script in soup.find_all('script',src='../history-nav.js'):script.decompose()
 soup.body.append(soup.new_tag('script',src='../history-nav.js',defer=True))
 soup.body['data-history-id']=id;soup.body['data-history-revision']=hashlib.sha256(json.dumps(o,ensure_ascii=False,sort_keys=True).encode()).hexdigest()[:12]
 path.write_text(str(soup))
 return {'id':id,'parts':len(parts),'quiz':len(o['quiz']),'bytes':path.stat().st_size}

def update_cache(root=ROOT):
 sw=root/'site/sw.js';text=sw.read_text()
 match=re.search(r'const FILES = (\[.*?\]);',text);assert match,'Cannot locate existing cache manifest'
 files=json.loads(match.group(1))
 for f in ['./history.css','./history-nav.js']:
  if f not in files:files.append(f)
 for f in files:assert (root/'site'/f.lstrip('./')).exists(),f
 text=text[:match.start(1)]+json.dumps(files,ensure_ascii=False)+text[match.end(1):]
 h=hashlib.sha256()
 for f in sorted((root/'site').rglob('*')):
  if f.is_file() and f!=sw:h.update(str(f.relative_to(root/'site')).encode());h.update(f.read_bytes())
 version='hist7-'+h.hexdigest()[:12]
 text=re.sub(r"const V = '[^']+';",f"const V = '{version}';",text,count=1)
 sw.write_text(text);return version

if __name__=='__main__':
 inputs=sys.argv[1:] or sorted((ROOT/'history_src/lessons').glob('*.json'))
 if not inputs:raise SystemExit('No reviewed lesson JSON files supplied.')
 for f in inputs:print(json.dumps(render_lesson(json.loads(Path(f).read_text())),ensure_ascii=False))
 print('Cache version:',update_cache())
