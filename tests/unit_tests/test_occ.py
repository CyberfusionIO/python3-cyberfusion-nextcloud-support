import os

import pytest

from cyberfusion.NextCloudSupport._occ import run_command
from cyberfusion.NextCloudSupport.exceptions import CommandFailedError


def test_run_command_raises_exception() -> None:
    with pytest.raises(CommandFailedError) as e:
        run_command(["doesntexist"], os.getcwd())

    assert e.value.command is not None
    assert e.value.return_code is not None
    assert e.value.stdout is not None
    assert e.value.stderr is not None
    assert e.value.streams is not None
