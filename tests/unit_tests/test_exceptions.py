from cyberfusion.NextCloudSupport.exceptions import CommandFailedError


def test_CommandFailedError_streams():
    STDOUT = "stdout"
    STDERR = "stderr"

    exception = CommandFailedError(
        command=["foobar"], return_code=1, stdout=STDOUT, stderr=STDERR
    )

    assert (
        exception.streams
        == f"Stdout:\n\n{exception.stdout}\n\nStderr:\n\n{exception.stderr}"
    )
