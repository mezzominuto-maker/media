#!/bin/bash
# Mix «Il Contesto»: voce 1,12x + musica (già in loop e normalizzata con loop_musica.py) + effetti
# uso: bash mix.sh VOCE.mp3 MUSICA.wav SFX.wav DURATA_VIDEO USCITA.m4a
V=$1; M=$2; S=$3; D=$4; OUT=$5
ffmpeg -v error -y -i "$V" -i "$M" -i "$S" -filter_complex "\
[0:a]atempo=1.12,volume=6.5dB,aresample=48000,apad=whole_dur=$D,asplit=2[v][key];\
[1:a]atrim=0:$D,asetpts=PTS-STARTPTS,aresample=48000[m0];\
[m0][key]sidechaincompress=threshold=0.06:ratio=2:attack=40:release=600:makeup=1[m1];\
[m1]afade=t=in:d=0.3[m];\
[2:a]volume=0.42,aresample=48000[s];\
[v][m][s]amix=inputs=3:normalize=0:duration=longest,atrim=0:$D,alimiter=limit=0.95[out]" -map "[out]" -c:a aac -b:a 192k "$OUT"
