# Unit tests for Term class

import pytest

from src.equatio.term import Term
from tests.testdata import (
    T_P1,
    T_P1_DICT,
    T_P2,
    T_P2_DICT,
    T_P3,
    T_P3_DICT,
    T_P4,
    T_P4_DICT,
)


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


@pytest.mark.parametrize(
    "t1, t2, result",
    [
        (T_P1, T_P2, True),
        (T_P1, T_P3, False),
        (T_P1, T_P4, False),
        (T_P2, T_P3, False),
        (T_P2, T_P4, False),
        (T_P3, T_P4, True),
        (
            Term("test", r"\frac{1}{2}a", "+"),
            Term("test2", r"\frac{a}{2}", "+"),
            False,
        ),  # mathematically same but different latex -> different sprite_id
    ],
)
def test_term_sprite_path_for_same_latex(t1, t2, result) -> None:
    """Test if (only) terms with same full latex code yield same sprite path."""
    assert result == (t1.get_sprite_path() == t2.get_sprite_path())


@pytest.mark.parametrize("t", [T_P1, T_P2, T_P3, T_P4])
def test_term_dict_cycle(t: Term) -> None:
    """Test if as_dict() and from_dict() cycle to same Term."""
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
