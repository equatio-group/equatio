# Unit tests for EquationSet class

from copy import deepcopy
import json
from pathlib import Path
import pytest

from src.equatio.equation import Equation
from src.equatio.equation_set import EquationSet
from src.equatio.term import Term
from tests.testdata import (
    GAS_LAW,
    NEXT_GAS_LAW,
    HYDROSTATIC,
    HYDROSTATIC_WRONG_SITES,
    FIRST_LAW,
)
from tests.testdata import (
    ONE_EQUATION_SET,
    ONE_EQUATION_SET_OTHER_EQUATION_NAME,
    SAME_ONE_EQUATION_SET,
)
from tests.testdata import OTHER_ONE_EQUATION_SET, FALSE_TWO_EQUATION_SET
from tests.testdata import term_dict_add_sprite_id_for_testing
from tests.testdata import (
    VERY_BASIC_EQUATION_SET,
    VERY_BASIC_EQUATION_SET_OTHER_WAY_ROUND,
    BASIC_EQUATION_SET,
)


@pytest.mark.parametrize(
    "es1, es2, result",
    [
        (ONE_EQUATION_SET, ONE_EQUATION_SET, True),
        (
            ONE_EQUATION_SET,
            ONE_EQUATION_SET_OTHER_EQUATION_NAME,
            True,
        ),  # name of equation in set should not matter
        (
            ONE_EQUATION_SET,
            SAME_ONE_EQUATION_SET,
            True,
        ),  # other (default) name of set should not matter
        (OTHER_ONE_EQUATION_SET, FALSE_TWO_EQUATION_SET, True),
        (ONE_EQUATION_SET, OTHER_ONE_EQUATION_SET, False),
        (VERY_BASIC_EQUATION_SET, VERY_BASIC_EQUATION_SET_OTHER_WAY_ROUND, True),
        (VERY_BASIC_EQUATION_SET, BASIC_EQUATION_SET, False),
    ],
)
def test_equation_set_equality(
    es1: EquationSet, es2: EquationSet, result: bool
) -> None:
    """Test equality overload for EquationSet."""
    assert result == (es1 == es2)


@pytest.mark.parametrize(
    "es, e, result",
    [
        (ONE_EQUATION_SET, GAS_LAW, True),
        (ONE_EQUATION_SET, FIRST_LAW, False),
        (
            ONE_EQUATION_SET,
            NEXT_GAS_LAW,
            True,
        ),  # since name of equation should not matter
    ],
)
def test_equation_set_contains(es: EquationSet, e: Equation, result: bool) -> None:
    """Test __contains__ overload for EquationSet."""
    assert result == (e in es)


@pytest.mark.parametrize(
    "es, e",
    [
        (ONE_EQUATION_SET, HYDROSTATIC),
        (VERY_BASIC_EQUATION_SET, FIRST_LAW),
        (BASIC_EQUATION_SET, HYDROSTATIC_WRONG_SITES),
    ],
)
def test_equation_set_add_remove_cycle(es: EquationSet, e: Equation) -> None:
    """Test if adding and then removing an equation cycles back to
    original EquationSet."""
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
    """Test if removing and then adding an equation cycles back to
    original EquationSet."""
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
    """Test removing an equation from an EquationSet."""
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
    """Test adding an equation to an EquationSet."""
    es_added: EquationSet = deepcopy(es)
    es_added.add_equation(e_to_add)
    assert es_added == es_new


# Test JSON import/export
@pytest.fixture(params=[ONE_EQUATION_SET, VERY_BASIC_EQUATION_SET, BASIC_EQUATION_SET])
def equation_set(request) -> EquationSet:
    return request.param


def test_equation_set_json_cycle(equation_set: EquationSet, tmp_path: Path) -> None:
    """Test if exporting to JSON and then importing cycles back to same EquationSet."""
    # tmp_path is a pytest built-in fixture providing a temp directory for file tests
    # export
    out_path = tmp_path / f"{equation_set.name.replace(' ', '_')}.json"
    equation_set.to_json(out_path)  # uses equation_set from fixture above
    # import
    es_in = EquationSet.from_json(out_path)
    assert equation_set == es_in


def test_equation_set_to_json(equation_set: EquationSet, tmp_path: Path) -> None:
    """Test if exporting to JSON yields expected dictionary structure."""
    # tmp_path is a pytest built-in fixture providing a temp directory for file tests
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
    """Test if importing from JSON with known structure yields expected EquationSet."""
    # tmp_path is a pytest built-in fixture providing a temp directory for file tests
    file = tmp_path / "eq.json"
    test_eq1_dict: dict[str, str | list[dict[str, str]]] = {
        "name": "eq1",
        "left": [
            term_dict_add_sprite_id_for_testing(
                {"name": "a", "sign": "+", "latex_code": "a"}
            )
        ],
        "right": [
            term_dict_add_sprite_id_for_testing(
                {"name": "b", "sign": "-", "latex_code": "b"}
            )
        ],
    }
    test_eq2_dict: dict[str, str | list[dict[str, str]]] = {
        "name": "eq2",
        "left": [
            term_dict_add_sprite_id_for_testing(
                {"name": "c", "sign": "+", "latex_code": "c"}
            ),
            term_dict_add_sprite_id_for_testing(
                {"name": "d", "sign": "-", "latex_code": "d"}
            ),
        ],
        "right": [
            term_dict_add_sprite_id_for_testing(
                {"name": "e", "sign": "+", "latex_code": "e"}
            )
        ],
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
