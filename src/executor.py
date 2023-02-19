from typing import List, Optional, Protocol, Sequence, Tuple
import abc
import dataclasses
import heapq


Value = Tuple[str, str]

Row = Tuple[Value, ...]


class BinaryExpression(Protocol):
    @abc.abstractmethod
    def execute(self, row: Row) -> bool:
        ...


@dataclasses.dataclass
class TrueExpression:
    ...

    def execute(self, row: Row) -> bool:
        return True


@dataclasses.dataclass
class FalseExpression:
    ...

    def execute(self, row: Row) -> bool:
        return False


@dataclasses.dataclass
class EqualExpression:
    column: str
    value: str

    def execute(self, row: Row) -> bool:
        for k, v in row:
            if k == self.column:
                return v == self.value

        raise Exception(f"Column {self.column} not found in row {row}.")


@dataclasses.dataclass
class AndExpression:
    left: BinaryExpression
    right: BinaryExpression

    def execute(self, row: Row) -> bool:
        return self.left.execute(row) and self.right.execute(row)


class Operator(Protocol):
    @abc.abstractmethod
    def next(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def execute(self) -> Row:
        raise NotImplementedError


@dataclasses.dataclass
class Scan:
    tuples: Sequence[Row]

    def __post_init__(self) -> None:
        self.index = -1

    def next(self) -> bool:
        self.index += 1

        return self.index < len(self.tuples)

    def execute(self) -> Row:
        return self.tuples[self.index]


@dataclasses.dataclass
class Projection:
    columns: Sequence[str]
    child: Operator

    def next(self) -> bool:
        return self.child.next()

    def execute(self) -> Row:
        result = []
        row = self.child.execute()

        for k, v in row:
            if k in self.columns:
                result.append((k, v))

        return tuple(result)


@dataclasses.dataclass
class Selection:
    expression: BinaryExpression
    child: Operator

    def __post_init__(self) -> None:
        self.current: Optional[Row] = None

    def next(self) -> bool:
        while self.child.next():
            row = self.child.execute()

            if self.expression.execute(row):
                self.current = row
                return True

        return False

    def execute(self) -> Row:
        assert self.current is not None
        return self.current


@dataclasses.dataclass
class Sort:
    column: str
    child: Operator

    def __post_init__(self) -> None:
        self.collect: bool = False
        self.heap: List[Tuple[str, Row]] = []

    def load(self):
        index = None

        while self.child.next():
            row = self.child.execute()

            if index is None:
                index = [item[0] for item in row].index(self.column)

            heapq.heappush(self.heap, (row[index], row))

    def next(self) -> bool:
        if not self.collect:
            self.load()
            self.collect = True

        return len(self.heap) > 0

    def execute(self) -> Row:
        return heapq.heappop(self.heap)[1]


@dataclasses.dataclass
class Limit:
    limit: int
    child: Operator

    def __post_init__(self) -> None:
        self.counter: int = 0

    def next(self) -> bool:
        increment = self.counter < self.limit and self.child.next()

        if increment:
            self.counter += 1

        return increment

    def execute(self) -> Row:
        return self.child.execute()
