# Unit tests for Equation class

import pytest

from src.equatio.equation import Equation
from src.equatio.term import Term
from tests.testdata import GAS_LAW_TERMS, GAS_LAW, GAS_LAW_DICT, NEXT_GAS_LAW
from tests.testdata import (
    HYDROSTATIC_TERMS,
    HYDROSTATIC,
    HYDROSTATIC_DICT,
    HYDROSTATIC_WRONG_SITES,
)
from tests.testdata import (
    FIRST_LAW_TERMS,
    FIRST_LAW,
    FIRST_LAW_DICT,
    FIRST_LAW_OTHER_ORDER,
)


@pytest.mark.parametrize(
    "e1, e2, result",
    [
        (GAS_LAW, NEXT_GAS_LAW, True),  # name does not matter (as of now)
        (HYDROSTATIC, HYDROSTATIC_WRONG_SITES, False),  # wrong sides
        (
            FIRST_LAW,
            FIRST_LAW_OTHER_ORDER,
            True,
        ),  # other order within sides should not matter
    ],
)
def test_equation_equality(e1: Equation, e2: Equation, result: bool) -> None:
    """Test equality overload for Equation."""
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
    """Test if all_terms property returns all terms in equation,
    regardless of side and order."""
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
    """Test check_input method of Equation."""
    assert result == e.check_input(left_test, right_test)


@pytest.mark.parametrize(
    "e",
    [GAS_LAW, HYDROSTATIC, HYDROSTATIC_WRONG_SITES, FIRST_LAW, FIRST_LAW_OTHER_ORDER],
)
def test_equation_dict_cycle(e: Equation) -> None:
    """Test if as_dict() and from_dict() cycle to same Equation."""
    assert e == Equation.from_dict(e.as_dict())


@pytest.mark.parametrize(
    "e, e_dict, result",
    [
        (GAS_LAW, GAS_LAW_DICT, True),
        (GAS_LAW, HYDROSTATIC_DICT, False),
        (
            HYDROSTATIC,
            HYDROSTATIC_DICT,
            False,
        ),  # one sprite_id will default to None in hydrostatic_dict
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
    """Test Equation conversion to dictionary."""
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
    """Test Equation constructor from dictionary."""
    assert result == (Equation.from_dict(e_dict) == e)
