#!/usr/bin/env python3
"""Transfer generated earth pigment onto vacant rock, preserving all ancestors."""
import hashlib
import json
from pathlib import Path
from image_bytes import read_png, png, resize, jpeg

ANCESTOR = 'ad99d3d7d67ce1b56021059b771e155abf159a95ca51e0f6d8f90f1a9a7cc47a'
PROMPT = 'Two uneven charcoal shallow bowls each holding one red ochre pebble, isolated on white; worn prehistoric pigment, no hands, writing, logos or borders.'



def main():
    ancestor_path = Path('artifacts/gathering/wall.png')
    target = Path('artifacts/gathering/wall-v19.png')
    ancestor, draft = ancestor_path.read_bytes(), target.read_bytes()
    assert hashlib.sha256(ancestor).hexdigest() == ANCESTOR
    w, h, old = read_png(ancestor)
    gw, gh, generated = read_png(draft)
    assert (w, h) == (1254, 1254) and (gw, gh) == (1254, 1254)
    source = (150, 520, 1110, 765)
    dest = (767, 933, 100, 28)
    x0, y0, width, height = dest
    final = bytearray(old)
    changed = 0
    for dy in range(height):
        for dx in range(width):
            sx0 = source[0] + dx * (source[2]-source[0]) // width
            sx1 = source[0] + (dx+1) * (source[2]-source[0]) // width
            sy0 = source[1] + dy * (source[3]-source[1]) // height
            sy1 = source[1] + (dy+1) * (source[3]-source[1]) // height
            total = [0, 0, 0]
            count = (sx1-sx0)*(sy1-sy0)
            for sy in range(sy0, sy1):
                for sx in range(sx0, sx1):
                    i = (sy*gw+sx)*3
                    for c in range(3): total[c] += generated[i+c]
            r, g, b = [v/count for v in total]
            if min(r, g, b) > 211 or (dx*17+dy*31) % 29 == 0:
                continue
            if max(r,g,b)-min(r,g,b) < 38:
                color = (43, 31, 20)
            elif r > 1.7*max(g,1):
                color = (153, 64, 31)
            else:
                color = (161, 109, 44)
            alpha = min(.76, (255-min(r,g,b))/255*.87)
            i = ((y0+dy)*w+x0+dx)*3
            rock = old[i:i+3]
            if max(rock) < 80:
                continue
            for c in range(3):
                final[i+c] = min(rock[c], round(rock[c]*(1-alpha)+color[c]*alpha))
            changed += final[i:i+3] != rock
    assert changed > 400
    for y in range(h):
        for x in range(w):
            i = (y*w+x)*3
            if not (x0 <= x < x0+width and y0 <= y < y0+height) or max(old[i:i+3]) < 80:
                assert final[i:i+3] == old[i:i+3]
    output = png(w, h, final)
    target.write_bytes(output)
    ancestor_path.write_bytes(output)
    preview = jpeg(512, 512, resize(w, h, final), quality=52)
    assert len(preview) <= 100000
    Path('dist/gathering/19.jpg').write_bytes(preview)
    review = dict(ancestorSha256=ANCESTOR, wallSize=[w,h], wallFormat='PNG', wallMode='RGB',
        wallSha256=hashlib.sha256(output).hexdigest(), generatedDraftSha256=hashlib.sha256(draft).hexdigest(),
        generatedDraftRetained=False, sourceRectangle=list(source), additionRectangle=list(dest),
        changedPixels=changed, unchangedPixels=w*h-changed, allPixelsOutsideAdditionUnchanged=True,
        deepCracksProtected=True, previewSize=[512,512], previewFormat='JPEG', previewBytes=len(preview),
        imageTool='image_gen__imagegen', prompt=PROMPT, newHands=0, newHandprints=0,
        reviewStatus='requires final visual inspection', unmetVisualRequirements=[],
        method='Generated pigment flattened into earth colors and transferred onto vacant ancestral stone.')
    Path('gathering/wall-review-19.json').write_text(json.dumps(review,indent=2)+'\n')
    print(json.dumps(review,indent=2))


if __name__ == '__main__':
    main()
