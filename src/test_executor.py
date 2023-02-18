from typing import Sequence

import pytest

import executor


@pytest.fixture
def tuples() -> Sequence[executor.Row]:
    return [
        (("key", "0"), ("value", "a")),
        (("key", "1"), ("value", "a")),
        (("key", "2"), ("value", "b")),
    ]


def test_scan(tuples: Sequence[executor.Row]) -> None:
    scan = executor.Scan(tuples)

    for item in tuples:
        assert scan.next()
        assert item == scan.execute()

    assert not scan.next()


def test_projection(tuples: Sequence[executor.Row]) -> None:
    # empty set
    scan = executor.Scan(tuples)
    projection = executor.Projection(set(), scan)

    for _ in tuples:
        assert projection.next()
        assert len(projection.execute()) == 0

    assert not projection.next()

    # non-empty set
    scan = executor.Scan(tuples)
    projection = executor.Projection({"value"}, scan)

    assert projection.next()
    assert projection.execute() == (("value", "a"),)

    assert projection.next()
    assert projection.execute() == (("value", "a"),)

    assert projection.next()
    assert projection.execute() == (("value", "b"),)

    assert not projection.next()


def test_selection(tuples: Sequence[executor.Row]) -> None:
    # true expression
    scan = executor.Scan(tuples)
    selection = executor.Selection(executor.TrueExpression(), scan)

    for item in tuples:
        assert selection.next()
        assert item == selection.execute()

    assert not selection.next()

    # false expression
    scan = executor.Scan(tuples)
    selection = executor.Selection(executor.FalseExpression(), scan)

    assert not selection.next()

    # equal expression
    scan = executor.Scan(tuples)
    selection = executor.Selection(executor.EqualExpression("value", "a"), scan)

    assert selection.next()
    assert selection.execute() == tuples[0]

    assert selection.next()
    assert selection.execute() == tuples[1]

    assert not selection.next()

    # equal-and expression
    scan = executor.Scan(tuples)
    left = executor.EqualExpression("key", "1")
    right = executor.EqualExpression("value", "a")
    selection = executor.Selection(executor.AndExpression(left, right), scan)

    assert selection.next()
    assert selection.execute() == tuples[1]

    assert not selection.next()


def test_limit(tuples: Sequence[executor.Row]) -> None:
    # all rows
    scan = executor.Scan(tuples)
    limit = executor.Limit(len(tuples) + 1, scan)

    for item in tuples:
        assert limit.next()
        assert item == limit.execute()

    assert not limit.next()

    # single row
    scan = executor.Scan(tuples)
    limit = executor.Limit(1, scan)

    assert limit.next()
    assert limit.execute() == tuples[0]

    assert not limit.next()
