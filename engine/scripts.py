"""
engine/scripts.py
Web engine içine enjekte edilen JavaScript ve CSS kaynakları.
"""

SMOOTH_SCROLL_CSS = """
html { scroll-behavior: smooth; }
* { scroll-behavior: smooth; }
"""

AUTO_DARK_MODE_CSS = """
@media (prefers-color-scheme: dark) {
    :root { color-scheme: dark; }
    body { background-color: #1c1b22 !important; color: #fbfbfe !important; }
    a { color: #5b5bef !important; }
    input, textarea, select {
        background-color: #2a2930 !important;
        color: #fbfbfe !important;
        border: 1px solid #35343e !important;
    }
    button {
        background-color: #2a2930 !important;
        color: #fbfbfe !important;
        border: 1px solid #35343e !important;
    }
}
"""

KEYBOARD_SCROLL_JS = """
(function() {
  if (window.__swiftx_kb) return;
  window.__swiftx_kb = true;
  const KEYS = { 32: 600, 33: -600, 34: 600, 38: -120, 40: 120 };
  const DURATION = 400;
  const EASE = t => t < 0.5 ? 2*t*t : -1+(4-2*t)*t;
  function smoothScroll(dy) {
    const el = document.scrollingElement || document.documentElement;
    const startY = el.scrollTop, start = performance.now();
    function step(now) {
      const t = Math.min((now - start) / DURATION, 1);
      el.scrollTop = startY + dy * EASE(t);
      if (t < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  window.addEventListener('keydown', function(e) {
    if (!document.activeElement || ['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)) return;
    const dy = KEYS[e.keyCode];
    if (dy === undefined) return;
    if (e.keyCode === 32) e.preventDefault();
    smoothScroll(dy);
  });
})();
"""

AUTO_DARK_MODE_JS = """
(function() {
    if (window.__auto_dark_mode) return;
    window.__auto_dark_mode = true;

    const darkTheme = window.matchMedia('(prefers-color-scheme: dark)');

    function applyDarkMode() {
        if (darkTheme.matches) {
            document.documentElement.style.colorScheme = 'dark';
            const style = document.createElement('style');
            style.textContent = `
                :root { color-scheme: dark; }
                body { background-color: #1c1b22 !important; color: #fbfbfe !important; }
                a { color: #5b5bef !important; }
                input, textarea, select {
                    background-color: #2a2930 !important;
                    color: #fbfbfe !important;
                }
            `;
            document.head.appendChild(style);
        }
    }

    applyDarkMode();
    darkTheme.addListener(() => applyDarkMode());
})();
"""
