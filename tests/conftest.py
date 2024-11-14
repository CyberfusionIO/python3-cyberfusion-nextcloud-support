import os
import shutil
from pathlib import Path
from typing import Generator

import pytest
from _pytest.config.argparsing import Parser
from requests_mock import Mocker
from sqlalchemy_utils import create_database, database_exists, drop_database

from cyberfusion.Common import download_from_url, generate_random_string
from cyberfusion.NextCloudSupport.instance import (
    DatabaseType,
    Instance,
)
from tests._urls import (
    URL_BOOKMARKS,
    URL_COSPEND,
    URL_NEXTCLOUD_2900,
    URL_POLLS,
)


@pytest.fixture(scope="session")
def bookmarks_archive() -> str:
    path = os.path.join(os.path.sep, "tmp", "bookmarks.tar.gz")

    if not os.path.exists(path):
        os.rename(download_from_url(URL_BOOKMARKS), path)

    return path


@pytest.fixture(scope="session")
def polls_archive() -> str:
    path = os.path.join(os.path.sep, "tmp", "polls.tar.gz")

    if not os.path.exists(path):
        os.rename(download_from_url(URL_POLLS), path)

    return path


@pytest.fixture(scope="session")
def cospend_archive() -> str:
    path = os.path.join(os.path.sep, "tmp", "cospend.tar.gz")

    if not os.path.exists(path):
        os.rename(download_from_url(URL_COSPEND), path)

    return path


@pytest.fixture(scope="session")
def nextcloud_2900_archive() -> str:
    path = os.path.join(os.path.sep, "tmp", "nextcloud.zip")

    if not os.path.exists(path):
        os.rename(download_from_url(URL_NEXTCLOUD_2900), path)

    return path


def pytest_addoption(parser: Parser) -> None:
    parser.addoption("--database-username", action="store", required=True)
    parser.addoption("--database-password", action="store", required=True)
    parser.addoption("--database-host", action="store", required=True)


@pytest.fixture
def database_username(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--database-username")


@pytest.fixture
def database_password(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--database-password")


@pytest.fixture
def database_host(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--database-host")


@pytest.fixture
def workspace_directory() -> Generator[str, None, None]:
    path = os.path.join(
        str(Path.home()), "nextcloud-" + generate_random_string().lower()
    )

    os.mkdir(path)

    yield path

    shutil.rmtree(path)


@pytest.fixture(autouse=True)
def app_download_mocks(
    requests_mock: Mocker,
    polls_archive: str,
    cospend_archive: str,
    bookmarks_archive: str,
) -> None:
    requests_mock.real_http = True

    requests_mock.get(
        URL_POLLS,
        status_code=200,
        content=open(polls_archive, "rb").read(),
    )

    requests_mock.get(
        URL_COSPEND,
        status_code=200,
        content=open(cospend_archive, "rb").read(),
    )

    requests_mock.get(
        URL_BOOKMARKS,
        status_code=200,
        content=open(bookmarks_archive, "rb").read(),
    )


@pytest.fixture
def instance_installed(
    workspace_directory: str,
    database_name: str,
    nextcloud_2900_archive: str,
    database_host: str,
    database_username: str,
    database_password: str,
) -> Instance:
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

    print(f"Created instance with NextCloud version {instance.version}")

    return instance


@pytest.fixture
def database_name() -> str:
    return generate_random_string()


@pytest.fixture(autouse=True)
def database(
    database_name: str,
    database_username: str,
    database_password: str,
    database_host: str,
) -> Generator[None, None, None]:
    url = (
        "mysql+pymysql://"
        + database_username
        + ":"
        + database_password
        + "@"
        + database_host
        + "/"
        + database_name
    )

    if not database_exists(url):
        create_database(url)

    yield

    drop_database(url)
