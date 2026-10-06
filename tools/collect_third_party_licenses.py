"""Refresh the bundled notices from the configured runtime without importing AI code."""
import hashlib
import importlib.metadata as metadata
import json
import re
import shutil
import sys
from pathlib import Path
from packaging.requirements import Requirement

ROOT = Path(__file__).resolve().parents[1]
LICENSES = ROOT / "licenses"
CORE = ["realesrgan", "gfpgan", "torch", "torchvision", "basicsr", "facexlib", "numpy", "Pillow", "opencv-python"]
OVERRIDES = {
    "realesrgan": ("Real-ESRGAN", "BSD-3-Clause", "Xintao Wang and contributors", "https://github.com/xinntao/Real-ESRGAN"),
    "gfpgan": ("GFPGAN", "Apache-2.0", "Xintao Wang, Yu Li, Honglun Zhang, Ying Shan / Tencent ARC", "https://github.com/TencentARC/GFPGAN"),
    "torch": ("PyTorch", "BSD-3-Clause (plus bundled third-party terms)", "PyTorch contributors", "https://github.com/pytorch/pytorch"),
    "torchvision": ("TorchVision", "BSD-3-Clause", "PyTorch contributors", "https://github.com/pytorch/vision"),
    "basicsr": ("BasicSR", "Apache-2.0", "Xintao Wang and contributors", "https://github.com/XPixelGroup/BasicSR"),
    "facexlib": ("facexlib", "MIT", "Xintao Wang and contributors", "https://github.com/xinntao/facexlib"),
    "pillow": ("Pillow", "MIT-CMU (plus bundled third-party terms)", "Pillow contributors / Secret Labs AB / Fredrik Lundh", "https://github.com/python-pillow/Pillow"),
    "opencv-python": ("OpenCV Python", "Apache-2.0 (OpenCV); MIT (packaging); third-party terms", "OpenCV contributors and opencv-python maintainers", "https://github.com/opencv/opencv-python"),
}
def canonical(name):
    return re.sub(r"[-_.]+", "-", name).lower()

def license_name(dist, texts):
    expression = dist.metadata.get("License-Expression")
    if expression:
        return expression
    declared = dist.metadata.get("License", "").strip()
    if len(declared) < 120 and any(word in declared for word in (" AND ", " OR ")):
        return declared
    # A few wheel metadata fields contradict their actual license; trust the text.
    text = "\n".join(texts).lower()
    if "permission is hereby granted, free of charge" in text:
        return "MIT"
    if "apache license" in text and "version 2.0" in text:
        return "Apache-2.0"
    if "bsd 3-clause" in text:
        return "BSD-3-Clause"
    value = dist.metadata.get("License", "").strip()
    if value and len(value) < 120 and "\n" not in value:
        return value
    classifiers = [c.split(" :: ")[-1] for c in dist.metadata.get_all("Classifier", []) if c.startswith("License ::")]
    return "; ".join(classifiers) or "See bundled license text"

def package_entry(name):
    dist = metadata.distribution(name)
    package_id = canonical(dist.metadata["Name"])
    folder = LICENSES / package_id
    folder.mkdir(parents=True, exist_ok=True)
    files = []
    seen = set()
    for record in dist.files or []:
        # Normalize RECORD entries that use Windows separators.
        record_path = str(record).replace("\\", "/")
        pieces = record_path.split("/")
        if not any(piece.endswith(".dist-info") for piece in pieces):
            continue
        if not any(token in pieces[-1].lower() for token in ("licen", "copying", "notice", "authors")):
            continue
        source = Path(dist.locate_file(record_path))
        if not source.is_file():
            continue
        at = next(i for i, piece in enumerate(pieces) if piece.endswith(".dist-info"))
        relative = Path(*pieces[at + 1:])
        if relative.as_posix() in seen:
            continue
        seen.add(relative.as_posix())
        output = folder / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, output)
        files.append(output.relative_to(ROOT).as_posix())
    if not files:
        # Upstream fallback texts are checked in for wheels that omit their license.
        files = [p.relative_to(ROOT).as_posix() for p in sorted(folder.glob("LICENSE*")) if p.is_file()]
    if not files:
        raise RuntimeError(f"No license text in installed distribution: {name}")
    files.sort(key=lambda p: ("notice" in Path(p).name.lower(), len(p), p))
    texts = [(ROOT / file).read_text(encoding="utf-8", errors="replace") for file in files]
    links = []
    for field in dist.metadata.get_all("Project-URL", []):
        if ", " in field:
            links.append(field.split(", ", 1))
    source = next((link for label, link in links if label.lower() in ("source", "source code", "repository")), None)
    source = source or dist.metadata.get("Home-page") or next((link for _, link in links), f"https://pypi.org/project/{dist.metadata['Name']}/")
    author = dist.metadata.get("Author") or dist.metadata.get("Author-email") or f"{dist.metadata['Name']} contributors"
    display, license_id, author, source = OVERRIDES.get(package_id, (dist.metadata["Name"], license_name(dist, texts), author, source))
    return dict(id=package_id, name=display, version=dist.version, license=license_id,
                author=author, source=source, license_files=files, kind="library", notes="")

def collect():
    LICENSES.mkdir(exist_ok=True)
    pending = list(CORE)
    included = {}
    while pending:
        name = pending.pop(0)
        key = canonical(name)
        if key in included:
            continue
        try:
            dist = metadata.distribution(name)
        except metadata.PackageNotFoundError:
            # Optional dependencies absent from the configured runtime are not shipped.
            continue
        included[key] = package_entry(name)
        for spec in dist.requires or []:
            requirement = Requirement(spec)
            if requirement.marker is None or requirement.marker.evaluate({"extra": ""}):
                pending.append(requirement.name)
    entries = [included.pop(canonical(name)) for name in CORE if canonical(name) in included]
    entries += sorted(included.values(), key=lambda e: e["name"].lower())
    runtime = Path(sys.base_prefix)
    python_license = LICENSES / "python" / "LICENSE.txt"
    python_license.parent.mkdir(exist_ok=True)
    shutil.copyfile(runtime / "LICENSE.txt", python_license)
    entries.append(dict(id="python", name="Python", version=sys.version.split()[0], license="PSF-2.0 and historical licenses", author="Python Software Foundation and contributors", source="https://www.python.org/", license_files=["licenses/python/LICENSE.txt"], kind="runtime", notes=""))
    import tkinter
    tk = tkinter.Tcl()
    tcl_version = str(tk.call("info", "patchlevel"))
    tk_license = LICENSES / "tk" / "license.terms"
    tk_license.parent.mkdir(exist_ok=True)
    shutil.copyfile(runtime / "tcl" / "tk8.6" / "license.terms", tk_license)
    tk_header = (runtime / "include" / "tk.h")
    tk_version = "8.6"
    index_file = runtime / "tcl" / "tk8.6" / "pkgIndex.tcl"
    if index_file.is_file():
        match = re.search(r"package ifneeded Tk ([\d.]+)", index_file.read_text())
        if match:
            tk_version = match[1]
    if tk_header.is_file():
        match = re.search(r'#define\s+TK_PATCH_LEVEL\s+"([^"]+)"', tk_header.read_text(errors="replace"))
        if match:
            tk_version = match[1]
    for name, version, file in [("Tcl", tcl_version, "licenses/tcl/LICENSE.txt"), ("Tk", tk_version, "licenses/tk/license.terms")]:
        entries.append(dict(id=name.lower(), name=name, version=version, license="Tcl/Tk license", author="Regents of the University of California, Sun Microsystems, Scriptics, ActiveState and contributors", source=f"https://github.com/tcltk/{name.lower()}", license_files=[file], kind="runtime", notes=""))
    model_specs = [
        ("realesrgan-x4plus", "RealESRGAN_x4plus", "v0.1.0 release / x4plus", "BSD-3-Clause (upstream project)", "Xintao Wang and Real-ESRGAN contributors", "https://github.com/xinntao/Real-ESRGAN/releases/tag/v0.1.0", "models/RealESRGAN_x4plus.pth", ["licenses/realesrgan/LICENSE"], "The checkpoint is distributed by the upstream project. Its project license is included; no separate checkpoint-specific license was identified."),
        ("gfpgan-v14", "GFPGANv1.4", "1.4", "Apache-2.0 (upstream project)", "Tencent ARC / GFPGAN contributors", "https://github.com/TencentARC/GFPGAN/releases/tag/v1.3.0", "models/face/GFPGANv1.4.pth", ["licenses/gfpgan/LICENSE"], "The model name is v1.4; its hosting release tag is v1.3.0. The project license is included; no separate checkpoint-specific license was identified."),
        ("retinaface-resnet50", "RetinaFace ResNet50", "facexlib v0.1.0 release", "MIT (code; checkpoint terms not separately stated)", "Jiankang Deng, biubug6 / Pytorch_Retinaface contributors; packaged by Xintao Wang", "https://github.com/xinntao/facexlib/releases/tag/v0.1.0", "models/face/detection_Resnet50_Final.pth", ["licenses/pytorch-retinaface/LICENSE.txt", "licenses/facexlib/LICENSE"], "Source implementation: https://github.com/biubug6/Pytorch_Retinaface. Release does not state a separate checkpoint license."),
        ("parsenet", "ParseNet face parsing", "facexlib v0.2.2 release", "MIT (facexlib); CC-BY-NC-SA-4.0 (PSFR-GAN source)", "Chaofeng Chen / PSFR-GAN contributors; adapted by Xintao Wang / facexlib", "https://github.com/xinntao/facexlib/releases/tag/v0.2.2", "models/face/parsing_parsenet.pth", ["licenses/facexlib/LICENSE", "licenses/psfrgan/LICENSE.txt"], "facexlib/parsing/parsenet.py says it is modified from https://github.com/chaofengc/PSFRGAN, whose source license is CC-BY-NC-SA-4.0. The checkpoint release does not separately state its license. Library and model terms must not be treated as interchangeable."),
    ]
    for ident, name, version, license_id, author, source, file, license_files, notes in model_specs:
        path = ROOT / file
        if not path.is_file():
            continue
        h = hashlib.sha256()
        with path.open("rb") as stream:
            while chunk := stream.read(4 * 1024 * 1024):
                h.update(chunk)
        entries.append(dict(id=ident, name=name, version=version, license=license_id, author=author, source=source,
                            license_files=license_files, kind="model", model_file=file, sha256=h.hexdigest(), notes=notes))
    # Retain an explicit entry for the adapted parsing source, separate from its weights.
    entries.append(dict(id="psfrgan-source", name="PSFR-GAN / ParseNet source", version="upstream source; no version declared", license="CC-BY-NC-SA-4.0", author="Chaofeng Chen and contributors", source="https://github.com/chaofengc/PSFRGAN", license_files=["licenses/psfrgan/LICENSE.txt"], kind="source", notes="ParseNet in facexlib identifies this project as its source. This credit concerns source code; checkpoint licensing is listed separately."))
    for entry in entries:
        for file in entry["license_files"]:
            if not (ROOT / file).is_file():
                raise RuntimeError(f"Missing license file: {file}")
    (LICENSES / "components.json").write_text(json.dumps({"schema_version": 1, "components": entries}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    notices = ["ARM AI Image Enhancer — THIRD-PARTY NOTICES", "",
               "Versions below describe the configured runtime and bundled model files.",
               "Full original license/copyright/NOTICE texts are in the licenses folder.",
               "Model files and library code are listed separately; a project license is",
               "not a blanket assertion of separate checkpoint or training-data rights.", ""]
    for entry in entries:
        notices += [f"{entry['name']} — {entry['version']}", f"Type: {entry['kind']}", f"License: {entry['license']}",
                    f"Developers: {entry['author']}", f"Source: {entry['source']}", "License files: " + ", ".join(entry["license_files"])]
        if entry.get("sha256"):
            notices += [f"Model file: {entry['model_file']}", f"SHA-256: {entry['sha256']}"]
        if entry["notes"]:
            notices += [entry["notes"]]
        notices += [""]
    (ROOT / "THIRD_PARTY_NOTICES.txt").write_text("\n".join(notices) + "\n", encoding="utf-8")
    print(f"Collected {len(entries)} components; {sum(e['kind']=='model' for e in entries)} model files")

if __name__ == "__main__":
    collect()
