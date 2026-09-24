"""Render the brown-on-transparent ship colorway via headless Chrome."""
import base64
import os
import subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROFILE = os.path.join(os.environ.get("TEMP", "/tmp"), "chrome_illo_profile")

svg = open(os.path.join(BASE, "svg", "ship_leak_light.svg"), encoding="utf-8").read()
b64 = base64.b64encode(svg.encode("utf-8")).decode()
w, h = 740 * 2, 440 * 2
html = (
    '<html><body style="margin:0;overflow:hidden">'
    f'<img src="data:image/svg+xml;base64,{b64}" '
    f'style="display:block;width:{w}px;height:{h}px"></body></html>'
)
hp = os.path.join(BASE, "png", "ship_leak_light.html")
with open(hp, "w", encoding="utf-8") as f:
    f.write(html)
out = os.path.join(BASE, "png", "ship_leak_light.png")
subprocess.run(
    [CHROME, "--headless=new", "--disable-gpu", "--no-first-run",
     "--default-background-color=00000000", f"--user-data-dir={PROFILE}",
     f"--window-size={w},{h}", f"--screenshot={out}", hp],
    capture_output=True, timeout=90,
)
print("ship_leak_light.png:", os.path.getsize(out), "bytes")
