from __future__ import annotations
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt


_DATA_DIR = Path(__file__).parents[2]
JSON_DIR = _DATA_DIR / "data"
SPRITE_DIR = _DATA_DIR / "sprites"

_DEFAULT_NAME = "MyEquations"


class EquationSet:
    """A collection of equation objects."""

    def __init__(self, equations: list[Equation], name: str = _DEFAULT_NAME) -> None:
        self.name = name
        unique_equations = []
        for equation in equations:  # uses Equation.__eq__ to check
            if equation not in unique_equations:
                unique_equations.append(equation)
        self.equations = sorted(unique_equations, key=lambda equ: equ.name)

    def __str__(self) -> str:
        eq_strings = "\n".join(f" - {equ}" for equ in self.equations)
        return (
            f"Equation set \"{self.name}\" with {len(self.equations)} equations:\n"
            f"{eq_strings}"
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, EquationSet):
            return False
        return self.equations == other.equations

    def __contains__(self, equation: Any) -> bool:
        if not isinstance(equation, Equation):
            return False
        return equation in self.equations

    def add_equation(self, new_equation: Equation) -> None:
        self.equations.append(new_equation)
        self.equations = sorted(self.equations, key=lambda equation: equation.name)

    def remove_equation(self, equation: Equation) -> None:
        if equation in self.equations:
            self.equations.remove(equation)
        else:
            raise ValueError("Equation not found in the set.")

    @property
    def all_terms(self) -> list[Term]:
        """All terms of all equations in the set, usage without brackets like `equation_set_object.all_terms`."""
        return list(itertools.chain.from_iterable(equation.all_terms for equation in self.equations))

    def to_json(self, json_path: Path | None = None) -> None:
        json_path = (
            json_path or JSON_DIR / f"{self.name.replace(' ', '_')}.json"
        )
        with json_path.open("w") as f:
            json.dump(
                [equation.as_dict() for equation in self.equations], f, indent=4
            )  # match python indentation for easier editing of JSON

    @classmethod
    def from_json(
        cls, file_path: Path, name: str | None = None
    ) -> EquationSet:
        name = name or file_path.stem.replace("_", " ")
        with file_path.open("r") as f:
            equations = [Equation.from_dict(elem) for elem in json.load(f)]
        return cls(equations, name)


class Equation:
    """An equation with terms divided into left and right part."""

    def __init__(self, name: str, left: list[Term], right: list[Term]) -> None:
        zero_term = Term("0", "0", "+")
        self.name = name
        # empty sides default to zero-term
        if not left:
            left = [zero_term]
        if not right:
            right = [zero_term]
        self.left = sorted(left, key=lambda t: t.latex_code)
        self.right = sorted(right, key=lambda t: t.latex_code)

    def __str__(self) -> str:
        left_terms = " ".join(str(t) for t in self.left)
        right_terms = " ".join(str(t) for t in self.right)
        return f"\"{self.name}\": {left_terms} = {right_terms}"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Equation):
            return False
        return self.left == other.left and self.right == other.right  # already sorted

    @property
    def all_terms(self) -> list[Term]:
        """All terms of equation, usage without brackets like `equation_object.all_terms`."""
        return [*self.left, *self.right]

    def check_input(self, test_left: list[Term], test_right: list[Term]) -> bool:
        return self._check_side(self.left, test_left) and self._check_side(
            self.right, test_right
        )

    def as_dict(self) -> dict[str, str | list[dict[str, str]]]:
        return {
            "name": self.name,
            "left": [t.as_dict() for t in self.left],
            "right": [t.as_dict() for t in self.right],
        }

    @classmethod
    def from_dict(cls, data: dict[str, str | list[dict[str, str]]]) -> "Equation":
        return cls(
            data["name"],
            [Term.from_dict(elem) for elem in data["left"]],
            [Term.from_dict(elem) for elem in data["right"]],
        )

    @staticmethod
    def _check_side(self_side: list[Term], test_side: list[Term]) -> bool:
        return len(self_side) == len(test_side) and all(
            [
                self_term == test_term
                for self_term, test_term in zip(
                    self_side, sorted(test_side, key=lambda t: t.latex_code)
                )
            ]
        )


class Term:
    """Part of an Equation."""

    def __init__(
        self, name: str, latex_code: str, sign: str, sprite_id: str | None = None
    ) -> None:
        self.name = name
        if sign not in ("+", "-"):
            raise ValueError('Invalid sign. Must be "+" (plus) or "-" (minus).')
        self.sign = sign
        self.latex_code = latex_code
        # ensure unique sprite_id based on sign and latex_code if not provided
        full_latex_code = f"{self.sign}{self.latex_code}"
        self.sprite_id = sprite_id or hashlib.sha1(full_latex_code.encode()).hexdigest()
        if not self.get_sprite_path().exists():
            # create sprite
            fig, ax = plt.subplots(figsize=(1, 1), dpi=100)
            try:
                ax.text(
                    0.5,
                    0.5,
                    f"${full_latex_code}$",
                    fontsize=20,
                    ha="center",
                    va="center",
                )
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
        return f"{self.sign} {self.latex_code}"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Term):
            return False
        # Currently, .name does not need to be the same
        # sprite_id will be the same if sign and latex_code are the same
        return self.sign == other.sign and self.latex_code == other.latex_code

    def get_sprite_path(self) -> Path:
        SPRITE_DIR.mkdir(parents=True, exist_ok=True)  # for first usage
        return SPRITE_DIR / f"{self.sprite_id}.png"

    def as_dict(self) -> dict[str, str | None]:
        return {
            "name": self.name,
            "sign": self.sign,
            "latex_code": self.latex_code,
            "sprite_id": self.sprite_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "Term":
        return cls(
            name=data["name"],
            latex_code=data["latex_code"],
            sign=data["sign"] if "sign" in data else "+",
            sprite_id=data.get("sprite_id") if "sprite_id" in data else None,
        )


# TODO: remove in final solution (and also remove corresponding and not needed JSONs)
if __name__ == "__main__":
    # Create terms for examples
    # (would only be needed in version with equation editor or type-in solution)
    TERM_1 = Term("x^2", "x^2", "+")
    TERM_2 = Term("yp/pi", r"\frac{yp}{\pi}", "-")
    TERM_3 = Term("dp/dz", r"\frac{\operatorname{d} p}{\operatorname{d} z}", "+")

    # Create equations for examples
    # (could be used to create equation after user pressed button "submit" e.g. to
    # create equation and either add to user_set for later comparison to board_set or
    # check directly if current user_equation is in board_set)
    EQUATION_1 = Equation("ExampleEquation1", [TERM_1], [TERM_2])
    EQUATION_2 = Equation("ExampleEquation2", [TERM_1, TERM_2], [TERM_3])

    # Create equation sets as examples (from_json would be used at beginning of game,
    # from_equations could be used to create user_set after user submitted equation(s))
    EQUATION_SET_FROM_JSON = EquationSet.from_json(JSON_DIR / "equation_set_example.json")
    EQUATION_SET_FROM_EQUATIONS = EquationSet([EQUATION_1, EQUATION_2], "ExampleSet")

    # print equation sets (only for development, debugging, testing...)
    print(f"{EQUATION_SET_FROM_EQUATIONS}\n")
    print(f"{EQUATION_SET_FROM_JSON}\n")

    # compare equation sets (could be used to check if user_set == board_set)
    print(f"{EQUATION_SET_FROM_EQUATIONS == EQUATION_SET_FROM_JSON=}\n")

    # check if equation is in set (could be used to check if user_equation in board_set)
    print(f"{EQUATION_1 in EQUATION_SET_FROM_JSON=}")
    print(f"{EQUATION_2 in EQUATION_SET_FROM_EQUATIONS=}\n")

    # How to get sprites for terms of equation set (to display them on the board)
    print("All sprite paths per term in EQUATION_SET_FROM_EQUATIONS:")
    for term in EQUATION_SET_FROM_EQUATIONS.all_terms:
        print(f"{term}: {term.get_sprite_path()}")
    print()

    # Save equation set to JSON (could be used temporarily to create standard_set.json
    # such that it would be loadable afterwards bc it needs to meet the format specs)
    EQUATION_SET_FROM_EQUATIONS.to_json()
    # or if you would like to change the name:
    EQUATION_SET_FROM_EQUATIONS.to_json(JSON_DIR / "standard_set.json")
    # now if you reload the equation set from JSON...
    equation_set1_reload = EquationSet.from_json(
        JSON_DIR / "second_equation_set_example.json"
    )
    # ...it should be the same as before
    print(f"{EQUATION_SET_FROM_EQUATIONS == equation_set1_reload=}")
