from pickle import FALSE

import pytest

from src.equatio.equation import Term, Equation

# Test Terms and their corresponding dictionaries
t_p1 = Term("pressure", "p", "+")
t_p1_dict = {
    "name": "pressure",
    "value": "p",
    "sign": "+",
}
t_p2 = Term("more_pressure", "p", "+")
t_p2_dict = {
    "name": "more_pressure",
    # no sign to check if default works
    "value": "p",
}
t_p3 = Term("pressure", "p", "-")
t_p3_dict = {
    "value": "p",
    "name": "pressure",
    "sign": "-",
}
t_p4 = Term("less_pressure", "p", "-")
t_p4_dict = {
    "sign": "-",
    "value": "p",
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
    "name, value, sign",
    [
        ("invalid_pressure", "p", "*"),
        ("invalid_pressure", "p", "1"),
        ("invalid_pressure", "p", "a"),
    ],
)
def test_term_invalid_sign_handling(name: str, value: str, sign: str) -> None:
    """test error handling for invalid signs in Term constructor"""
    with pytest.raises(ValueError):
        Term(name, value, sign)


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


# Test equations
# ideal gas law for meteorology
p = Term("pressure", "p", "+")
rho_R_T = Term("density, specific gas constant, temperature", r"\rho R T", "+")
gas_law_terms = [rho_R_T, p]  # not in order of left - right
gas_law = Equation("ideal gas law for meteorology", [p], [rho_R_T])
next_gas_law = Equation("ideal gas law (not only) for meteorology", [p], [rho_R_T])
gas_law_dict = {
    "name": "ideal gas law for meteorology",
    "left": [{"name": "pressure", "value": "p", "sign": "+"}],
    "right": [{"name": "density, specific gas constant, temperature", "value": r"\rho R T", "sign": "+"}],
}
# hydrostatic equation
dp_dz = Term(
    "vertical pressure gradient",
    r"\frac{\operatorname{d} p}{\operatorname{d} z",
    "+",
)
rho_g = Term("density, gravitational acceleration", r"\rho g", "-")
hydrostatic_terms = [dp_dz, rho_g]
hydrostatic = Equation("hydrostatic equation", [dp_dz], [rho_g])
hydrostatic_wrong_sides = Equation("hydrostatic equation",[rho_g],[dp_dz])
hydrostatic_dict = {
    "name": "hydrostatic equation",
    "left": [{"name": "vertical pressure gradient", "value": r"\frac{\operatorname{d} p}{\operatorname{d} z"}],  # sign should default to "+"
    "right": [{"name": "density, gravitational acceleration", "value": r"\rho g", "sign": "-"}],
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
    "left": [{"name": "total differential of inner energy", "value": r"\operatorname{d} U", "sign": "+"}],
    "right": [{"name": "partial differential of work", "value": r"\partial W", "sign": "+"}, {"name": "partial differential of heat", "value": r"\partial Q", "sign": "+"}],  # other order
}

@pytest.mark.parametrize(
    "e1, e2, result",
    [
        (gas_law, next_gas_law, True),
        (hydrostatic, hydrostatic_wrong_sides, False),  # wrong sides
        (first_law, first_law_other_order, True), # other order within sides should not matter
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
    ]
)
def test_equation_get_items(e: Equation, terms: list[Term], result: bool) -> None:
    assert result == (sorted(e.get_all_terms(), key=lambda term: term.value) == sorted(terms, key=lambda term: term.value))

@pytest.mark.parametrize(
    "e, left_test, right_test, result",
    [
        (gas_law, gas_law_terms[0:1], gas_law_terms[1:2], False),
        (gas_law, gas_law_terms[1:2], gas_law_terms[0:1], True),
        (gas_law, gas_law_terms, hydrostatic_terms, False),
        (hydrostatic, hydrostatic_terms[0:1], hydrostatic_terms[1:2], True),
        (hydrostatic_wrong_sides, hydrostatic_terms[0:1], hydrostatic_terms[1:2], False),
        (hydrostatic_wrong_sides, hydrostatic_terms[1:2], hydrostatic_terms[0:1], True),
        (first_law, first_law_terms[0:1], first_law_terms[1:2], False),
        (first_law, first_law_terms[0:1], first_law_terms[1:3], True),
        (first_law_other_order, first_law_terms[0:1], first_law_terms[1:3], True),
    ]
)
def test_equation_check_input(e: Equation, left_test: list[Term], right_test: list[Term], result: bool) -> None:
    assert result == e.check_input(left_test, right_test)

@pytest.mark.parametrize(
    "e", [gas_law, hydrostatic, hydrostatic_wrong_sides, first_law, first_law_other_order]
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
        (first_law, first_law_dict, False),  # other (alphabetically wrong) order in dict
        (first_law_other_order, first_law_dict, False),  # same here although order in constructor and dict are the same (gets sorted during construction)
    ]
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
    ]
)
def test_equation_from_dict(e_dict: dict, e: Equation, result: bool) -> None:
    assert result == (Equation.from_dict(e_dict) == e)