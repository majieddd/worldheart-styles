"""Contact sheet with the key burned in.

A bare grid cannot tell you WHICH prompt produced the plate you like, which is
the whole reason the review sheet exists in the method. The label is part of
the instrument, not decoration.
"""
import sys, glob, os
from PIL import Image, ImageDraw

def build(paths, out, cols=4, cell=520, label=True):
    rows = (len(paths) + cols - 1) // cols
    ch = round(cell * 9 / 16)
    lab = 30 if label else 0
    sheet = Image.new('RGB', (cols * cell, rows * (ch + lab)), (18, 18, 20))
    d = ImageDraw.Draw(sheet)
    for i, p in enumerate(paths):
        im = Image.open(p).convert('RGB')
        sc = max(cell / im.width, ch / im.height)
        im = im.resize((round(im.width * sc), round(im.height * sc)), Image.LANCZOS)
        l, t = (im.width - cell) // 2, (im.height - ch) // 2
        im = im.crop((l, t, l + cell, t + ch))
        x, y = (i % cols) * cell, (i // cols) * (ch + lab)
        sheet.paste(im, (x, y + lab))
        if label:
            d.text((x + 6, y + 8), os.path.basename(p)[:-4][:46], fill=(235, 235, 240))
    sheet.save(out, quality=92)
    print(out, sheet.size, len(paths), 'plates')

if __name__ == '__main__':
    ps = sorted(glob.glob(sys.argv[1]))
    build(ps, sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 4)
