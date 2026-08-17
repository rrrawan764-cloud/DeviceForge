import subprocess
from typing import List, Optional


class AdbHandler:
    """Handles ADB protocol commands for connected Android devices."""

    def __init__(self, adb_path: str = "tools/adb.exe"):
        self.adb_path = adb_path

    def _run_cmd(self, serial: Optional[str], args: List[str]) -> str:
        cmd = [self.adb_path]
        if serial:
            cmd.extend(["-s", serial])
        cmd.extend(args)
        
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return res.stdout.strip()
        except Exception:
            return ""

    def shell(self, serial: str, command: str) -> str:
        return self._run_cmd(serial, ["shell", command])

    def install_apk(self, serial: str, apk_path: str) -> bool:
        output = self._run_cmd(serial, ["install", "-r", apk_path])
        return "Success" in output

    def uninstall_app(self, serial: str, package_name: str) -> bool:
        output = self._run_cmd(serial, ["uninstall", package_name])
        return "Success" in output

    def reboot(self, serial: str, mode: str = "") -> str:
        args = ["reboot"]
        if mode:
            args.append(mode)
        return self._run_cmd(serial, args)
