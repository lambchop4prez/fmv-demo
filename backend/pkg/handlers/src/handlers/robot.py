from typing import Sequence


class RobotHandlers:
    def __init__(self, robot: str) -> None:
        self.robot = robot

    def primes(self, count: int) -> Sequence[int]:
        list = []
        for t in range(1, count + 1, 2):
            for i in range(2, int(t**0.5) + 1):
                if t % i == 0:
                    break  # Not prime
            list.append(t)  # is a prime
        return list
