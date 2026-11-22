Nawy Today — Android + Web icon pack
====================================
android/res/                 copy into app/src/main/res/
  mipmap-*/ic_launcher.png            legacy square icon (48/72/96/144/192)
  mipmap-*/ic_launcher_round.png      legacy round icon
  mipmap-*/ic_launcher_foreground.png adaptive foreground (108/162/216/324/432), card kept inside the safe zone
  mipmap-*/ic_launcher_monochrome.png themed-icon layer (Android 13+), white glyph on transparent
  mipmap-anydpi-v26/ic_launcher.xml (+_round)  adaptive-icon definition (background / foreground / monochrome)
  values/ic_launcher_background.xml   background colour #111318
android/play-store/ic_launcher-playstore-512.png   Google Play 512x512 (full-bleed)

web/
  favicon.svg, favicon.ico (16/32/48), favicon-16/32/48.png
  apple-touch-icon.png (180, full-bleed)
  icon-192/512.png (purpose: any)  icon-maskable-192/512.png (purpose: maskable, content inside the 80% safe circle)
  manifest.webmanifest, head-snippet.html (paste into <head>)
Note: favicon.svg is a simplified vector (no soft shadow); the PNGs carry the full gloss.
