"""Inline the neck geometry module into the viewer page so the output is one self-contained file."""
from pathlib import Path
root = Path(__file__).resolve().parent.parent
geo = (root / "src/neck-geometry.js").read_text()
(root / "neck/index.html").write_text((root / "src/cad.html").read_text().replace("/*NECKGEO*/", geo))
print("wrote neck/index.html")
