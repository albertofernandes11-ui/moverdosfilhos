#!/usr/bin/env bash
# Junta os dois vídeos num Reel vertical 1080x1920 (9:16), 30 fps.
# - Amplia de 480x860 para 1080x1920 (Lanczos) com redução leve de ruído,
#   nitidez, contraste e cor para o efeito HD.
# - Transição suave de 0,5 s entre os vídeos (imagem e som).
# - Iguala o volume dos dois (o segundo é bem mais baixo).
set -euo pipefail
cd "$(dirname "$0")"
V="scale=1080:-2:flags=lanczos,crop=1080:1920,fps=30,hqdn3d=1.5:1.5:4:4,unsharp=5:5:0.9:5:5:0,eq=contrast=1.05:saturation=1.10,format=yuv420p,setsar=1"
A="aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=11"
D1=$(ffprobe -v error -show_entries format=duration -of csv=p=0 originais/video-1.mp4)
OFF=$(python3 -c "print(round($D1-0.5,3))")
ffmpeg -y -v error -i originais/video-1.mp4 -i originais/video-2.mp4 -filter_complex "
[0:v]$V[v0];[1:v]$V[v1];
[v0][v1]xfade=transition=fade:duration=0.5:offset=$OFF,fade=t=in:st=0:d=0.3[v];
[0:a]$A[a0];[1:a]$A[a1];[a0][a1]acrossfade=d=0.5[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 16 -profile:v high -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart reel-abracos-1080x1920.mp4
