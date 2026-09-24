"""Generate duotone spot illustrations for the Global Superstore board deck.

Style: flat institutional line art in the deck palette. Strokes are brown ink,
fills are beige/tan, red is used sparingly as the "loss" accent. All canvases
are wide vignettes designed to sit in the empty lower-right of slide columns.
"""
import os

INK = "#322014"      # dark brown ink (main strokes on light slides)
BROWN = "#5A3921"    # accent brown (fills, secondary strokes)
MUTED = "#8A7B6B"    # muted gray-brown
TAN = "#C5A681"      # tan / gold accent (coins)
RED = "#A22727"      # crimson accent (loss markers)
BEIGE = "#E2DCD2"    # beige fill
CREAM = "#E2DCD2"    # stroke color on the dark panel

HEAD = (
    'xmlns="http://www.w3.org/2000/svg" '
    'stroke-linecap="round" stroke-linejoin="round"'
)

# ---------------------------------------------------------------- 1. title hero
# Globe with a rising growth arrow, coin stack and a small storefront.
HERO = f'''<svg {HEAD} viewBox="0 0 960 470">
  <g fill="none" stroke="{BROWN}" stroke-width="9">
    <!-- globe -->
    <circle cx="330" cy="235" r="150" fill="#FFFFFF"/>
    <ellipse cx="330" cy="235" rx="66" ry="150"/>
    <path d="M 189 185 H 471 M 189 285 H 471"/>
    <path d="M 330 85 V 385"/>
    <!-- growth arrow sweeping up from the globe -->
    <path d="M 250 320 C 420 300 560 220 640 110" stroke-width="13"/>
    <path d="M 585 108 L 648 100 L 636 162" stroke-width="13"/>
    <!-- coin stack bottom left -->
    <ellipse cx="140" cy="382" rx="54" ry="19" fill="{BEIGE}"/>
    <ellipse cx="140" cy="356" rx="54" ry="19" fill="{BEIGE}"/>
    <ellipse cx="140" cy="330" rx="54" ry="19" fill="{TAN}"/>
  </g>
  <!-- storefront upper right -->
  <g fill="none" stroke="{BROWN}" stroke-width="9">
    <path d="M 700 260 V 400 H 920 V 260" fill="#FFFFFF"/>
    <path d="M 676 260 L 700 196 H 920 L 944 260 Z" fill="{BEIGE}"/>
    <path d="M 715 260 V 236 M 775 260 V 236 M 835 260 V 236 M 895 260 V 236" stroke-width="7"/>
    <rect x="770" y="310" width="80" height="90" fill="{TAN}"/>
    <path d="M 726 400 V 330 H 762 V 400 M 858 400 V 330 H 894 V 400"/>
  </g>
  <!-- red location pin on the globe + sparkles -->
  <g>
    <path d="M 330 152 C 310 152 296 168 296 186 C 296 210 330 236 330 236 C 330 236 364 210 364 186 C 364 168 350 152 330 152 Z"
          fill="{RED}" stroke="{INK}" stroke-width="7"/>
    <circle cx="330" cy="185" r="11" fill="#FFFFFF" stroke="none"/>
  </g>
  <g stroke="{TAN}" stroke-width="8" fill="none">
    <path d="M 560 380 v 34 M 543 397 h 34"/>
    <path d="M 620 300 v 26 M 607 313 h 26"/>
  </g>
</svg>'''

# ------------------------------------------------------- 2. leaking ship (dark)
# Container ship with a cracked hull losing coins, cream lines on dark panel.
SHIP_LEAK = f'''<svg {HEAD} viewBox="0 0 740 440">
  <g fill="none" stroke="{CREAM}" stroke-width="9">
    <!-- hull -->
    <path d="M 90 300 H 620 L 570 380 H 160 Z" fill="none"/>
    <!-- containers on deck -->
    <rect x="170" y="230" width="90" height="70" fill="none"/>
    <rect x="270" y="230" width="90" height="70" fill="none"/>
    <rect x="370" y="230" width="90" height="70" fill="none"/>
    <rect x="320" y="160" width="90" height="70" fill="none"/>
    <path d="M 480 300 V 170 H 545 V 300"/>
    <!-- crack in the hull -->
    <path d="M 262 322 l 16 14 l -12 12 l 18 15" stroke="{CREAM}" stroke-width="7"/>
  </g>
  <!-- one red container -->
  <rect x="270" y="230" width="90" height="70" fill="{RED}" opacity="0.85"/>
  <!-- coins dripping from the crack -->
  <g fill="{TAN}" stroke="{CREAM}" stroke-width="6">
    <circle cx="286" cy="402" r="14"/>
  </g>
  <g fill="none" stroke="{CREAM}" stroke-width="7">
    <path d="M 340 396 q 6 10 0 20" opacity="0.9"/>
    <path d="M 240 402 q -6 10 0 20" opacity="0.9"/>
  </g>
  <!-- water line -->
  <path d="M 60 420 q 40 -18 80 0 t 80 0 t 80 0 t 80 0 t 80 0 t 80 0 t 80 0 t 80 0"
        fill="none" stroke="{CREAM}" stroke-width="8" opacity="0.75"/>
</svg>'''

# ------------------------------------------------------------- 3. margin gauge
GAUGE = f'''<svg {HEAD} viewBox="0 0 740 300">
  <g fill="none" stroke="{BROWN}" stroke-width="11">
    <!-- dial: safe zone (beige, thick) then thin track -->
    <path d="M 150 250 A 220 220 0 0 1 370 30" stroke="{BEIGE}" stroke-width="30"/>
    <path d="M 370 30 A 220 220 0 0 1 590 250" stroke-width="11"/>
    <!-- ticks -->
    <path d="M 370 62 V 92 M 205 105 l 20 24 M 143 250 h 30 M 567 250 h 30 M 517 105 l -20 24" stroke-width="8"/>
    <!-- needle pinned just left of centre -->
    <path d="M 370 250 L 282 106" stroke="{INK}" stroke-width="14"/>
  </g>
  <circle cx="370" cy="250" r="22" fill="{BROWN}"/>
  <!-- red deficit marker on the left of the dial -->
  <circle cx="163" cy="206" r="16" fill="{RED}"/>
</svg>'''

# ------------------------------------------------------------- 4. leaky bucket
BUCKET = f'''<svg {HEAD} viewBox="0 0 740 300">
  <g fill="none" stroke="{BROWN}" stroke-width="10">
    <!-- bucket -->
    <path d="M 200 90 L 236 250 H 356 L 392 90 Z" fill="#FFFFFF"/>
    <ellipse cx="296" cy="90" rx="96" ry="26" fill="{BEIGE}"/>
    <path d="M 212 70 Q 296 20 380 70"/>
    <!-- crack -->
    <path d="M 356 226 l -16 12 l 14 12" stroke-width="8"/>
    <!-- puddle -->
    <path d="M 430 272 q 30 -14 60 0 t 60 0" stroke-width="8" opacity="0.8"/>
    <path d="M 570 272 q 22 -10 44 0" stroke-width="8" opacity="0.5"/>
  </g>
  <!-- coins escaping the crack -->
  <g fill="{TAN}" stroke="{INK}" stroke-width="6">
    <circle cx="392" cy="248" r="13"/>
    <circle cx="428" cy="208" r="13" opacity="0.95"/>
    <circle cx="462" cy="168" r="13" opacity="0.85"/>
  </g>
  <!-- dashed escape trajectory -->
  <path d="M 372 234 Q 420 190 478 128" fill="none" stroke="{RED}" stroke-width="7"
        stroke-dasharray="2 22"/>
  <!-- small counterweight: the profitable core endures -->
  <g fill="{TAN}" stroke="{INK}" stroke-width="6">
    <circle cx="620" cy="248" r="18"/>
  </g>
</svg>'''

# ------------------------------------------------------------- 5. globe + pins
GLOBE = f'''<svg {HEAD} viewBox="0 0 740 300">
  <g fill="none" stroke="{BROWN}" stroke-width="10">
    <circle cx="300" cy="158" r="118" fill="#FFFFFF"/>
    <ellipse cx="300" cy="158" rx="52" ry="118" stroke-width="8"/>
    <path d="M 190 122 H 410 M 190 194 H 410" stroke-width="8"/>
    <path d="M 300 40 V 276" stroke-width="8"/>
    <!-- dotted loss route between two pins -->
    <path d="M 292 96 C 380 60 470 70 540 130" stroke="{MUTED}" stroke-width="7" stroke-dasharray="1 20"/>
    <!-- baseline -->
    <path d="M 620 268 H 700" stroke-width="9" opacity="0.55"/>
  </g>
  <!-- red pin (loss-maker) with pulse -->
  <circle cx="288" cy="92" r="26" fill="{RED}" opacity="0.18" stroke="none"/>
  <path d="M 288 66 C 272 66 260 79 260 94 C 260 114 288 134 288 134 C 288 134 316 114 316 94 C 316 79 304 66 288 66 Z"
        fill="{RED}" stroke="{INK}" stroke-width="7"/>
  <circle cx="288" cy="92" r="9" fill="#FFFFFF" stroke="none"/>
  <!-- brown pin (destination) -->
  <path d="M 544 112 C 530 112 520 123 520 136 C 520 152 544 168 544 168 C 544 168 568 152 568 136 C 568 123 558 112 544 112 Z"
        fill="{BROWN}" stroke="{INK}" stroke-width="7"/>
  <circle cx="544" cy="135" r="8" fill="#FFFFFF" stroke="none"/>
</svg>'''

# --------------------------------------------------------- 6. tables + big tag
TABLE_TAG = f'''<svg {HEAD} viewBox="0 0 740 300">
  <!-- table -->
  <g fill="none" stroke="{BROWN}" stroke-width="10">
    <rect x="90" y="128" width="390" height="26" rx="8" fill="{BEIGE}"/>
    <path d="M 128 154 V 258 M 442 154 V 258" stroke-width="16"/>
    <path d="M 150 226 H 420" stroke-width="9" opacity="0.55"/>
  </g>
  <!-- oversized discount tag hanging off the edge -->
  <g transform="rotate(16 555 148)">
    <path d="M 500 150 H 640 L 668 186 L 640 222 H 500 Z" fill="{BEIGE}" stroke="{BROWN}" stroke-width="9"/>
    <circle cx="524" cy="186" r="10" fill="#FFFFFF" stroke="{BROWN}" stroke-width="7"/>
    <text x="592" y="205" font-family="Georgia, 'Times New Roman', serif" font-size="60" font-weight="bold"
          fill="{BROWN}" stroke="none" text-anchor="middle">%</text>
  </g>
  <path d="M 480 141 Q 505 122 525 140" fill="none" stroke="{MUTED}" stroke-width="7"/>
  <!-- freight cost dragging it under -->
  <path d="M 672 224 q 12 20 -4 38" fill="none" stroke="{RED}" stroke-width="8"/>
</svg>'''

# ------------------------------------------------------------ 7. discount cliff
CLIFF = f'''<svg {HEAD} viewBox="0 0 740 300">
  <!-- zero baseline -->
  <path d="M 56 250 H 700" stroke="{MUTED}" stroke-width="7" opacity="0.6"/>
  <g fill="none" stroke="{BROWN}" stroke-width="10">
    <!-- healthy bars sliding down -->
    <path d="M 90 250 V 130" stroke="{BEIGE}" stroke-width="42"/>
    <path d="M 190 250 V 168" stroke="{BEIGE}" stroke-width="42"/>
    <path d="M 290 250 V 206" stroke="{BEIGE}" stroke-width="42"/>
  </g>
  <!-- the 20% line -->
  <path d="M 350 40 V 262" stroke="{RED}" stroke-width="8" stroke-dasharray="14 14"/>
  <!-- loss bars falling -->
  <g fill="none" stroke="{RED}" stroke-width="10">
    <path d="M 420 250 V 296" stroke-width="0"/>
    <path d="M 430 250 l 0 34" stroke="{RED}" stroke-width="26"/>
    <path d="M 530 250 l 0 44" stroke="{RED}" stroke-width="26"/>
    <path d="M 630 250 l 0 30" stroke="{RED}" stroke-width="26"/>
  </g>
  <!-- trend arrow diving over the cliff -->
  <path d="M 120 96 C 260 84 420 110 560 196 L 640 236" fill="none" stroke="{INK}" stroke-width="11"/>
  <path d="M 596 232 L 648 240 L 630 190" fill="none" stroke="{INK}" stroke-width="11"/>
  <!-- % glyph on the tallest healthy bar -->
  <text x="90" y="112" font-family="Georgia, 'Times New Roman', serif" font-size="52" font-weight="bold"
        fill="{BROWN}" stroke="none" text-anchor="middle">%</text>
</svg>'''

# --------------------------------------------------------------- 8. freight
TRUCK = f'''<svg {HEAD} viewBox="0 0 740 300">
  <g fill="none" stroke="{BROWN}" stroke-width="10">
    <!-- box body + cab -->
    <rect x="100" y="118" width="330" height="100" rx="10" fill="#FFFFFF"/>
    <path d="M 430 142 H 536 L 592 186 V 218 H 430 Z" fill="#FFFFFF"/>
    <rect x="452" y="152" width="48" height="34" rx="6" fill="{BEIGE}" stroke-width="8"/>
  </g>
  <!-- crates in the box (drawn open-topped for a lighter look) -->
  <g fill="none" stroke="{BROWN}" stroke-width="8">
    <rect x="128" y="140" width="64" height="60" fill="{BEIGE}"/>
    <rect x="204" y="140" width="64" height="60"/>
    <path d="M 236 140 V 200 M 204 170 h 64" stroke-width="6"/>
  </g>
  <!-- wheels -->
  <g fill="#FFFFFF" stroke="{INK}" stroke-width="9">
    <circle cx="180" cy="232" r="26"/>
    <circle cx="470" cy="232" r="26"/>
    <circle cx="540" cy="232" r="26"/>
  </g>
  <g fill="{INK}" stroke="none">
    <circle cx="180" cy="232" r="8"/>
    <circle cx="470" cy="232" r="8"/>
    <circle cx="540" cy="232" r="8"/>
  </g>
  <!-- heavy freight coin weighing on the load -->
  <g fill="{TAN}" stroke="{INK}" stroke-width="6">
    <circle cx="265" cy="52" r="24"/>
  </g>
  <path d="M 249 44 a 24 24 0 0 1 32 0" fill="none" stroke="{BROWN}" stroke-width="5"/>
  <path d="M 265 96 v 26 m -9 -11 l 9 11 l 9 -11" fill="none" stroke="{RED}" stroke-width="7"/>
  <!-- motion dashes + ground -->
  <g stroke="{MUTED}" stroke-width="8" fill="none">
    <path d="M 40 148 h 34 M 24 178 h 40"/>
    <path d="M 76 268 H 680" stroke-width="9" opacity="0.55"/>
  </g>
</svg>'''

# --------------------------------------------------------- 9. gavel + checklist
GAVEL = f'''<svg {HEAD} viewBox="0 0 740 400">
  <!-- checklist card -->
  <g fill="none" stroke="{BROWN}" stroke-width="9">
    <rect x="70" y="60" width="250" height="290" rx="14" fill="#FFFFFF"/>
    <path d="M 108 128 h 60 M 108 200 h 60 M 108 272 h 60" stroke="{BEIGE}" stroke-width="14"/>
  </g>
  <g fill="none" stroke="{RED}" stroke-width="9">
    <path d="M 190 122 l 14 14 l 26 -28"/>
    <path d="M 190 194 l 14 14 l 26 -28"/>
    <path d="M 190 266 l 14 14 l 26 -28"/>
  </g>
  <!-- gavel: head + handle as one rotated unit -->
  <g transform="rotate(-40 520 240)">
    <rect x="452" y="196" width="18" height="88" rx="7" fill="{INK}" stroke="none"/>
    <rect x="570" y="196" width="18" height="88" rx="7" fill="{INK}" stroke="none"/>
    <rect x="466" y="206" width="108" height="68" rx="14" fill="{BROWN}" stroke="{INK}" stroke-width="8"/>
    <path d="M 520 274 L 520 366" stroke="{INK}" stroke-width="15"/>
  </g>
  <!-- strike pedestal -->
  <g fill="none" stroke="{BROWN}" stroke-width="10">
    <path d="M 386 322 h 96 l 12 20 h -120 Z" fill="{BEIGE}"/>
    <path d="M 368 342 H 512" stroke-width="12"/>
  </g>
  <!-- impact sparks -->
  <g stroke="{RED}" stroke-width="8" fill="none">
    <path d="M 372 232 l -24 -10 M 380 268 l -26 4"/>
  </g>
</svg>'''

# ---------------------------------------------------------------- 10. sail ship
SAIL = f'''<svg {HEAD} viewBox="0 0 740 360">
  <g fill="none" stroke="{BROWN}" stroke-width="10">
    <!-- hull -->
    <path d="M 150 250 H 590 L 540 310 H 210 Z" fill="{BEIGE}"/>
    <!-- masts -->
    <path d="M 300 250 V 70 M 460 250 V 110" stroke-width="11"/>
    <!-- sails -->
    <path d="M 300 84 C 226 108 206 168 214 226 H 300 Z" fill="#FFFFFF"/>
    <path d="M 316 92 C 396 116 420 172 410 226 H 316 Z" fill="#FFFFFF"/>
    <path d="M 476 122 C 528 140 544 184 538 226 H 476 Z" fill="#FFFFFF"/>
    <!-- pennant -->
    <path d="M 300 70 l -44 12 l 44 12" fill="{RED}" stroke-width="7"/>
  </g>
  <!-- the little leak: drips below the waterline -->
  <g fill="none" stroke="{MUTED}" stroke-width="7">
    <path d="M 330 318 q 5 9 0 17" opacity="0.9"/>
    <path d="M 356 322 q 5 9 0 17" opacity="0.65"/>
  </g>
  <circle cx="416" cy="330" r="9" fill="{TAN}" stroke="{INK}" stroke-width="5"/>
  <!-- waves -->
  <path d="M 90 336 q 38 -16 76 0 t 76 0 t 76 0 t 76 0 t 76 0 t 76 0 t 76 0"
        fill="none" stroke="{BROWN}" stroke-width="8" opacity="0.7"/>
</svg>'''

# ------------------------------------------------------------------------ main
ILLOS = {
    "hero_title": HERO,
    "ship_leak": SHIP_LEAK,
    "gauge_flat": GAUGE,
    "leaky_bucket": BUCKET,
    "globe_pins": GLOBE,
    "table_tag": TABLE_TAG,
    "discount_cliff": CLIFF,
    "freight_truck": TRUCK,
    "gavel_check": GAVEL,
    "sail_ship": SAIL,
}

if __name__ == "__main__":
    outdir = os.path.join(os.path.dirname(__file__), "svg")
    os.makedirs(outdir, exist_ok=True)
    for name, svg in ILLOS.items():
        with open(os.path.join(outdir, f"{name}.svg"), "w", encoding="utf-8") as f:
            f.write(svg)
    print(f"wrote {len(ILLOS)} SVGs to {outdir}")
