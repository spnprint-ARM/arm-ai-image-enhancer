from app.device.device_manager import DeviceManager
from app.engine.realesrgan_engine import RealESRGANEngine


class EngineManager:

    def __init__(self):
        self.device_manager = DeviceManager()
        self.engine = None

    def create_engine(self, device="AUTO"):

        if device == "AUTO":
            selected = self.device_manager.get_default_device()
        else:
            selected = self.device_manager.get_device(device)

        if selected is None:
            raise RuntimeError(
                f"ไม่พบ Device: {device}"
            )

        if selected.backend == "CUDA":

            self.engine = RealESRGANEngine(
                tile=256,
                tile_pad=10,
                pre_pad=0,
                half=False,
                device_override=selected.device_id,
            )

            return self.engine

        if selected.backend == "CPU":

            self.engine = RealESRGANEngine(
                tile=128,
                tile_pad=10,
                pre_pad=0,
                half=False,
                device_override="cpu",
            )

            return self.engine

        if selected.backend == "DIRECTML":
            self.engine = RealESRGANEngine(
                tile=128,
                tile_pad=10,
                pre_pad=0,
                half=False,
                device_override=selected.device_id,
            )

            return self.engine

        raise RuntimeError(
            f"ยังไม่รองรับ Backend: {selected.backend}"
        )

    def get_engine(self):

        if self.engine is None:
            self.create_engine("AUTO")

        return self.engine
