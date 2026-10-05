from pathlib import Path
import time
import math

import torch
from PIL import Image
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer


class RealESRGANEngine:
    """
    Arm AI Image Enhancer
    Real-ESRGAN backend สำหรับ NVIDIA CUDA
    """

    def __init__(
        self,
        model_path=None,
        tile=256,
        tile_pad=10,
        pre_pad=0,
        half=False,
        device_override=None,
    ):
        # -------------------------------------------------
        # Paths
        # -------------------------------------------------
        self.root_dir = Path(__file__).resolve().parents[2]

        if model_path is None:
            model_path = self.root_dir / "models" / "RealESRGAN_x4plus.pth"

        self.model_path = Path(model_path)

        # -------------------------------------------------
        # Device
        # -------------------------------------------------
        self.directml = bool(device_override and str(device_override).startswith("dml:"))
        if self.directml:
            try:
                import torch_directml
                index = int(str(device_override).split(":", 1)[1])
                self.device = torch_directml.device(index)
                self._directml_name = torch_directml.device_name(index)
            except Exception as exc:
                raise RuntimeError(
                    "DirectML is selected but could not be initialized. "
                    "Install the optional torch-directml package and verify the GPU driver."
                ) from exc
        else:
            self.device = torch.device(
                device_override or ("cuda" if torch.cuda.is_available() else "cpu")
            )
            self._directml_name = None

        self.use_half = bool(half and self.device.type == "cuda")

        # -------------------------------------------------
        # Real-ESRGAN x4plus architecture
        # -------------------------------------------------
        self.model = RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=23,
            num_grow_ch=32,
            scale=4,
        )

        # -------------------------------------------------
        # Real-ESRGAN
        # -------------------------------------------------
        self.upsampler = RealESRGANer(
            scale=4,
            model_path=str(self.model_path),
            model=self.model,
            tile=tile,
            tile_pad=tile_pad,
            pre_pad=pre_pad,
            half=self.use_half,
            device=self.device,
        )

    def device_name(self):
        """คืนชื่ออุปกรณ์ที่กำลังใช้งาน"""

        if self.device.type == "cuda":
            return torch.cuda.get_device_name(0)

        if self.directml:
            return self._directml_name or "DirectML GPU"

        return "CPU"

    def enhance(self, input_path, output_path, scale=4, progress_callback=None, cancel_check=None):
        """
        Upscale ภาพ

        scale:
            2 = 2x
            4 = 4x

        return:
            dictionary ข้อมูลผลลัพธ์
        """

        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            raise FileNotFoundError(
                f"ไม่พบไฟล์ภาพ: {input_path}"
            )

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"ไม่พบโมเดล: {self.model_path}"
            )

        if cancel_check and cancel_check():
            raise InterruptedError("Processing stopped by user")

        if scale not in (2, 4):
            raise ValueError(
                "V1 รองรับ Scale 2x และ 4x"
            )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # -------------------------------------------------
        # Read image
        # -------------------------------------------------
        image = Image.open(input_path)

        original_size = image.size

        # Real-ESRGAN รองรับ RGB/RGBA
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGB")

        # -------------------------------------------------
        # Convert PIL -> numpy
        # -------------------------------------------------
        import numpy as np

        img = np.array(image)

        # -------------------------------------------------
        # GPU timing
        # -------------------------------------------------
        if self.device.type == "cuda":
            torch.cuda.synchronize()

        start_time = time.perf_counter()

        # -------------------------------------------------
        # AI Upscale
        # -------------------------------------------------
        if progress_callback:
            height, width = img.shape[:2]
            tile = self.upsampler.tile_size
            total_tiles = 1 if not tile else math.ceil(width / tile) * math.ceil(height / tile)
            completed_tiles = [0]

            def on_tile(_model, _inputs, _output):
                if cancel_check and cancel_check():
                    raise InterruptedError("Processing stopped by user")
                completed_tiles[0] += 1
                progress_callback(min(100, round(100 * completed_tiles[0] / total_tiles)))

            hook = self.upsampler.model.register_forward_hook(on_tile)
            try:
                output, _ = self.upsampler.enhance(img, outscale=scale)
            finally:
                hook.remove()
        else:
            output, _ = self.upsampler.enhance(img, outscale=scale)

        if cancel_check and cancel_check():
            raise InterruptedError("Processing stopped by user")

        # -------------------------------------------------
        # GPU timing
        # -------------------------------------------------
        if self.device.type == "cuda":
            torch.cuda.synchronize()

        elapsed = time.perf_counter() - start_time

        # -------------------------------------------------
        # Save
        # -------------------------------------------------
        result = Image.fromarray(output)

        result.save(output_path)

        output_size = result.size

        # -------------------------------------------------
        # VRAM information
        # -------------------------------------------------
        vram_used_mb = None

        if self.device.type == "cuda":
            vram_used_mb = (
                torch.cuda.max_memory_allocated()
                / 1024
                / 1024
            )

            torch.cuda.reset_peak_memory_stats()

        return {
            "input": str(input_path),
            "output": str(output_path),
            "device": self.device_name(),
            "precision": "FP16" if self.use_half else "FP32",
            "scale": scale,
            "input_size": original_size,
            "output_size": output_size,
            "time_seconds": round(elapsed, 3),
            "vram_peak_mb": (
                round(vram_used_mb, 1)
                if vram_used_mb is not None
                else None
            ),
        }


def create_engine():
    """
    สร้าง Engine ด้วยค่าที่ทดสอบแล้วกับ
    GTX 1660 Ti 6GB
    """

    root = Path(__file__).resolve().parents[2]

    model_path = (
        root
        / "models"
        / "RealESRGAN_x4plus.pth"
    )

    return RealESRGANEngine(
        model_path=model_path,
        tile=256,
        tile_pad=10,
        pre_pad=0,
        half=False,   # FP32 เพราะเครื่องนี้ทดสอบแล้วว่าถูกต้อง
    )
