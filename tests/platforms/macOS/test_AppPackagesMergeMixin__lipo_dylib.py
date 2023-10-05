import subprocess
from pathlib import Path

import pytest

from briefcase.exceptions import BriefcaseCommandError

from ...utils import create_file


@pytest.mark.parametrize("debug", [True, False])
def test_lipo_dylib(dummy_command, tmp_path, debug, capsys):
    """A binary library can be merged with lipo."""
    if debug:
        dummy_command.logger.verbosity = 1

    # Create 3 source binaries.
    create_file(tmp_path / "source-1" / "path" / "to" / "file.dylib", "dylib-1")
    create_file(tmp_path / "source-2" / "path" / "to" / "file.dylib", "dylib-2")
    create_file(tmp_path / "source-3" / "path" / "to" / "file.dylib", "dylib-3")

    # Merge the libraries
    dummy_command.lipo_dylib(
        Path("path") / "to" / "file.dylib",
        tmp_path / "target",
        [
            tmp_path / "source-1",
            tmp_path / "source-2",
            tmp_path / "source-3",
        ],
    )

    # Lipo was invoked with three sources
    dummy_command.tools.subprocess.run.assert_called_once_with(
        [
            "lipo",
            "-create",
            "-output",
            tmp_path / "target" / "path" / "to" / "file.dylib",
            tmp_path / "source-1" / "path" / "to" / "file.dylib",
            tmp_path / "source-2" / "path" / "to" / "file.dylib",
            tmp_path / "source-3" / "path" / "to" / "file.dylib",
        ],
        check=True,
    )

    # Output only happens if in debug mode
    output = capsys.readouterr().out.split("\n")
    assert len(output) == (2 if debug else 1)


@pytest.mark.parametrize("debug", [True, False])
def test_lipo_dylib_partial(dummy_command, tmp_path, debug, capsys):
    """If a source doesn't have the library, it isn't included in the merge."""
    if debug:
        dummy_command.logger.verbosity = 1

    # Create 2 source binaries. Source-2 doesn't have the binary.
    create_file(tmp_path / "source-1" / "path" / "to" / "file.dylib", "dylib-1")
    create_file(tmp_path / "source-3" / "path" / "to" / "file.dylib", "dylib-3")

    # Merge the libraries
    dummy_command.lipo_dylib(
        Path("path") / "to" / "file.dylib",
        tmp_path / "target",
        [
            tmp_path / "source-1",
            tmp_path / "source-3",
        ],
    )

    # Lipo was invoked with three sources
    dummy_command.tools.subprocess.run.assert_called_once_with(
        [
            "lipo",
            "-create",
            "-output",
            tmp_path / "target" / "path" / "to" / "file.dylib",
            tmp_path / "source-1" / "path" / "to" / "file.dylib",
            tmp_path / "source-3" / "path" / "to" / "file.dylib",
        ],
        check=True,
    )

    # Output only happens if in debug mode
    output = capsys.readouterr().out.split("\n")
    assert len(output) == (2 if debug else 1)


@pytest.mark.parametrize("debug", [True, False])
def test_lipo_dylib_merge_error(dummy_command, tmp_path, debug, capsys):
    """If the merge process fails, an exception is raised."""
    if debug:
        dummy_command.logger.verbosity = 1

    # Create 3 source binaries.
    create_file(tmp_path / "source-1" / "path" / "to" / "file.dylib", "dylib-1")
    create_file(tmp_path / "source-2" / "path" / "to" / "file.dylib", "dylib-2")
    create_file(tmp_path / "source-3" / "path" / "to" / "file.dylib", "dylib-3")

    # lipo raises an exception.
    dummy_command.tools.subprocess.run.side_effect = subprocess.CalledProcessError(
        returncode=-1, cmd="lipo..."
    )

    # Merge the libraries. This raises an exception:
    with pytest.raises(
        BriefcaseCommandError,
        match=r"Unable to create fat library for path[/\\]to[/\\]file\.dylib",
    ):
        dummy_command.lipo_dylib(
            Path("path") / "to" / "file.dylib",
            tmp_path / "target",
            [
                tmp_path / "source-1",
                tmp_path / "source-2",
                tmp_path / "source-3",
            ],
        )

    # Lipo was invoked with three sources
    dummy_command.tools.subprocess.run.assert_called_once_with(
        [
            "lipo",
            "-create",
            "-output",
            tmp_path / "target" / "path" / "to" / "file.dylib",
            tmp_path / "source-1" / "path" / "to" / "file.dylib",
            tmp_path / "source-2" / "path" / "to" / "file.dylib",
            tmp_path / "source-3" / "path" / "to" / "file.dylib",
        ],
        check=True,
    )

    # Output only happens if in debug mode
    output = capsys.readouterr().out.split("\n")
    assert len(output) == (2 if debug else 1)
