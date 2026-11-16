#!/usr/bin/env python3
"""Genera il sito di Sara Rinaldi nella cartella public/ (è quella da pubblicare).

Uso:   python3 build.py
Per aggiungere un articolo: copia un file in content/articoli/, cambia testata e testo, rilancia questo script.
"""
import html, json, math, re, shutil, sys
from pathlib import Path
from urllib.parse import quote

# ============ CONFIGURAZIONE (da completare) ============
SITE_URL = "https://sararinaldimentalcoach.com"
NAME = "Sara Rinaldi"
BRAND = "Mindset Revolution"
EMAIL = "sara.rinaldi.training@gmail.com"
PIVA = ""         # es. "P.IVA 01234567890"
INDIRIZZO = ""    # es. "Via Roma 1, 44121 Ferrara (FE)"
CONSERVAZIONE = ""  # es. "per 12 mesi dall'ultimo scambio, se non nasce un rapporto professionale"
AGGIORNATA = "16 novembre 2026"
# ========================================================

ROOT = Path(__file__).parent
OUT = ROOT / "public"
ACC, RING = "#4651b0", "#d3d7ea"
CTA_LABEL = "Prenota la sessione gratuita"
MAILTO = ("mailto:" + EMAIL + "?subject=" + quote("Prenotazione sessione gratuita di 30 minuti")
          + "&body=" + quote("Ciao Sara,\nvorrei prenotare la sessione gratuita di 30 minuti.\n\nNome:\nDi cosa mi occupo:\nGiorni e orari che preferisco:\n"))
warnings = []
# Finché mancano i dati il sito è in "prova": non viene indicizzato dai motori di ricerca.
READY = bool(PIVA and INDIRIZZO and CONSERVAZIONE)

def todo(label):
    warnings.append(label)
    return f'<span class="todo">[{label}]</span>'

def esc(s): return html.escape(s, quote=False)
def inline(s):
    s = esc(s)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)

# ---------- grafica ----------
def hero_art():
    W, H, n, acc = 1200, 600, 21, 9
    g = ""
    for i in range(n):
        base = 40 + i * (H - 80) / (n - 1)
        d = ""
        for x in range(0, W + 1, 10):
            t = x / W; e = math.sin(math.pi * t)
            y = H / 2 + (base - H / 2) * (0.22 + 0.78 * e) + 46 * math.sin(t * 6.2 + i * 0.3) * e
            d += ("M" if x == 0 else "L") + f"{x} {y:.1f} "
        on = i == acc
        g += (f'<path d="{d}" stroke="{ACC if on else RING}" stroke-opacity="{0.65 if on else 1}" '
              f'stroke-width="{1.3 if on else 1}" vector-effect="non-scaling-stroke"/>')
    return (f'<svg viewBox="0 0 {W} {H}" fill="none" preserveAspectRatio="none" aria-hidden="true">'
            '<defs><linearGradient id="wfade" x1="0" x2="1" y1="0" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
            '<stop offset=".16" stop-color="#fff"/><stop offset=".84" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="wmask"><rect width="{W}" height="{H}" fill="url(#wfade)"/></mask></defs><g mask="url(#wmask)">{g}</g></svg>')

def mini_arcs(n):
    s = '<svg viewBox="0 0 96 56" fill="none" aria-hidden="true">'
    for i in range(n):
        r = 12 + i * 12
        s += (f'<path d="M{48 - r} 52 A{r} {r} 0 0 1 {48 + r} 52" stroke="{ACC if i == n - 1 else "#a9aed0"}" '
              'stroke-width="1.4" stroke-linecap="round"/>')
    return s + f'<circle cx="48" cy="52" r="2.5" fill="{ACC}"/></svg>'

def round_svg():
    s = '<svg viewBox="0 0 340 340" fill="none" aria-hidden="true">'
    for i, r in enumerate([168, 150, 132]):
        dash = ' stroke-dasharray="2 6"' if i == 2 else ""
        s += f'<circle cx="170" cy="170" r="{r}" stroke="{ACC if i == 1 else RING}" stroke-width="1"{dash}/>'
    return s + f'<circle cx="{170 + 150 * math.cos(-0.9):.1f}" cy="{170 + 150 * math.sin(-0.9):.1f}" r="4" fill="{ACC}"/></svg>'

# ---------- articoli ----------
def parse_article(path):
    raw = path.read_text(encoding="utf-8")
    _, fm, body = raw.split("---\n", 2)
    meta = {}
    for line in fm.strip().splitlines():
        k, v = line.split(":", 1); meta[k.strip()] = v.strip()
    meta["slug"] = path.stem
    meta["words"] = len(re.findall(r"\w+", body))
    meta["minutes"] = max(1, round(meta["words"] / 200))
    meta["html"] = md_to_html(body)
    return meta

def md_to_html(md):
    out, lines, i = [], md.strip("\n").splitlines(), 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip(): i += 1; continue
        if ln.startswith("::: "):
            cls = ln[4:].strip(); i += 1; buf = []
            while i < len(lines) and lines[i].strip() != ":::":
                if lines[i].strip(): buf.append(f"<p>{inline(lines[i].strip())}</p>")
                i += 1
            out.append(f'<div class="{cls}">{"".join(buf)}</div>'); i += 1; continue
        if ln.startswith("### "): out.append(f"<h3>{inline(ln[4:])}</h3>"); i += 1; continue
        if ln.startswith("## "): out.append(f"<h2>{inline(ln[3:])}</h2>"); i += 1; continue
        if ln.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(f"<li>{inline(lines[i][2:])}</li>"); i += 1
            out.append(f'<ul>{"".join(items)}</ul>'); continue
        buf = []
        while i < len(lines) and lines[i].strip() and not lines[i].startswith(("#", "- ", "::: ")):
            buf.append(lines[i].strip()); i += 1
        out.append(f"<p>{inline(' '.join(buf))}</p>")
    return "\n".join(out)

ARTICLES = [parse_article(p) for p in sorted((ROOT / "content/articoli").glob("*.md"))]
ORDER = ["costo-nascosto-autosabotaggio-blocco-mentale", "riprogrammare-identita-successo-business", "riprogrammare-sistema-nervoso-performance"]
ARTICLES.sort(key=lambda a: ORDER.index(a["slug"]) if a["slug"] in ORDER else 99)

# ---------- struttura comune ----------
def head(title, desc, path, og_type="website", extra="", robots="index, follow"):
    if not READY: robots = "noindex, nofollow"
    url = SITE_URL + path
    t = esc(title)
    return f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{t}</title>
<meta name="description" content="{html.escape(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#f7f7fb">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta property="og:type" content="{og_type}">
<meta property="og:locale" content="it_IT">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE_URL}/img/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="/fonts/jost-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/dm-sans-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/style.css">
{extra}</head>
<body>
<a class="skip" href="#main">Vai al contenuto</a>
'''

def header(active=""):
    def a(href, label, key, cls=""):
        cur = ' aria-current="page"' if key and key == active else ""
        return f'<a href="{href}"{cur}{(" class=" + chr(34) + cls + chr(34)) if cls else ""}>{label}</a>'
    return f'''<header class="top">
  <div class="wrap hdr">
    <nav class="l" aria-label="Principale">
      {a("/#metodo", "Metodo", "")}
      {a("/#storia", "Storia", "")}
      {a("/#percorso", "Percorso", "")}
    </nav>
    <a class="brand" href="/">{BRAND}<small>{NAME} · Coaching</small></a>
    <nav class="r" aria-label="Secondaria">
      {a("/#perchi", "A chi è rivolto", "")}
      {a("/blog/", "Blog", "blog")}
      {a("/#contatti", "Contatti", "", "cta")}
    </nav>
    <button class="menu-btn" id="menuBtn" type="button" aria-expanded="false" aria-controls="mnav"><span>Menu</span><i aria-hidden="true"></i></button>
  </div>
  <nav class="mnav" id="mnav" aria-label="Menu" hidden>
    <a class="l" href="/#metodo">Metodo</a>
    <a class="l" href="/#storia">Storia</a>
    <a class="l" href="/#percorso">Percorso</a>
    <a class="l" href="/#perchi">A chi è rivolto</a>
    <a class="l" href="/blog/">Blog</a>
    <a class="btn" href="/#contatti">{CTA_LABEL}</a>
  </nav>
</header>
'''

def footer():
    legal = " · ".join(x for x in [NAME, PIVA, INDIRIZZO] if x) if (PIVA or INDIRIZZO) else ""
    if not PIVA or not INDIRIZZO:
        warnings.append("Footer: mancano P.IVA e/o indirizzo")
    return f'''<footer class="sitefoot">
  <div class="row"><span>© 2026 {NAME} · {BRAND}</span><a href="/privacy">Privacy policy</a><a href="/blog/">Blog</a></div>
  {f'<div>{esc(legal)}</div>' if legal else ''}
  <p class="note">Il mental coaching non è psicoterapia né un trattamento sanitario e non sostituisce il parere di un medico o di uno psicologo.</p>
</footer>
<script src="/site.js" defer></script>
</body>
</html>
'''

def cards(items, cls="cards"):
    out = f'<div class="{cls}">'
    for a in items:
        out += (f'<a class="card" href="/blog/{a["slug"]}"><span class="k">{esc(a["tag"])} · {a["minutes"]} min</span>'
                f'<h3>{esc(a["title"])}</h3><p>{esc(a["description"])}</p><span class="go">Leggi l\'articolo →</span></a>')
    return out + "</div>"

def write(rel, content):
    p = OUT / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(content, encoding="utf-8")

# ---------- home ----------
def contact_block():
    return f'''<section class="contact" id="contatti">
    <p class="label">Contatti</p>
    <span class="free">Sessione gratuita · 30 minuti</span>
    <h2>Il tuo successo è il mio unico obiettivo.</h2>
    <p class="lead2">Che tu sia un imprenditore, un atleta, un professionista o semplicemente una persona che sente il bisogno di sbloccare il proprio potenziale e ritrovare la propria strada: se vuoi evolvere senza perdere la tua serenità, iniziamo da qui. Scrivimi per prenotare la tua sessione gratuita di 30 minuti.</p>
    <ul class="ticks"><li>Riservatezza assoluta</li><li>Niente schemi rigidi</li><li>Sessioni da 30–45 minuti</li></ul>
    <a class="btn" href="{MAILTO}">Prenota la sessione gratuita</a>
    <p class="addr">oppure scrivi a <a class="textlink" href="mailto:{EMAIL}">{EMAIL}</a><button class="copybtn" type="button" data-copy="{EMAIL}">Copia</button></p>
  </section>'''

def home():
    return f'''<main id="main" class="wrap">
  <section class="hero">
    <div class="hero-art" aria-hidden="true">{hero_art()}</div>
    <h1>Performance d'eccellenza. <em>Equilibrio</em> duraturo.</h1>
    <p class="lead">Inizia oggi la tua evoluzione. Con un percorso strutturato impariamo a mappare i reali obiettivi, gestire la pressione interna e definire flussi d'azione efficaci per sbloccare la tua visione di successo.</p>
    <div class="actions">
      <a class="btn" href="#contatti">{CTA_LABEL}</a>
      <a class="btn ghost" href="#percorso">Scopri il percorso</a>
    </div>
    <dl class="numbers">
      <div><dd>5+</dd><dt>anni di esperienza</dt></div>
      <div><dd>3–4</dd><dt>sessioni al mese</dt></div>
      <div><dd>30–45′</dd><dt>di focus intenso</dt></div>
      <div><dd>Assoluta</dd><dt>riservatezza</dt></div>
    </dl>
  </section>

  <section class="block" id="metodo">
    <div class="head">
      <p class="label">Il metodo</p>
      <h2>Tre mosse per passare dall'intenzione all'azione.</h2>
    </div>
    <div class="three">
      <div>{mini_arcs(1)}<h3>Mappare</h3><p class="w">I reali obiettivi</p><p class="t">Partiamo da dove sei: il tuo ruolo, la tua routine, ciò che vuoi davvero. Troviamo il tuo «perché», la forza che regge tutto il resto.</p></div>
      <div>{mini_arcs(2)}<h3>Gestire</h3><p class="w">La pressione interna</p><p class="t">Lavoriamo su stress, credenze limitanti e conflitti, perché l'eccellenza non si paghi con la tua serenità.</p></div>
      <div>{mini_arcs(3)}<h3>Agire</h3><p class="w">Flussi d'azione efficaci</p><p class="t">Gli esercizi pratici tra una sessione e l'altra trasformano ciò che hai capito in abitudini concrete.</p></div>
    </div>
    <p class="center"><a class="textlink" href="#percorso">Vedi i 5 passaggi dell'Intake Session →</a></p>
  </section>

  <section class="block" id="storia">
    <div class="story">
      <div class="head">
        <p class="label">La mia storia</p>
        <h2>Ho imparato a leggere le persone viaggiando.</h2>
      </div>
      <div class="round">{round_svg()}<img class="photo" alt="{NAME}" width="245" height="245" src="/img/sara.jpg"></div>
      <div class="prose">
        <p>Ciao, sono Sara. A 19 anni ho preso in mano la mia vita e ho iniziato a girare il mondo. Non sono diventata una coach restando seduta dietro una scrivania a leggere manuali di teoria.</p>
        <p>Ho viaggiato, esplorato, vissuto da vicino i volti e le storie di culture diverse. Questo viaggio mi ha permesso di sviluppare un dono innato: la capacità di <strong>leggere le persone oltre la superficie</strong>, decodificando i loro reali bisogni in pochi istanti.</p>
        <p>Da oltre 5 anni metto questa sensibilità internazionale al servizio di chiunque desideri una svolta: dai profili junior ai ruoli di livello senior, fino a chi semplicemente vuole ritrovare la bussola nella propria vita quotidiana.</p>
        <p class="sig">Sara Rinaldi</p>
      </div>
    </div>
    <p class="pull">{mini_arcs(3)}Il vero successo non è una vetta da raggiungere in solitudine, ma un percorso da fare insieme, proteggendo il tuo tempo, la tua serenità e la tua salute.<small>La mia filosofia: il valore del dono</small></p>
  </section>

  <section class="block" id="percorso">
    <div class="head">
      <p class="label">L'alleanza strategica</p>
      <h2>Si comincia con l'Intake Session.</h2>
      <p>È la base del nostro viaggio: uno spazio protetto, coperto da riservatezza assoluta, in cui mappiamo la tua situazione attuale. Niente schemi rigidi.</p>
    </div>
    <ol class="stepper">
      <li><span class="num">1</span><h3>Decodifica del ruolo e della routine</h3><p>Analizziamo la tua attività professionale o atletica per individuare dove perdi focus o dove si accumula lo stress operativo.</p></li>
      <li><span class="num">2</span><h3>Il potere del «perché»</h3><p>Troviamo la tua vera forza motrice e i valori non negoziabili su cui poggia la tua resilienza.</p></li>
      <li><span class="num">3</span><h3>Mappatura degli ostacoli</h3><p>Affrontiamo sia i limiti esterni (team, mercato, rivalità sportive) sia quelli interni (credenze limitanti, paura di fallire).</p></li>
      <li><span class="num">4</span><h3>Analisi delle aspettative</h3><p>Definiamo le tue priorità assolute: più autostima, gestione agile dei conflitti, organizzazione del tempo.</p></li>
      <li><span class="num">5</span><h3>Logistica personalizzata</h3><p>Un ritmo attivo di incontri, con esercizi pratici da svolgere tra una sessione e l'altra.</p></li>
    </ol>
    <div class="chips"><span class="chip">3–4 sessioni al mese</span><span class="chip">30–45 minuti ciascuna</span><span class="chip">Esercizi tra un incontro e l'altro</span></div>
    <p class="center"><a class="btn" href="#contatti">{CTA_LABEL}</a></p>
  </section>

  <section class="block" id="perchi">
    <div class="head">
      <p class="label">A chi è rivolto</p>
      <h2>Per chi vuole evolvere senza perdere la serenità.</h2>
    </div>
    <div class="panels">
      <div class="panel">{mini_arcs(1)}<h3>Imprenditori</h3><p>Decisioni, team e pressione del mercato.</p></div>
      <div class="panel">{mini_arcs(2)}<h3>Atleti</h3><p>Focus, gestione della gara e della rivalità.</p></div>
      <div class="panel">{mini_arcs(3)}<h3>Professionisti</h3><p>Dai profili junior ai ruoli di livello senior.</p></div>
      <div class="panel">{mini_arcs(4)}<h3>Chi cerca la rotta</h3><p>Ritrovare la bussola nella vita quotidiana.</p></div>
    </div>
  </section>

  <section class="block" id="blog">
    <div class="head">
      <p class="label">Il blog</p>
      <h2>Letture per mettersi in movimento.</h2>
      <p>Spunti pratici su blocchi mentali, identità e gestione della pressione.</p>
    </div>
    {cards(ARTICLES)}
    <p class="center"><a class="textlink" href="/blog/">Tutti gli articoli →</a></p>
  </section>

  {contact_block()}
</main>
<div class="dock" id="dock"><a class="btn" href="#contatti">{CTA_LABEL}</a></div>
'''

DESC_HOME = "Mental coaching per imprenditori, atleti e professionisti: un percorso strutturato per gestire la pressione, sbloccare il potenziale e ritrovare equilibrio. Prenota una sessione gratuita di 30 minuti."
ldjson_home = f'''<script type="application/ld+json">{{"@context":"https://schema.org","@type":"ProfessionalService","name":"{BRAND}","url":"{SITE_URL}/","image":"{SITE_URL}/img/og.png","description":"Mental coaching per imprenditori, atleti e professionisti.","founder":{{"@type":"Person","name":"{NAME}","jobTitle":"Mental coach"}},"areaServed":"IT","inLanguage":"it"}}</script>
'''
write("index.html", head(f"{BRAND} · {NAME}, mental coach", DESC_HOME, "/", extra=ldjson_home) + header() + home() + footer())

# ---------- blog ----------
blog_main = f'''<main id="main" class="wrap page">
  <div class="head">
    <p class="label">Il blog</p>
    <h1 style="font-size:clamp(40px,7vw,80px)">Letture per mettersi in movimento.</h1>
    <p>Spunti pratici su blocchi mentali, identità e gestione della pressione.</p>
  </div>
  {cards(ARTICLES, "cards list")}
</main>
'''
write("blog/index.html", head(f"Blog · {BRAND}", "Articoli di mental coaching su blocchi mentali, identità e gestione della pressione, per professionisti, imprenditori e atleti.", "/blog/") + header("blog") + blog_main + footer())

for a in ARTICLES:
    others = [x for x in ARTICLES if x["slug"] != a["slug"]]
    main = f'''<main id="main" class="wrap page">
  <article class="article">
    <header>
      <nav class="crumb" aria-label="Percorso"><a href="/">Home</a><span aria-hidden="true">/</span><a href="/blog/">Blog</a></nav>
      <h1>{esc(a["title"])}</h1>
      <p class="deck">{esc(a["description"])}</p>
      <p class="info">{NAME} · {a["minutes"]} min di lettura</p>
    </header>
    <div class="body">
{a["html"]}
    </div>
    <aside class="cta-box" aria-label="Prenota la sessione gratuita">
      <span class="free">Sessione gratuita · 30 minuti</span>
      <h2>{esc(a["cta_title"])}</h2>
      <p>{esc(a["cta_text"])}</p>
      <a class="btn" href="{MAILTO}">Prenota la sessione gratuita di 30 minuti</a>
      <p class="addr">oppure scrivi a <a class="textlink" href="mailto:{EMAIL}">{EMAIL}</a></p>
    </aside>
  </article>
  <section class="more"><h2>Continua a leggere</h2>{cards(others)}</section>
</main>
'''
    ld = ('<script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["description"],
        "author": {"@type": "Person", "name": NAME}, "publisher": {"@type": "Organization", "name": BRAND},
        "mainEntityOfPage": f'{SITE_URL}/blog/{a["slug"]}', "image": f"{SITE_URL}/img/og.png", "inLanguage": "it"},
        ensure_ascii=False) + "</script>\n")
    write(f"blog/{a['slug']}.html", head(f'{a["meta_title"]} | {NAME}', a["description"], f'/blog/{a["slug"]}', "article", ld) + header("blog") + main + footer())

# ---------- privacy ----------
def fill(md):
    rep = {"{{TITOLARE}}": f"<strong>{NAME}</strong>",
           "{{INDIRIZZO}}": INDIRIZZO or todo("indirizzo da inserire"),
           "{{PIVA}}": PIVA or todo("partita IVA da inserire"),
           "{{EMAIL}}": f'<a href="mailto:{EMAIL}">{EMAIL}</a>',
           "{{CONSERVAZIONE}}": (esc(CONSERVAZIONE) + ".") if CONSERVAZIONE else todo("tempo di conservazione da decidere con il commercialista") + "."}
    for k, v in rep.items(): md = md.replace(k, v)
    return md

def privacy_html(md):
    out = []
    for blk in md.strip().split("\n\n"):
        blk = blk.strip()
        if blk.startswith("## "): out.append(f"<h2>{esc(blk[3:])}</h2>")
        elif blk.startswith("- "):
            items = "".join(f"<li>{rich(x[2:])}</li>" for x in blk.splitlines())
            out.append(f"<ul>{items}</ul>")
        else: out.append(f"<p>{rich(blk)}</p>")
    return "\n".join(out)

def rich(s):
    # consente solo i tag che inseriamo noi (a, span, strong); il resto viene mostrato come testo
    tokens = re.split(r"(<[^>]+>)", s)
    return "".join(t if t.startswith("<") else re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(t)) for t in tokens)

pmd = fill((ROOT / "content/privacy.md").read_text(encoding="utf-8"))
priv = f'''<main id="main" class="wrap page">
  <div class="legal">
    <h1>Privacy policy</h1>
    <p class="upd">Informativa ai sensi degli artt. 13 e 14 del Regolamento (UE) 2016/679 · Ultimo aggiornamento: {AGGIORNATA}</p>
    <div class="body">
{privacy_html(pmd)}
    </div>
  </div>
</main>
'''
write("privacy.html", head(f"Privacy policy · {BRAND}", "Informativa sul trattamento dei dati personali del sito di Sara Rinaldi.", "/privacy") + header() + priv + footer())

# ---------- 404 ----------
nf = '''<main id="main" class="wrap"><div class="notfound"><p class="label">Errore 404</p><h1>Pagina non trovata.</h1><p>Il link potrebbe essere cambiato o non esistere più.</p><a class="btn" href="/">Torna alla home</a></div></main>
'''
write("404.html", head(f"Pagina non trovata · {BRAND}", "Pagina non trovata.", "/404", robots="noindex") + header() + nf + footer())

# ---------- file statici, sitemap, robots ----------
shutil.copy(ROOT / "static/style.css", OUT / "style.css")
shutil.copytree(ROOT / "static/fonts", OUT / "fonts", dirs_exist_ok=True)
shutil.copytree(ROOT / "static/img", OUT / "img", dirs_exist_ok=True)
for f in ["site.js", "favicon.svg", "apple-touch-icon.png"]:
    if (ROOT / "static" / f).exists(): shutil.copy(ROOT / "static" / f, OUT / f)

urls = ["/", "/blog/"] + [f'/blog/{a["slug"]}' for a in ARTICLES] + ["/privacy"]
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
      + "".join(f"  <url><loc>{SITE_URL}{u}</loc></url>\n" for u in urls) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n" if READY else "User-agent: *\nDisallow: /\n")

print(f"Generate {len(urls)} pagine in {OUT}")
if not READY: print("MODALITÀ PROVA: il sito non verrà indicizzato da Google finché non compili PIVA, INDIRIZZO e CONSERVAZIONE.")
for w in sorted(set(warnings)): print("ATTENZIONE:", w)
