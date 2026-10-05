from dataclasses import dataclass
from typing import List

import torch


@dataclass
class DeviceInfo:
    device_id: str
    name: str
    backend: str
    available: bool
    memory_mb: int | None = None


class DeviceManager:
    """Detect CPU, NVIDIA CUDA, and optional experimental DirectML devices."""

    def __init__(self):
        self.devices: List[DeviceInfo] = []
        self.detect_devices()

    def detect_devices(self):
        self.devices.clear()
        self.devices.append(DeviceInfo("cpu", "CPU", "CPU", True))

        if torch.cuda.is_available():
            for index in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(index)
                self.devices.append(
                    DeviceInfo(
                        device_id=f"cuda:{index}",
                        name=torch.cuda.get_device_name(index),
                        backend="CUDA",
                        available=True,
                        memory_mb=int(props.total_memory / 1024 / 1024),
                    )
                )

        # Optional package: keep CUDA and CPU unaffected if absent or unusable.
        try:
            import torch_directml

            for index in range(torch_directml.device_count()):
                try:
                    name = torch_directml.device_name(index)
                except Exception:
                    name = f"DirectML GPU {index}"
                self.devices.append(
                    DeviceInfo(f"dml:{index}", name, "DIRECTML", True)
                )
        except Exception:
            pass

    def get_devices(self) -> List[DeviceInfo]:
        return self.devices

    def get_device(self, device_id: str) -> DeviceInfo | None:
        return next((device for device in self.devices if device.device_id == device_id), None)

    def get_default_device(self) -> DeviceInfo:
        # Preserve the tested NVIDIA preference, then use DirectML, then CPU.
        for backend in ("CUDA", "DIRECTML", "CPU"):
            for device in self.devices:
                if device.backend == backend and device.available:
                    return device
        return self.devices[0]

    def print_devices(self):
        print("=" * 60)
        print("ARM AI DEVICE MANAGER")
        print("=" * 60)
        for device in self.devices:
            memory = f" | VRAM: {device.memory_mb} MB" if device.memory_mb else ""
            print(f"{device.device_id:10} | {device.backend:8} | {device.name} | AVAILABLE{memory}")
        print("=" * 60)


if __name__ == "__main__":
    manager = DeviceManager()
    manager.print_devices()
    print("DEFAULT DEVICE:", manager.get_default_device().name)
