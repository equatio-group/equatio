from copy import deepcopy
import json
from pathlib import Path
import pytest

from src.equatio.equation import Term, Equation, EquationSet

# Test Terms and their corresponding dictionaries
t_p1 = Term("pressure", "p", "+")
t_p1_dict = {
    "name": "pressure",
    "latex_code": "p",
    "sign": "+",
}
t_p2 = Term("more_pressure", "p", "+")
t_p2_dict = {
    "name": "more_pressure",
    # no sign to check if default works
    "latex_code": "p",
}
t_p3 = Term("pressure", "p", "-")
t_p3_dict = {
    "latex_code": "p",
    "name": "pressure",
    "sign": "-",
}
t_p4 = Term("less_pressure", "p", "-")
t_p4_dict = {
    "sign": "-",
    "latex_code": "p",
    "name": "less_pressure",
}


@pytest.mark.parametrize(
    "t1, t2, result",
    [
        (t_p1, t_p2, True),
        (t_p1, t_p3, False),
        (t_p1, t_p4, False),
        (t_p2, t_p3, False),
        (t_p2, t_p4, False),
        (t_p3, t_p4, True),
    ],
)
def test_term_equality(t1: Term, t2: Term, result: bool) -> None:
    """test equality overload for Term"""
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
    """test error handling for invalid signs in Term constructor"""
    with pytest.raises(ValueError):
        Term(name, latex_code, sign)


@pytest.mark.parametrize("t", [t_p1, t_p2, t_p3, t_p4])
def test_term_dict_cycle(t: Term) -> None:
    """test if as_dicht() and from_dict() cycle to same Term"""
    assert t == Term.from_dict(t.as_dict())


@pytest.mark.parametrize(
    "t, t_dict",
    [
        (t_p1, t_p1_dict),
        # no test for case 2 because dict does not use sign (to test for default value)
        (t_p3, t_p3_dict),
        (t_p4, t_p4_dict),
    ],
)
def test_term_as_dict(t: Term, t_dict: dict[str, str]) -> None:
    """test Term conversion to dictionary"""
    assert t.as_dict() == t_dict


@pytest.mark.parametrize(
    "t_dict, t",
    [
        (t_p1_dict, t_p1),
        (t_p2_dict, t_p2),
        (t_p3_dict, t_p3),
        (t_p4_dict, t_p4),
    ],
)
def test_term_from_dict(t_dict: dict[str, str], t: Term) -> None:
    """test Term constructor from dictionary"""
    assert t.from_dict(t_dict) == t


# Test equations and their corresponding dictionaries
# ideal gas law for meteorology
p = Term("pressure", "p", "+")
rho_R_T = Term("density, specific gas constant, temperature", r"\rho R T", "+")
gas_law_terms = [rho_R_T, p]  # not in order of left - right
gas_law = Equation("ideal gas law for meteorology", [p], [rho_R_T])
next_gas_law = Equation("ideal gas law (not only) for meteorology", [p], [rho_R_T])
gas_law_dict = {
    "name": "ideal gas law for meteorology",
    "left": [{"name": "pressure", "latex_code": "p", "sign": "+"}],
    "right": [
        {
            "name": "density, specific gas constant, temperature",
            "latex_code": r"\rho R T",
            "sign": "+",
        }
    ],
}
# hydrostatic equation
dp_dz = Term(
    "vertical pressure gradient",
    r"\frac{\operatorname{d} p}{\operatorname{d} z}",
    "+",
)
rho_g = Term("density, gravitational acceleration", r"\rho g", "-")
hydrostatic_terms = [dp_dz, rho_g]
hydrostatic = Equation("hydrostatic equation", [dp_dz], [rho_g])
hydrostatic_wrong_sides = Equation("hydrostatic equation", [rho_g], [dp_dz])
hydrostatic_dict = {
    "name": "hydrostatic equation",
    "left": [
        {
            "name": "vertical pressure gradient",
            "latex_code": r"\frac{\operatorname{d} p}{\operatorname{d} z}",
        }
    ],  # sign should default to "+"
    "right": [
        {"name": "density, gravitational acceleration", "latex_code": r"\rho g", "sign": "-"}
    ],
}
# first law of thermodynamics
dU = Term("total differential of inner energy", r"\operatorname{d} U", "+")
delQ = Term("partial differential of heat", r"\partial Q", "+")
delW = Term("partial differential of work", r"\partial W", "+")
first_law_terms = [dU, delQ, delW]
first_law = Equation("first law of thermodynamics", [dU], [delQ, delW])
first_law_other_order = Equation("first law of thermodynamics", [dU], [delW, delQ])
first_law_dict = {
    "name": "first law of thermodynamics",
    "left": [
        {
            "name": "total differential of inner energy",
            "latex_code": r"\operatorname{d} U",
            "sign": "+",
        }
    ],
    "right": [
        {"name": "partial differential of work", "latex_code": r"\partial W", "sign": "+"},
        {"name": "partial differential of heat", "latex_code": r"\partial Q", "sign": "+"},
    ],  # other order
}


@pytest.mark.parametrize(
    "e1, e2, result",
    [
        (gas_law, next_gas_law, True),
        (hydrostatic, hydrostatic_wrong_sides, False),  # wrong sides
        (
            first_law,
            first_law_other_order,
            True,
        ),  # other order within sides should not matter
    ],
)
def test_equation_equality(e1: Equation, e2: Equation, result: bool) -> None:
    assert result == (e1 == e2)


@pytest.mark.parametrize(
    "e, terms, result",
    [
        (gas_law, gas_law_terms, True),
        (hydrostatic, hydrostatic_terms, True),
        (first_law, first_law_terms, True),
        (gas_law, hydrostatic_terms, False),
        (hydrostatic, first_law_terms, False),
        (first_law, gas_law_terms, False),
    ],
)
def test_equation_get_items(e: Equation, terms: list[Term], result: bool) -> None:
    assert result == (
        sorted(e.get_all_terms(), key=lambda term: term.latex_code)
        == sorted(terms, key=lambda term: term.latex_code)
    )


@pytest.mark.parametrize(
    "e, left_test, right_test, result",
    [
        (gas_law, gas_law_terms[0:1], gas_law_terms[1:2], False),
        (gas_law, gas_law_terms[1:2], gas_law_terms[0:1], True),
        (gas_law, gas_law_terms, hydrostatic_terms, False),
        (hydrostatic, hydrostatic_terms[0:1], hydrostatic_terms[1:2], True),
        (
            hydrostatic_wrong_sides,
            hydrostatic_terms[0:1],
            hydrostatic_terms[1:2],
            False,
        ),
        (hydrostatic_wrong_sides, hydrostatic_terms[1:2], hydrostatic_terms[0:1], True),
        (first_law, first_law_terms[0:1], first_law_terms[1:2], False),
        (first_law, first_law_terms[0:1], first_law_terms[1:3], True),
        (first_law_other_order, first_law_terms[0:1], first_law_terms[1:3], True),
    ],
)
def test_equation_check_input(
    e: Equation, left_test: list[Term], right_test: list[Term], result: bool
) -> None:
    assert result == e.check_input(left_test, right_test)


@pytest.mark.parametrize(
    "e",
    [gas_law, hydrostatic, hydrostatic_wrong_sides, first_law, first_law_other_order],
)
def test_eqation_dict_cycle(e: Equation) -> None:
    assert e == Equation.from_dict(e.as_dict())


@pytest.mark.parametrize(
    "e, e_dict, result",
    [
        (gas_law, gas_law_dict, True),
        (gas_law, hydrostatic_dict, False),
        (hydrostatic, hydrostatic_dict, False),  # sign is missing in hydrostatic_dict
        (hydrostatic_wrong_sides, hydrostatic_dict, False),
        (
            first_law,
            first_law_dict,
            False,
        ),  # other (alphabetically wrong) order in dict
        (
            first_law_other_order,
            first_law_dict,
            False,
        ),  # same here although order in constructor and dict are the same (gets sorted during construction)
    ],
)
def test_equation_as_dict(e: Equation, e_dict: dict, result: bool) -> None:
    assert result == (e.as_dict() == e_dict)


@pytest.mark.parametrize(
    "e_dict, e, result",
    [
        (gas_law_dict, gas_law, True),
        (gas_law_dict, hydrostatic, False),
        (hydrostatic_dict, hydrostatic, True),  # missing sign should be added
        (hydrostatic_dict, hydrostatic_wrong_sides, False),
        (first_law_dict, first_law, True),  # other order in dict shoud work fine
        (first_law_dict, first_law_other_order, True),
    ],
)
def test_equation_from_dict(e_dict: dict, e: Equation, result: bool) -> None:
    assert result == (Equation.from_dict(e_dict) == e)


# Test EquationSets
one_equation_set = EquationSet([gas_law], "one term set")
same_one_equation_set = EquationSet([gas_law])  # with default name
other_one_equation_set = EquationSet([first_law], "other one term set")
false_two_equation_set = EquationSet(
    [first_law, first_law_other_order], "one term set"
)  # should only yield one equation in set
very_basic_equation_set = EquationSet([gas_law, hydrostatic], "basic equations")
very_basic_equation_set_other_way_round = EquationSet(
    [hydrostatic, gas_law], "basic equations"
)
basic_equation_set = EquationSet([gas_law, hydrostatic, first_law], "basic equations")


@pytest.mark.parametrize(
    "es1, es2, result",
    [
        (one_equation_set, one_equation_set, True),
        (one_equation_set, same_one_equation_set, True),
        (other_one_equation_set, false_two_equation_set, True),
        (one_equation_set, other_one_equation_set, False),
        (very_basic_equation_set, very_basic_equation_set_other_way_round, True),
        (very_basic_equation_set, basic_equation_set, False),
    ],
)
def test_equation_set_equality(
    es1: EquationSet, es2: EquationSet, result: bool
) -> None:
    assert result == (es1 == es2)


@pytest.mark.parametrize(
    "es, e",
    [
        (one_equation_set, hydrostatic),
        (very_basic_equation_set, first_law),
        (basic_equation_set, hydrostatic_wrong_sides),
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
        (one_equation_set, gas_law),
        (very_basic_equation_set, hydrostatic),
        (basic_equation_set, first_law),
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
        (very_basic_equation_set, hydrostatic, one_equation_set),
        (basic_equation_set, first_law, very_basic_equation_set),
        (basic_equation_set, first_law, very_basic_equation_set_other_way_round),
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
        (one_equation_set, hydrostatic, very_basic_equation_set),
        (very_basic_equation_set, first_law, basic_equation_set),
        (very_basic_equation_set_other_way_round, first_law, basic_equation_set),
    ],
)
def test_equation_set_add(
    es: EquationSet, e_to_add: Equation, es_new: EquationSet
) -> None:
    es_added: EquationSet = deepcopy(es)
    es_added.add_equation(e_to_add)
    assert es_added == es_new


# Test JSON import/export
@pytest.fixture(params=[one_equation_set, very_basic_equation_set, basic_equation_set])
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
    #TODO: add name test after implementation of JSON name storing in equation.py
    for i, eq in enumerate(equation_set.equations):
        for j, term in enumerate(eq.left):
            assert test_data[i]["left"][j] == term.as_dict()
        for j, term in enumerate(eq.right):
            assert test_data[i]["right"][j] == term.as_dict()


def test_equation_set_from_json_manual(tmp_path):
    file = tmp_path / "eq.json"
    test_eq1_dict: dict[str, str | list[dict[str, str]]] = {
        "name": "eq1",
        "left": [{"name": "a", "sign": "+", "latex_code": "a"}],
        "right": [{"name": "b", "sign": "-", "latex_code": "b"}],
    }
    test_eq2_dict: dict[str, str | list[dict[str, str]]] = {
        "name": "eq2",
        "left": [
            {"name": "c", "sign": "+", "latex_code": "c"},
            {"name": "d", "sign": "-", "latex_code": "d"},
        ],
        "right": [{"name": "e", "sign": "+", "latex_code": "e"}],
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
