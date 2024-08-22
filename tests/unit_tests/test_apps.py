import pytest

from cyberfusion.NextCloudSupport.app import App
from cyberfusion.NextCloudSupport.exceptions import AppNotInstalledError
from cyberfusion.NextCloudSupport.instance import Instance


def test_app_version_not_installed(
    instance_installed: Instance,
) -> None:
    with pytest.raises(AppNotInstalledError):
        App(instance_installed, "doesntexist").version


def test_app_install_name_and_url(
    instance_installed: Instance,
) -> None:
    with pytest.raises(ValueError, match="^Specify either name or URL$"):
        App.install(
            instance_installed,
            name="example.com",
            url="https://example.com",
        )
