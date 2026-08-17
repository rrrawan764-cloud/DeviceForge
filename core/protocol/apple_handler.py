import subprocess
from typing import Optional


class AppleHandler:
    """Handles professional servicing and diagnostic protocols for iOS devices (iPhone/iPad)."""

    def __init__(self):
        pass

    def _run_cmd(self, cmd: list) -> str:
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            return res.stdout.strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def get_device_info(self) -> str:
        """Reads device name, iOS version, UDID, and battery status for connected iPhone."""
        output = self._run_cmd(["ideviceinfo"])
        return output

    def get_serial(self) -> str:
        return self._run_cmd(["idevice_id", "-l"])

    def enter_recovery(self, udid: Optional[str] = None) -> str:
        cmd = ["ideviceenterrecovery"]
        if udid:
            cmd.append(udid)
        return self._run_cmd(cmd)

    def reboot(self) -> str:
        return self._run_cmd(["idevicediagnostics", "restart"])
