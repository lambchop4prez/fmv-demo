from handlers import RobotHandlers


def test_primes() -> None:
    subject = RobotHandlers("test")
    result = subject.primes(3)
    assert result == [1, 3, 5]
