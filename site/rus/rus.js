(function(){
 var KEY='rus7.v1',NAMES=['Не начато','Читаем','Повторить','Усвоено'];
 var S={};try{S=JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){}
 S.st=S.st||{};S.quiz=S.quiz||{};
 function save(){try{localStorage.setItem(KEY,JSON.stringify(S))}catch(e){}}
 var side=document.getElementById('side'),menu=document.getElementById('menu');
 var TOTAL=side?parseInt(side.dataset.total||'0',10):0;
 var stEl=document.querySelector('.status[data-t]');
 function paint(){
  var done=0;
  document.querySelectorAll('.nl[data-t]').forEach(function(a){a.dataset.s=S.st[a.dataset.t]||0});
  document.querySelectorAll('.card[data-t]').forEach(function(c){var s=S.st[c.dataset.t]||0;c.dataset.s=s;var b=c.querySelector('.badge');if(b)b.textContent=NAMES[s]});
  for(var k in S.st){if(S.st[k]==3)done++}
  var g=document.getElementById('gbar');if(g)g.style.width=(TOTAL?done/TOTAL*100:0)+'%';
  var t=document.getElementById('gtxt');if(t)t.textContent=done+' из '+TOTAL+' усвоено';
  var hb=document.getElementById('hbar');if(hb)hb.style.width=(TOTAL?done/TOTAL*100:0)+'%';
  var hn=document.getElementById('hnum');if(hn)hn.textContent=done;
  var hl=document.getElementById('htot');if(hl)hl.textContent=TOTAL;
  if(stEl){var s=S.st[stEl.dataset.t]||0;stEl.dataset.s=s;stEl.querySelector('.st').textContent=NAMES[s]}
 }
 if(stEl)stEl.querySelector('.st').addEventListener('click',function(){var n=stEl.dataset.t;S.st[n]=((S.st[n]||0)+1)%4;save();paint()});
 function setMenu(open){if(!side||!menu)return;side.classList.toggle('open',open);menu.setAttribute('aria-expanded',String(open))}
 if(menu&&side)menu.addEventListener('click',function(){setMenu(!side.classList.contains('open'))});
 var closeMenu=side&&side.querySelector('.side-close');
 if(closeMenu)closeMenu.addEventListener('click',function(){setMenu(false);menu.focus()});
 document.addEventListener('keydown',function(e){if(e.key==='Escape'&&side&&side.classList.contains('open')){setMenu(false);menu.focus()}});
 document.addEventListener('click',function(e){if(side&&side.classList.contains('open')&&!side.contains(e.target)&&e.target!==menu)setMenu(false)});
 // тесты
 document.querySelectorAll('.rq').forEach(function(box){
  var id=box.dataset.id,qs=box.querySelectorAll('.q'),total=qs.length,right=0,answered=0;
  var sc=box.querySelector('.score');
  function upd(){
   if(answered<total){sc.textContent='Отвечено: '+answered+' из '+total;return}
   sc.textContent='Результат: '+right+' из '+total+(right==total?' 🎉':right>=total*0.7?' — хорошо!':' — стоит повторить');sc.classList.add('done');
   S.quiz[id]=right+'/'+total;save();
   if(right<total*0.7){var sx=document.querySelector('.status[data-t="'+id+'"]');if(sx&&(S.st[id]||0)!=3){S.st[id]=2;save();paint()}}
  }
  qs.forEach(function(q){q.querySelectorAll('.opt').forEach(function(b){b.addEventListener('click',function(){
   var ok=b.dataset.i===q.dataset.a;
   q.querySelectorAll('.opt').forEach(function(o){o.disabled=true;if(o.dataset.i===q.dataset.a)o.classList.add('ok')});
   if(!ok)b.classList.add('bad');else right++;
   answered++;q.querySelector('.expl').hidden=false;upd();
  })})});
  if(S.quiz[id]&&sc)sc.textContent='Прошлый результат: '+S.quiz[id];
 });
 // «Показать ответ»
 document.querySelectorAll('.rev').forEach(function(b){b.addEventListener('click',function(){
  var e=b.nextElementSibling;e.hidden=!e.hidden;b.textContent=e.hidden?'Показать ответ':'Скрыть ответ';
 })});
 // алгоритм Н/НН
 var tb=document.getElementById('tree'),td=document.getElementById('tree-data');
 if(tb&&td){
  var D=JSON.parse(td.textContent),i=0;
  function show(){
   var h;
   if(i>=D.steps.length){h='<div class="tres"><b class="big2">'+D.end[0]+'</b>'+D.end[1]+'</div>';
    tb.innerHTML=h+'<div class="tbtns"><button id="tr">Проверить другое слово</button></div>';document.getElementById('tr').onclick=function(){i=0;show()};return}
   var s=D.steps[i];
   tb.innerHTML='<p class="tstep">Шаг '+(i+1)+' из '+D.steps.length+'</p><p class="tq">'+s[0]+'</p><p class="th">'+s[1]+'</p><div class="tbtns"><button id="ty">Да</button><button id="tn">Нет</button></div>';
   document.getElementById('ty').onclick=function(){tb.innerHTML='<div class="tres"><b class="big2">'+s[2][0]+'</b>'+s[2][1]+'</div><div class="tbtns"><button id="tr">Проверить другое слово</button></div>';document.getElementById('tr').onclick=function(){i=0;show()}};
   document.getElementById('tn').onclick=function(){i++;show()};
  }
  show();
 }
 paint();
})();
