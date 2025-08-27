import json
from pathlib import Path


class EquationSet:
    """A collection of equation objects"""

    DEFAULT_NAME = "MyEquations"

    def __init__(self, equations: list["Equation"], name: str = DEFAULT_NAME) -> None:
        self.name = name
        unique_equations = []
        for equation in equations:  # uses Equation.__eq__ to check
            if equation not in unique_equations:
                unique_equations.append(equation)
        self.equations = sorted(unique_equations, key=lambda equation: equation.name)
        # TODO: are empty EquationSets allowed?

    def __repr__(self) -> str:
        eq_names = ", ".join(equation.name for equation in self.equations)
        return (
            f'EquationSet("{self.name}", containing {len(self.equations)} '
            f"equations: {eq_names})"
        )

    def __eq__(self, other: "EquationSet") -> bool:
        # Currently only works if other has the right equation names
        return self.equations == other.equations

    def add_equation(self, new_equation: "Equation") -> None:
        self.equations.append(new_equation)
        self.equations = sorted(self.equations, key=lambda equation: equation.name)

    def remove_equation(self, equation: "Equation") -> None:
        self.equations.remove(equation)
        # TODO: raise error if equation is not in set?

    def to_json(self, json_file: Path) -> None:
        # TODO: include name in JSON
        with json_file.open("w") as f:
            json.dump([equation.as_dict() for equation in self.equations], f, indent=4)

    @staticmethod
    def from_json(filepath: Path, name: str = DEFAULT_NAME) -> "EquationSet":
        # TODO: include name in JSON
        with filepath.open("r") as f:
            equations = [Equation.from_dict(elem) for elem in json.load(f)]
        return EquationSet(equations, name)


class Equation:
    """An equation with terms divided into left and right part"""

    def __init__(self, name: str, left: list["Term"], right: list["Term"]) -> None:
        self.name = name
        self.left = sorted(left, key=lambda term: term.latex_code)
        self.right = sorted(right, key=lambda term: term.latex_code)
        # TODO: check that left and right side are not empty (or default to zero-term?)

    def __repr__(self) -> str:
        left_terms = " ".join(str(term) for term in self.left)
        right_terms = " ".join(str(term) for term in self.right)
        return f'Equation("{self.name}": {left_terms} = {right_terms})'

    def __eq__(self, other: "Equation") -> bool:
        return self.left == other.left and self.right == other.right  # already sorted

    def get_all_terms(self) -> list["Term"]:
        return self.left + self.right

    def check_input(self, test_left: list["Term"], test_right: list["Term"]) -> bool:
        return self._check_side(self.left, test_left) and self._check_side(
            self.right, test_right
        )

    def as_dict(self) -> dict[str, str | list[dict[str, str]]]:
        return {
            "name": self.name,
            "left": [term.as_dict() for term in self.left],
            "right": [term.as_dict() for term in self.right],
        }

    @staticmethod
    def from_dict(data: dict[str, str | list[dict[str, str]]]) -> "Equation":
        return Equation(
            data["name"],
            [Term.from_dict(elem) for elem in data["left"]],
            [Term.from_dict(elem) for elem in data["right"]],
        )

    @staticmethod
    def _check_side(self_side: list["Term"], test_side: list["Term"]) -> bool:
        return (
            False
            if len(self_side) != len(test_side)
            else all(
                [
                    self_term == test_term
                    for self_term, test_term in zip(
                        self_side, sorted(test_side, key=lambda term: term.latex_code)
                    )
                ]
            )
        )


class Term:
    """Part of an Equation"""

    def __init__(self, name: str, latex_code: str, sign: str = "+") -> None:
        self.name = name
        if sign in ("+", "-"):
            self.sign = sign
        else:
            raise ValueError('Invalid sign. Must be "+" (plus) or "-" (minus).')
        self.latex_code = latex_code

    def __repr__(self) -> str:
        return f'Term("{self.name}": {self.sign} {self.latex_code})'

    def __str__(self) -> str:
        return f"{self.sign} {self.latex_code}"

    def __eq__(self, other: "Term") -> bool:
        # Currently, .name does not need to be the same
        return self.sign == other.sign and self.latex_code == other.latex_code

    def as_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "sign": self.sign,
            "latex_code": self.latex_code,
        }

    @staticmethod
    def from_dict(data: dict[str, str]) -> "Term":
        return Term(
            name=data["name"],
            latex_code=data["latex_code"],
            sign=data["sign"] if "sign" in data else "+",
        )
