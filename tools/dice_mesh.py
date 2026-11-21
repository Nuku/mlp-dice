"""Ponyfinder wrap geometry, face numbering, and GLB serialization."""
import io
import json
import math
import struct
from functools import cache

from PIL import ImageDraw, ImageFont

TILE = 128
PHI = (1 + math.sqrt(5)) / 2
INK = "#fff0d2"

def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def cross(a, b):
    x, y, z = a
    u, v, w = b
    return y * w - z * v, z * u - x * w, x * v - y * u


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def scale(v, k):
    return tuple(x * k for x in v)


def unit(v):
    return scale(v, 1 / math.hypot(*v))


def mean(points):
    return tuple(sum(values) / len(points) for values in zip(*points))


def lerp(a, b, weight):
    return tuple(x + (y - x) * weight for x, y in zip(a, b))


def normal(points):
    return unit(cross(sub(points[1], points[0]), sub(points[2], points[0])))


def dice_shapes():
    """Use the Dice So Nice face directions and the companion models' approximate sizes.

    Reference for value layout: Dice So Nice DICE_SHAPE, also recorded in Dicer's
    compat/dsn-layouts.js. The coin and cube follow the companion models' axis layout.
    The d4 values belong to vertices, pointing away from the resting face.
    """
    sides = 32
    ring = [(math.cos(i * math.tau / sides), math.sin(i * math.tau / sides)) for i in range(sides)]
    coin = [(x, y, z) for z in (-0.14, 0.14) for x, y in ring]
    yield "d2", 51, coin, [
        (list(range(sides)), 1), (list(range(sides, sides * 2)), 2),
        *[([i, (i + 1) % sides, (i + 1) % sides + sides, i + sides], None) for i in range(sides)],
    ]

    tetra = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]
    yield "d4", 82, tetra, [
        ([j for j in range(4) if j != i], value) for i, value in enumerate((1, 2, 4, 3))
    ]

    cube = [(x, y, z) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    yield "d6", 90, cube, [
        ([0, 1, 5, 4], 1), ([0, 1, 3, 2], 2), ([0, 2, 6, 4], 3),
        ([1, 3, 7, 5], 4), ([4, 5, 7, 6], 5), ([2, 3, 7, 6], 6),
    ]

    octa = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    yield "d8", 104, octa, list(zip(
        [[0, 2, 4], [0, 4, 3], [0, 3, 5], [0, 5, 2], [1, 3, 4], [1, 4, 2], [1, 2, 5], [1, 5, 3]],
        [5, 3, 1, 7, 2, 8, 6, 4],
    ))

    c = math.cos(math.pi / 5)
    height = (1 - c) / (1 + c)
    kites = [
        (math.cos(i * math.pi / 5), math.sin(i * math.pi / 5), (-1 if i % 2 == 0 else 1) * height)
        for i in range(10)
    ] + [(0, 0, -1), (0, 0, 1)]
    kite_faces = list(zip(
        [[5, 6, 7, 11], [4, 3, 2, 10], [1, 2, 3, 11], [0, 9, 8, 10], [7, 8, 9, 11],
         [8, 7, 6, 10], [9, 0, 1, 11], [2, 1, 0, 10], [3, 4, 5, 11], [6, 5, 4, 10]],
        [1, 2, 5, 10, 7, 4, 3, 8, 9, 6],
    ))
    yield "d10", 97, kites, kite_faces
    yield "d100", 97, kites, kite_faces

    a, b = 1 / PHI, PHI
    dodeca = [
        (0, a, b), (0, a, -b), (0, -a, b), (0, -a, -b), (b, 0, a), (b, 0, -a),
        (-b, 0, a), (-b, 0, -a), (a, b, 0), (a, -b, 0), (-a, b, 0), (-a, -b, 0),
        (1, 1, 1), (1, 1, -1), (1, -1, 1), (1, -1, -1), (-1, 1, 1), (-1, 1, -1),
        (-1, -1, 1), (-1, -1, -1),
    ]
    yield "d12", 90, dodeca, list(zip(
        [[2, 14, 4, 12, 0], [15, 9, 11, 19, 3], [16, 10, 17, 7, 6], [6, 7, 19, 11, 18],
         [6, 18, 2, 0, 16], [18, 11, 9, 14, 2], [1, 17, 10, 8, 13], [1, 13, 5, 15, 3],
         [13, 8, 12, 4, 5], [5, 4, 14, 9, 15], [0, 12, 8, 10, 16], [3, 19, 7, 17, 1]],
        [7, 5, 3, 11, 12, 9, 4, 1, 2, 10, 8, 6],
    ))

    icosa = [
        (-1, b, 0), (1, b, 0), (-1, -b, 0), (1, -b, 0), (0, -1, b), (0, 1, b),
        (0, -1, -b), (0, 1, -b), (b, 0, -1), (b, 0, 1), (-b, 0, -1), (-b, 0, 1),
    ]
    yield "d20", 95, icosa, list(zip(
        [[0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11], [1, 5, 9], [5, 11, 4],
         [11, 10, 2], [10, 7, 6], [7, 1, 8], [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8],
         [3, 8, 9], [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1]],
        [10, 17, 3, 16, 8, 7, 12, 20, 6, 19, 5, 18, 4, 11, 13, 15, 2, 14, 9, 1],
    ))


def face_projection(points, n):
    center = mean(points)
    up = unit(sub(points[0], center))
    right = cross(up, n)
    xy = [(dot(sub(p, center), right), -dot(sub(p, center), up)) for p in points]
    stretch = (TILE / 2 - 7) / max(abs(axis) for p in xy for axis in p)
    return [(TILE / 2 + x * stretch, TILE / 2 + y * stretch) for x, y in xy]


def mesh(kind, radius, vertices, faces):
    """Inset each numbered panel, then stitch its bevels and corners into one mesh."""
    factor = radius / math.hypot(*vertices[0])
    vertices = [scale(p, factor) for p in vertices]
    positions, normals, texcoords, indices = [], [], [], []
    panels, edges, corners = [], {}, [[] for _ in vertices]
    face_count = sum(value is not None for _, value in faces)
    cols = 8 if face_count > 16 else 4
    rows = math.ceil((face_count + 1) / cols)  # Keep one cell free for the bevel color.
    size = (cols * TILE, (1 << (rows - 1).bit_length()) * TILE)
    metal_uv = ((size[0] - 4) / size[0], (size[1] - 4) / size[1])

    def polygon(points, uvs, n):
        if dot(normal(points), n) < 0:
            points, uvs = points[::-1], uvs[::-1]
        start = len(positions)
        positions.extend(points)
        normals.extend([n] * len(points))
        texcoords.extend(uvs)
        for i in range(1, len(points) - 1):
            indices.extend((start, start + i, start + i + 1))

    def trim(points):
        n = normal(points)
        if dot(n, mean(points)) < 0:
            n = scale(n, -1)
        polygon(points, [metal_uv] * len(points), n)

    for loop, value in faces:
        original = [vertices[i] for i in loop]
        n = normal(original)
        if dot(n, mean(original)) < 0:
            loop = [loop[0], *loop[:0:-1]]
            original = [vertices[i] for i in loop]
            n = normal(original)
        center = mean(original)
        points = [lerp(p, center, 0.072) for p in original]
        if value is None:
            polygon(points, [metal_uv] * len(points), n)
        else:
            xy = face_projection(points, n)
            i = len(panels)
            offset = (i % cols * TILE, i // cols * TILE)
            uvs = [((offset[0] + x) / size[0], (offset[1] + y) / size[1]) for x, y in xy]
            polygon(points, uvs, n)
            panels.append((value, offset, xy, loop))
        for i, vertex in enumerate(loop):
            next_i = (i + 1) % len(loop)
            edge = (vertex, loop[next_i])
            opposite = edges.pop(edge[::-1], None)
            if opposite is None:
                edges[edge] = (points[i], points[next_i])
            else:
                trim([points[i], points[next_i], *opposite])
            corners[vertex].append(points[i])

    if edges:
        raise ValueError(f"{kind}: open edges")
    for vertex, points in zip(vertices, corners):
        n = unit(vertex)
        center = mean(points)
        right = unit(sub(points[0], center))
        up = cross(n, right)
        points.sort(key=lambda p: math.atan2(dot(sub(p, center), up), dot(sub(p, center), right)))
        trim(points)

    return positions, normals, texcoords, indices, size, panels


def mix(a, b, amount):
    return tuple(round(x) for x in lerp(a, b, amount))


@cache
def font(font_path, size):
    return ImageFont.truetype(font_path, size)


def number(tile, label, font_path, size, pt, base):
    draw = ImageDraw.Draw(tile)
    glyph = font(font_path, size)
    draw.text(pt, label, anchor="mm", font=glyph, fill=INK, stroke_width=2, stroke_fill=base)
    if label in ("6", "9", "60", "90"):
        half = glyph.getlength(label) * .31
        y = pt[1] + size * .40
        draw.line([(pt[0] - half, y), (pt[0] + half, y)], INK, width=2)


def write_glb(path, geometry, atlas):
    positions, normals, uv, indices, _, _ = geometry
    data = bytearray()
    views, accessors = [], []

    def add_view(raw, target=None):
        data.extend(b"\0" * (-len(data) % 4))
        view = {"buffer": 0, "byteOffset": len(data), "byteLength": len(raw)}
        if target:
            view["target"] = target
        views.append(view)
        data.extend(raw)
        return len(views) - 1

    for rows, length in ((positions, 3), (normals, 3), (uv, 2)):
        raw = b"".join(struct.pack("<" + "f" * length, *row) for row in rows)
        accessor = {"bufferView": add_view(raw, 34962), "componentType": 5126,
                    "count": len(rows), "type": f"VEC{length}"}
        if rows is positions:
            accessor["min"] = [min(axis) for axis in zip(*rows)]
            accessor["max"] = [max(axis) for axis in zip(*rows)]
        accessors.append(accessor)
    raw = struct.pack(f"<{len(indices)}H", *indices)
    accessors.append({"bufferView": add_view(raw, 34963), "componentType": 5123,
                      "count": len(indices), "type": "SCALAR"})

    png = io.BytesIO()
    atlas.quantize(colors=192).save(png, format="PNG", optimize=True)
    image = add_view(png.getvalue())
    data.extend(b"\0" * (-len(data) % 4))
    doc = {
        "asset": {"version": "2.0", "generator": "MLP Dice (Ponyfinder wrap geometry)"},
        "scene": 0, "scenes": [{"nodes": [0]}], "nodes": [{"mesh": 0}],
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0, "NORMAL": 1, "TEXCOORD_0": 2},
                                   "indices": 3, "material": 0}]}],
        "materials": [{"pbrMetallicRoughness": {"baseColorTexture": {"index": 0},
                                               "metallicFactor": .22, "roughnessFactor": .44}}],
        "textures": [{"source": 0, "sampler": 0}],
        "samplers": [{"magFilter": 9729, "minFilter": 9987, "wrapS": 33071, "wrapT": 33071}],
        "images": [{"bufferView": image, "mimeType": "image/png"}],
        "buffers": [{"byteLength": len(data)}], "bufferViews": views, "accessors": accessors,
    }
    header = json.dumps(doc, separators=(",", ":")).encode()
    header += b" " * (-len(header) % 4)
    glb = struct.pack("<4sII", b"glTF", 2, 28 + len(header) + len(data))
    path.write_bytes(glb + struct.pack("<I4s", len(header), b"JSON") + header
                     + struct.pack("<I4s", len(data), b"BIN\0") + data)
