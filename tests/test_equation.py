from copy import deepcopy
import hashlib
import json
from pathlib import Path
import pytest

from src.equatio.equation import Term, Equation, EquationSet


def term_dict_add_sprite_id_for_testing(term_dict: dict[str, str]) -> dict[str, str]:
    """Add a sprite_id to a term dictionary based on its content."""
    sprite_id: str = hashlib.sha1("".join([term_dict["sign"], term_dict["latex_code"]]).encode()).hexdigest()
    term_dict_with_id = term_dict.copy()
    term_dict_with_id["sprite_id"] = sprite_id
    return term_dict_with_id


# Test Terms and their corresponding dictionaries
T_P1 = Term("pressure", "p", "+")
T_P1_DICT = term_dict_add_sprite_id_for_testing({
    "name": "pressure",
    "latex_code": "p",
    "sign": "+",
})
T_P2 = Term("more_pressure", "p", "+")
T_P2_DICT = term_dict_add_sprite_id_for_testing({
    "name": "more_pressure",
    "sign": "+",
    "latex_code": "p",
})
T_P3 = Term("pressure", "p", "-")
T_P3_DICT = term_dict_add_sprite_id_for_testing({
    "latex_code": "p",
    "name": "pressure",
    "sign": "-",
})
T_P4 = Term("less_pressure", "p", "-")
T_P4_DICT = term_dict_add_sprite_id_for_testing({
    "sign": "-",
    "latex_code": "p",
    "name": "less_pressure",
})

@pytest.mark.parametrize(
    "t1, t2, result",
    [
        (T_P1, T_P2, True),
        (T_P1, T_P3, False),
        (T_P1, T_P4, False),
        (T_P2, T_P3, False),
        (T_P2, T_P4, False),
        (T_P3, T_P4, True),
    ],
)
def test_term_equality(t1: Term, t2: Term, result: bool) -> None:
    """Test equality overload for Term."""
    assert result == (t1 == t2)


@pytest.mark.parametrize(
    "name, latex_code, sign",
    [
        ("invalid_pressure", "p", "*"),
        ("invalid_pressure", "p", "1"),
        ("invalid_pressure", "p", "a"),
    ],
)
def test_term_invalid_sign_handling(name: str, latex_code: str, sign: str) -> None:
    """Test error handling for invalid signs in Term constructor."""
    with pytest.raises(ValueError):
        Term(name, latex_code, sign)


@pytest.mark.parametrize("t", [T_P1, T_P2, T_P3, T_P4])
def test_term_dict_cycle(t: Term) -> None:
    """Test if as_dicht() and from_dict() cycle to same Term."""
    assert t == Term.from_dict(t.as_dict())


@pytest.mark.parametrize(
    "t, t_dict",
    [
        (T_P1, T_P1_DICT),
        # no test for case 2 because dict does not use sign (to test for default value)
        (T_P3, T_P3_DICT),
        (T_P4, T_P4_DICT),
    ],
)
def test_term_as_dict(t: Term, t_dict: dict[str, str]) -> None:
    """Test Term conversion to dictionary."""
    assert t.as_dict() == t_dict


@pytest.mark.parametrize(
    "t_dict, t",
    [
        (T_P1_DICT, T_P1),
        (T_P2_DICT, T_P2),
        (T_P3_DICT, T_P3),
        (T_P4_DICT, T_P4),
    ],
)
def test_term_from_dict(t_dict: dict[str, str], t: Term) -> None:
    """Test Term constructor from dictionary."""
    assert t.from_dict(t_dict) == t


# Test equations and their corresponding dictionaries
# ideal gas law for meteorology
P = Term("pressure", "p", "+")
RHO_R_T = Term("density, specific gas constant, temperature", r"\rho R T", "+")
GAS_LAW_TERMS = [RHO_R_T, P]  # not in order of left - right
GAS_LAW = Equation("ideal gas law for meteorology", [P], [RHO_R_T])
NEXT_GAS_LAW = Equation("ideal gas law (not only) for meteorology", [P], [RHO_R_T])
GAS_LAW_DICT = {
    "name": "ideal gas law for meteorology",
    "left": [term_dict_add_sprite_id_for_testing({"name": "pressure", "latex_code": "p", "sign": "+"})],
    "right": [term_dict_add_sprite_id_for_testing(
        {
            "name": "density, specific gas constant, temperature",
            "latex_code": r"\rho R T",
            "sign": "+",
        })
    ],
}
# hydrostatic equation
DP_DZ = Term(
    "vertical pressure gradient",
    r"\frac{\operatorname{d} p}{\operatorname{d} z}",
    "+",
)
RHO_G = Term("density, gravitational acceleration", r"\rho g", "-")
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
    "right": [term_dict_add_sprite_id_for_testing(
        {
            "name": "density, gravitational acceleration",
            "latex_code": r"\rho g",
            "sign": "-",
        })
    ],
}
# first law of thermodynamics
D_U = Term("total differential of inner energy", r"\operatorname{d} U", "+")
DEL_Q = Term("partial differential of heat", r"\partial Q", "+")
DEL_W = Term("partial differential of work", r"\partial W", "+")
FIRST_LAW_TERMS = [D_U, DEL_Q, DEL_W]
FIRST_LAW = Equation("first law of thermodynamics", [D_U], [DEL_Q, DEL_W])
FIRST_LAW_OTHER_ORDER = Equation("first law of thermodynamics", [D_U], [DEL_W, DEL_Q])
FIRST_LAW_DICT = {
    "name": "first law of thermodynamics",
    "left": [term_dict_add_sprite_id_for_testing(
        {
            "name": "total differential of inner energy",
            "latex_code": r"\operatorname{d} U",
            "sign": "+",
        })
    ],
    "right": [term_dict_add_sprite_id_for_testing(
        {
            "name": "partial differential of work",
            "latex_code": r"\partial W",
            "sign": "+",
        }), term_dict_add_sprite_id_for_testing(
        {
            "name": "partial differential of heat",
            "latex_code": r"\partial Q",
            "sign": "+",
        }),
    ],  # other order
}


@pytest.mark.parametrize(
    "e1, e2, result",
    [
        (GAS_LAW, NEXT_GAS_LAW, True),
        (HYDROSTATIC, HYDROSTATIC_WRONG_SITES, False),  # wrong sides
        (
                FIRST_LAW,
                FIRST_LAW_OTHER_ORDER,
                True,
        ),  # other order within sides should not matter
    ],
)
def test_equation_equality(e1: Equation, e2: Equation, result: bool) -> None:
    assert result == (e1 == e2)


@pytest.mark.parametrize(
    "e, terms, result",
    [
        (GAS_LAW, GAS_LAW_TERMS, True),
        (HYDROSTATIC, HYDROSTATIC_TERMS, True),
        (FIRST_LAW, FIRST_LAW_TERMS, True),
        (GAS_LAW, HYDROSTATIC_TERMS, False),
        (HYDROSTATIC, FIRST_LAW_TERMS, False),
        (FIRST_LAW, GAS_LAW_TERMS, False),
    ],
)
def test_equation_get_items(e: Equation, terms: list[Term], result: bool) -> None:
    assert result == (
        sorted(e.all_terms, key=lambda term: term.latex_code)
        == sorted(terms, key=lambda term: term.latex_code)
    )


@pytest.mark.parametrize(
    "e, left_test, right_test, result",
    [
        (GAS_LAW, GAS_LAW_TERMS[0:1], GAS_LAW_TERMS[1:2], False),
        (GAS_LAW, GAS_LAW_TERMS[1:2], GAS_LAW_TERMS[0:1], True),
        (GAS_LAW, GAS_LAW_TERMS, HYDROSTATIC_TERMS, False),
        (HYDROSTATIC, HYDROSTATIC_TERMS[0:1], HYDROSTATIC_TERMS[1:2], True),
        (
                HYDROSTATIC_WRONG_SITES,
                HYDROSTATIC_TERMS[0:1],
                HYDROSTATIC_TERMS[1:2],
                False,
        ),
        (HYDROSTATIC_WRONG_SITES, HYDROSTATIC_TERMS[1:2], HYDROSTATIC_TERMS[0:1], True),
        (FIRST_LAW, FIRST_LAW_TERMS[0:1], FIRST_LAW_TERMS[1:2], False),
        (FIRST_LAW, FIRST_LAW_TERMS[0:1], FIRST_LAW_TERMS[1:3], True),
        (FIRST_LAW_OTHER_ORDER, FIRST_LAW_TERMS[0:1], FIRST_LAW_TERMS[1:3], True),
    ],
)
def test_equation_check_input(
    e: Equation, left_test: list[Term], right_test: list[Term], result: bool
) -> None:
    assert result == e.check_input(left_test, right_test)


@pytest.mark.parametrize(
    "e",
    [GAS_LAW, HYDROSTATIC, HYDROSTATIC_WRONG_SITES, FIRST_LAW, FIRST_LAW_OTHER_ORDER],
)
def test_equation_dict_cycle(e: Equation) -> None:
    assert e == Equation.from_dict(e.as_dict())


@pytest.mark.parametrize(
    "e, e_dict, result",
    [
        (GAS_LAW, GAS_LAW_DICT, True),
        (GAS_LAW, HYDROSTATIC_DICT, False),
        (HYDROSTATIC, HYDROSTATIC_DICT, False),  # one sprite_id will default to None in hydrostatic_dict
        (HYDROSTATIC_WRONG_SITES, HYDROSTATIC_DICT, False),
        (
                FIRST_LAW,
                FIRST_LAW_DICT,
                False,
        ),  # other (alphabetically wrong) order in dict
        (
                FIRST_LAW_OTHER_ORDER,
                FIRST_LAW_DICT,
                False,
        ),  # same here although order in constructor and dict are the same (gets sorted during construction)
    ],
)
def test_equation_as_dict(e: Equation, e_dict: dict, result: bool) -> None:
    assert result == (e.as_dict() == e_dict)


@pytest.mark.parametrize(
    "e_dict, e, result",
    [
        (GAS_LAW_DICT, GAS_LAW, True),
        (GAS_LAW_DICT, HYDROSTATIC, False),
        (HYDROSTATIC_DICT, HYDROSTATIC, True),  # missing sign should be added
        (HYDROSTATIC_DICT, HYDROSTATIC_WRONG_SITES, False),
        (FIRST_LAW_DICT, FIRST_LAW, True),  # other order in dict should work fine
        (FIRST_LAW_DICT, FIRST_LAW_OTHER_ORDER, True),
    ],
)
def test_equation_from_dict(e_dict: dict, e: Equation, result: bool) -> None:
    assert result == (Equation.from_dict(e_dict) == e)


# Test EquationSets
ONE_EQUATION_SET = EquationSet([GAS_LAW], "one term set")
SAME_ONE_EQUATION_SET = EquationSet([GAS_LAW])  # with default name
OTHER_ONE_EQUATION_SET = EquationSet([FIRST_LAW], "other one term set")
FALSE_TWO_EQUATION_SET = EquationSet(
    [FIRST_LAW, FIRST_LAW_OTHER_ORDER], "one term set"
)  # should only yield one equation in set
VERY_BASIC_EQUATION_SET = EquationSet([GAS_LAW, HYDROSTATIC], "basic equations")
VERY_BASIC_EQUATION_SET_OTHER_WAY_ROUND = EquationSet(
    [HYDROSTATIC, GAS_LAW], "basic equations"
)
BASIC_EQUATION_SET = EquationSet([GAS_LAW, HYDROSTATIC, FIRST_LAW], "basic equations")


@pytest.mark.parametrize(
    "es1, es2, result",
    [
        (ONE_EQUATION_SET, ONE_EQUATION_SET, True),
        (ONE_EQUATION_SET, SAME_ONE_EQUATION_SET, True),
        (OTHER_ONE_EQUATION_SET, FALSE_TWO_EQUATION_SET, True),
        (ONE_EQUATION_SET, OTHER_ONE_EQUATION_SET, False),
        (VERY_BASIC_EQUATION_SET, VERY_BASIC_EQUATION_SET_OTHER_WAY_ROUND, True),
        (VERY_BASIC_EQUATION_SET, BASIC_EQUATION_SET, False),
    ],
)
def test_equation_set_equality(
    es1: EquationSet, es2: EquationSet, result: bool
) -> None:
    assert result == (es1 == es2)


@pytest.mark.parametrize(
    "es, e",
    [
        (ONE_EQUATION_SET, HYDROSTATIC),
        (VERY_BASIC_EQUATION_SET, FIRST_LAW),
        (BASIC_EQUATION_SET, HYDROSTATIC_WRONG_SITES),
    ],
)
def test_equation_set_add_remove_cycle(es: EquationSet, e: Equation) -> None:
    new_es: EquationSet = deepcopy(es)
    new_es.add_equation(e)
    new_es.remove_equation(e)
    assert es == new_es


@pytest.mark.parametrize(
    "es, e",
    [
        (ONE_EQUATION_SET, GAS_LAW),
        (VERY_BASIC_EQUATION_SET, HYDROSTATIC),
        (BASIC_EQUATION_SET, FIRST_LAW),
    ],
)
def test_equation_set_remove_add_cycle(es: EquationSet, e: Equation) -> None:
    new_es: EquationSet = deepcopy(es)
    new_es.remove_equation(e)
    new_es.add_equation(e)
    assert es == new_es


@pytest.mark.parametrize(
    "es, e_to_remove, es_new",
    [
        (VERY_BASIC_EQUATION_SET, HYDROSTATIC, ONE_EQUATION_SET),
        (BASIC_EQUATION_SET, FIRST_LAW, VERY_BASIC_EQUATION_SET),
        (BASIC_EQUATION_SET, FIRST_LAW, VERY_BASIC_EQUATION_SET_OTHER_WAY_ROUND),
    ],
)
def test_equation_set_remove(
    es: EquationSet, e_to_remove: Equation, es_new: EquationSet
) -> None:
    es_removed: EquationSet = deepcopy(es)
    es_removed.remove_equation(e_to_remove)
    assert es_removed == es_new


@pytest.mark.parametrize(
    "es, e_to_add, es_new",
    [
        (ONE_EQUATION_SET, HYDROSTATIC, VERY_BASIC_EQUATION_SET),
        (VERY_BASIC_EQUATION_SET, FIRST_LAW, BASIC_EQUATION_SET),
        (VERY_BASIC_EQUATION_SET_OTHER_WAY_ROUND, FIRST_LAW, BASIC_EQUATION_SET),
    ],
)
def test_equation_set_add(
    es: EquationSet, e_to_add: Equation, es_new: EquationSet
) -> None:
    es_added: EquationSet = deepcopy(es)
    es_added.add_equation(e_to_add)
    assert es_added == es_new


# Test JSON import/export
@pytest.fixture(params=[ONE_EQUATION_SET, VERY_BASIC_EQUATION_SET, BASIC_EQUATION_SET])
def equation_set(request) -> EquationSet:
    return request.param


def test_equation_set_json_cycle(equation_set: EquationSet, tmp_path: Path) -> None:
    # tmp_path is a pytest built-in fixture providing a temp directory for file tests
    # export
    out_path = tmp_path / f"{equation_set.name.replace(' ', '_')}.json"
    equation_set.to_json(out_path)
    # import
    es_in = EquationSet.from_json(out_path)
    assert equation_set == es_in


def test_equation_set_to_json(equation_set: EquationSet, tmp_path: Path) -> None:
    out_path = tmp_path / "eq.json"
    equation_set.to_json(out_path)
    test_data = json.loads(out_path.read_text())

    assert isinstance(test_data, list)
    for i, eq in enumerate(equation_set.equations):
        for j, term in enumerate(eq.left):
            assert test_data[i]["left"][j] == term.as_dict()
        for j, term in enumerate(eq.right):
            assert test_data[i]["right"][j] == term.as_dict()


def test_equation_set_from_json_manual(tmp_path):
    file = tmp_path / "eq.json"
    test_eq1_dict: dict[str, str | list[dict[str, str]]] = {
        "name": "eq1",
        "left": [term_dict_add_sprite_id_for_testing({"name": "a", "sign": "+", "latex_code": "a"})],
        "right": [term_dict_add_sprite_id_for_testing({"name": "b", "sign": "-", "latex_code": "b"})],
    }
    test_eq2_dict: dict[str, str | list[dict[str, str]]] = {
        "name": "eq2",
        "left": [
            term_dict_add_sprite_id_for_testing({"name": "c", "sign": "+", "latex_code": "c"}),
            term_dict_add_sprite_id_for_testing({"name": "d", "sign": "-", "latex_code": "d"}),
        ],
        "right": [term_dict_add_sprite_id_for_testing({"name": "e", "sign": "+", "latex_code": "e"})],
    }
    file.write_text(
        json.dumps(
            [
                test_eq1_dict,
                test_eq2_dict,
            ],
            indent=4,
        )
    )

    es = EquationSet.from_json(file)

    assert len(es.equations) == 2
    assert es.name == "eq"  # from filename without .json
    for eq, eq_dict in zip(es.equations, [test_eq1_dict, test_eq2_dict]):
        assert eq.as_dict() == eq_dict
        assert eq.name == eq_dict["name"]
        assert eq.left == [Term.from_dict(t) for t in eq_dict["left"]]
        assert eq.right == [Term.from_dict(t) for t in eq_dict["right"]]
