(function(){
 var parts=[].slice.call(document.querySelectorAll('.history-part'));
 if(!parts.length)return;
 var id=document.body.dataset.historyId,key='hist7.brief.'+id+'.part';
 var sel=document.getElementById('history-select'),all=document.getElementById('history-all');
 var prev=document.getElementById('history-prev'),next=document.getElementById('history-next'),controls=document.getElementById('history-controls');
 var idx=0,full=false;
 try{idx=parseInt(localStorage.getItem(key)||'0',10)||0}catch(e){}
 idx=Math.max(0,Math.min(parts.length-1,idx));
 function paint(jump){
  parts.forEach(function(p,i){p.hidden=!full&&i!==idx});sel.value=String(idx);
  prev.disabled=idx===0;next.disabled=idx===parts.length-1;controls.hidden=full;
  all.textContent=full?'По пунктам':'Весь пересказ';all.setAttribute('aria-pressed',String(full));
  document.getElementById('history-counter').textContent=full?'Все пункты':(idx+1)+' из '+parts.length;
  document.getElementById('history-step').textContent=(idx+1)+' / '+parts.length;
  try{localStorage.setItem(key,String(idx))}catch(e){}
  if(jump){var h=parts[idx].querySelector('h2');h.focus({preventScroll:true});h.scrollIntoView({block:'start',behavior:'auto'})}
 }
 sel.addEventListener('change',function(){idx=Number(sel.value);full=false;paint(true)});
 all.addEventListener('click',function(){full=!full;paint(false)});
 prev.addEventListener('click',function(){if(idx>0){idx--;paint(true)}});
 next.addEventListener('click',function(){if(idx<parts.length-1){idx++;paint(true)}});
 paint(false);
})();
