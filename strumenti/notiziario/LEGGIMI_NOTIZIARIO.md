# Notiziario – nuova modalità (dal 18/11/2026)

Video 9:16 di 31,5 s con immagini e video reali per ogni notizia, titoli animati con parole chiave in giallo,
musica «Background News» (miromaxmusic, Pixabay) con gli stacchi sugli accenti (136 BPM, 3 battute per notizia).
Carosello: slide_01 (apertura) e slide_07 (chiusura) dal kit; slide_02…06 = le 5 notizie nella nuova grafica.
Copertina dei video: sempre cover.jpg del kit.

## Comandi
1. Immagini: `python3 strumenti/notiziario/scarica.py CARTELLA_CLIP foto:ID video:ID:fps[:v] ...`
2. Video + slide: `python3 strumenti/notiziario/crea.py config.json CARTELLA_USCITA`
   → video.mp4, slide_02.jpg … slide_06.jpg, prev_1.jpg … prev_5.jpg (un fotogramma per notizia per il controllo)

## config.json
```json
{"date_label": "Mercoledì 18 novembre",
 "news": [[CATEGORIA, TITOLO, TESTO, FONTE], ... 5 ...],          // come news.json del kit
 "evidenza": ["parole gialle 1", "...", "...", "...", "..."],     // 1-3 parole del TITOLO per notizia
 "clip_dir": "/tmp/mm/clip",
 "shots": [ [["pxf123.jpg", 0, 0.5, 0.5], ["px456.mp4", 1.0, 0.5, 0.5]],  // 2 immagini per notizia
            ... ],
 "sondaggio": {"notizia": 3, "titolo": "SONDAGGIO SWG PER LA7 · 16 NOVEMBRE",
               "barre": [["Centrosinistra", 44.9], ["Centrodestra", 43.6], ...]}   // facoltativo
}
```
- shot = [file, secondo di partenza (video) o 0 (foto), fuoco orizzontale 0-1, fuoco verticale 0-1, {"luce": 1.5} facoltativo per schiarire].
- file: nome nella cartella clip, oppure "repo:spiegato/condono/foto/montecitorio.jpg" per le foto nel repo.
- La prima immagine di ogni notizia è anche lo sfondo della sua slide del carosello: scegli la più chiara e riconoscibile.

## Regole per le immagini
- Coerenti con la notizia: il luogo (città, palazzo, ponte), l'istituzione o l'oggetto di cui si parla.
- MAI foto o video di politici o persone riconoscibili presi dal web; MAI immagini che sembrano mostrare l'evento
  se non lo mostrano (niente esplosioni, scontri, incidenti generici spacciati per quello della notizia).
- Pexels: id con WebSearch (allowed_domains ["pexels.com"]), es. «pexels video Moscow Kremlin night».
- Foto già pronte nel repo: spiegato/condono/foto/montecitorio.jpg (Montecitorio di notte), aula.jpg (Aula della Camera).
  Sono di Wikimedia Commons: se usate, aggiungi in descrizione «Foto: Wikimedia Commons».
- Sondaggi: usa "sondaggio" con le barre (stesso colore giallo per le due coalizioni, grigio-blu per i partiti).
