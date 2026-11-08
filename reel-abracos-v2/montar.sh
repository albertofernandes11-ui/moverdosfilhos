#!/usr/bin/env bash
# Reel vertical 1080x1920, 30 fps, SEM áudio (a música entra no app).
# Segue o Reel de referência: cortes secos entre as cenas, cada cena termina
# ~2 s depois que o abraço começa, e a última cena segura o abraço até o fim.
# Gera duas versões: sem texto e com o texto fixo "O neto o dia inteiro:".
# Realce leve para HD: redução de ruído, nitidez, contraste e cor.
set -euo pipefail
cd "$(dirname "$0")"
V="scale=1080:-2:flags=lanczos,crop=1080:1920,fps=30,hqdn3d=1:1:3:3,unsharp=5:5:0.7:5:5:0,eq=contrast=1.05:saturation=1.10,format=yuv420p,setsar=1"
# fim de cada cena (s): abraço começa ~2,7 / 2,6 / 3,5 / 3,5
C1=4.8; C2=4.7; C3=5.4
FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
TXT="drawtext=fontfile=$FONT:text='O neto o dia inteiro\:':fontsize=64:fontcolor=white:box=1:boxcolor=black@0.55:boxborderw=22:x=(w-text_w)/2:y=220"

build() {  # $1 = filtro extra no final, $2 = arquivo
  ffmpeg -y -v error -i originais/video-1.mp4 -i originais/video-2.mp4 -i originais/video-3.mp4 -i originais/video-4.mp4 -filter_complex "
  [0:v]trim=0:$C1,setpts=PTS-STARTPTS,$V[a];
  [1:v]trim=0:$C2,setpts=PTS-STARTPTS,$V[b];
  [2:v]trim=0:$C3,setpts=PTS-STARTPTS,$V[c];
  [3:v]setpts=PTS-STARTPTS,$V[d];
  [a][b][c][d]concat=n=4:v=1:a=0$1[v]" \
    -map "[v]" -an -c:v libx264 -preset slow -crf 16 -profile:v high -pix_fmt yuv420p \
    -movflags +faststart "$2"
}
build "" reel-abracos-1080x1920.mp4
build ",$TXT" reel-abracos-com-texto-1080x1920.mp4
