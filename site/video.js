(function(){
 // Видеоразборы по параграфам (YouTube, канал Tatiana Themis — серия «История Нового времени 7 / Мединский»).
 // [id видео, длительность]. Ключ — номер страницы (1..21).
 var V={
  1:['ISlQzbwqXHg','19:45'],2:['wo59YKor-AE','20:31'],3:['-3OXpYC13w4','28:22'],
  4:['jAWJPzGAEw0','21:51'],5:['7qENzDfLRf0','23:23'],6:['0-XWz2pn1FI','21:54'],
  7:['ZkX6b6oPIvM','19:16'],8:['2GJ6BqdvDpU','16:03'],9:['jyqb3gc5hYQ','17:24'],
  10:['Xuesbuv0WyM','15:50'],11:['TbUq1jnH8S4','21:20'],12:['0-NkuYcP7zU','20:02'],
  13:['PvU415Sj464','22:08'],14:['utScbaZw6jA','26:20'],15:['JzGoDqhh5xY','19:20'],
  16:['THpKSNjSIgI','19:20'],17:['k-9y_Wklnas','21:45'],18:['0UH2FBSgaTk','19:39'],
  19:['HSh9Yx7bYis','12:38'],20:['OTqONm6hPB8','21:50'],21:['hrqxQNeJDOA','12:03']
 };
 var m=location.pathname.match(/\/p\/(\d+)\.html/);if(!m)return;
 var n=parseInt(m[1],10),v=V[n];if(!v)return;
 var st=document.querySelector('.status');if(!st)return;
 var id=v[0],url='https://www.youtube.com/watch?v='+id;
 var box=document.createElement('section');box.className='vid';
 box.innerHTML='<h2>🎬 Видеоразбор параграфа</h2>'+
  '<div class="vframe"><button class="vplay" type="button" aria-label="Смотреть видео">'+
  '<img src="https://i.ytimg.com/vi/'+id+'/hqdefault.jpg" alt="" loading="lazy">'+
  '<span class="pb">▶</span><span class="dur">'+v[1]+'</span></button></div>'+
  '<p class="vmeta">Смотрите вместе с чтением шпаргалки. Если видео не открывается — <a href="'+url+'" target="_blank" rel="noopener">смотреть на YouTube ↗</a></p>';
 st.parentNode.insertBefore(box,st.nextSibling);
 box.querySelector('.vplay').addEventListener('click',function(){
  var f=document.createElement('iframe');
  f.src='https://www.youtube-nocookie.com/embed/'+id+'?autoplay=1&rel=0';
  f.title='Видеоразбор параграфа '+n;f.allow='accelerometer; autoplay; encrypted-media; picture-in-picture; fullscreen';
  f.allowFullscreen=true;f.referrerPolicy='strict-origin-when-cross-origin';
  box.querySelector('.vframe').replaceChildren(f);
 });
})();
