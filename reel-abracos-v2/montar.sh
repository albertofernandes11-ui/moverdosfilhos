#!/usr/bin/env bash
# Reel vertical 1080x1920, 30 fps, SEM áudio (a música entra no app).
# 4 vídeos em sequência com transições rápidas de 0,4 s:
#   1→2 zoom, 2→3 deslize lateral, 3→4 flash branco; fade para preto no fim.
# Realce leve para HD: redução de ruído, nitidez, contraste e cor.
set -euo pipefail
cd "$(dirname "$0")"
T=0.4
V="scale=1080:-2:flags=lanczos,crop=1080:1920,fps=30,hqdn3d=1:1:3:3,unsharp=5:5:0.7:5:5:0,eq=contrast=1.05:saturation=1.10,format=yuv420p,setsar=1,settb=1/30"
dur() { ffprobe -v error -show_entries format=duration -of csv=p=0 "originais/video-$1.mp4"; }
D1=$(dur 1); D2=$(dur 2); D3=$(dur 3); D4=$(dur 4)
read O1 O2 O3 END <<<"$(python3 -c "
t=$T; d=[$D1,$D2,$D3,$D4]
o1=d[0]-t; o2=o1+d[1]-t; o3=o2+d[2]-t; end=o3+d[3]
print(round(o1,3),round(o2,3),round(o3,3),round(end,3))")"
ffmpeg -y -v error -i originais/video-1.mp4 -i originais/video-2.mp4 -i originais/video-3.mp4 -i originais/video-4.mp4 -filter_complex "
[0:v]$V[a];[1:v]$V[b];[2:v]$V[c];[3:v]$V[d];
[a][b]xfade=transition=zoomin:duration=$T:offset=$O1[ab];
[ab][c]xfade=transition=smoothleft:duration=$T:offset=$O2[abc];
[abc][d]xfade=transition=fadewhite:duration=$T:offset=$O3,fade=t=out:st=$(python3 -c "print($END-0.6)"):d=0.6[v]" \
  -map "[v]" -an -c:v libx264 -preset slow -crf 16 -profile:v high -pix_fmt yuv420p \
  -movflags +faststart reel-abracos-1080x1920.mp4
