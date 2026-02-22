from unittest.mock import Mock

from pytest import fixture
from pytest_mock import MockerFixture
from repository import RobotRepository


@fixture
def anyio_backend() -> str:
    return "asyncio"


@fixture
def fake_robot_repository(mocker: MockerFixture) -> Mock:
    return mocker.Mock(spec=RobotRepository)  # type: ignore
