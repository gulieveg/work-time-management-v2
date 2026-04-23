from typing import Any, Generator, List


def zip_iterables(*iterables) -> Generator[List[Any], None, None]:
    iterators: List = [iter(iterable) for iterable in iterables]

    while True:
        result: List = []
        for iterable in iterators:
            try:
                result.append(next(iterable))
            except StopIteration:
                return
        yield result
