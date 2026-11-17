#!/bin/bash
# Audio «Il Contesto» v3: voce 1,12x + Winery (Aylex) con ducking leggero + effetti
# uso: ./mix_v3.sh VOLUME_MUSICA USCITA.m4a
V=${1:-0.25}; OUT=${2:-audio_v3.m4a}
ffmpeg -v error -y -i voce.mp3 -i winery.mp3 -i sfx2.wav -filter_complex "\
[0:a]atempo=1.12,volume=6.5dB,aresample=48000,apad=whole_dur=75.4,asplit=2[v][key];\
[1:a]atrim=0:75.4,asetpts=PTS-STARTPTS,volume=$V,aresample=48000[m0];\
[m0][key]sidechaincompress=threshold=0.06:ratio=2:attack=40:release=600:makeup=1[m1];\
[m1]afade=t=in:d=0.5,afade=t=out:st=73.6:d=1.8[m];\
[2:a]aresample=48000[s];\
[v][m][s]amix=inputs=3:normalize=0:duration=longest,atrim=0:75.333,alimiter=limit=0.95[out]" -map "[out]" -c:a aac -b:a 192k "$OUT"
