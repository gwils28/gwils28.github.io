#!/usr/bin/env python3
"""Prépare des photos de voyage pour un album de la section Migration.

    python3 scripts/album-photos.py <dossier-source> <slug-album> [--max 2500]

- redresse chaque photo selon son orientation EXIF (photos de téléphone) ;
- la réduit à --max px sur le grand côté (2500 par défaut) ;
- l'enregistre en JPEG (qualité 88) SANS métadonnées : ni GPS, ni appareil ;
- la range dans content/migration/<slug-album>/ sous 01.jpg, 02.jpg…,
  dans l'ordre de prise de vue (date EXIF, à défaut le nom du fichier).

Si l'album n'existe pas encore, il est créé depuis archetypes/migration.md
(en brouillon). Les photos déjà présentes dans l'album sont conservées : les
nouvelles sont numérotées à la suite.

Dépendance : Pillow (python3 -m pip install Pillow). Les fichiers HEIC
d'iPhone demandent en plus pillow-heif (python3 -m pip install pillow-heif).
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageOps

try:  # HEIC facultatif
    from pillow_heif import register_heif_opener

    register_heif_opener()
except ImportError:
    pass

ROOT = Path(__file__).resolve().parent.parent
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".tif", ".tiff"}
DATE_TAKEN = 36867  # EXIF DateTimeOriginal
DATE_FALLBACK = 306  # EXIF DateTime


def taken_at(path: Path) -> str:
    """Date de prise de vue « AAAA:MM:JJ HH:MM:SS », ou "" si inconnue."""
    try:
        with Image.open(path) as im:
            exif = im.getexif()
            date = exif.get_ifd(0x8769).get(DATE_TAKEN) or exif.get(DATE_FALLBACK)
            return str(date or "")
    except Exception:
        return ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("source", type=Path, help="dossier contenant les photos d'origine")
    parser.add_argument("slug", help="nom du dossier de l'album, ex. japon-2025")
    parser.add_argument("--max", type=int, default=2500, help="taille max du grand côté, en px")
    args = parser.parse_args()

    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", args.slug):
        sys.exit("Le slug doit être en minuscules, sans accents ni espaces : ex. japon-2025")

    photos = [p for p in args.source.iterdir() if p.suffix.lower() in EXTENSIONS]
    if not photos:
        sys.exit(f"Aucune photo trouvée dans {args.source}")
    photos.sort(key=lambda p: (taken_at(p) or "9999", p.name.lower()))

    album = ROOT / "content" / "migration" / args.slug
    if not (album / "index.md").exists():
        subprocess.run(["hugo", "new", f"migration/{args.slug}/index.md"], cwd=ROOT, check=True)

    start = len([p for p in album.iterdir() if p.suffix.lower() in EXTENSIONS])
    for n, src in enumerate(photos, start=start + 1):
        dest = album / f"{n:02d}.jpg"
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            im.thumbnail((args.max, args.max), Image.LANCZOS)
            # Pas d'argument exif= : le fichier sort sans aucune métadonnée.
            im.save(dest, "JPEG", quality=88, optimize=True, progressive=True)
        print(f"{src.name} → {dest.relative_to(ROOT)}  ({im.width}×{im.height})")

    print(f"\n{len(photos)} photo(s) prête(s) dans {album.relative_to(ROOT)}/")
    print("Reste à remplir index.md (titre, lieu, date) et à passer draft à false.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
