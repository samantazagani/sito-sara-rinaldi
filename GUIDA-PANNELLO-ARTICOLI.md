# Pannello per scrivere gli articoli

Pagina riservata `https://sararinaldimentalcoach.com/admin`: Sara scrive il testo, preme **Pubblica**,
l'articolo viene salvato nel repository (un file in `content/articoli/`) e Cloudflare ripubblica il sito da solo.

## Come funziona
- `static/admin/index.html` è la pagina (si copia in `public/admin/` con `python3 build.py`).
- `worker/index.js` è una piccola API su `/api/*`: controlla la password e scrive su GitHub. Il resto del sito resta statico.
- `wrangler.jsonc` dice a Cloudflare di pubblicare insieme sito e API. **Il nome deve essere uguale a quello del progetto** (`sito-sara-rinaldi`).

## Installazione (una volta sola, la fai tu)

### 1. Token GitHub (solo per questo repository)
GitHub → Settings → Developer settings → Personal access tokens → **Fine-grained tokens** → Generate new token.
- Repository access: *Only select repositories* → `sito-sara-rinaldi`
- Permissions → Repository permissions → **Contents: Read and write**
- Scadenza: massimo 1 anno. Segnati la data per rinnovarlo.
Copia il token (si vede una volta sola).

### 2. Carica i file nel repository
Sostituisci/aggiungi: `wrangler.jsonc`, `worker/`, `static/`, `content/`, `build.py`, `public/`.
Controlla in `wrangler.jsonc` che `GITHUB_REPO` sia `tuo-utente/nome-repository`.

### 3. Impostazioni del progetto su Cloudflare
Workers & Pages → `sito-sara-rinaldi` → Settings → Build:
- **Build command:** `python3 build.py`
- **Deploy command:** `npx wrangler deploy`
(la cartella dei file statici è già indicata in `wrangler.jsonc`)

### 4. Segreti
Settings → Variables and Secrets → Add, tipo **Secret**:
- `ADMIN_PASSWORD`: una password lunga, solo lettere e numeri (niente accenti)
- `GITHUB_TOKEN`: il token del punto 1

### 5. Prova
Apri `/admin`, entra, scrivi un articolo di prova e pubblicalo. Dopo 1–2 minuti deve comparire su `/blog/`.
Il pannello non cancella articoli: per togliere la prova elimina il file su GitHub (`content/articoli/<indirizzo>.md`).

## Se qualcosa non va
- **"Configurazione incompleta":** manca un segreto o `GITHUB_REPO`.
- **"Password errata":** controlla `ADMIN_PASSWORD` (dopo averla cambiata serve un nuovo deploy).
- **"Salvataggio non riuscito (GitHub 401/403/404)":** token scaduto, permessi insufficienti o repository sbagliato.
- **Il sito non si aggiorna:** guarda la scheda Deployments del progetto su Cloudflare e leggi il registro della build.

## Sicurezza
Chi ha la password può pubblicare testo sul sito. Dalla password non si arriva al resto dell'account GitHub: il token vale solo per questo repository.
Il testo scritto nel pannello non può inserire codice nelle pagine: il sito converte solo titoli, grassetto ed elenchi.

---

# Per Sara: come pubblicare un articolo
1. Apri `sararinaldimentalcoach.com/admin` e inserisci la password.
2. Premi **Nuovo articolo**.
3. Scrivi il **titolo**, una **descrizione breve** (la vedono i lettori e Google), una **categoria**.
4. Scrivi il testo. Per un titolo di sezione clicca sulla riga e premi **Titolo**; per il grassetto seleziona le parole e premi **Grassetto**; per un elenco seleziona le righe e premi **Elenco**. Per andare a capo lascia una riga vuota.
5. Premi **Anteprima** per vedere com'è, poi **Pubblica**. Il sito si aggiorna in 1–2 minuti.
6. Per correggere un articolo: nell'elenco premi **Modifica**, cambia e premi di nuovo **Pubblica**.
