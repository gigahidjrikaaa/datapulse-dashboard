"""Render the deck's SVG illustrations to transparent PNGs via headless Chrome."""
import base64
import os
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
SVG_DIR = os.path.join(BASE, "svg")
PNG_DIR = os.path.join(BASE, "png")
os.makedirs(PNG_DIR, exist_ok=True)

SIZES = {
    "hero_title": (960, 470),
    "ship_leak": (740, 440),
    "gauge_flat": (740, 300),
    "leaky_bucket": (740, 300),
    "globe_pins": (740, 300),
    "table_tag": (740, 300),
    "discount_cliff": (740, 300),
    "freight_truck": (740, 300),
    "gavel_check": (740, 400),
    "sail_ship": (740, 360),
}

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE = os.path.join(os.environ.get("TEMP", "/tmp"), "chrome_illo_profile")


def main() -> None:
    for name, (w, h) in SIZES.items():
        svg = open(os.path.join(SVG_DIR, name + ".svg"), encoding="utf-8").read()
        b64 = base64.b64encode(svg.encode("utf-8")).decode()
        html = (
            '<html><body style="margin:0;padding:0;overflow:hidden">'
            f'<img src="data:image/svg+xml;base64,{b64}" '
            f'style="display:block;width:{w * 2}px;height:{h * 2}px"></body></html>'
        )
        hp = os.path.join(PNG_DIR, name + ".html")
        with open(hp, "w", encoding="utf-8") as f:
            f.write(html)
        out = os.path.join(PNG_DIR, name + ".png")
        cmd = [
            CHROME,
            "--headless=new",
            "--disable-gpu",
            "--no-first-run",
            "--hide-scrollbars",
            "--force-device-scale-factor=1",
            "--default-background-color=00000000",
            f"--user-data-dir={PROFILE}",
            f"--window-size={w * 2},{h * 2}",
            f"--screenshot={out}",
            hp,
        ]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        ok = os.path.exists(out)
        status = f"ok ({os.path.getsize(out)} bytes)" if ok else "FAIL " + r.stderr[-200:]
        print(f"{name}: {status}")


if __name__ == "__main__":
    main()
