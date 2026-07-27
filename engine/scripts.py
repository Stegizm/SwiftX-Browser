"""
engine/scripts.py
Web engine içine enjekte edilen JavaScript ve CSS kaynakları.
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

SMOOTH_SCROLL_JS = """
(function() {
  if (window.__swiftx_smooth) return;
  window.__swiftx_smooth = true;

  // ── Ayarlar ──
  var TARGET_FPS = 60;
  var FRAME_MS = 1000 / TARGET_FPS;
  var SMOOTH_FACTOR = 0.85;     // 0-1 arası,越高越平滑
  var MIN_DELTA = 0.3;          // 最小滚动阈值，避免微颤

  var targetY = 0;
  var currentY = 0;
  var rafId = null;
  var lastTime = 0;
  var scrolling = false;

  function getScrollEl() {
    // Aktif element scrollable ise onu kullan, değilse document
    var el = document.activeElement;
    if (el && el !== document.body && el !== document.documentElement) {
      var style = window.getComputedStyle(el);
      if ((style.overflowY === 'auto' || style.overflowY === 'scroll') &&
          el.scrollHeight > el.clientHeight) {
        return el;
      }
    }
    return document.scrollingElement || document.documentElement;
  }

  function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  function animate(now) {
    if (!scrolling) return;

    if (now - lastTime < FRAME_MS) {
      rafId = requestAnimationFrame(animate);
      return;
    }
    lastTime = now;

    var el = getScrollEl();
    var diff = targetY - el.scrollTop;

    if (Math.abs(diff) < MIN_DELTA) {
      el.scrollTop = targetY;
      scrolling = false;
      return;
    }

    // Smooth lerp ile hedefe yaklaştır
    el.scrollTop += diff * SMOOTH_FACTOR;
    rafId = requestAnimationFrame(animate);
  }

  function startScroll() {
    if (!scrolling) {
      scrolling = true;
      lastTime = performance.now();
      rafId = requestAnimationFrame(animate);
    }
  }

  // ── Mouse wheel ──
  window.addEventListener('wheel', function(e) {
    var tag = document.activeElement ? document.activeElement.tagName : '';
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
    if (e.ctrlKey || e.shiftKey) return;
    // Video player içindeyken smooth scroll devre dışı
    var target = e.target;
    while (target && target !== document.body && target !== document.documentElement) {
      if (target.tagName === 'VIDEO' || target.tagName === 'IFRAME' ||
          target.classList.contains('html5-video-container') ||
          target.classList.contains('ytd-player') ||
          target.getAttribute('id') === 'movie_player') {
        return; // Video oynatıcıysa normal davranış
      }
      target = target.parentElement;
    }

    e.preventDefault();

    var el = getScrollEl();
    // deltaY'yi normalize et (trackpad vs mouse farkını azalt)
    var delta = -e.deltaY;
    // Trackpad çok küçük delta gönderir, mouse daha büyük
    // Her ikisini de makul bir aralığa çek
    var step = delta;
    if (Math.abs(delta) > 100) {
      // Trackpad: küçült
      step = Math.sign(delta) * Math.min(Math.abs(delta) * 0.6, 600);
    } else if (Math.abs(delta) < 50) {
      // Mouse wheel: çarp
      step = delta * 3;
    }

    targetY = el.scrollTop + step;
    // Sınırları kontrol et
    targetY = Math.max(0, Math.min(targetY, el.scrollHeight - el.clientHeight));

    startScroll();
  }, { passive: false });
})();
"""

KEYBOARD_SCROLL_JS = """
(function() {
  if (window.__swiftx_kb) return;
  window.__swiftx_kb = true;
  var KEYS = { 32: 600, 33: -600, 34: 600, 38: -120, 40: 120 };
  var DURATION = 300;
  function easeOutCubic(t) { return 1 - Math.pow(1 - t, 3); }
  function smoothScroll(dy) {
    var el = document.scrollingElement || document.documentElement;
    var startY = el.scrollTop, start = performance.now();
    function step(now) {
      var t = Math.min((now - start) / DURATION, 1);
      el.scrollTop = startY + dy * easeOutCubic(t);
      if (t < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  window.addEventListener('keydown', function(e) {
    if (!document.activeElement || ['INPUT','TEXTAREA','SELECT'].includes(document.activeElement.tagName)) return;
    var dy = KEYS[e.keyCode];
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

    function applyDarkMode() {
        // about:blank veya document hazır değilse atla
        if (!document.documentElement || !document.head) return;
        var darkTheme = window.matchMedia('(prefers-color-scheme: dark)');
        if (darkTheme.matches) {
            document.documentElement.style.colorScheme = 'dark';
            var style = document.createElement('style');
            style.textContent =
                ':root { color-scheme: dark; }' +
                'body { background-color: #1c1b22 !important; color: #fbfbfe !important; }' +
                'a { color: #5b5bef !important; }' +
                'input, textarea, select { background-color: #2a2930 !important; color: #fbfbfe !important; }';
            document.head.appendChild(style);
        }
    }

    applyDarkMode();
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyDarkMode);
})();
"""
