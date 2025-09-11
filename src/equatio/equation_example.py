from equation import Equation
from term import Term
from equation_set import EquationSet
from pathlib import Path

_DATA_DIR = Path(__file__).parents[2]
JSON_DIR = _DATA_DIR / "data"


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
    EQUATION_SET_FROM_JSON = EquationSet.from_json(
        JSON_DIR / "equation_set_example.json"
    )
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

    #Testing add and remove methods
    NEWTERM1 = Term("\\tau_w","\\frac{\\tau_w}{\\rho}","+")
    NEWTERM2 = Term("U_*^2","U_*^2","+")
    print(EQUATION_1.__str__())
    print(isinstance(NEWTERM1, Term))
    EQUATION_1.add_left(NEWTERM1)
    EQUATION_1.add_right(NEWTERM2)
    print(EQUATION_1.__str__())

    EQUATION_1.remove_left(NEWTERM1)
    #EQUATION_1.remove_left(NEWTERM2)
    EQUATION_1.remove_right(NEWTERM2)
    print(EQUATION_1.__str__())
