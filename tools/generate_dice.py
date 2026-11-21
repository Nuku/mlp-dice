"""Build the MLP Dice assets and runtime catalog from characters.json."""

import argparse
import json
import math
from pathlib import Path
from random import Random

from PIL import Image, ImageColor, ImageDraw, ImageOps

from cutie_marks import draw_mark
from dice_mesh import TILE, dice_shapes, font, lerp, mesh, mix, number, write_glb


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets/dice"
CENTER = (64, 64)
RESAMPLE = Image.Resampling.LANCZOS


def thumbnail(image, size):
    copy = image.copy()
    copy.thumbnail(size, RESAMPLE)
    return copy


def mark_tile(mark, size):
    tile = Image.new("RGBA", (size, size))
    stamp = thumbnail(mark, (round(size * .84), round(size * .84)))
    tile.alpha_composite(stamp, ((size - stamp.width) // 2, (size - stamp.height) // 2))
    return tile


def crest(mark, palette, font_path):
    base, mid, accent = palette
    badge = Image.new("RGBA", (384, 384))
    pen = ImageDraw.Draw(badge)
    border = [(192, 16), (359, 83), (325, 273), (192, 364), (59, 273), (25, 83)]
    pen.polygon(border, fill=base)
    pen.line([*border, border[0]], accent, width=12, joint="curve")
    inner = [lerp((192, 184), p, .87) for p in border]
    pen.line([*inner, inner[0]], mid, width=4, joint="curve")
    symbol = thumbnail(mark, (205, 166))
    badge.alpha_composite(symbol, ((384 - symbol.width) // 2, 128 - symbol.height // 2))
    pen.line([(112, 229), (272, 229)], mix(mid, accent, .52), width=4)
    pen.text((192, 273), "20", font=font(font_path, 102), anchor="mm",
             fill="#fff8ed", stroke_fill=base, stroke_width=3)
    return badge.crop(badge.getbbox())


def paint_surface(panel, surface, palette, stamp, seed):
    base, mid, accent = palette
    pen = ImageDraw.Draw(panel)
    rng = Random(seed)
    pattern = mix(mid, accent, .26)
    dim = mix(base, mid, .65)
    for radius in range(90, 12, -4):
        shade = .23 + .51 * math.sin(radius / 90 * math.pi)
        pen.ellipse((64 - radius, 64 - radius, 64 + radius, 64 + radius),
                    fill=mix(base, mid, shade))
    if surface == "spectrum":
        colors = ("#ff5259", "#ffc843", "#82e270", "#79d8ed", "#cc8cf6")
        for offset in (-67, 3, 72):
            for stripe, color in enumerate(colors):
                y = offset + 4 * stripe
                pen.line([(0, y + 63), (128, y + 6)], mix(mid, ImageColor.getrgb(color), .60), 3)
    elif surface in ("rays", "vinyl"):
        for radius in range(18, 120, 8):
            pen.ellipse((64 - radius, 64 - radius, 64 + radius, 64 + radius),
                        outline=pattern if radius % 3 == 0 else dim)
        if surface == "rays":
            for index in range(24):
                angle = index * math.tau / 24
                pen.line([CENTER, (64 + 92 * math.cos(angle), 64 + 92 * math.sin(angle))], pattern)
    elif surface in ("staff", "strata", "stripes", "ribbons"):
        for y in range(-25, 160, 8):
            points = [(x, y + 7 * math.sin(x / 21 + y / 23)
                       + (x / 3 if surface == "stripes" else 0)) for x in range(0, 130, 3)]
            pen.line(points, pattern if y % 3 == 0 else dim, 2 if surface == "stripes" else 1)
    elif surface in ("facets", "lattice", "stitch", "cartography"):
        for n in range(-128, 256, 20):
            pen.line([(n, 0), (n + 128, 128)], pattern)
            pen.line([(n, 0), (n - 128, 128)], dim)
        if surface == "cartography":
            pen.ellipse((8, 8, 120, 120), outline=pattern, width=2)
            pen.line([(0, 64), (128, 64)], pattern)
            pen.line([(64, 0), (64, 128)], pattern)
    elif surface in ("battlement", "tread", "orchard", "meadow"):
        for y in range(-8, 146, 15):
            for x in range(-14 + (y % 2) * 10, 142, 23):
                if surface == "battlement":
                    pen.line([(x, y + 8), (x + 6, y + 8), (x + 6, y), (x + 14, y),
                              (x + 14, y + 8), (x + 21, y + 8)], pattern, 2)
                elif surface == "tread":
                    pen.line([(x, y), (x + 10, y + 7), (x + 20, y)], pattern, 2)
                elif surface == "orchard":
                    pen.ellipse((x, y, x + 12, y + 7), outline=pattern)
                    pen.line([(x, y + 9), (x + 15, y - 2)], dim)
                else:
                    pen.arc((x, y, x + 18, y + 24), 195, 295, fill=pattern, width=2)
    elif surface == "scales":
        for y in range(-9, 135, 9):
            for x in range(-18 + (y % 2) * 9, 144, 18):
                pen.arc((x, y - 9, x + 18, y + 9), 0, 180, fill=pattern, width=2)
    else:
        for _ in range(34):
            x, y = rng.randrange(TILE), rng.randrange(TILE)
            radius = rng.randrange(2, 7)
            if surface in ("bubbles", "gears"):
                pen.ellipse((x - radius, y - radius, x + radius, y + radius), outline=pattern)
            else:
                pen.line([(x, y), (x + radius, y + (radius if x % 2 else -radius))], pattern, 2)
    for y in (19, 63, 106):
        for x in ((29, 93) if y != 63 else (6, 113)):
            panel.paste(stamp, (x - stamp.width // 2, y - stamp.height // 2), stamp)
    for _ in range(85):
        x, y = rng.randrange(TILE), rng.randrange(TILE)
        pen.point((x, y), mix(panel.getpixel((x, y)), accent, .26))


def paint_panel(kind, value, polygon, loop, palette, surface, emblem, stamp, font_path):
    base, mid, accent = palette
    tile = Image.new("RGB", (TILE, TILE), base)
    paint_surface(tile, surface, palette, stamp, f"{kind}:{value}")
    pen = ImageDraw.Draw(tile)
    edge = mix(base, accent, .66)
    for inset, color, width in ((.955, edge, 2), (.87, accent, 1), (.81, mid, 1)):
        path = [lerp(CENTER, point, inset) for point in polygon]
        pen.line([*path, path[0]], fill=color, width=width, joint="curve")

    if kind == "d4":
        for vertex, point in zip(loop, polygon):
            x, y = lerp(CENTER, point, .59)
            digit = Image.new("RGBA", (30, 30))
            number(digit, str((1, 2, 4, 3)[vertex]), font_path, 22, (15, 15), base)
            angle = math.degrees(math.atan2(64 - point[1], point[0] - 64)) - 90
            digit = digit.rotate(angle, resample=Image.Resampling.BICUBIC)
            tile.paste(digit, (round(x - 15), round(y - 15)), digit)
        pen.ellipse((58, 58, 70, 70), outline=accent)
    elif kind == "d20" and value == 20:
        tile.paste(emblem, ((TILE - emblem.width) // 2, 65 - emblem.height // 2), emblem)
    else:
        small = kind in ("d8", "d10", "d20", "d100")
        w, h = (23, 21) if small else (30, 27)
        pen.ellipse((64 - w, 64 - h, 64 + w, 64 + h), fill=base, outline=edge, width=2)
        pen.ellipse((67 - w, 67 - h, 61 + w, 61 + h), outline=mid)
        label = str(value)
        if kind == "d100":
            label = f"{value % 10 * 10:02d}"
        elif kind == "d10":
            label = str(value % 10)
        number(tile, label, font_path, 31 if small else 39, (64, 63), base)
    return tile


def build_assets(characters, font_path):
    geometries = {kind: mesh(kind, radius, verts, faces)
                  for kind, radius, verts, faces in dice_shapes()}
    for folder in ("crests", "marks"):
        (ASSETS / folder).mkdir(parents=True, exist_ok=True)
    for entry in characters:
        slug = entry["slug"]
        palette = tuple(map(ImageColor.getrgb, entry["palette"]))
        master = draw_mark(entry["mark"])
        mark = master.crop(master.getbbox())
        mark_tile(mark, 128).save(ASSETS / "marks" / f"{slug}.png", optimize=True)
        badge = crest(mark, palette, font_path)
        # Dicer uses the full square. Keep the numbered artwork inside its triangular face.
        face = Image.new("RGBA", (256, 256))
        face.alpha_composite(ImageOps.pad(badge, (192, 192), RESAMPLE), (32, 32))
        face.save(ASSETS / "crests" / f"{slug}.png", optimize=True)
        emblem = thumbnail(badge, (47, 48))
        stamp = mark_tile(mark, 23)
        stamp.putalpha(stamp.getchannel("A").point(lambda alpha: alpha * .37))
        out = ASSETS / "skins" / slug
        out.mkdir(parents=True, exist_ok=True)
        for kind, geometry in geometries.items():
            size, panels = geometry[-2:]
            atlas = Image.new("RGB", size, mix(palette[0], palette[2], .34))
            for value, offset, polygon, loop in panels:
                panel = paint_panel(kind, value, polygon, loop, palette, entry["surface"],
                                    emblem, stamp, font_path)
                atlas.paste(panel, offset)
            write_glb(out / f"{kind}.glb", geometry, atlas)
        print(entry["name"], flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("font", help="path to Constantia Bold or another bold serif TrueType font")
    args = parser.parse_args()
    font(args.font, 24)
    characters = json.loads((ROOT / "tools/characters.json").read_text(encoding="utf-8"))
    if len({entry["slug"] for entry in characters}) != len(characters):
        raise ValueError("Character slugs must be unique")
    build_assets(characters, args.font)
    keys = ("slug", "name", "palette", "motion", "speed")
    catalog = [{key: entry[key] for key in keys} for entry in characters]
    (ROOT / "scripts/catalog.js").write_text(
        "// Generated from tools/characters.json by tools/generate_dice.py.\n"
        + "export const CHARACTERS = [\n"
        + "".join(f"    {json.dumps(entry, ensure_ascii=False)},\n" for entry in catalog)
        + "];\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
