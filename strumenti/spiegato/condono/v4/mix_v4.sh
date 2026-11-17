#!/bin/bash
# Audio «Il Contesto» v4: voce 1,12x + Winery con ducking + effetti (v4/sfx.wav da render_v4.py sfx)
D=60.06428571428571
ffmpeg -v error -y -i v4/voce.mp3 -i winery.mp3 -i v4/sfx.wav -filter_complex "\
[0:a]atempo=1.12,volume=6.5dB,aresample=48000,apad=whole_dur=$D,asplit=2[v][key];\
[1:a]atrim=0:$D,asetpts=PTS-STARTPTS,volume=0.25,aresample=48000[m0];\
[m0][key]sidechaincompress=threshold=0.06:ratio=2:attack=40:release=600:makeup=1[m1];\
[m1]afade=t=in:d=0.3,afade=t=out:st=58.46428571428571:d=1.6[m];\
[2:a]volume=0.42,aresample=48000[s];\
[v][m][s]amix=inputs=3:normalize=0:duration=longest,atrim=0:$D,alimiter=limit=0.95[out]" -map "[out]" -c:a aac -b:a 192k "${1:-audio_v4.m4a}"
