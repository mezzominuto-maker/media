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
  - verifica alle 19:00;
  - «Il Contesto – proposte del giorno», ogni giorno alle 18:32: 3 argomenti di politica/economia con il testo completo per ElevenLabs, salvati in strumenti/spiegato/proposte/<data>.md. L'utente sceglie, manda la voce in una chat, si fa il video e dopo l'OK si programma per il giorno dopo alle 17:30. Quando il format funziona: valutare ElevenLabs Starter + API per automatizzare la voce.

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
- **Nome della rubrica:** «Il Contesto». In alto nel video: MEZZO MINUTO · IL CONTESTO. Cartellino finale: «Il Contesto · Capire le notizie». La didascalia inizia con «🔎 Il Contesto». Temi: politica italiana, esteri ed economia.
- **Formato:** video di 60-80 secondi che spiega una notizia con contesto e storia. Voce AI generata dall'utente con ElevenLabs (voce «Raf – Casual Narrator»), grafiche animate nei colori del marchio (blu notte e giallo), sottotitoli parola per parola, la domanda finale nei commenti.
- **Primo video:** «Il quarto condono edilizio?», file in strumenti/spiegato/condono/.
  - render.py disegna i fotogrammi; align.py allinea le parole alla voce leggendo le pause.
  - Versione 2: voce accelerata a 1,12x con atempo, musica «Rebellion» di Johny Grimes a volume circa 0,065 sotto la voce.
- **Musica:** Free To Use. In descrizione va SEMPRE la citazione: «Music from Free To Use – Rebellion by Johny Grimes – freetouse.com/music».
- **Etichetta AI:** da impostare su ogni social.
- **Versione 3 (17/11, in attesa di OK):** condono_v3_ilcontesto.mp4, render_v3.py + foto/scene.json, 10 foto Wikimedia Commons in foto/ (crediti e riga per la descrizione in foto/CREDITI.md). Musica: «Winery» di Aylex (winery.mp3) a volume 0,25 con ducking leggero sotto la voce, mix con spiegato/condono/mix_v3.sh. Citazione v3: «Music from Free To Use – Winery by Aylex – freetouse.com/music».

## Stato al 17 novembre 2026, ore 16:40

### Reel programmati su Metricool (tutti e 4 i social)
| Giorno | 12:00 | 21:00 |
|---|---|---|
| Mar 17 | Servizi segreti (Renzi) | Manganellata (Vannacci) |
| Mer 18 | Schlein, multinazionali | Conte, bollette |
| Gio 19 | Renzi, promesse | Saviano, caso Delmastro |
| Ven 20 | Tajani–Francia | Schlein, salari |
| Sab 21 | Grimaldi a Giorgetti | Kamala (prova su IG) |
| Dom 22 | Schlein, energia | LIBERO |

Didascalie dei reel 18-22: strumenti/caps_reel_18-22.json. Gli id aggiornati si recuperano con getScheduledPosts.

### Rubrica «Il Contesto»
- **Video:** strumenti/spiegato/condono/condono_v2_ilcontesto.mp4 (75 secondi), già approvato nello stile.
- **Il formato in breve:**
  - voce ElevenLabs a 1,12x;
  - grafiche animate con scatti, zoom, colpi di camera e sfondo a righe che cambia colore per tema;
  - sottotitoli parola per parola;
  - barra di avanzamento in alto;
  - fruscio a ogni cambio scena e tonfo sui momenti forti.
- **Richieste dell'utente:** più ritmo e immagini reali.
- **Copertina della rubrica (modello unico):** strumenti/spiegato/copertina.py. Foto in alto sfumata nel blu, pillola gialla «🔎 IL CONTESTO», occhiello, titolo con parole gialle tra *asterischi*, sottotitolo, «Capire le notizie». Il testo resta nella fascia 4:5 della griglia (--anteprima salva il ritaglio). Cartellino finale del video: «Il Contesto · Capire le notizie» (C maiuscola). Copertina del condono: condono/v4/copertina.jpg. Video v4 approvato e PROGRAMMATO il 18/11 alle 17:30 su IG, FB, TikTok e YouTube (uuid IG -3878371438400352805, FB -3391707101039148481, TikTok 5750442658837120559, YouTube 5684302869708361009), copertina su IG/FB/TikTok, aggiunto al calendario. La procedura completa della rubrica è nella skill «mezzo-minuto-il-contesto».
- **Versione 4 (17/11 sera, in attesa di OK):** testo nuovo più corto (voce ElevenLabs in v4/voce.mp3), 60 s, clip vere da Pexels scaricate senza chiave API (foto: images.pexels.com/photos/ID/pexels-photo-ID.jpeg; video: videos.pexels.com/video-files/ID/ID-hd_1080_1920_25fps.mp4, risoluzione e fps da indovinare), stacchi a ogni frase, contatori, schede, effetti sonori sintetizzati. File: condono_v4_ilcontesto.mp4, render_v4.py, cartella v4/ (CREDITI.md con la riga per la descrizione). Il dominio pexels.com e pixabay.com sono nell'elenco dei siti permessi; le pagine dei siti però hanno il blocco anti-robot, si cerca con la ricerca web.
- **PROSSIMO PASSO:** OK dell'utente sulla v3, poi pubblicazione (crediti foto in descrizione). ~~Fatto il 17/11:~~ con internet attivo, scaricare foto e video gratuiti con licenza libera (Pexels, Pixabay, Wikimedia Commons; NON foto di politici prese dal web) di case abusive, cantieri, ruspe e demolizioni, Montecitorio/Camera, paesaggi della Campania. Inserirli nelle scene con zoom e movimento, poi rifare la versione 3 e mandarla all'utente. Citare le fonti delle immagini se la licenza lo chiede.
- **Pubblicazione** (dopo l'OK dell'utente):
  - slot proposto alle 17:30 sui 4 social;
  - didascalia che inizia con «🔎 Il Contesto»;
  - citazione della musica;
  - etichetta AI (instagramData.isAiGenerated, tiktokData.isAigc, youtubeData.isAiGeneratedContent).
- **Metodo per i prossimi video:**
  1. scegliere il tema più discusso (Google Trends e prime pagine);
  2. copione di 200-220 parole con fonti, da approvare;
  3. l'utente genera la voce con ElevenLabs e la manda;
  4. montaggio con render.py adattato, bozza e OK.

### Altro
- **Monetizzazione Facebook:** l'utente ha inviato il modulo di interesse (categoria «Sito web di notizie e media»). Si attende l'invito.
- **Instagram:** il 15 e il 16 novembre ha limitato l'attività dell'account per didascalie uguali tra carosello e reel; ora sono sempre diverse.
- **Idea in valutazione:** un terzo reel alle 17:30 solo su TikTok e YouTube. Non ancora deciso.
- **Live su TikTok:** sbloccate, ma l'utente per ora non le vuole fare.
- **Da ricordare:**
  - la copertina YouTube del notiziario a volte va impostata a mano;
  - le clip di Otto e mezzo hanno un rischio di Content ID.
