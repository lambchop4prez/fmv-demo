from handlers import RobotHandlers


def test_primes() -> None:
    subject = RobotHandlers("test")
    result = subject.primes(5)
    assert result == [1, 3, 5]
