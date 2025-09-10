# Classes for equations and terms, including JSON import/export and sprite generation
# (only logic for objects, no GUI or game logic)


from __future__ import annotations
from pathlib import Path
from typing import Any

#import matplotlib.pyplot as plt
from src.equatio.term import Term


# Path constants
_DATA_DIR = Path(__file__).parents[2]
JSON_DIR = _DATA_DIR / "data"
SPRITE_DIR = _DATA_DIR / "sprites"

# Default name constant
_DEFAULT_SET_NAME = "MyEquations"

class Equation:
    """An equation with terms divided into left and right part."""

    def __init__(self, name: str, left: list[Term], right: list[Term]) -> None:
        """Initialise with name, left side terms, and right side terms.
        Empty sides default to a zero term. Sort terms for each side by latex_code."""
        ZERO_TERM = Term("0", "0", "+")
        self.name = name
        self.left = sorted(left or [ZERO_TERM], key=lambda t: t.latex_code)
        self.right = sorted(right or [ZERO_TERM], key=lambda t: t.latex_code)

    def __str__(self) -> str:
        """String representation of the equation."""
        left_terms = " ".join(str(t) for t in self.left)
        right_terms = " ".join(str(t) for t in self.right)
        return f'"{self.name}": {left_terms} = {right_terms}'

    def __eq__(self, other: Any) -> bool:
        """Check equality with another Equation based on left and right terms,
        ignoring the name."""
        if not isinstance(other, Equation):
            return False
        return self.left == other.left and self.right == other.right  # already sorted

    @property
    def all_terms(self) -> list[Term]:
        """Property to get all terms of the equation.
        Usage without brackets like `equation.all_terms`."""
        return [*self.left, *self.right]

    def check_input(self, test_left: list[Term], test_right: list[Term]) -> bool:
        """Check if provided left and right term lists match the equation's sides,
        ignoring order and name."""
        return self._check_side(self.left, test_left) and self._check_side(
            self.right, test_right
        )

    def as_dict(self) -> dict[str, str | list[dict[str, str]]]:
        """Convert the equation to a dictionary. Used for JSON export."""
        return {
            "name": self.name,
            "left": [t.as_dict() for t in self.left],
            "right": [t.as_dict() for t in self.right],
        }

    @classmethod
    def from_dict(cls, data: dict[str, str | list[dict[str, str]]]) -> Equation:
        """Create an Equation object from a dictionary. Used for JSON import."""
        return cls(
            data["name"],
            [Term.from_dict(elem) for elem in data["left"]],
            [Term.from_dict(elem) for elem in data["right"]],
        )

    @staticmethod
    def _check_side(self_side: list[Term], test_side: list[Term]) -> bool:
        """Helper method to check if two sides (lists of terms) are equal,
        ignoring order and name."""
        return len(self_side) == len(test_side) and all(
            [
                self_term == test_term
                for self_term, test_term in zip(
                    self_side, sorted(test_side, key=lambda t: t.latex_code)
                )
            ]
        )




