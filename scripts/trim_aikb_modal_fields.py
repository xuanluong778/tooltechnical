"""Remove extra fields from aikb create/edit modal in settings.html."""
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "templates" / "settings.html"
text = p.read_text(encoding="utf-8")
marker_start = '<label for="aikbTone">'
marker_end = '<motion class="apik-modal-err" id="aikbModalErr">'
if marker_end not in text:
    marker_end = '<div class="apik-modal-err" id="aikbModalErr">'
start = text.find(marker_start)
if start == -1:
    raise SystemExit("start marker not found")
# back to opening <motion of tone grid
block_start = text.rfind("\n", 0, start)
# find line with aikb-grid2 before tone
grid_pos = text.rfind('<div class="aikb-grid2">', 0, start)
if grid_pos == -1 or start - grid_pos > 200:
    grid_pos = text.rfind("\n", 0, start)
    block_start = grid_pos
else:
    block_start = grid_pos
end = text.find(marker_end)
if end == -1:
    raise SystemExit("end marker not found")
new_text = text[:block_start] + "\n\n                        " + marker_end + text[end + len(marker_end) :]
p.write_text(new_text, encoding="utf-8")
print("OK: trimmed modal fields")
