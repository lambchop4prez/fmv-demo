from unittest.mock import Mock

import pytest
from service.robot import RobotService


@pytest.mark.anyio
async def test_list_calls_repository(fake_robot_repository: Mock) -> None:
    subject = RobotService(fake_robot_repository)

    result = await subject.list()

    assert result is not None
    assert fake_robot_repository.list.called
