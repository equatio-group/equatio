from __future__ import annotations
import itertools
import json
from pathlib import Path
from typing import Any

from src.equatio.equation import Equation
from src.equatio.term import Term


_DATA_DIR = Path(__file__).parents[2]
JSON_DIR = _DATA_DIR / "data"
SPRITE_DIR = _DATA_DIR / "sprites"

# Default name constant
_DEFAULT_SET_NAME = "MyEquations"

class EquationSet:
    """A collection of equation objects."""

    def __init__(
        self, equations: list[Equation], name: str = _DEFAULT_SET_NAME
    ) -> None:
        """Initialise with list of Equation objects and optional name.
        Only unique equations are kept, sorted by name."""
        self.name = name
        unique_equations = []
        for equation in equations:  # uses Equation.__eq__ to check
            if equation not in unique_equations:
                unique_equations.append(equation)
        self.equations = sorted(unique_equations, key=lambda equ: equ.name)

    def __str__(self) -> str:
        """String representation of the set, listing all equations as item list."""
        eq_strings = "\n".join(f" - {equ}" for equ in self.equations)
        return (
            f'Equation set "{self.name}" with {len(self.equations)} equations:\n'
            f"{eq_strings}"
        )

    def __eq__(self, other: Any) -> bool:
        """Check equality with another EquationSet based on contained equations
        but not their names."""
        if not isinstance(other, EquationSet):
            return False
        return self.equations == other.equations  # equation name could be different

    def __contains__(self, equation: Any) -> bool:
        """Check if an equation is in the set (like `if equation in equation_set: ...`).
        Equation name does not matter."""
        if not isinstance(equation, Equation):
            return False
        return equation in self.equations

    def add_equation(self, new_equation: Equation) -> None:
        """Add a new equation to the set if not already present, keeping the list
        sorted by name."""
        if not isinstance(new_equation, Equation):
            raise ValueError("Only Equation objects can be added to the set.")
        if new_equation not in self.equations:
            self.equations.append(new_equation)
            self.equations = sorted(self.equations, key=lambda equation: equation.name)

    def remove_equation(self, equation: Equation) -> None:
        """Remove an equation from the set. Raises ValueError if the equation is
        not found."""
        if equation in self.equations:
            self.equations.remove(equation)
        else:
            raise ValueError("Equation not found in the set.")

    @property
    def all_terms(self) -> list[Term]:
        """Property to get all terms from all equations in the set.
        Usage without brackets like `equation_set.all_terms`."""
        return list(
            itertools.chain.from_iterable(
                equation.all_terms for equation in self.equations
            )
        )

    def to_json(self, json_path: Path | None = None) -> None:
        """Save the equation set to a JSON file. If no path is provided,
        saves to JSON_DIR with the set name."""
        json_path = json_path or JSON_DIR / f"{self.name.replace(' ', '_')}.json"
        with json_path.open("w") as f:
            json.dump(
                [equation.as_dict() for equation in self.equations], f, indent=4
            )  # match python indentation for easier editing of JSON with Python IDE

    @classmethod
    def from_json(cls, file_path: Path, name: str | None = None) -> EquationSet:
        """Load an equation set from a JSON file. Optionally provide a name,
        otherwise use the file stem."""
        name = name or file_path.stem.replace("_", " ")
        with file_path.open("r") as f:
            equations = [Equation.from_dict(elem) for elem in json.load(f)]
        return cls(equations, name)
