# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "templates" / "settings.html"
text = p.read_text(encoding="utf-8")

start = '                        <motion class="aikb-grid2">\n                            <motion>\n                                <label for="aikbTone">'
start = text.find('                        <div class="aikb-grid2">\n                            <motion>\n                                <label for="aikbTone">')
if start < 0:
    start = text.find('                        <div class="aikb-grid2">\n                            <motion>\n                                <label for="aikbTone">')
if start < 0:
    start = text.find('                        <div class="aikb-grid2">')
    if start < 0:
        raise SystemExit("start not found")

# find second aikb-grid2 (tone/lang) - first is brand/website
idx = text.find('                        <div class="aikb-grid2">')
idx2 = text.find('                        <motion class="aikb-grid2">', idx + 1) if idx >= 0 else -1
if idx2 < 0:
    idx2 = text.find('                        <div class="aikb-grid2">', idx + 1)
if idx2 < 0:
    raise SystemExit("tone grid not found")

end = text.find('                        <div class="apik-modal-err" id="aikbModalErr">', idx2)
if end < 0:
    raise SystemExit("end not found")

text = text[:idx2] + text[end:]
p.write_text(text, encoding="utf-8")
print("removed modal fields", idx2, end)
