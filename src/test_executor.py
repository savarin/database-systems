import executor


def test_scan() -> None:
    tuples = [
        ("key", 1, "value", "a"),
        ("key", 2, "value", "a"),
        ("key", 3, "value", "b"),
    ]

    node = executor.Scan(tuples)

    for item in tuples:
        assert node.next()
        assert item == node.execute()
