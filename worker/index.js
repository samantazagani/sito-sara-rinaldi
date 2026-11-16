/**
 * Mini API per scrivere gli articoli dal pannello /admin.
 *
 * - Le richieste a /api/* passano da qui, tutto il resto è servito come sito statico.
 * - Protezione: password (ADMIN_PASSWORD, segreto di Cloudflare) inviata nell'intestazione X-Admin-Password.
 * - Salvataggio: crea/aggiorna file in content/articoli/ del repository GitHub (GITHUB_TOKEN, segreto).
 *   Ogni salvataggio è un commit: Cloudflare ricostruisce e ripubblica il sito da solo.
 */

const DIR = "content/articoli";
const SLUG_RE = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const KEYS = ["title", "meta_title", "description", "tag", "date", "cta_title", "cta_text"];
const LIMITS = { title: 200, meta_title: 200, description: 400, tag: 60, cta_title: 200, cta_text: 800, body: 60000 };

const json = (data, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });

const enc = new TextEncoder();
const dec = new TextDecoder();

function b64encode(str) {
  const bytes = enc.encode(str);
  let bin = "";
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
  return btoa(bin);
}
function b64decode(b64) {
  const bin = atob(b64.replace(/\s/g, ""));
  return dec.decode(Uint8Array.from(bin, (c) => c.charCodeAt(0)));
}

async function sameSecret(a, b) {
  const [x, y] = await Promise.all([crypto.subtle.digest("SHA-256", enc.encode(a)), crypto.subtle.digest("SHA-256", enc.encode(b))]);
  const xa = new Uint8Array(x), ya = new Uint8Array(y);
  let diff = 0;
  for (let i = 0; i < xa.length; i++) diff |= xa[i] ^ ya[i];
  return diff === 0;
}

/* ---------- formato dei file (testata + testo) ---------- */
export function parseArticle(raw) {
  const text = raw.replace(/\r\n/g, "\n");
  if (!text.startsWith("---\n")) throw new Error("File senza testata");
  const end = text.indexOf("\n---\n", 4);
  if (end < 0) throw new Error("Testata non chiusa");
  const fields = {};
  for (const line of text.slice(4, end).split("\n")) {
    const i = line.indexOf(":");
    if (i > 0) fields[line.slice(0, i).trim()] = line.slice(i + 1).trim();
  }
  return { fields, body: text.slice(end + 5).replace(/^\n+/, "") };
}

export function serializeArticle(fields, body) {
  const order = [...KEYS, ...Object.keys(fields).filter((k) => !KEYS.includes(k))];
  const lines = order.filter((k) => fields[k]).map((k) => `${k}: ${String(fields[k]).replace(/\s*\n\s*/g, " ").trim()}`);
  return `---\n${lines.join("\n")}\n---\n${body.replace(/\r\n/g, "\n").trim()}\n`;
}

/* ---------- GitHub ---------- */
function gh(env, path, init = {}) {
  return fetch(`https://api.github.com/repos/${env.GITHUB_REPO}/${path}`, {
    ...init,
    headers: {
      authorization: `Bearer ${env.GITHUB_TOKEN}`,
      accept: "application/vnd.github+json",
      "x-github-api-version": "2022-11-28",
      "user-agent": "sito-sara-admin",
      ...(init.headers || {}),
    },
  });
}

async function readFile(env, slug) {
  const res = await gh(env, `contents/${DIR}/${slug}.md?ref=${encodeURIComponent(env.GITHUB_BRANCH || "main")}`);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`GitHub ${res.status}`);
  const data = await res.json();
  return { sha: data.sha, text: b64decode(data.content) };
}

async function listArticles(env) {
  const res = await gh(env, `contents/${DIR}?ref=${encodeURIComponent(env.GITHUB_BRANCH || "main")}`);
  if (!res.ok) throw new Error(`GitHub ${res.status}`);
  const files = (await res.json()).filter((f) => f.type === "file" && f.name.endsWith(".md")).slice(0, 60);
  const items = await Promise.all(
    files.map(async (f) => {
      const slug = f.name.replace(/\.md$/, "");
      try {
        const file = await readFile(env, slug);
        const { fields } = parseArticle(file.text);
        return { slug, title: fields.title || slug, date: fields.date || "" };
      } catch {
        return { slug, title: slug, date: "" };
      }
    })
  );
  return items.sort((a, b) => (b.date || "").localeCompare(a.date || "") || a.title.localeCompare(b.title));
}

function clean(input) {
  const out = {};
  for (const k of ["title", "description", "tag", "cta_title", "cta_text"]) {
    const v = String(input[k] ?? "").replace(/\s*\n\s*/g, " ").trim();
    if (v.length > LIMITS[k]) throw new Error(`Campo troppo lungo: ${k}`);
    out[k] = v;
  }
  const body = String(input.body ?? "").replace(/\r\n/g, "\n").trim();
  if (body.length > LIMITS.body) throw new Error("Testo troppo lungo");
  if (!out.title) throw new Error("Manca il titolo");
  if (!out.description) throw new Error("Manca la descrizione breve");
  if (body.length < 50) throw new Error("Il testo è troppo corto");
  return { fields: out, body };
}

async function saveArticle(env, slug, input, overwrite) {
  const { fields, body } = clean(input);
  const existing = await readFile(env, slug);
  if (existing && !overwrite) return json({ error: "Esiste già un articolo con questo indirizzo." }, 409);
  let merged = { ...fields };
  if (existing) merged = { ...parseArticle(existing.text).fields, ...fields }; // conserva i campi che il pannello non mostra
  if (!merged.date) merged.date = new Date().toISOString().slice(0, 10);
  const payload = {
    message: `${existing ? "Modifica" : "Nuovo"} articolo: ${fields.title}`.slice(0, 120),
    content: b64encode(serializeArticle(merged, body)),
    branch: env.GITHUB_BRANCH || "main",
  };
  if (existing) payload.sha = existing.sha;
  const res = await gh(env, `contents/${DIR}/${slug}.md`, { method: "PUT", body: JSON.stringify(payload) });
  if (!res.ok) return json({ error: `Salvataggio non riuscito (GitHub ${res.status}).` }, 502);
  return json({ ok: true, slug, updated: Boolean(existing) });
}

/* ---------- instradamento ---------- */
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (!url.pathname.startsWith("/api/")) return env.ASSETS ? env.ASSETS.fetch(request) : new Response("Not found", { status: 404 });

    if (!env.ADMIN_PASSWORD || !env.GITHUB_TOKEN || !env.GITHUB_REPO) return json({ error: "Configurazione incompleta." }, 500);

    let password = "";
    try { password = decodeURIComponent(request.headers.get("x-admin-password") || ""); } catch { /* password non valida */ }
    if (!password || !(await sameSecret(password, env.ADMIN_PASSWORD))) {
      await new Promise((r) => setTimeout(r, 900)); // rallenta i tentativi a caso
      return json({ error: "Password errata." }, 401);
    }

    try {
      const m = url.pathname.match(/^\/api\/articles(?:\/([^/]+))?$/);
      if (!m) return json({ error: "Non trovato." }, 404);
      const slug = m[1];

      if (!slug && request.method === "GET") return json({ articles: await listArticles(env) });

      if (slug) {
        if (!SLUG_RE.test(slug) || slug.length > 90) return json({ error: "Indirizzo non valido." }, 400);
        if (request.method === "GET") {
          const file = await readFile(env, slug);
          if (!file) return json({ error: "Articolo non trovato." }, 404);
          const { fields, body } = parseArticle(file.text);
          return json({ slug, fields, body });
        }
        if (request.method === "PUT" || request.method === "POST") {
          const input = await request.json();
          return await saveArticle(env, slug, input, request.method === "PUT");
        }
      }
      return json({ error: "Metodo non consentito." }, 405);
    } catch (e) {
      return json({ error: e.message || "Errore." }, e.message && /^(Manca|Campo|Testo|Il testo)/.test(e.message) ? 400 : 500);
    }
  },
};
