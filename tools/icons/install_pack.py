#!/usr/bin/env python3
"""Installs the icon pack in tools/icons/pack into the app (D-177). Run from the repo root:

    python3 tools/icons/install_pack.py

The pack (from the owner, "Nawy Today" calendar-page icon) is the source of truth. This copies each
file where it belongs and derives the few files the pack does not have, from the pack's own
monochrome layer, so nothing is drawn twice:

  web      public/icons/{icon-192,icon-512,icon-maskable-512,apple-touch-icon}.png, icon.svg, favicon.ico
           public/icons/icon-monochrome-512.png        (derived: the manifest's themed-icon entry)
  android  tools/android/res/{mipmap-*,values}/...     (launcher: legacy, round, adaptive, themed)
           tools/android/res/drawable-*/ic_stat_taqweem.png   (derived: the notification glyph)
           tools/android/playstore-icon-512.png

Needs Pillow only. Not part of CI: the results are committed, and tests/build/icons.test.ts checks them.
"""
import shutil
from pathlib import Path

from PIL import Image

PACK = Path('tools/icons/pack')
WEB = Path('public/icons')
RES = Path('tools/android/res')

DENSITIES = ('mdpi', 'hdpi', 'xhdpi', 'xxhdpi', 'xxxhdpi')
STAT_SIZES = dict(zip(DENSITIES, (24, 36, 48, 72, 96)))  # the notification icon is 24 dp


def copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


def glyph() -> Image.Image:
    """The white calendar glyph (header bar + the filled cells), cropped to its own bounds."""
    layer = Image.open(PACK / 'android/res/mipmap-xxxhdpi/ic_launcher_monochrome.png').convert('RGBA')
    box = layer.getchannel('A').getbbox()
    if box is None:
        raise SystemExit('the monochrome layer is empty')
    return layer.crop(box)


def centered(img: Image.Image, canvas: int, height: int) -> Image.Image:
    """`img` scaled to `height` px tall (keeping its shape), centred on a transparent square."""
    width = round(img.width * height / img.height)
    scaled = img.resize((width, height), Image.LANCZOS)
    out = Image.new('RGBA', (canvas, canvas), (0, 0, 0, 0))
    out.paste(scaled, ((canvas - width) // 2, (canvas - height) // 2), scaled)
    return out


def main() -> None:
    # --- web ---
    for name in ('icon-192.png', 'icon-512.png', 'icon-maskable-512.png', 'apple-touch-icon.png', 'favicon.ico'):
        copy(PACK / 'web' / name, WEB / name)
    copy(PACK / 'web/favicon.svg', WEB / 'icon.svg')

    # themed icon on the web: the Android themed layer, scaled like the layer is inside its 432 canvas
    layer = Image.open(PACK / 'android/res/mipmap-xxxhdpi/ic_launcher_monochrome.png').convert('RGBA')
    layer.resize((512, 512), Image.LANCZOS).save(WEB / 'icon-monochrome-512.png')

    # --- android ---
    for path in (PACK / 'android/res').rglob('*'):
        if path.is_file():
            copy(path, RES / path.relative_to(PACK / 'android/res'))
    copy(PACK / 'android/play-store/ic_launcher-playstore-512.png', Path('tools/android/playstore-icon-512.png'))

    # notification glyph: white on transparent (Android uses only the alpha), ~8% margin
    g = glyph()
    for density, size in STAT_SIZES.items():
        out = RES / f'drawable-{density}' / 'ic_stat_taqweem.png'
        out.parent.mkdir(parents=True, exist_ok=True)
        centered(g, size, round(size * 0.84)).save(out)

    print('icons installed from', PACK)


if __name__ == '__main__':
    main()
