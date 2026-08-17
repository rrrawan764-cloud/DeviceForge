import subprocess
from typing import List, Optional


class FastbootHandler:
    """Handles Fastboot protocol commands for flashing and bootloader control."""

    def __init__(self, fastboot_path: str = "tools/fastboot.exe"):
        self.fastboot_path = fastboot_path

    def _run_cmd(self, serial: Optional[str], args: List[str]) -> str:
        cmd = [self.fastboot_path]
        if serial:
            cmd.extend(["-s", serial])
        cmd.extend(args)
        
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return res.stdout.strip() + "\n" + res.stderr.strip()
        except Exception as e:
            return str(e)

    def get_variable(self, serial: str, var_name: str) -> str:
        output = self._run_cmd(serial, ["getvar", var_name])
        for line in output.splitlines():
            if var_name in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    return parts[1].strip()
        return ""

    def flash_partition(self, serial: str, partition: str, image_path: str) -> str:
        return self._run_cmd(serial, ["flash", partition, image_path])

    def reboot(self, serial: str, target: str = "") -> str:
        args = ["reboot"]
        if target:
            args.append(target)
        return self._run_cmd(serial, args)
