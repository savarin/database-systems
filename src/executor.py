from typing import Sequence, Tuple, Union
import dataclasses


@dataclasses.dataclass
class Scan:
    tuples: Sequence[Tuple[Union[str, int], ...]]

    def __post_init__(self):
        self.index = -1

    def next(self) -> bool:
        self.index += 1

        return self.index < len(self.tuples)

    def execute(self) -> Tuple[Union[str, int], ...]:
        return self.tuples[self.index]
