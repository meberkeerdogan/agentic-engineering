from pathlib import Path

assert Path("alpha.txt").read_text("utf-8") == "alpha\n"
assert Path("beta.txt").read_text("utf-8") == "beta\n"
assert Path("combined.txt").read_text("utf-8") == "alpha+beta\n"
