from pathlib import Path

alpha = Path("alpha.txt").read_text("utf-8").strip()
beta = Path("beta.txt").read_text("utf-8").strip()
Path("combined.txt").write_text(f"{alpha}+{beta}\n", encoding="utf-8")
