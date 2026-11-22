// @vitest-environment node
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { describe, expect, it } from 'vitest';

// The icon pack (D-177) is installed by tools/icons/install_pack.py and committed. These checks stop
// a wrong-sized or missing file from reaching a build: Android does not refuse one at build time,
// it just shows a stretched or default icon.

const read = (file: string): Buffer => readFileSync(path.resolve(file));

/** Width, height and PNG colour type (6 = with alpha, 2 = without), from the file header. */
function png(file: string): { width: number; height: number; colorType: number } {
  const b = read(file);
  expect(b.subarray(1, 4).toString('latin1'), `${file} is not a PNG`).toBe('PNG');
  return { width: b.readUInt32BE(16), height: b.readUInt32BE(20), colorType: b[25] ?? -1 };
}

const DENSITIES = { mdpi: 1, hdpi: 1.5, xhdpi: 2, xxhdpi: 3, xxxhdpi: 4 } as const;

describe('web icons', () => {
  it.each([
    ['icon-192.png', 192],
    ['icon-512.png', 512],
    ['icon-maskable-512.png', 512],
    ['icon-monochrome-512.png', 512],
    ['apple-touch-icon.png', 180],
  ])('%s is %d px square', (name, size) => {
    const { width, height } = png(`public/icons/${name}`);
    expect([width, height]).toEqual([size, size]);
  });

  it('has a favicon.ico holding the 16, 32 and 48 px images, and an SVG', () => {
    const ico = read('public/icons/favicon.ico');
    expect(ico.readUInt16LE(2)).toBe(1); // type: icon
    const count = ico.readUInt16LE(4);
    const sizes = Array.from({ length: count }, (_, i) => {
      const side = ico[6 + i * 16] ?? 0; // 0 means 256
      return side === 0 ? 256 : side;
    }).sort((a, b) => a - b);
    expect(sizes).toEqual([16, 32, 48]);
    expect(read('public/icons/icon.svg').toString('utf8')).toContain('<svg');
  });
});

describe('android icons', () => {
  const res = 'tools/android/res';

  it.each(Object.entries(DENSITIES))('%s has all launcher layers', (density, scale) => {
    const legacy = 48 * scale;
    const layer = 108 * scale;
    for (const name of ['ic_launcher', 'ic_launcher_round']) {
      const { width, height } = png(`${res}/mipmap-${density}/${name}.png`);
      expect([width, height]).toEqual([legacy, legacy]);
    }
    for (const name of ['ic_launcher_foreground', 'ic_launcher_monochrome']) {
      const { width, height, colorType } = png(`${res}/mipmap-${density}/${name}.png`);
      expect([width, height]).toEqual([layer, layer]);
      expect(colorType, `${name} needs an alpha channel`).toBe(6);
    }
  });

  it.each(Object.entries(DENSITIES))('%s notification icon is 24 dp', (density, scale) => {
    const { width, height, colorType } = png(`${res}/drawable-${density}/ic_stat_taqweem.png`);
    expect([width, height]).toEqual([24 * scale, 24 * scale]);
    expect(colorType).toBe(6);
  });

  it('wires the adaptive icon to the background colour, foreground and themed layer', () => {
    for (const name of ['ic_launcher', 'ic_launcher_round']) {
      const xml = read(`${res}/mipmap-anydpi-v26/${name}.xml`).toString('utf8');
      expect(xml).toContain('@color/ic_launcher_background');
      expect(xml).toContain('@mipmap/ic_launcher_foreground');
      expect(xml).toContain('@mipmap/ic_launcher_monochrome');
    }
    const colors = read(`${res}/values/ic_launcher_background.xml`).toString('utf8');
    expect(colors).toContain('ic_launcher_background');
  });

  it('has the 512 px Play Store icon and the 1024 x 500 feature graphic', () => {
    const icon = png('tools/android/playstore-icon-512.png');
    expect([icon.width, icon.height]).toEqual([512, 512]);
    const feature = png('tools/android/play/feature-graphic-1024x500.png');
    expect([feature.width, feature.height]).toEqual([1024, 500]);
  });

  it('keeps the notification icon name the config and the manifest refer to', () => {
    const config = JSON.parse(read('capacitor.config.json').toString('utf8')) as {
      plugins: { LocalNotifications: { smallIcon: string } };
    };
    expect(config.plugins.LocalNotifications.smallIcon).toBe('ic_stat_taqweem');
  });
});
