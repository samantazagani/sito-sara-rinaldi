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
})();
