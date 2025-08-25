import pytest

from src.equatio.equation import Term

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
    "sign": "+",
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
        (t_p2, t_p2_dict),
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
