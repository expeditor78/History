(function(){
 var parts=[].slice.call(document.querySelectorAll('.history-part'));
 if(!parts.length)return;
 var id=document.body.dataset.historyId,revision=document.body.dataset.historyRevision;
 var sel=document.getElementById('history-select'),all=document.getElementById('history-all');
 var prev=document.getElementById('history-prev'),next=document.getElementById('history-next'),controls=document.getElementById('history-controls');
 var idx=0,full=false,key='hist7.lesson.'+id+'.part';
 try{idx=parseInt(localStorage.getItem(key)||'0',10)||0}catch(e){}
 idx=Math.max(0,Math.min(parts.length-1,idx));
 function paint(jump){
  parts.forEach(function(p,i){p.hidden=!full&&i!==idx});
  sel.value=String(idx);prev.disabled=idx===0;next.disabled=idx===parts.length-1;controls.hidden=full;
  all.textContent=full?'По частям':'Вся тема';all.setAttribute('aria-pressed',String(full));
  document.getElementById('history-counter').textContent=full?'Все разделы':(idx+1)+' из '+parts.length;
  document.getElementById('history-step').textContent=(idx+1)+' / '+parts.length;
  try{localStorage.setItem(key,String(idx))}catch(e){}
  if(jump){var h=parts[idx].querySelector('h2');h.focus({preventScroll:true});h.scrollIntoView({block:'start',behavior:'auto'})}
 }
 sel.addEventListener('change',function(){idx=Number(sel.value);full=false;paint(true)});
 all.addEventListener('click',function(){full=!full;paint(false)});
 prev.addEventListener('click',function(){if(idx>0){idx--;paint(true)}});
 next.addEventListener('click',function(){if(idx<parts.length-1){idx++;paint(true)}});
 paint(false);
 // Preserve the learner's records; do not treat a result from the old questions as this new test.
 var quiz=document.querySelector('.quiz'),score=quiz&&quiz.querySelector('.score'),scoreKey='hist7.lesson.'+id+'.quizRevision';
 if(score){
  var old=false;try{old=localStorage.getItem(scoreKey)!==revision}catch(e){}
  if(old&&score.textContent.indexOf('Прошлый результат:')===0)score.textContent+=' (из предыдущего теста; вопросы обновлены)';
  quiz.addEventListener('click',function(){setTimeout(function(){if(score.classList.contains('done')){try{localStorage.setItem(scoreKey,revision)}catch(e){}}},0)});
 }
})();
