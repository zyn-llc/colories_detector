(function () {
  // Guard against re-binding on every Streamlit rerun (the script tag is
  // re-inserted each run, but the browser tab and its window object persist).
  if (window.__caiBound) return;
  window.__caiBound = true;

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) entry.target.classList.add('cai-visible');
    });
  }, { threshold: 0.12 });

  function bindReveal() {
    document.querySelectorAll('.cai-reveal:not(.cai-visible)').forEach(function (el) {
      observer.observe(el);
    });
  }

  function bindDropzoneHighlight() {
    var zone = document.querySelector('[data-testid="stFileUploaderDropzone"]');
    if (!zone) return;
    var wrap = zone.closest('[data-testid="stFileUploader"]') || zone.parentElement;
    ['dragenter', 'dragover'].forEach(function (evt) {
      zone.addEventListener(evt, function () { wrap.classList.add('cai-dragover'); });
    });
    ['dragleave', 'drop'].forEach(function (evt) {
      zone.addEventListener(evt, function () { wrap.classList.remove('cai-dragover'); });
    });
  }

  // Streamlit re-renders the DOM on every rerun; poll briefly so newly created
  // elements (after a language switch, a new upload, etc.) still get bound.
  setInterval(function () {
    bindReveal();
    bindDropzoneHighlight();
  }, 400);
})();
