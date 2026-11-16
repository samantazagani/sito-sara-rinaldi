/* Menu mobile, pulsante fisso di prenotazione, copia email. Nessun tracciamento. */
(function () {
  var btn = document.getElementById("menuBtn"), nav = document.getElementById("mnav");
  function setMenu(open) { if (!nav) return; nav.hidden = !open; btn.setAttribute("aria-expanded", String(open)); }
  if (btn && nav) {
    btn.addEventListener("click", function () { setMenu(nav.hidden); });
    nav.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });
    window.addEventListener("resize", function () { if (innerWidth > 820) setMenu(false); });
  }

  var dock = document.getElementById("dock");
  if (dock) {
    if (!("IntersectionObserver" in window)) { dock.classList.add("on"); }
    else {
      var seen = new Map();
      var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) { seen.set(e.target, e.isIntersecting); });
        dock.classList.toggle("on", !Array.from(seen.values()).some(Boolean));
      });
      [document.querySelector(".hero .actions"), document.getElementById("contatti"), document.querySelector(".sitefoot")]
        .forEach(function (t) { if (t) { seen.set(t, false); io.observe(t); } });
    }
  }

  document.addEventListener("click", function (e) {
    var b = e.target.closest("[data-copy]");
    if (!b) return;
    var txt = b.getAttribute("data-copy"), old = b.textContent;
    function done() { b.textContent = "Copiato"; setTimeout(function () { b.textContent = old; }, 1800); }
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(done, function () {});
  });

  /* intestazione con ombra dopo lo scorrimento */
  var top = document.querySelector("header.top");
  if (top) {
    var onScroll = function () { top.classList.toggle("scrolled", window.scrollY > 8); };
    window.addEventListener("scroll", onScroll, { passive: true }); onScroll();
  }

  /* comparsa allo scorrimento */
  if (document.documentElement.classList.contains("anim")) {
    var sel = ".head, .three > div, .stepper, .stepper li, .panel, .card, .pull, .contact, .round, .prose, .chips, .center, .cta-box, .more h2, .formula";
    var reveal = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); reveal.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    document.querySelectorAll(sel).forEach(function (el) { reveal.observe(el); });
  }

  /* linee ondulate dell'hero: movimento lento, in pausa fuori schermo o a scheda nascosta */
  var art = document.querySelector(".hero-art svg");
  if (art && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var paths = art.querySelectorAll("path"), W = 1200, H = 600, n = paths.length, visible = true, last = 0, t0 = performance.now();
    new IntersectionObserver(function (es) { visible = es[0].isIntersecting; if (visible) requestAnimationFrame(frame); }).observe(art);
    function frame(now) {
      if (!visible || document.hidden) return;
      requestAnimationFrame(frame);
      if (now - last < 33) return;
      last = now;
      var ph = (now - t0) / 1000 * 0.35;
      for (var i = 0; i < n; i++) {
        var base = 40 + i * (H - 80) / (n - 1), d = "";
        for (var x = 0; x <= W; x += 10) {
          var t = x / W, e = Math.sin(Math.PI * t);
          var y = H / 2 + (base - H / 2) * (0.22 + 0.78 * e) + 46 * Math.sin(t * 6.2 + i * 0.3 + ph) * e;
          d += (x === 0 ? "M" : "L") + x + " " + y.toFixed(1) + " ";
        }
        paths[i].setAttribute("d", d);
      }
    }
    document.addEventListener("visibilitychange", function () { if (!document.hidden && visible) requestAnimationFrame(frame); });
    requestAnimationFrame(frame);
  }
})();
