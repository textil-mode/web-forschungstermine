// Custom Cursor (Bold-Yellow-Signature) — auf Touch-Geräten inaktiv
(function(){
  if (window.matchMedia && window.matchMedia('(hover:none)').matches) return;
  const dot = document.getElementById('cursorDot');
  if (!dot) return;
  let tx=-100, ty=-100, cx=-100, cy=-100;
  document.addEventListener('mousemove', e => { tx=e.clientX; ty=e.clientY; });
  function raf(){
    cx += (tx-cx)*0.22; cy += (ty-cy)*0.22;
    dot.style.transform = 'translate3d('+cx+'px,'+cy+'px,0) translate(-50%,-50%)';
    requestAnimationFrame(raf);
  }
  raf();
  // Hover-Vergrößerung über interaktiven Elementen (auch dynamisch gerendert)
  document.addEventListener('mouseover', e => {
    if (e.target.closest('a,button,.toggle,.event,.cal-ev,.cta')) dot.classList.add('is-hover');
  });
  document.addEventListener('mouseout', e => {
    if (e.target.closest('a,button,.toggle,.event,.cal-ev,.cta')) dot.classList.remove('is-hover');
  });
})();
