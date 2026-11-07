"""Versão para Stories do Instagram (9:16).

Gera em 2x (2160x3840) e entrega também em 1080x1920, que é o tamanho exato
dos Stories: subindo nesse tamanho, o Instagram não redimensiona a imagem.
As faixas de cima e de baixo ficam livres para a barra do Instagram e o
campo de resposta não cobrirem as fotos.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

BASE = Path(__file__).parent
SRC = BASE / "originais"
S = 2                                   # escala de trabalho
W, H = 1080 * S, 1920 * S
SIDE, GAP, TOP, BOTTOM, R = 36 * S, 22 * S, 190 * S, 230 * S, 22 * S
BG, GOLD = (24, 20, 14), (214, 178, 102)

# (arquivo, foco x, foco y) para o recorte: onde estão os rostos/corpo
GRID = [
    ("foto-1.jpg", 0.42, 0.55), ("foto-2.jpg", 0.47, 0.60),
    ("foto-4.jpg", 0.60, 0.55), ("foto-3.jpg", 0.55, 0.55),
    ("foto-5.jpg", 0.61, 0.55), ("foto-6.jpg", 0.61, 0.55),
]

cw = (W - 2 * SIDE - GAP) // 2
ch = (H - TOP - BOTTOM - 2 * GAP) // 3


def crop_fill(img, fx, fy, w, h):
    ratio = w / h
    if img.width / img.height > ratio:
        cw_, ch_ = round(img.height * ratio), img.height
    else:
        cw_, ch_ = img.width, round(img.width / ratio)
    x = min(max(round(fx * img.width - cw_ / 2), 0), img.width - cw_)
    y = min(max(round(fy * img.height - ch_ / 2), 0), img.height - ch_)
    return img.crop((x, y, x + cw_, y + ch_)).resize((w, h), Image.LANCZOS)


def limpa_marca(img, f):
    """Cobre o texto "Galaxy A54 5G" da foto-2 com o piso logo abaixo dele."""
    if f != "foto-2.jpg":
        return img
    patch = img.crop((60, 1530, 340, 1595))
    m = Image.new("L", patch.size, 0)
    ImageDraw.Draw(m).rectangle((8, 8, patch.width - 9, patch.height - 9), fill=255)
    img.paste(patch, (60, 1460), m.filter(ImageFilter.GaussianBlur(5)))
    return img


def hd(img):
    img = img.filter(ImageFilter.UnsharpMask(radius=2.2, percent=70, threshold=2))
    img = ImageEnhance.Contrast(img).enhance(1.06)
    return ImageEnhance.Color(img).enhance(1.08)


canvas = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(canvas)
mask = Image.new("L", (cw, ch), 0)
ImageDraw.Draw(mask).rounded_rectangle((0, 0, cw, ch), R, fill=255)
for i, (f, fx, fy) in enumerate(GRID):
    col, row = i % 2, i // 2
    x, y = SIDE + col * (cw + GAP), TOP + row * (ch + GAP)
    img = hd(crop_fill(limpa_marca(Image.open(SRC / f).convert("RGB"), f), fx, fy, cw, ch))
    d.rounded_rectangle((x - 3 * S, y - 3 * S, x + cw + 3 * S - 1, y + ch + 3 * S - 1), R + 3 * S, fill=GOLD)
    canvas.paste(img, (x, y), mask)

canvas.save(BASE / "stories-natal-2x.jpg", quality=100, subsampling=0)
small = canvas.resize((1080, 1920), Image.LANCZOS).filter(
    ImageFilter.UnsharpMask(radius=0.8, percent=40, threshold=1))
small.save(BASE / "stories-natal-1080x1920.jpg", quality=100, subsampling=0)
small.save(BASE / "stories-natal-1080x1920.png", optimize=True)
