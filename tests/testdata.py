import hashlib

from src.equatio.term import Term
from src.equatio.equation import Equation
from src.equatio.equation_set import EquationSet


# Helper function
def term_dict_add_sprite_id_for_testing(term_dict: dict[str, str]) -> dict[str, str]:
    """Add a sprite_id to a term dictionary based on its content."""
    sprite_id: str = hashlib.sha1(
        "".join([term_dict["sign"], term_dict["latex_code"]]).encode()
    ).hexdigest()
    term_dict_with_id = term_dict.copy()
    term_dict_with_id["sprite_id"] = sprite_id
    return term_dict_with_id


# TERMS
T_P1 = Term("pressure", "p", "+")
T_P1_DICT = term_dict_add_sprite_id_for_testing(
    {
        "name": "pressure",
        "latex_code": "p",
        "sign": "+",
    }
)
T_P2 = Term("more_pressure", "p", "+")
T_P2_DICT = term_dict_add_sprite_id_for_testing(
    {
        "name": "more_pressure",
        "sign": "+",
        "latex_code": "p",
    }
)
T_P3 = Term("pressure", "p", "-")
T_P3_DICT = term_dict_add_sprite_id_for_testing(
    {
        "latex_code": "p",
        "name": "pressure",
        "sign": "-",
    }
)
T_P4 = Term("less_pressure", "p", "-")
T_P4_DICT = term_dict_add_sprite_id_for_testing(
    {
        "sign": "-",
        "latex_code": "p",
        "name": "less_pressure",
    }
)
P = Term("pressure", "p", "+")
RHO_R_T = Term("density, specific gas constant, temperature", r"\rho R T", "+")
DP_DZ = Term(
    "vertical pressure gradient",
    r"\frac{\operatorname{d} p}{\operatorname{d} z}",
    "+",
)
RHO_G = Term("density, gravitational acceleration", r"\rho g", "-")
D_U = Term("total differential of inner energy", r"\operatorname{d} U", "+")
DEL_Q = Term("partial differential of heat", r"\partial Q", "+")
DEL_W = Term("partial differential of work", r"\partial W", "+")

# EQUATIONS
GAS_LAW_TERMS = [RHO_R_T, P]  # not in order of left - right
GAS_LAW = Equation("ideal gas law for meteorology", [P], [RHO_R_T])
NEXT_GAS_LAW = Equation("ideal gas law (not only) for meteorology", [P], [RHO_R_T])
GAS_LAW_DICT = {
    "name": "ideal gas law for meteorology",
    "left": [
        term_dict_add_sprite_id_for_testing(
            {"name": "pressure", "latex_code": "p", "sign": "+"}
        )
    ],
    "right": [
        term_dict_add_sprite_id_for_testing(
            {
                "name": "density, specific gas constant, temperature",
                "latex_code": r"\rho R T",
                "sign": "+",
            }
        )
    ],
}
HYDROSTATIC_TERMS = [DP_DZ, RHO_G]
HYDROSTATIC = Equation("hydrostatic equation", [DP_DZ], [RHO_G])
HYDROSTATIC_WRONG_SITES = Equation("hydrostatic equation", [RHO_G], [DP_DZ])
HYDROSTATIC_DICT = {
    "name": "hydrostatic equation",
    "left": [
        {
            "name": "vertical pressure gradient",
            "latex_code": r"\frac{\operatorname{d} p}{\operatorname{d} z}",
            "sign": "+",
        }  # no sprite_id to test if equality test will fail here as intended
    ],
    "right": [
        term_dict_add_sprite_id_for_testing(
            {
                "name": "density, gravitational acceleration",
                "latex_code": r"\rho g",
                "sign": "-",
            }
        )
    ],
}
FIRST_LAW_TERMS = [D_U, DEL_Q, DEL_W]
FIRST_LAW = Equation("first law of thermodynamics", [D_U], [DEL_Q, DEL_W])
FIRST_LAW_OTHER_ORDER = Equation("first law of thermodynamics", [D_U], [DEL_W, DEL_Q])
FIRST_LAW_DICT = {
    "name": "first law of thermodynamics",
    "left": [
        term_dict_add_sprite_id_for_testing(
            {
                "name": "total differential of inner energy",
                "latex_code": r"\operatorname{d} U",
                "sign": "+",
            }
        )
    ],
    "right": [
        term_dict_add_sprite_id_for_testing(
            {
                "name": "partial differential of work",
                "latex_code": r"\partial W",
                "sign": "+",
            }
        ),
        term_dict_add_sprite_id_for_testing(
            {
                "name": "partial differential of heat",
                "latex_code": r"\partial Q",
                "sign": "+",
            }
        ),
    ],  # other order
}

# EQUATION SETS
ONE_EQUATION_SET = EquationSet([GAS_LAW], "one equation set")
ONE_EQUATION_SET_OTHER_EQUATION_NAME = EquationSet([NEXT_GAS_LAW], "one equation set")
SAME_ONE_EQUATION_SET = EquationSet([GAS_LAW])  # with default name
OTHER_ONE_EQUATION_SET = EquationSet([FIRST_LAW], "other one equation set")
FALSE_TWO_EQUATION_SET = EquationSet(
    [FIRST_LAW, FIRST_LAW_OTHER_ORDER], "one equation set"
)  # should only yield one equation in set
VERY_BASIC_EQUATION_SET = EquationSet([GAS_LAW, HYDROSTATIC], "basic equations")
VERY_BASIC_EQUATION_SET_OTHER_WAY_ROUND = EquationSet(
    [HYDROSTATIC, GAS_LAW], "basic equations"
)
BASIC_EQUATION_SET = EquationSet([GAS_LAW, HYDROSTATIC, FIRST_LAW], "basic equations")
