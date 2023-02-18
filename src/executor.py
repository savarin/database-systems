from typing import Optional, Protocol, Sequence, Tuple
import abc
import dataclasses


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

    def execute(self) -> Optional[Row]:
        return self.current
