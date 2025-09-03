from __future__ import annotations  # helps with typing
import hashlib
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
# Spacing of 2 new lines on module level

_DATA_DIR = Path(__file__).parents[2]
JSON_DIR = _DATA_DIR / "data"
SPRITE_DIR = _DATA_DIR / "sprites"

_DEFAULT_NAME = "MyEquations"

# Maybe split module into three separate ones. One per class. This reduces the scrolling and overload on the reader. "What might be connected how in between?". Module separation clears this up.
class EquationSet:
    """A collection of equation objects."""

    def __init__(self, equations: list[Equation], name: str = _DEFAULT_NAME) -> None:
        self.name = name
        unique_equations = []
        for equation in equations:  # nice!
            if equation not in unique_equations:
                unique_equations.append(equation)
        self.equations = sorted(unique_equations, key=lambda equ: equ.name)

    def __str__(self) -> str:  # __repr__ is used to have a string representation, which is valid Python code to define the object, __str__ is just a visualization
        eq_names = ", ".join(equ.name for equ in self.equations)
        return (
            f'EquationSet("{self.name}", containing {len(self.equations)} '
            f"equations: {eq_names})"  # Stay with one type of quotes either " or '
        )

    def __eq__(self, other: Any) -> bool:  # You cannot be sure, which object is used on comparison
        # Currently only works if other has the right equation names
        if not isinstance(other, EquationSet):
            return False

        return self.equations == other.equations

    def add_equation(self, new_equation: Equation) -> None:
        self.equations.append(new_equation)
        self.equations = sorted(self.equations, key=lambda equation: equation.name)  # used multiple times, maybe make a method for this `self.sort_equations()`

    def remove_equation(self, equation: Equation) -> None:
        if equation in self.equations:
            self.equations.remove(equation)
        else:
            raise ValueError("Equation not found in the set.")

    def to_json(self, json_path: Path | None = None) -> None:
        json_path = json_path or JSON_DIR / f"{self.name.replace(' ', '_')}.json"  # syntactic sugar
        with json_path.open("w") as f:
            json.dump([equation.as_dict() for equation in self.equations], f, indent=4)  # Why not default indent? Put a comment on that.

    @classmethod
    def from_json(cls, file_path: Path, name: str | None = None) -> EquationSet:  # typical use case for a class method
        name = name or file_path.stem.replace("_", " ")
        with file_path.open("r") as f:
            equations = [Equation.from_dict(elem) for elem in json.load(f)]
        return cls(equations, name)


class Equation:
    """An equation with terms divided into left and right part."""

    def __init__(self, name: str, left: list[Term], right: list[Term]) -> None:
        zero_term = Term("0", "0", "+")
        self.name = name
        self.left = sorted(left or [zero_term], key=lambda t: t.latex_code)
        self.right = sorted(right or [zero_term], key=lambda t: t.latex_code)

    def __str__(self) -> str:  # see above
        left_terms = " ".join(str(t) for t in self.left)
        right_terms = " ".join(str(t) for t in self.right)
        return f'Equation("{self.name}": {left_terms} = {right_terms})'

    def __eq__(self, other: Equation) -> bool:
        return self.left == other.left and self.right == other.right  # already sorted

    def get_all_terms(self) -> list[Term]:  # this could be a property, if you want to have a look at it, see below
        return self.left + self.right

    # @property
    # def all_terms(self) -> list[Term]:  # used without parenthesis, like an attribute. There a slides in OOP for it
    #     return self.left + self.right

    def check_input(self, test_left: list[Term], test_right: list[Term]) -> bool:
        return (
            self._check_side(self.left, test_left)
            and self._check_side(self.right, test_right)
        )

    def as_dict(self) -> dict[str, str | list[dict[str, str]]]:  # maybe a custom type? `EquationDict = dict[str, str | list[dict[str, str]]]`
        return {
            "name": self.name,
            "left": [t.as_dict() for t in self.left],
            "right": [t.as_dict() for t in self.right],
        }

    @classmethod
    def from_dict(cls, data: dict[str, str | list[dict[str, str]]]) -> Equation:  # maybe a custom type? `EquationDict = dict[str, str | list[dict[str, str]]]`
        return cls(
            data["name"],
            [Term.from_dict(elem) for elem in data["left"]],
            [Term.from_dict(elem) for elem in data["right"]],
        )

    @staticmethod
    def _check_side(self_side: list[Term], test_side: list[Term]) -> bool:
        return (  # Should be the same, please check! It is a bad habit to return an explicit Boolean in a simple if case
            len(self_side) == len(test_side)
            or all(
                [
                    self_term == test_term
                    for self_term, test_term in zip(
                        self_side, sorted(test_side, key=lambda t: t.latex_code)
                    )
                ]
            )
        )


class Term:
    """Part of an Equation."""

    def __init__(
        self, name: str, latex_code: str, sign: str = "", sprite_id: str | None = None  # "+" could be a dangerous default
    ) -> None:
        if sign not in ("+", "-"):
            raise ValueError('Invalid sign. Must be "+" (plus) or "-" (minus).')

        self.name = name
        self.sign = sign
        self.latex_code = latex_code
        # ensure unique sprite_id based on sign and latex_code if not provided
        full_latex_code = "".join([self.sign, self.latex_code])  # no f-string bc of {}  # Have you tried f-string? Shouldn't be an issue, as the value of the variables doesn't matter
        self.sprite_id = sprite_id or hashlib.sha1(full_latex_code.encode()).hexdigest()

        # check if sprite exists  # unnecessary comment
        if not self.get_sprite_path().exists():
            # create sprite
            fig, ax = plt.subplots(figsize=(1, 1), dpi=100)
            try:
                ax.text(
                    0.5,
                    0.5,
                    f"${full_latex_code}$",  # see above
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

    def __str__(self) -> str:  # see above
        return f'Term("{self.name}": {self.sign} {self.latex_code})'

    # def __str__(self) -> str:  # Why have you multiple str representations?
    #     return f"{self.sign} {self.latex_code}"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Term):
            return False
        # Currently, .name does not need to be the same
        return self.sign == other.sign and self.latex_code == other.latex_code

    def get_sprite_path(self) -> Path:
        SPRITE_DIR.mkdir(parents=True, exist_ok=True)  # git doesnt track empty`folders
        return SPRITE_DIR / f"{self.sprite_id}.png"

    def as_dict(self) -> dict[str, str | None]:
        return {
            "name": self.name,
            "sign": self.sign,
            "latex_code": self.latex_code,
            "sprite_id": self.sprite_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Term:
        return cls(
            name=data["name"],
            latex_code=data["latex_code"],
            sign=data["sign"] if "sign" in data else "+",
            sprite_id=data.get("sprite_id") if "sprite_id" in data else None,
        )

# can be removed in final solution
if __name__ == "__main__":
    # Example usage
    term1 = Term("x^2", "x^2")
    term2 = Term("yp/pi", r"\frac{yp}{\pi}", "-")
    term3 = Term("dp/dz", r"\frac{\operatorname{d} p}{\operatorname{d} z}")
    for term in (term1, term2, term3):
        print(term.get_sprite_path())
    equation1 = Equation("ExampleEquation1", [term1], [term2])
    equation2 = Equation("ExampleEquation2", [term1, term2], [term3])
    equation_set1 = EquationSet([equation1, equation2], "second equation set example")
    equation_set2 = EquationSet.from_json(JSON_DIR / "equation_set_example.json")
    print(equation_set1.equations)
    print(equation_set2.equations)
    print(equation_set1 == equation_set2)
    equation_set1.to_json()
    equation_set1_reload = EquationSet.from_json(
        JSON_DIR / "second_equation_set_example.json"
    )
    print(equation_set1 == equation_set1_reload)
