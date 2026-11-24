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
  - «Mezzo Minuto giornaliero», ogni giorno alle 18:07: notiziario alle 19:30 e caroselli alle 20:00. DAL 18/11 NUOVA MODALITÀ: immagini/video Pexels per ogni notizia, musica «Background News» (Pixabay), titoli animati; carosello = slide 1 e 7 del kit + slide 2-6 nuove; copertina sempre del kit. Strumenti e regole: strumenti/notiziario/LEGGIMI_NOTIZIARIO.md (crea.py, scarica.py);
  - verifica alle 19:00: fatti E coerenza delle immagini (rifà video/slide con crea.py in <cartella>-v2 se serve);
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
- **Musica:** citare in descrizione solo i brani Free To Use (es. Winery); i brani Pixabay non vanno citati (vedi spiegato/musica/BRANI.md).
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
- **Musiche (dal 17/11 sera):** 3 brani in strumenti/spiegato/musica/ (Winery, Epic Classical Strings short e medium). Si sceglie in base a tono e ritmo del parlato (regole in musica/BRANI.md); i brani corti si allungano con loop_musica.py (chiusa alla fine del video), mix con musica/mix.sh.
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


### Regola del 20/11: fatti E contesto verificati («Il Contesto»)
- Non basta che ogni frase sia vera da sola: deve essere vera nel contesto. Prima di chiudere un testo verificare dove e da chi si decide davvero la questione (manovra, legge a parte, programma elettorale, Ue...), la data di ogni citazione («risponde», «dice» solo se recente) e che gli accostamenti non suggeriscano legami falsi.
- Caso patrimoniale (20/11): la chiusa «la manovra va approvata entro fine anno» faceva credere che la patrimoniale si decidesse in manovra (non c'è, maggioranza contraria, AVS la vuole nel programma elettorale); la citazione di Meloni era di giugno. Corretti con due nuove frasi registrate dall'utente e montate in voce.mp3 (build_voce.py).
- Caso Landini (20/11): il 20/11 in piazza ha rilanciato la patrimoniale con cifre diverse (1,5%, 20 miliardi, una sola fonte) dai 25 miliardi nel testo: tolta la cifra.
- Regola dell'utente: le domande critiche («ma oggi ha detto qualcosa?», «si può fare davvero lì?») le deve fare l'autore da solo, prima di consegnare testo e bozza, e scriverle con le risposte nel file delle proposte.
- Le regole sono state aggiunte al prompt dell'attività «Il Contesto – proposte del giorno» e alla skill «mezzo-minuto-il-contesto» (SKILL.md aggiornato mandato all'utente il 20/11 da salvare).

### Il Contesto – quinto video: gasolio (23/11 sera)
- «Gasolio, da oggi più tasse»: PROGRAMMATO martedì 24/11 alle 17:30 su IG, FB, TikTok, YouTube (uuid IG -3547837755177154621, FB 2128191073489800553, TikTok -4217827581591009535, YouTube -6080303975938701510), copertina su IG/FB/TikTok, etichetta AI, musica Epic Classical Strings short (Pixabay, non citata). Durata 62 s. Aggiunto al calendario (clips/contesto_gasolio.mp4).
- File in strumenti/spiegato/gasolio/: render_q.py (modello gioco/render_z.py; nuove grafiche: contatore decimale, barre gasolio/benzina, freccia giù, cronologia STOP/sconto), align.py, voce.mp3, CREDITI.md, copertina.jpg, gasolio_ilcontesto.mp4 (72 MB). Testo e fonti in proposte/2026-11-23.md (articoli letti per intero con WebFetch).
- Controllo del 24/11 alle 13:30: NESSUNA proroga (ANSA 24/11 «gasolio stabile a 2,196 dopo scadenza taglio accise»; QuiFinanza, Il Sole 24 Ore: sconto terminato). Mimit 24/11: benzina 1,939, gasolio 2,196. Il video resta corretto, post confermati. (Regola precedente: se il governo proroga lo sconto, il testo («Da oggi paghi più tasse», «Per ora, nessuna proroga») va cambiato o il post spostato.
- Regola dell'utente del 23/11: l'attività serale prova sempre a leggere gli articoli interi con WebFetch; se l'accesso non viene autorizzato, va avanti con i soli titoli (prompt dell'attività aggiornato).

### Il Contesto – quarto video: gioco d'azzardo (22/11 sera)
- «Più giochi, più incassa lo Stato?»: PROGRAMMATO lunedì 23/11 alle 17:30 su IG, FB, TikTok, YouTube (uuid IG 8344680464334212423, FB -8174516436804222727, TikTok -1662318506148016923, YouTube -954564663356865610), copertina su IG/FB/TikTok, etichetta AI, musica Winery (citata). Durata 61 s. Aggiunto al calendario (clips/contesto_gioco.mp4).
- File in strumenti/spiegato/gioco/: render_z.py (modello giovani/render_g.py, nuove grafiche: settimana del Lotto con il mercoledì, frecce in su), align.py, voce.mp3, CREDITI.md, copertina.jpg, gioco_ilcontesto.mp4. Testo v2 «più preciso possibile» chiesto dall'utente: dati ufficiali ADM, misure elencate una per una al condizionale, cifre incerte tolte (vedi proposte/2026-11-22.md).
- Nota: il 22/11 alle 20:00 il carosello Instagram è uscito con l'avviso «Instagram restricted activity on the account».
- faster-whisper non utilizzabile qui (huggingface bloccato dal proxy): allineamento con silencedetect come sempre.

### Il Contesto – terzo video: patrimoniale (20/11 sera)
- «Chi ha più soldi deve pagare di più?»: PROGRAMMATO sabato 21/11 alle 17:30 su IG, FB, TikTok, YouTube (uuid IG -5494171512366608698, FB 1337628520539048794, TikTok -8692843028317845548, YouTube -6139121205942925617), copertina su IG/FB/TikTok, etichetta AI, musica Epic Classical Strings short (Pixabay, non citata). Durata 75 s. Aggiunto al calendario (clips/contesto_patrimoniale.mp4).
- File in strumenti/spiegato/patrimoniale/: render_x.py, align.py, build_voce.py (voce_v1.mp3 + frasi corrette voce_landini/voce_meloni/voce_finale → voce.mp3), CREDITI.md, copertina.jpg, patrimoniale_ilcontesto.mp4.

### Il Contesto – secondo video: pensioni (18/11 sera)
- «Pensione a 64 o a 67 anni?»: PROGRAMMATO giovedì 19/11 alle 17:30 su IG, FB, TikTok, YouTube (uuid IG 6905948456809612096, FB -4657113323266882123, TikTok 6342134572808422020, YouTube 7927338401068632058), copertina su IG/FB/TikTok, etichetta AI, musica Winery. Aggiunto al calendario.
- File in strumenti/spiegato/pensioni/: render_p.py (scaletta agganciata alle parole con S(i), si riallinea da sola con words.json), align.py (scarta i tratti spuriosi <0,15 s), stima_tempi.py (bozza senza voce), voce.mp3, CREDITI.md, copertina.jpg, pensioni_ilcontesto.mp4.
- Regole nuove chieste dall'utente: le citazioni vanno verificate parola per parola su almeno due fonti (qui Adnkronos e Alanews, 18/11) e messe tra virgolette; sui temi ancora in discussione si usa il condizionale («salirebbe», «arriverebbero», «potrebbe ancora cambiare»).
- Attività serale «Il Contesto – proposte»: prima esecuzione il 18/11 (strumenti/spiegato/proposte/2026-11-18.md). Limite: la ricerca web restituisce solo i titoli; per leggere gli articoli servirebbe autorizzare le testate in WebFetch.

### Altro
- **Monetizzazione Facebook:** l'utente ha inviato il modulo di interesse (categoria «Sito web di notizie e media»). Si attende l'invito.
- **Instagram:** il 15 e il 16 novembre ha limitato l'attività dell'account per didascalie uguali tra carosello e reel; ora sono sempre diverse.
- **Idea in valutazione:** un terzo reel alle 17:30 solo su TikTok e YouTube. Non ancora deciso.
- **Live su TikTok:** sbloccate, ma l'utente per ora non le vuole fare.
- **Da ricordare:**
  - la copertina YouTube del notiziario a volte va impostata a mano;
  - le clip di Otto e mezzo hanno un rischio di Content ID.

- **Instagram Trial Reel:** non usarli. Il 21/11 il reel Kamala (tipo TRIAL_REEL) è andato in errore: l'account non ha abbastanza follower per i reel di prova. Ripubblicato come REEL normale alle 21:35.

- **Carosello Instagram tolto (dal 23/11/2026, richiesta dell'utente):** Instagram limitava l'account sui caroselli delle 20:00 ("restricted activity"). Su Instagram il notiziario esce solo come reel + storia; il carosello resta su Facebook (20:00) e TikTok. Aggiornate le attività delle 18:07 e delle 19:00.
