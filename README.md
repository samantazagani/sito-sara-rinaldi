# Sito di Sara Rinaldi · Mindset Revolution

Sito statico (HTML + CSS, nessun database). La cartella da pubblicare è **public/**.

## Pubblicazione su Cloudflare
Framework: None · Comando di build: vuoto · Cartella di output: `public`

## Prima di andare online (in `build.py`, sezione CONFIGURAZIONE)
- `PIVA` e `INDIRIZZO`: dati di Sara per footer e privacy policy
- `CONSERVAZIONE`: per quanto tempo si conservano le email (da decidere con il commercialista)
Poi rilancia `python3 build.py`: lo script avvisa se mancano dati.
Finché mancano, il sito è in **modalità prova** (non indicizzato da Google). Appena li compili e rilanci lo script, la protezione si toglie da sola.

## Aggiungere un articolo
1. Copia un file in `content/articoli/` e cambia testata (title, meta_title, description, tag, cta_title, cta_text) e testo.
   Nel testo: `## ` titolo, `### ` sottotitolo, `- ` elenco, `**grassetto**`.
2. `python3 build.py`
3. Carica le modifiche: il sito si aggiorna da solo.
Il nome del file diventa l'indirizzo: `blog/<nome-file>`.
