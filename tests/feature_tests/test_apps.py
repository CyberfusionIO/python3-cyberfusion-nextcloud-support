import pytest

from cyberfusion.NextCloudSupport.app import App
from cyberfusion.NextCloudSupport.instance import Instance
from tests._urls import URL_BOOKMARKS, URL_COSPEND, URL_POLLS


@pytest.mark.xdist_group(name="app")
def test_app_str(instance_installed: Instance) -> None:
    app = instance_installed.get_app("provisioning_api")

    assert (
        str(app)
        == app.name
        + " ("
        + app.version
        + ", available: "
        + str(app.available_version)
        + ", enabled: "
        + str(app.is_enabled)
        + ")"
    )


@pytest.mark.xdist_group(name="app")
def test_app_version(instance_installed: Instance) -> None:
    app = instance_installed.get_app("provisioning_api")

    assert app.version.count(".") == 2, [
        str(a) for a in instance_installed.installed_apps
    ]


@pytest.mark.xdist_group(name="app")
def test_app_install_name(instance_installed: Instance) -> None:
    APP_NAME = "polls"

    App.install(instance_installed, name=APP_NAME)

    instance_installed.get_app(APP_NAME)


@pytest.mark.xdist_group(name="app")
def test_app_is_disabled_disabled(
    instance_installed: Instance,
) -> None:
    app = instance_installed.get_app("bruteforcesettings")  # Disabled by default

    assert app.is_enabled is False, [str(a) for a in instance_installed.installed_apps]


@pytest.mark.xdist_group(name="app")
def test_app_is_disabled_enabled(
    instance_installed: Instance,
) -> None:
    app = instance_installed.get_app("survey_client")  # Enabled by default

    assert app.is_enabled is True, [str(a) for a in instance_installed.installed_apps]


@pytest.mark.xdist_group(name="app")
def test_app_enable(instance_installed: Instance) -> None:
    app = instance_installed.get_app("bruteforcesettings")  # Disabled by default

    assert app.is_enabled is False, [str(a) for a in instance_installed.installed_apps]

    app.enable()

    assert app.is_enabled is True, [str(a) for a in instance_installed.installed_apps]


@pytest.mark.xdist_group(name="app")
def test_app_disable(instance_installed: Instance) -> None:
    app = instance_installed.get_app("survey_client")  # Enabled by default

    assert app.is_enabled is True, [str(a) for a in instance_installed.installed_apps]

    app.disable()

    assert app.is_enabled is False, [str(a) for a in instance_installed.installed_apps]


@pytest.mark.xdist_group(name="app")
def test_app_install_url(instance_installed: Instance) -> None:
    App.install(instance_installed, url=URL_COSPEND)

    instance_installed.get_app("cospend")


@pytest.mark.xdist_group(name="app")
def test_app_update_available(instance_installed: Instance) -> None:
    ORIGINAL_VERSION = "14.2.1"

    App.install(instance_installed, url=URL_BOOKMARKS)

    app = instance_installed.get_app("bookmarks")

    assert app.version == ORIGINAL_VERSION, [
        str(a) for a in instance_installed.installed_apps
    ]

    old_version, new_version = app.update()

    assert old_version == ORIGINAL_VERSION
    assert new_version != ORIGINAL_VERSION

    assert app.version != ORIGINAL_VERSION, [
        str(a) for a in instance_installed.installed_apps
    ]


@pytest.mark.xdist_group(name="app")
def test_app_update_unavailable(instance_installed: Instance) -> None:
    APP_NAME = "polls"

    App.install(instance_installed, name=APP_NAME)

    app = instance_installed.get_app(APP_NAME)

    old_version, new_version = app.update()

    assert old_version == new_version


@pytest.mark.xdist_group(name="app")
def test_app_available_version_available(
    instance_installed: Instance,
) -> None:
    App.install(
        instance_installed,
        url=URL_BOOKMARKS,
    )
    App.install(  # Install second app with available update to test filtering logic
        instance_installed,
        url=URL_POLLS,
    )

    app = instance_installed.get_app("bookmarks")

    assert app.available_version is not None, [
        str(a) for a in instance_installed.installed_apps
    ]


@pytest.mark.xdist_group(name="app")
def test_app_available_version_unavailable(
    instance_installed: Instance,
) -> None:
    APP_NAME = "polls"

    App.install(instance_installed, name=APP_NAME)

    app = instance_installed.get_app(APP_NAME)

    assert app.available_version is None, [
        str(a) for a in instance_installed.installed_apps
    ]


@pytest.mark.xdist_group(name="app")
def test_app_remove(instance_installed: Instance) -> None:
    APP_NAME = "polls"

    App.install(instance_installed, name=APP_NAME)

    app = instance_installed.get_app(APP_NAME)

    app.remove()

    assert not any(app.name == APP_NAME for app in instance_installed.installed_apps)
