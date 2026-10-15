"""Add one generated pigment mark while preserving the recovered wall byte-for-byte elsewhere."""
import hashlib
import json
import struct
import zlib
from pathlib import Path

from image_bytes import jpeg, png, read_png, resize

ROOT = Path(__file__).resolve().parent.parent
WALL = ROOT / "artifacts/line-3/wall.png"
MARK = ROOT / "artifacts/line-3/mark-39.png"
OUT = ROOT / "artifacts/line-3/wall-v19.png"
ANCESTOR = "d5ced1ae1b0f28c38e721effdba87b0dba3465bf5257c8d1266796136eb0e76b"
PROMPT = (
    "Isolated sparse prehistoric cave pigment on white: one squat charcoal-black oval stone "
    "seated in a shallow red-ochre crescent cradle, with one tiny yellow-ochre pebble. "
    "Flat worn mineral daubs, no frog, hands, text, numbers, symbols, logos or border."
)


def read_rgba(data):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("mark is not PNG")
    offset, compressed = 8, bytearray()
    for _ in range(16):
        size = int.from_bytes(data[offset:offset + 4], "big")
        kind = data[offset + 4:offset + 8]
        body = data[offset + 8:offset + 8 + size]
        if zlib.crc32(kind + body) != int.from_bytes(data[offset + 8 + size:offset + 12 + size], "big"):
            raise ValueError("mark PNG CRC mismatch")
        if kind == b"IHDR":
            w, h, bits, color, compression, filters, interlace = struct.unpack(">IIBBBBB", body)
            if (bits, color, compression, filters, interlace) != (8, 6, 0, 0, 0):
                raise ValueError("expected noninterlaced RGBA mark")
        elif kind == b"IDAT":
            compressed.extend(body)
        elif kind == b"IEND":
            break
        offset += size + 12
    raw = zlib.decompress(compressed)
    stride = w * 4
    if len(raw) != (stride + 1) * h:
        raise ValueError("mark PNG length mismatch")
    pixels, previous = bytearray(), bytearray(stride)
    for y in range(h):
        kind = raw[y * (stride + 1)]
        row = bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = row[i - 4] if i >= 4 else 0
            b = previous[i]
            c = previous[i - 4] if i >= 4 else 0
            if kind == 0:
                prediction = 0
            elif kind == 1:
                prediction = a
            elif kind == 2:
                prediction = b
            elif kind == 3:
                prediction = (a + b) // 2
            elif kind == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                prediction = a if pa <= pb and pa <= pc else b if pb <= pc else c
            else:
                raise ValueError("unsupported mark filter")
            row[i] = (row[i] + prediction) & 255
        pixels.extend(row)
        previous = row
    return w, h, pixels


def main():
    ancestor = WALL.read_bytes()
    assert hashlib.sha256(ancestor).hexdigest() == ANCESTOR
    w, h, old = read_png(ancestor)
    mw, mh, mark = read_rgba(MARK.read_bytes())
    points = [(x, y) for y in range(mh) for x in range(mw) if mark[(y * mw + x) * 4 + 3] > 20]
    sx0, sy0 = min(x for x, y in points), min(y for x, y in points)
    sx1, sy1 = max(x for x, y in points) + 1, max(y for x, y in points) + 1

    # Vacant upper-right rock, away from the inherited arcs, bowl, stones and cracks.
    x0, y0, width, height = 1030, 236, 126, 84
    final = bytearray(old)
    changed = 0
    for dy in range(height):
        for dx in range(width):
            x, y = x0 + dx, y0 + dy
            i = (y * w + x) * 3
            rock = old[i:i + 3]
            if max(rock) < 70:
                continue
            xa = sx0 + dx * (sx1 - sx0) // width
            xb = sx0 + (dx + 1) * (sx1 - sx0) // width
            ya = sy0 + dy * (sy1 - sy0) // height
            yb = sy0 + (dy + 1) * (sy1 - sy0) // height
            samples = []
            for gy in range(ya, yb):
                for gx in range(xa, xb):
                    j = (gy * mw + gx) * 4
                    r, g, b, a = mark[j:j + 4]
                    if a > 20:
                        if r > g * 1.15 and g > 55 and b < g * .9:
                            pigment = (157, 70, 39)
                        elif r > 105 and g > 80 and b < 135:
                            pigment = (177, 127, 43)
                        else:
                            pigment = (55, 44, 33)
                        samples.append((pigment, a / 255))
            if not samples:
                continue
            coverage = sum(a for _, a in samples) / ((xb - xa) * (yb - ya))
            color = [sum(c * a for c, a in ((pig[0][k], pig[1]) for pig in samples)) / sum(a for _, a in samples)
                     for k in range(3)]
            alpha = min(.76, coverage * .76)
            for k in range(3):
                final[i + k] = round(rock[k] * (1 - alpha) + color[k] * alpha)
            if final[i:i + 3] != rock:
                changed += 1
    assert changed > 600
    for y in range(h):
        for x in range(w):
            i = (y * w + x) * 3
            if not (x0 <= x < x0 + width and y0 <= y < y0 + height) or max(old[i:i + 3]) < 70:
                assert final[i:i + 3] == old[i:i + 3]

    encoded = png(w, h, final)
    OUT.write_bytes(encoded)
    WALL.write_bytes(encoded)
    thumbnail = resize(w, h, final)
    preview = jpeg(512, 512, thumbnail, 52)
    assert len(preview) <= 100_000
    (ROOT / "dist/line-3/39.jpg").write_bytes(preview)
    review = {
        "number": 39,
        "ancestorSha256": ANCESTOR,
        "wall": {"paths": ["artifacts/line-3/wall.png", "artifacts/line-3/wall-v19.png"],
                 "dimensions": [w, h], "format": "PNG", "mode": "RGB",
                 "sha256": hashlib.sha256(encoded).hexdigest()},
        "preview": {"path": "dist/line-3/39.jpg", "dimensions": [512, 512],
                    "format": "JPEG", "bytes": len(preview)},
        "additionRectangle": [x0, y0, width, height],
        "changedPixels": changed, "unchangedPixels": w * h - changed,
        "allPixelsOutsideAdditionUnchanged": True,
        "imageTool": "built-in image_gen imagegen",
        "prompt": PROMPT,
        "reviewStatus": "requires final visual inspection",
        "unmetVisualRequirements": []
    }
    (ROOT / "line-3/wall-review-39.json").write_text(json.dumps(review, indent=2) + "\n")
    print(json.dumps(review, indent=2))


if __name__ == "__main__":
    main()
