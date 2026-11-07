"""Monta as 6 fotos num único painel em alta resolução.

Nenhuma foto é reduzida: as paisagens ficam no tamanho original (1600x1200)
e os retratos são ampliados com Lanczos para 1600 px de largura. Depois cada
foto recebe um realce leve (nitidez, contraste e cor) para o efeito HD.
Saídas: PNG sem perda e JPEG qualidade 100 sem subamostragem de cor.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

BASE = Path(__file__).parent
SRC = BASE / "originais"

M, G, R = 80, 40, 28           # margem, espaço entre fotos, raio dos cantos
CELL_W = 1600                   # largura de cada foto
BG = (24, 20, 14)               # fundo escuro quente
GOLD = (214, 178, 102)          # filete dourado

top = ["foto-1.jpg", "foto-2.jpg", "foto-3.jpg"]      # retratos
bottom = ["foto-4.jpg", "foto-5.jpg", "foto-6.jpg"]   # paisagens


def hd(img: Image.Image, width: int) -> Image.Image:
    h = round(img.height * width / img.width)
    if img.size != (width, h):
        img = img.resize((width, h), Image.LANCZOS)
    img = img.filter(ImageFilter.UnsharpMask(radius=2.2, percent=70, threshold=2))
    img = ImageEnhance.Contrast(img).enhance(1.06)
    img = ImageEnhance.Color(img).enhance(1.08)
    img = ImageEnhance.Sharpness(img).enhance(1.15)
    return img


def paste_rounded(canvas, img, x, y):
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *img.size), R, fill=255)
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle((x - 4, y - 4, x + img.width + 3, y + img.height + 3), R + 4, fill=GOLD)
    canvas.paste(img, (x, y), mask)


rows = [[hd(Image.open(SRC / f).convert("RGB"), CELL_W) for f in fs] for fs in (top, bottom)]
row_h = [max(i.height for i in r) for r in rows]
W = 2 * M + 3 * CELL_W + 2 * G
H = 2 * M + sum(row_h) + G
canvas = Image.new("RGB", (W, H), BG)

y = M
for r, rh in zip(rows, row_h):
    x = M
    for img in r:
        paste_rounded(canvas, img, x, y)
        x += CELL_W + G
    y += rh + G

canvas.save(BASE / "montagem-natal-hd.png", optimize=True)
canvas.save(BASE / "montagem-natal-hd.jpg", quality=100, subsampling=0, dpi=(300, 300))
print(canvas.size)
