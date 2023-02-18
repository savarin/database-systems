from typing import Protocol, Sequence, Tuple, Union
import abc
import dataclasses


Value = Union[str, int]

Row = Tuple[Value, ...]


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

    def __post_init__(self):
        self.index = -1

    def next(self) -> bool:
        self.index += 1

        return self.index < len(self.tuples)

    def execute(self) -> Row:
        return self.tuples[self.index]
