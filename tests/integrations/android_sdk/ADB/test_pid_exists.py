import subprocess
from unittest.mock import Mock

from briefcase.integrations.android_sdk import ADB


def test_pid_exists_succeed(mock_tools):
    "adb.pid_exists() can be called on an process that exists."
    adb = ADB(mock_tools, "exampleDevice")
    adb.run = Mock(return_value="")
    assert adb.pid_exists("1234")
    adb.run.assert_called_once_with("shell", "test", "-e", "/proc/1234", stealth=False)


def test_pid_exists_stealth(mock_tools):
    "adb.pid_exists() can be called in stealth mode on an process that exists."
    adb = ADB(mock_tools, "exampleDevice")
    adb.run = Mock(return_value="")
    assert adb.pid_exists("1234", stealth=True)
    adb.run.assert_called_once_with("shell", "test", "-e", "/proc/1234", stealth=True)


def test_pid_does_not_exist(mock_tools):
    "If adb.pid_exists() returns a PID of 0, it is interpreted as the process not existing."
    adb = ADB(mock_tools, "exampleDevice")
    adb.run = Mock(side_effect=subprocess.CalledProcessError(returncode=1, cmd="test"))
    assert not adb.pid_exists("9999") is None
    adb.run.assert_called_once_with("shell", "test", "-e", "/proc/9999", stealth=False)
