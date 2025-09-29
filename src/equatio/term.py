# Class for the representation of a term within an equation
# (only logic for objects, no GUI or game logic)

from __future__ import annotations
import hashlib
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

_DATA_DIR = Path(__file__).parents[2]
JSON_DIR = _DATA_DIR / "data"
SPRITE_DIR = _DATA_DIR / "sprites"


class Term:
    """Part of an Equation."""

    def __init__(
        self, name: str, latex_code: str, sign: str, sprite_id: str | None = None
    ) -> None:
        """Initialise with name, LaTeX code, sign ("+" or "-"), and optional sprite_id.
        Generates and saves sprite if not existing."""
        self.name = name
        if sign not in ("+", "-"):
            raise ValueError('Invalid sign. Must be "+" (plus) or "-" (minus).')
        self.sign = sign
        self.latex_code = latex_code
        # ensure unique sprite_id based on sign and latex_code if not provided
        full_latex_code = f"{self.sign}{self.latex_code}"
        self.sprite_id = sprite_id or hashlib.sha1(full_latex_code.encode()).hexdigest()
        if not self.get_sprite_path().exists():
            # create sprite with matplotlib as png with transparent background
            fig, ax = plt.subplots(figsize=(1, 1), dpi=100)
            try:
                ax.text(
                    0.5,
                    0.5,
                    f"${full_latex_code}$",
                    fontsize=20,
                    ha="center",
                    va="center",
                )  # center the LaTeX code in sprite
            except Exception as e:
                raise ValueError(f"Invalid LaTeX code: {latex_code}") from e
            ax.axis("off")
            plt.savefig(
                self.get_sprite_path(),
                bbox_inches="tight",
                pad_inches=0.1,
                transparent=True,
            )
            plt.close(fig)

    def __str__(self) -> str:
        """String representation of the term."""
        return f"{self.sign} {self.latex_code}"

    def __eq__(self, other: Any) -> bool:
        """Check equality with another Term based on sign and LaTeX code,
        (currently) ignoring name. Sprite ID will be the same if sign and LaTeX code
        are the same."""
        if not isinstance(other, Term):
            return False
        return self.sign == other.sign and self.latex_code == other.latex_code

    def get_sprite_path(self) -> Path:
        """Get the file path of the sprite image for this term.
        Creates the sprite directory if it doesn't exist."""
        SPRITE_DIR.mkdir(parents=True, exist_ok=True)  # for first usage on machine
        return SPRITE_DIR / f"{self.sprite_id}.png"

    def as_dict(self) -> dict[str, str | None]:
        """Convert the term to a dictionary. Used for JSON export."""
        return {
            "name": self.name,
            "sign": self.sign,
            "latex_code": self.latex_code,
            "sprite_id": self.sprite_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Term:
        """Create a Term object from a dictionary. Used for JSON import."""
        return cls(
            name=data["name"],
            latex_code=data["latex_code"],
            sign=data["sign"] if "sign" in data else "+",
            sprite_id=data.get("sprite_id") if "sprite_id" in data else None,
        )
