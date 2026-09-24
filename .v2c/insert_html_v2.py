"""Insert spot illustrations into board_deck.html (v2, measured placements)
and regenerate board_deck.pdf."""
import base64
import os
import re
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
PRES = os.path.join(ROOT, "presentation")
PNG_DIR = os.path.join(BASE, "png")

# name -> (section index 0-based, left, top, w, h) in CSS px on the 1280x720 canvas
HTML_PLACEMENTS = {
    "hero_title":       (0, 725, 94, 485, 237),
    "ship_leak_light":  (1, 90, 548, 215, 128),
    "gauge_flat":       (3, 922, 552, 291, 118),
    "leaky_bucket":     (4, 922, 552, 291, 118),
    "globe_pins":       (5, 922, 552, 291, 118),
    "table_tag":        (6, 922, 552, 291, 118),
    "discount_cliff":   (7, 922, 552, 291, 118),
    "freight_truck":    (8, 922, 552, 291, 118),
    "gavel_check":      (14, 944, 142, 259, 140),
    "sail_ship":        (15, 930, 240, 290, 141),
}

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE = os.path.join(os.environ.get("TEMP", "/tmp"), "chrome_pdf_profile3")


def main() -> None:
    path = os.path.join(PRES, "board_deck.html")
    with open(path, encoding="utf-8") as f:
        html = f.read()

    opens = list(re.finditer(r'<section class="s[^"]*"[^>]*>', html))
    assert len(opens) == 16, f"expected 16 sections, found {len(opens)}"

    inserts = []
    for name, (sec_idx, l, t, w, h) in HTML_PLACEMENTS.items():
        with open(os.path.join(PNG_DIR, name + ".png"), "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        img = (
            f'<img class="spot" src="data:image/png;base64,{b64}" '
            f'style="position:absolute;left:{l}px;top:{t}px;width:{w}px;height:{h}px;">'
        )
        inserts.append((opens[sec_idx].end(), img))

    for pos, img in sorted(inserts, key=lambda p: -p[0]):
        html = html[:pos] + img + html[pos:]

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("html: inserted", len(HTML_PLACEMENTS), "images")

    tmp_pdf = os.path.join(os.environ.get("TEMP", "/tmp"), "board_deck_new.pdf")
    if os.path.exists(tmp_pdf):
        os.remove(tmp_pdf)
    url = "file:///" + path.replace("\\", "/").replace(" ", "%20")
    r = subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
         f"--user-data-dir={PROFILE}", "--no-pdf-header-footer",
         f"--print-to-pdf={tmp_pdf}", url],
        capture_output=True, text=True, timeout=180,
    )
    import pymupdf
    pages = len(pymupdf.open(tmp_pdf))
    assert pages == 16, f"expected 16 pages, got {pages}"
    dst = os.path.join(PRES, "board_deck.pdf")
    with open(tmp_pdf, "rb") as fsrc, open(dst, "wb") as fdst:
        fdst.write(fsrc.read())
    print(f"pdf: re-rendered 16 pages ({os.path.getsize(dst)} bytes)")


if __name__ == "__main__":
    main()
