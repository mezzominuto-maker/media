# Musiche della rubrica «Il Contesto»

Tre brani a disposizione. Per ogni video se ne sceglie UNO in base al tono dell'argomento e al ritmo del parlato.

| Brano | File | Tempo | Carattere | Durata | Loop |
|---|---|---|---|---|---|
| Winery – Aylex (Free To Use) | winery.mp3 | 89 BPM | calmo, neutro, «spiegato» | 117 s | non serve |
| Epic Classical Strings (short) – dayznyanlinnhtet | epic_strings_short.mp3 | 129 BPM | archi incalzanti ma leggeri, con pause e un crescendo finale | 17 s | battute 4-7 |
| Epic Classical Strings (medium) – dayznyanlinnhtet | epic_strings_medium.mp3 | 129 BPM | archi pieni, epici, cresce di continuo | 18 s | battute 5-8 |

## Come scegliere
1. **Tono dell'argomento**
   - economia quotidiana, tasse, bollette, pensioni, regole che cambiano, tono «ti spiego» → **Winery**;
   - scontro politico, voto in bilico, polemica, decisione imminente, tensione → **Epic short**;
   - temi gravi o storici: guerra, crisi internazionali, scandali, svolte storiche → **Epic medium**.
2. **Ritmo del parlato** (dalla voce allineata, v4/words.json): se la voce è fitta, con poche pause e tanti numeri, scegli il brano meno pieno tra quelli adatti (Epic short invece di medium, Winery invece di Epic short). Un brano pieno sopra una voce fitta confonde.
3. **Varietà**: evita lo stesso brano per più di 2 video di fila, se il tono lo permette.
4. Nel messaggio con la bozza scrivi quale brano hai scelto e perché, in una riga.

## Loop dei brani corti
`python3 loop_musica.py epic_strings_short.mp3 <durata video> musica.wav --battute 4-7`
`python3 loop_musica.py epic_strings_medium.mp3 <durata video> musica.wav --battute 5-8`
`python3 loop_musica.py winery.mp3 <durata video> musica.wav` (Winery: serve solo a tagliare e normalizzare; la chiusa cade alla fine)
- Il blocco scelto si ripete a tempo, la chiusa cade esattamente alla fine del video (sul cartellino finale), il risultato è normalizzato a -25,3 LUFS (= Winery a volume 0,25).
- Blocchi scelti misurando giunture (somiglianza armonica e salto di livello): short 4-7 giuntura quasi perfetta (+0,2 dB); medium 5-8 salto -0,9 dB.

## Mix
`bash mix.sh voce.mp3 musica.wav sfx.wav <durata video> uscita.m4a`
Voce 1,12x +6,5 dB, musica a volume 1,0 (già normalizzata) con sidechain leggero, effetti a 0,42.

## Crediti in descrizione
- Winery: obbligatorio «🎵 Music from Free To Use – Winery by Aylex – freetouse.com/music».
- Epic Classical Strings: probabilmente Pixabay (nome file tipico), dove la citazione non è obbligatoria; per correttezza: «🎵 Musica: Epic Classical Strings – dayznyanlinnhtet (Pixabay)». Da confermare con l'utente.
