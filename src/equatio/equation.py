import json
from pathlib import Path


class EquationSet:
    """A collection of equation objects"""

    DEFAULT_NAME = "MyEquations"

    def __init__(self, equations: list["Equation"], name: str = DEFAULT_NAME) -> None:
        self.name = name
        self.equations = sorted(equations, key=lambda equation: equation.name)

    def __repr__(self) -> str:
        return (f"EquationSet(\"{self.name}\", "
                + f"containing {len(self.equations)} equations: "
                + ", ".join(equation.name for equation in self.equations)
                + ")"
                )

    def __eq__(self, other: "EquationSet") -> bool:
        # Currently only works if other has the right equation names
        return self.equations == other.equations

    def add_equation(self, new_equation: "Equation") -> None:
        self.equations.append(new_equation)
        self.equations = sorted(self.equations, key=lambda equation: equation.name)

    def remove_equation(self, equation: "Equation") -> None:
        self.equations.remove(equation)

    def to_json(self, json_file: Path) -> None:
        with json_file.open("w") as f:
            json.dump([equation.as_dict() for equation in self.equations], f, indent=4)

    @staticmethod
    def from_json(filename: str, name:str = DEFAULT_NAME) -> "EquationSet":
        with open(filename, "r") as f:
            equations = json.load(f)
        return EquationSet(equations, name)


class Equation:
    """An equation with terms divided into left and right part"""

    def __init__(self, name: str, left: list["Term"], right: list["Term"]) -> None:
        self.name = name
        self.left = sorted(left, key=lambda term: term.value)
        self.right = sorted(right, key=lambda term: term.value)

    def __repr__(self) -> str:
        return (f"Equation(\"{self.name}\": "
                + " ".join(str(term) for term in self.left)
                + " = "
                + " ".join(str(term) for term in self.right)
                + ")"
                )

    def get_all_terms(self) -> list["Term"]:
        return self.left + self.right

    def check_input(self, test_left: list["Term"], test_right: list["Term"]) -> bool:
        return (
                self._check_side(self.left, test_left)
                and self._check_side(self.right, test_right)
        )

    def as_dict(self) -> dict:
        return{
            "name": self.name,
            "left": [term.as_dict() for term in self.left],
            "right": [term.as_dict() for term in self.right],
        }

    @staticmethod
    def _check_side(self_side: list["Term"], test_side: list["Term"]) -> bool:
        return all(
            [
                self_term == test_term
                for self_term, test_term in zip(
                self_side, sorted(test_side, key=lambda term: term.value)
            )
            ]
        )


class Term:
    """Part of an Equation"""

    def __init__(self, name: str, value: str, sign: str = "+") -> None:
        self.name = name
        if sign in ("+", "-"):
            self.sign = sign
        else:
            raise ValueError("Invalid sign. Must be \"+\" (plus) or \"-\" (minus).")
        self.value = value

    def __repr__(self) -> str:
        return f"Term(\"{self.name}\": {self.sign} {self.value})"

    def __str__(self) -> str:
        return f"{self.sign} {self.value}"

    def __eq__(self, other: "Term") -> bool:
        # Currently, .name does not need to be the same
        return self.sign == other.sign and self.value == other.value

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "sign": self.sign,
            "value": self.value,
        }

    @staticmethod
    def from_dict(data: dict) -> "Term":
        return Term(
            name=data["name"],
            value=data["value"],
            sign=data["sign"],
        )


# just for testing and as example
if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).resolve().parents[2]
    JSON_TEST_PATH = PROJECT_ROOT / "data" / "equations.json"
    p = Term("pressure",
             "p",
             "+")
    rho_R_T = Term(
        "density, specific gas constant, temperature",
        r"\rho R T",
        "+")
    ideal_gas_law_meteo = Equation(
        "ideal gas law for meteorology",
        [p],
        [rho_R_T])
    dp_dz = Term(
        "vertical pressure gradient",
        r"\frac{\operatorname{d} p}{\operatorname{d} z",
        "+")
    rho_g = Term(
        "density, gravitational acceleration",
        r"\rho g",
        "-")
    hydrostatic_equation = Equation(
        "hydrostatic equation",
        [dp_dz],
        [rho_g])
    dU = Term(
        "total differential of inner energy",
        r"\operatorname{d} U",
        "+")
    delQ = Term(
        "partial differential of heat",
        r"\partial Q",
        "+")
    delW = Term(
        "partial differential of work",
        r"\partial W",
        "+")
    first_law = Equation(
        "first law of thermodynamics",
        [dU],
        [delQ, delW])
    my_equations = EquationSet([ideal_gas_law_meteo, hydrostatic_equation, first_law])
    print(my_equations)
    for eq in my_equations.equations:
        print(eq)
    my_equations.to_json(JSON_TEST_PATH)
    with JSON_TEST_PATH.open("r") as file:
        json_data = json.load(file)
        print(json_data)
