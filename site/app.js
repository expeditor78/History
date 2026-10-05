(function(){
 var BASE=document.currentScript?document.currentScript.src.replace(/app\.js.*$/,''):'';
 var NAMES=['Не начато','Читаем','Повторить','Усвоено'];
 var KEY='hist7.v1';
 var S=JSON.parse(localStorage.getItem(KEY)||'{}');S.st=S.st||{};S.quiz=S.quiz||{};
 function save(){localStorage.setItem(KEY,JSON.stringify(S));}
 function cur(){var m=location.pathname.match(/\/p\/(\d+)\.html/);return m?parseInt(m[1],10):0}
 function paint(){
  var done=0;
  document.querySelectorAll('.nl[data-p]').forEach(function(a){var s=S.st[a.dataset.p]||0;a.dataset.s=s;});
  for(var k in S.st){if(S.st[k]==3)done++}
  var g=document.getElementById('gbar');if(g)g.style.width=(done/21*100)+'%';
  var t=document.getElementById('gtxt');if(t)t.textContent=done+' из 21 усвоено';
  var hb=document.getElementById('hbar');if(hb)hb.style.width=(done/21*100)+'%';
  var hn=document.getElementById('hnum');if(hn)hn.textContent=done;
  document.querySelectorAll('.card[data-p]').forEach(function(c){var s=S.st[c.dataset.p]||0;c.dataset.s=s;c.querySelector('.badge').textContent=NAMES[s];});
  var st=document.getElementById('st');if(st){var n=cur(),s=S.st[n]||0;st.parentNode.dataset.s=s;st.textContent=NAMES[s];}
  var c=document.getElementById('cont');if(c){for(var i=1;i<=21;i++){if((S.st[i]||0)!=3){c.href='p/'+(i<10?'0':'')+i+'.html';c.textContent=(S.st[i]?'Продолжить':'Начать')+' → § '+i;break}}}
 }
 var st=document.getElementById('st');
 if(st)st.addEventListener('click',function(){var n=cur();S.st[n]=((S.st[n]||0)+1)%4;save();paint();});
 var menu=document.getElementById('menu'),side=document.getElementById('side');
 if(menu)menu.addEventListener('click',function(){side.classList.toggle('open')});
 document.addEventListener('click',function(e){if(side&&side.classList.contains('open')&&!side.contains(e.target)&&e.target!==menu)side.classList.remove('open')});
 // карты: ссылки в боковом меню всех страниц и кнопки на главной
 var MAPS=[['🧭 Карта открытий','map.html'],['🏰 Карта Европы','europe.html'],['🌷 Нидерланды','netherlands.html'],['👑 Англия','england.html'],['🕌 Азия и Африка','asia.html']];
 if(side&&!side.querySelector('a[href$="map.html"]')){
  var an=side.querySelector('a[href$="timeline.html"]'),ref=an?an.nextSibling:side.querySelector('.chh');
  MAPS.forEach(function(m){var a=document.createElement('a');a.className='nl';a.href=BASE+m[1];a.textContent=m[0];side.insertBefore(a,ref)});
 }
 var qk=document.querySelector('.quick');
 if(qk&&!qk.querySelector('a[href$="map.html"]')){
  MAPS.forEach(function(m){var a=document.createElement('a');a.className='btn ghost';a.href=BASE+m[1];a.textContent=m[0];qk.appendChild(a)});
 }
 // quiz
 var quiz=document.querySelector('.quiz');
 if(quiz){
  var n=cur(),total=0,right=0,answered=0;
  var qs=quiz.querySelectorAll('.q:not(.open)');total=qs.length;
  var sc=quiz.querySelector('.score');
  function upd(){
   if(answered<total){sc.textContent='Отвечено: '+answered+' из '+total;return}
   sc.textContent='Результат: '+right+' из '+total+(right==total?' 🎉':right>=total*0.7?' — хорошо!':' — стоит повторить');sc.classList.add('done');
   S.quiz[n]=right+'/'+total;save();
   if(right<total*0.7&&(S.st[n]||0)!=3){S.st[n]=2;save();paint()}
  }
  qs.forEach(function(q){q.querySelectorAll('.opt').forEach(function(b){b.addEventListener('click',function(){
    var ok=b.dataset.l===q.dataset.a;
    q.querySelectorAll('.opt').forEach(function(o){o.disabled=true;if(o.dataset.l===q.dataset.a)o.classList.add('ok')});
    if(!ok)b.classList.add('bad');else right++;
    answered++;q.querySelector('.expl').hidden=false;upd();
  })})});
  quiz.querySelectorAll('.show').forEach(function(b){b.addEventListener('click',function(){b.nextElementSibling.hidden=false;b.hidden=true})});
  if(S.quiz[n]){sc.textContent='Прошлый результат: '+S.quiz[n]}
 }
 // PWA: офлайн и кнопка «Установить приложение» (не в APK и не по file://)
 var inApp=location.hostname==='appassets.androidplatform.net';
 if(!inApp&&'serviceWorker' in navigator&&(location.protocol==='https:'||location.hostname==='localhost')){
  navigator.serviceWorker.register(BASE+'sw.js').catch(function(){});
  var dp;
  window.addEventListener('beforeinstallprompt',function(e){
   e.preventDefault();dp=e;
   var pr=document.querySelector('.prog');if(!pr||document.getElementById('inst'))return;
   var b=document.createElement('button');b.id='inst';b.className='inst';b.textContent='⬇️ Установить приложение';
   b.onclick=function(){dp.prompt();dp.userChoice.then(function(){b.remove()})};
   pr.parentNode.insertBefore(b,pr.nextSibling);
  });
  window.addEventListener('appinstalled',function(){var b=document.getElementById('inst');if(b)b.remove()});
 }
 paint();
})();
