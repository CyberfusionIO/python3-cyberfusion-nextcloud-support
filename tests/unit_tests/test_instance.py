import os
from typing import Generator

import pytest

from cyberfusion.NextCloudSupport.exceptions import (
    AppNotInstalledError,
    CommandFailedError,
)
from cyberfusion.NextCloudSupport.instance import (
    DirectoryNotEmptyError,
    Instance,
)


def test_instance_download_directory_not_empty(
    workspace_directory: Generator[str, None, None],
) -> None:
    with open(os.path.join(workspace_directory, "test.txt"), "w"):
        pass

    with pytest.raises(DirectoryNotEmptyError):
        Instance.download(
            workspace_directory,
        )


def test_instance_get_app_not_installed(
    instance_installed_static_version: Instance,
) -> None:
    with pytest.raises(AppNotInstalledError):
        instance_installed_static_version.get_app("doesntexist")


def test_instance_refresh_raw_app_update_list_unset(
    instance_installed_static_version: Instance,
) -> None:
    assert "raw_app_update_list" not in instance_installed_static_version.__dict__

    instance_installed_static_version.refresh_raw_app_update_list()


def test_instance_refresh_raw_app_list_unset(
    instance_installed_static_version: Instance,
) -> None:
    assert "raw_app_list" not in instance_installed_static_version.__dict__

    instance_installed_static_version.refresh_raw_app_list()


def test_instance_update_raises_exception(
    instance_installed_static_version: Instance,
) -> None:
    os.unlink(
        os.path.join(instance_installed_static_version.path, "updater", "updater.phar")
    )  # Make command fail

    with pytest.raises(CommandFailedError) as e:
        instance_installed_static_version.update()

    assert e.value.command is not None
    assert e.value.return_code is not None
    assert e.value.stdout is not None
    assert e.value.stderr is not None
    assert e.value.streams is not None
