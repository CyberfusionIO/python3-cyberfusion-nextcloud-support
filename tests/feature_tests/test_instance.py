import os
import subprocess
from typing import Generator

import pytest

from cyberfusion.Common import generate_random_string
from cyberfusion.NextCloudSupport._occ import PHP_BIN
from cyberfusion.NextCloudSupport.app import App
from cyberfusion.NextCloudSupport.instance import (
    DatabaseType,
    Instance,
    MailAccountAuthMethod,
    SSLMode,
)
from tests._urls import URL_BOOKMARKS


def test_instance_download_from_nextcloud(
    workspace_directory: Generator[str, None, None],
) -> None:
    Instance.download(workspace_directory, zip_path=None)

    assert os.path.isfile(os.path.join(workspace_directory, "index.php"))


def test_instance_download_from_zip(
    workspace_directory: Generator[str, None, None],
    nextcloud_2900_archive: str,
) -> None:
    Instance.download(workspace_directory, zip_path=nextcloud_2900_archive)

    assert os.path.isfile(os.path.join(workspace_directory, "index.php"))


def test_instance_install(
    workspace_directory: Generator[str, None, None],
    database_name: str,
    database_host: str,
    database_username: str,
    database_password: str,
) -> None:
    Instance.download(
        workspace_directory,
    )

    Instance.install(
        workspace_directory,
        database_host=database_host,
        database_name=database_name,
        database_username=database_username,
        database_password=database_password,
        admin_user="admin",
        admin_password=generate_random_string(),
        database_type=DatabaseType.MYSQL,
    )


def test_instance_update_available(
    workspace_directory: Generator[str, None, None],
    nextcloud_2900_archive: str,
    database_name: str,
    database_host: str,
    database_username: str,
    database_password: str,
) -> None:
    ORIGINAL_VERSION = "29.0.0.19"

    Instance.download(workspace_directory, zip_path=nextcloud_2900_archive)

    Instance.install(
        workspace_directory,
        database_host=database_host,
        database_name=database_name,
        database_username=database_username,
        database_password=database_password,
        admin_user="admin",
        admin_password=generate_random_string(),
        database_type=DatabaseType.MYSQL,
    )

    instance = Instance(workspace_directory)

    assert instance.version == ORIGINAL_VERSION

    old_version, new_version = instance.update()

    assert old_version == ORIGINAL_VERSION
    assert new_version != ORIGINAL_VERSION

    assert instance.version != ORIGINAL_VERSION


def test_instance_update_unavailable(
    instance_installed: Instance,
) -> None:
    old_version, new_version = instance_installed.update()

    assert old_version == new_version


def test_instance_available_version_available(
    workspace_directory: Generator[str, None, None],
    nextcloud_2900_archive: str,
    database_name: str,
    database_host: str,
    database_username: str,
    database_password: str,
) -> None:
    Instance.download(workspace_directory, zip_path=nextcloud_2900_archive)

    Instance.install(
        workspace_directory,
        database_host=database_host,
        database_name=database_name,
        database_username=database_username,
        database_password=database_password,
        admin_user="admin",
        admin_password=generate_random_string(),
        database_type=DatabaseType.MYSQL,
    )

    instance = Instance(workspace_directory)

    subprocess.run(  # NextCloud caches update results
        [
            PHP_BIN,
            "-d",
            "memory_limit=512M",
            "occ",
            "--no-interaction",
            "config:app:delete",
            "core",
            "lastupdatedat",
        ],
        check=True,
        cwd=instance.path,
    )

    assert instance.available_version is not None


def test_instance_available_version_unavailable(
    instance_installed: Instance,
) -> None:
    assert instance_installed.available_version is None


def test_instance_version(instance_installed: Instance) -> None:
    assert instance_installed.version.count(".") >= 2


def test_instance_set_get_system_config_str(
    instance_installed: Instance,
) -> None:
    NAME = "defaultapp"
    VALUE = "deck"

    instance_installed.set_system_config(NAME, VALUE)

    assert instance_installed.get_system_config(NAME) == VALUE


def test_instance_set_get_system_config_int(
    instance_installed: Instance,
) -> None:
    NAME = "loglevel"
    VALUE = 1

    instance_installed.set_system_config(NAME, VALUE)

    assert instance_installed.get_system_config(NAME) == VALUE


def test_instance_set_get_system_config_bool_true(
    instance_installed: Instance,
) -> None:
    NAME = "maintenance"
    VALUE = True

    instance_installed.set_system_config(NAME, VALUE)

    assert instance_installed.get_system_config(NAME) == VALUE


def test_instance_set_get_system_config_bool_false(
    instance_installed: Instance,
) -> None:
    NAME = "maintenance"
    VALUE = False

    instance_installed.set_system_config(NAME, VALUE)

    assert instance_installed.get_system_config(NAME) == VALUE


def test_instance_set_get_system_config_float(
    instance_installed: Instance,
) -> None:
    NAME = "version"
    VALUE = 1.1

    instance_installed.set_system_config(NAME, VALUE)

    assert instance_installed.get_system_config(NAME) == VALUE


def test_instance_set_get_system_config_index(
    instance_installed: Instance,
) -> None:
    NAME = "trusted_domains"
    VALUE = "example.com"

    instance_installed.set_system_config(NAME, VALUE, 2)

    assert VALUE in instance_installed.get_system_config(NAME)


def test_instance_installed_apps(
    instance_installed: Instance,
) -> None:
    assert len(instance_installed.installed_apps) >= 52


def test_instance_users(instance_installed: Instance) -> None:
    assert len(instance_installed.users) == 1


@pytest.mark.xdist_group(name="app")
def test_instance_create_mail_account(
    instance_installed: Instance,
) -> None:
    App.install(instance_installed, "mail")

    instance_installed.create_mail_account(
        user_id=instance_installed.users[0].id,
        name=instance_installed.users[0].name,
        email_address="example@example.com",
        imap_hostname="localhost",
        imap_port=143,
        imap_ssl_mode=SSLMode.NONE,
        imap_username="example@example.com",
        imap_password="pass",
        smtp_host="localhost",
        smtp_port=25,
        smtp_ssl_mode=SSLMode.NONE,
        smtp_username="example@example.com",
        smtp_password="pass",
        auth_method=MailAccountAuthMethod.PASSWORD,
    )


@pytest.mark.xdist_group(name="app")
def test_instance_raw_app_list(instance_installed: Instance) -> None:
    assert isinstance(instance_installed.raw_app_list, dict)


@pytest.mark.xdist_group(name="app")
def test_instance_raw_app_update_list(
    instance_installed: Instance,
) -> None:
    assert isinstance(instance_installed.raw_app_update_list, list)


@pytest.mark.xdist_group(name="app")
def test_instance_refresh_raw_app_list(
    instance_installed: Instance,
) -> None:
    APP_NAME = "mail"

    # App not installed

    assert (
        APP_NAME
        not in instance_installed.raw_app_list["enabled"]
        | instance_installed.raw_app_list["disabled"]
    )

    # Install app

    App.install(instance_installed, APP_NAME)

    # Cache not refreshed

    assert (
        APP_NAME
        not in instance_installed.raw_app_list["enabled"]
        | instance_installed.raw_app_list["disabled"]
    )

    instance_installed.refresh_raw_app_list()

    # Cache refreshed

    assert (
        APP_NAME
        in instance_installed.raw_app_list["enabled"]
        | instance_installed.raw_app_list["disabled"]
    )


@pytest.mark.xdist_group(name="app")
def test_instance_refresh_raw_app_update_list(
    instance_installed: Instance,
) -> None:
    APP_NAME = "bookmarks"

    # App not installed

    assert APP_NAME not in [
        line.split(" ")[0] for line in instance_installed.raw_app_update_list
    ]

    # Install app

    App.install(
        instance_installed,
        url=URL_BOOKMARKS,
    )

    # Cache not refreshed

    assert APP_NAME not in [
        line.split(" ")[0] for line in instance_installed.raw_app_update_list
    ]

    instance_installed.refresh_raw_app_update_list()

    # Cache refreshed

    assert APP_NAME in [
        line.split(" ")[0] for line in instance_installed.raw_app_update_list
    ]
