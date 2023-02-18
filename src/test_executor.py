from typing import Sequence, Tuple

import pytest

import executor


@pytest.fixture
def tuples() -> Sequence[Tuple[Tuple[str, str], ...]]:
    return [
        (("key", "0"), ("value", "a")),
        (("key", "1"), ("value", "a")),
        (("key", "2"), ("value", "b")),
    ]


def test_scan(tuples: Sequence[Tuple[Tuple[str, str], ...]]) -> None:
    scan = executor.Scan(tuples)

    for item in tuples:
        assert scan.next()
        assert item == scan.execute()

    assert not scan.next()


def test_selection(tuples: Sequence[Tuple[Tuple[str, str], ...]]) -> None:
    scan = executor.Scan(tuples)
    selection = executor.Selection(executor.TrueExpression(), scan)

    for item in tuples:
        assert scan.next()
        assert item == scan.execute()

    assert not selection.next()

    scan = executor.Scan(tuples)
    selection = executor.Selection(executor.FalseExpression(), scan)

    assert not selection.next()
