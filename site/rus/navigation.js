/* Короткие экраны вместо одной длинной ленты. Без JS всё остаётся читаемым. */
(function () {
 'use strict';
 var main = document.querySelector('main');
 if (!main) return;
 var headings = Array.from(main.querySelectorAll('h2'));
 var sections = [], host;
 // В итоговом тесте сохраняем один общий результат, но показываем по 10 вопросов.
 var finalQuiz = main.querySelector('.rq[data-id="final"]');
 if (finalQuiz) {
  host = finalQuiz;
  var questions = Array.from(finalQuiz.querySelectorAll('.q'));
  for (var i = 0; i < questions.length; i += 10) {
   var chunk = document.createElement('section');
   var title = document.createElement('h2');
   title.textContent = 'Вопросы ' + (i + 1) + '–' + Math.min(i + 10, questions.length);
   chunk.appendChild(title);
   host.insertBefore(chunk, questions[i]);
   questions.slice(i, i + 10).forEach(function (q) { chunk.appendChild(q); });
   sections.push(chunk);
  }
 } else {
  if (headings.length < 2) return;
  host = headings[0].parentNode;
  headings = headings.filter(function (h) { return h.parentNode === host; });
  headings.forEach(function (h) {
   var section = document.createElement('section');
   host.insertBefore(section, h);
   section.appendChild(h);
   var node = section.nextSibling;
   while (node && !(node.nodeType === 1 && (node.tagName === 'H2' || node.matches('.pager,.about')))) {
    var next = node.nextSibling;
    section.appendChild(node);
    node = next;
   }
   sections.push(section);
  });
 }
 if (sections.length < 2) return;
 var key = 'rus7.navigation.' + location.pathname;
 var current = 0, all = false, learnOnly = false;
 try { current = Number(localStorage.getItem(key) || 0); } catch (e) {}
 if (!Number.isInteger(current) || current < 0 || current >= sections.length) current = 0;
 var nav = document.createElement('nav');
 nav.className = 'lesson-nav';
 nav.setAttribute('aria-label', 'Разделы этой страницы');
 nav.innerHTML = '<div class="lesson-nav-row"><label for="section-select">Содержание</label>' +
  '<span class="section-count" aria-live="polite"></span><button type="button" class="all-sections" aria-pressed="false">Вся тема</button></div>' +
  '<select id="section-select" aria-label="Перейти к разделу"></select><div class="section-shortcuts"></div>';
 host.insertBefore(nav, sections[0]);
 var select = nav.querySelector('select'), count = nav.querySelector('.section-count');
 var toggle = nav.querySelector('.all-sections'), shortcuts = nav.querySelector('.section-shortcuts');
 sections.forEach(function (s, i) {
  s.className = 'lesson-section'; s.id = 'part-' + (i + 1);
  var heading = s.querySelector('h2'); heading.tabIndex = -1;
  var option = document.createElement('option'); option.value = i;
  option.textContent = (i + 1) + '. ' + heading.textContent; select.appendChild(option);
 });
 var pager = document.createElement('div'); pager.className = 'section-pager';
 pager.innerHTML = '<button type="button" class="section-prev">← Назад</button><span class="section-position"></span><button type="button" class="section-next">Дальше →</button>';
 host.insertBefore(pager, sections[sections.length - 1].nextSibling);
 var prev = pager.querySelector('.section-prev'), next = pager.querySelector('.section-next');
 function save() { try { localStorage.setItem(key, String(current)); } catch (e) {} }
 function jumpTo(target) {
  // Мгновенный переход: глобальная плавная прокрутка не должна пролистывать всю тему.
  var html = document.documentElement, before = html.style.scrollBehavior;
  html.style.scrollBehavior = 'auto';
  target.scrollIntoView({block: 'start', behavior: 'auto'});
  html.style.scrollBehavior = before;
 }

 function paint() {
  sections.forEach(function (s, i) {
   s.hidden = !all && i !== current;
   s.classList.toggle('rule-only', !all && learnOnly && i === current && !!s.querySelector('.textbook-rule'));
  });
  select.value = current;
  count.textContent = all ? sections.length + ' разделов' : (current + 1) + ' из ' + sections.length;
  toggle.textContent = all ? 'По разделам' : 'Вся тема';
  toggle.setAttribute('aria-pressed', String(all)); pager.hidden = all;
  prev.disabled = current === 0; next.disabled = current === sections.length - 1;
  pager.querySelector('.section-position').textContent = (current + 1) + ' / ' + sections.length;
  shortcuts.replaceChildren();
  if (!all) {
   if (sections[current].querySelector('.textbook-rule')) {
    var mode = document.createElement('button'); mode.type = 'button'; mode.className = 'learn-mode';
    mode.textContent = learnOnly ? 'С объяснением' : 'Только правило';
    mode.setAttribute('aria-pressed', String(learnOnly));
    mode.addEventListener('click', function () { learnOnly = !learnOnly; paint(); jumpTo(sections[current]); });
    shortcuts.appendChild(mode);
   }
   [['.rule', 'Правило'], ['.demo', 'Разбор'], ['.ask,.rq,.q', 'Проверить себя']].forEach(function (item, n) {
    var target = sections[current].querySelector(item[0]);
    if (!target || (learnOnly && target.closest('.lesson-explanation'))) return;
    if (!target.id) target.id = sections[current].id + '-jump-' + n;
    var a = document.createElement('a'); a.href = '#' + target.id; a.textContent = item[1]; shortcuts.appendChild(a);
   });
  }
 }
 function setHash(id) { try { history.replaceState(null, '', '#' + id); } catch (e) {} }
 function open(index, scroll) {
  current = index; all = false;
  if (!sections[current].querySelector('.textbook-rule')) learnOnly = false;
  save(); paint(); setHash(sections[current].id);
  if (scroll) {
   sections[current].querySelector('h2').focus({preventScroll: true});
   jumpTo(sections[current]);
  }
 }
 select.addEventListener('change', function () { open(Number(select.value), true); });
 prev.addEventListener('click', function () { if (current > 0) open(current - 1, true); });
 next.addEventListener('click', function () { if (current + 1 < sections.length) open(current + 1, true); });
 toggle.addEventListener('click', function () { all = !all; learnOnly = false; paint(); });
 function fromHash(scroll) {
  var id; try { id = decodeURIComponent(location.hash.slice(1)); } catch (e) { return; }
  if (!id) return;
  var target = document.getElementById(id);
  var index = sections.findIndex(function (s) { return s === target || s.contains(target); });
  if (index < 0) return;
  current = index; all = false;
  if (target.closest('.lesson-explanation')) learnOnly = false;
  save(); paint();
  if (scroll) jumpTo(target);
 }
 window.addEventListener('hashchange', function () { fromHash(true); });
 paint(); fromHash(false);
 if (location.hash) requestAnimationFrame(function () { fromHash(true); });
})();
