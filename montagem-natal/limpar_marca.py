"""Remove a marca "Galaxy A54 5G" do canto inferior esquerdo das fotos.

1. O texto está no mesmo lugar em todas as fotos, então o formato exato das
   letras sai do mínimo de brilho entre as 6 (só o texto é claro em todas).
2. Os pixels das letras são reconstruídos pela vizinhança (inpainting) e
   recebem a textura (grão do piso, grama etc.) de um trecho logo acima,
   para não ficar mancha lisa.
Lê de originais/ e grava em limpas/; o resto da foto não é alterado.
"""
from pathlib import Path
import cv2
import numpy as np

BASE = Path(__file__).parent
OUT = BASE / "limpas"
OUT.mkdir(exist_ok=True)
X0, X1, B0, B1 = 50, 350, 140, 70          # caixa: x e distância até a base
SHIFT = 40                                  # de onde vem a textura (px acima)

files = sorted((BASE / "originais").glob("foto-*.jpg"))
imgs = [cv2.imread(str(f)) for f in files]
rois = [cv2.cvtColor(im[im.shape[0] - B0:im.shape[0] - B1, X0:X1], cv2.COLOR_BGR2GRAY) for im in imgs]
glyph = (np.min(np.stack(rois), 0) > 135).astype(np.uint8) * 255
glyph = cv2.dilate(glyph, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)), iterations=1)

for f, img in zip(files, imgs):
    h, w = img.shape[:2]
    mask = np.zeros((h, w), np.uint8)
    mask[h - B0:h - B1, X0:X1] = glyph
    base = cv2.inpaint(img, mask, 4, cv2.INPAINT_TELEA).astype(np.float32)
    src = np.roll(img, SHIFT, axis=0).astype(np.float32)          # pixel de 34 px acima
    grain = src - cv2.GaussianBlur(src, (0, 0), 2.5)
    fill = np.clip(base + grain, 0, 255)
    soft = cv2.GaussianBlur(mask, (0, 0), 1.2).astype(np.float32)[..., None] / 255
    out = img.astype(np.float32) * (1 - soft) + fill * soft
    cv2.imwrite(str(OUT / f.name), out.round().astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 100])
    print(f.name, "ok")
