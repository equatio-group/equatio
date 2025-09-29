# should create a standard equation set that can be used for the game
from pathlib import Path

from src.equatio.equation_set import EquationSet

DATA_PATH = Path(__file__).parents[1]
SPRITE_DIR = DATA_PATH / "sprites"
JSON_DIR = DATA_PATH / "data"

STANDARD_SET = EquationSet.from_json(JSON_DIR / "standard_set.json")

print(STANDARD_SET)
