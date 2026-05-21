from pathlib import Path

p = Path(__file__).resolve().parents[1] / "templates" / "settings.html"
lines = p.read_text(encoding="utf-8").splitlines()
d = "d" + "iv"

for i, line in enumerate(lines):
    if "aikbLoadErr" in line and "class=" in line:
        lines[i] = f'                <{d} id="aikbLoadErr" class="aip-load-err" hidden></{d}>'
    line = lines[i]
    if "</motion>" in line or "<motion " in line:
        lines[i] = line.replace("</motion>", f"</{d}>").replace("<motion ", f"<{d} ")

text = "\n".join(lines) + "\n"
# fix aikbModal close before import
text = text.replace(
    "                    </form>\n                </div>\n\n            <motion class=\"apik-modal-backdrop aikb-modal\" id=\"aikbImportModal\"".replace("motion", d),
    f"                    </form>\n                </{d}>\n            </{d}>\n\n            <{d} class=\"apik-modal-backdrop aikb-modal\" id=\"aikbImportModal\"",
)
p.write_text(text, encoding="utf-8")
print("fixed")
