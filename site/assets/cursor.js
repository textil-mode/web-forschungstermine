// Custom Cursor (Tex Started 01): Cyan-Punkt + nachlaufender Ring. Auf Touch inaktiv.
(function(){
  if (window.matchMedia && window.matchMedia('(hover:none)').matches) return;
  const dot = document.getElementById('cursor');
  const ring = document.getElementById('cursorRing');
  if (!dot || !ring) return;
  document.addEventListener('mousemove', e => {
    dot.style.left = e.clientX + 'px';
    dot.style.top = e.clientY + 'px';
    ring.style.left = e.clientX + 'px';
    ring.style.top = e.clientY + 'px';
  });
})();
