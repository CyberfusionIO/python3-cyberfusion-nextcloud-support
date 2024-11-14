from cyberfusion.NextCloudSupport._occ import run_command
from cyberfusion.NextCloudSupport.instance import Instance


def test_run_command(instance_installed_static_version: Instance) -> None:
    run_command(["update:check"], instance_installed_static_version.path)
