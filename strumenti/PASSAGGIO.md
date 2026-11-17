# Mezzo Minuto: passaggio a una nuova chat

Leggi tutto questo file prima di lavorare. Rispondi sempre in italiano e in modo breve: l'utente usa il telefono.

## Account e strumenti
- **Metricool:** blogId/brandId 7995542, fuso Europe/Rome.
  - Crea prima il post Instagram con l'URL raw di GitHub, poi riusa l'URL static.metricool.com restituito per Facebook, TikTok e YouTube.
  - updateScheduledPost vuole l'info completa; dopo ogni modifica l'id cambia, l'uuid resta.
- **GitHub:** repo mezzominuto-maker/media.
  - Reel in reels/<data>/; strumenti in strumenti/ (vedi LEGGIMI.md).
  - URL raw: https://raw.githubusercontent.com/mezzominuto-maker/media/main/...
- **Calendario:** artefatto b58d0948-5703-4dd1-8732-ca27467b2f1c.
  - Lo si rigenera con strumenti/calendario/gen.py a partire da calendar.json.
- **Attività programmate:**
  - «Mezzo Minuto giornaliero», ogni giorno alle 18:07: notiziario alle 19:30 e caroselli alle 20:00;
  - verifica alle 19:00.

## Regole fisse dei reel dei dibattiti
- **Apertura:** frase forte di 2-4 secondi, poi il reel INTERO. Il parlato non si taglia mai e l'apertura viene dallo STESSO file sorgente.
- **Impaginazione:** schermo intero con sfumatura; titolo giallo; sottotitolo con nome, partito e luogo; riquadro «IL CONTESTO» con fatti verificati; cartellino finale con domanda e sigla. Il volto sta sotto il titolo, centrato, e nessun sottotitolo deve risultare tagliato.
- **Titoli:** quelli tra «» devono essere citazioni testuali. Niente frasi al limite.
- **Hashtag:** 5, uguali su tutti e 4 i social. Mai #capezzone, mai parole come bomba, attentato, armi o morti. Niente #mezzominuto e niente #shorts sui reel dei dibattiti. Il notiziario invece ne usa 7.
- **Facebook:**
  - post separato;
  - titolo + 2 + testo al massimo 400 caratteri (contali con Python);
  - riga «👉 Segui Mezzo Minuto: il contesto verificato dei dibattiti.»;
  - la domanda va nel primo commento.
- **Approvazione:** manda sempre una bozza e aspetta l'OK prima di pubblicare clip nuove.
- **Programmazione:**
  - reel alle 12:00 e alle 21:00;
  - mai due clip della stessa fonte nello stesso giorno, mai due clip di Renzi nello stesso giorno;
  - l'ordine si decide in base al potenziale. Facebook è il social prioritario.
- **Caroselli:** la didascalia del carosello Instagram deve essere sempre diversa da quella del reel.

## Nuovo formato «Il Contesto» (rubrica, in prova)
- **Nome della rubrica:** «Il Contesto». In alto nel video: MEZZO MINUTO · IL CONTESTO. Cartellino finale: «Il Contesto · capire le notizie». La didascalia inizia con «🔎 Il Contesto». Temi: politica italiana, esteri ed economia.
- **Formato:** video di 60-80 secondi che spiega una notizia con contesto e storia. Voce AI generata dall'utente con ElevenLabs (voce «Raf – Casual Narrator»), grafiche animate nei colori del marchio (blu notte e giallo), sottotitoli parola per parola, la domanda finale nei commenti.
- **Primo video:** «Il quarto condono edilizio?», file in strumenti/spiegato/condono/.
  - render.py disegna i fotogrammi; align.py allinea le parole alla voce leggendo le pause.
  - Versione 2: voce accelerata a 1,12x con atempo, musica «Rebellion» di Johny Grimes a volume circa 0,065 sotto la voce.
- **Musica:** Free To Use. In descrizione va SEMPRE la citazione: «Music from Free To Use – Rebellion by Johny Grimes – freetouse.com/music».
- **Etichetta AI:** da impostare su ogni social.
- **Da fare:** versione 3 con immagini reali (case abusive, ruspa, Camera, Campania; foto dei politici solo se fornite dall'utente).
