# -*- mode: python ; coding: utf-8 -*-
import importlib.util
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = [
    # The packaged GUI is Tkinter based. Include it explicitly because
    # PyInstaller can silently omit it when the build host's Tcl/Tk probing
    # fails, which otherwise produces an app that installs but cannot launch.
    '_tkinter',
    'tkinter',
    'tkinter.filedialog',
    'tkinter.font',
    'tkinter.messagebox',
    'tkinter.simpledialog',
    'tkinter.ttk',
    'basicsr.archs.rrdbnet_arch',
    # basicsr.data imports dataset modules dynamically by scanning data/*.py;
    # reds_dataset then imports this utility, which PyInstaller cannot infer.
    'basicsr.utils.flow_util',
    'realesrgan.archs.srvgg_arch',
    'gfpgan.archs.gfpganv1_clean_arch',
    'facexlib.utils.face_restoration_helper',
    'simple_lama_inpainting',
    'simple_lama_inpainting.models.model',
    'simple_lama_inpainting.utils.util',
]
for package in (
    'basicsr.archs', 'basicsr.losses', 'basicsr.models',
    'realesrgan.archs', 'realesrgan.data', 'realesrgan.models',
    'gfpgan.archs', 'gfpgan.data', 'gfpgan.models',
):
    hiddenimports += collect_submodules(package)
hiddenimports += collect_submodules('facexlib.detection')
hiddenimports += collect_submodules('simple_lama_inpainting')

# The bundled build runtime keeps tkinter/Tcl outside site-packages. Explicitly
# expose them to Analysis so a failed Tcl/Tk probe cannot silently omit the GUI.
runtime_root = Path(sys.base_prefix).resolve()
runtime_python_lib = runtime_root / 'Lib'
runtime_tcl = runtime_root / 'tcl'
if not (runtime_python_lib / 'tkinter' / '__init__.py').is_file():
    raise RuntimeError('tkinter source not found in runtime: ' + str(runtime_python_lib))
if not (runtime_tcl / 'tcl8.6' / 'init.tcl').is_file():
    raise RuntimeError('Tcl runtime not found in runtime: ' + str(runtime_tcl))
tkinter_source_files = [
    (str(path), 'tkinter/' + path.parent.relative_to(runtime_python_lib / 'tkinter').as_posix())
    for path in sorted((runtime_python_lib / 'tkinter').rglob('*.py'))
]
if not tkinter_source_files:
    raise RuntimeError('tkinter source files were not found in runtime')

# These packages discover architecture modules by scanning the on-disk
# *_arch.py files at import time. PyInstaller's PYZ archive alone does not
# create those folders, so include the source files as data as well.
dynamic_arch_files = []
dynamic_data_files = []
for package in ('basicsr', 'realesrgan', 'gfpgan'):
    package_spec = importlib.util.find_spec(package)
    if package_spec is None or not package_spec.origin:
        raise RuntimeError('Required package not found while building: ' + package)
    arch_folder = Path(package_spec.origin).parent / 'archs'
    if not arch_folder.is_dir():
        raise RuntimeError('Required architecture folder not found: ' + str(arch_folder))
    dynamic_arch_files.extend(
        (str(path), package + '/archs') for path in sorted(arch_folder.glob('*.py'))
    )

# BasicSR scans its package's data directory from the filesystem at import
# time. Include the source files as data so this directory exists in the
# frozen app (the Python modules in the PYZ archive are not enough).
basicsr_spec = importlib.util.find_spec('basicsr')
if basicsr_spec is None or not basicsr_spec.origin:
    raise RuntimeError('Required package not found while building: basicsr')
basicsr_root = Path(basicsr_spec.origin).parent
data_folder = basicsr_root / 'data'
if not data_folder.is_dir():
    raise RuntimeError('Required BasicSR data folder not found: ' + str(data_folder))
dynamic_data_files.extend(
    (str(path), 'basicsr/' + path.relative_to(basicsr_root).parent.as_posix())
    for path in sorted(data_folder.rglob('*.py'))
)

# BasicSR, Real-ESRGAN and GFPGAN scan these folders at runtime to discover
# losses, datasets and models. Include their sources as data as well as hidden
# imports so both the scan and the later dynamic imports work in the frozen app.
dynamic_scanned_files = []
runtime_scanned_dirs = {
    'basicsr': ('losses', 'models'),
    'realesrgan': ('data', 'models'),
    'gfpgan': ('data', 'models'),
}
for package, folders in runtime_scanned_dirs.items():
    package_spec = importlib.util.find_spec(package)
    if package_spec is None or not package_spec.origin:
        raise RuntimeError('Required package not found while building: ' + package)
    package_root = Path(package_spec.origin).parent
    for folder_name in folders:
        folder = package_root / folder_name
        if not folder.is_dir():
            raise RuntimeError('Required runtime-scanned folder not found: ' + str(folder))
        dynamic_scanned_files.extend(
            (str(path), package + '/' + folder_name)
            for path in sorted(folder.glob('*.py'))
        )


a = Analysis(
    ['C:/ArmAI/app/gui/main.py'],
    pathex=['C:/ArmAI', str(runtime_python_lib)],
    binaries=[],
    datas=[('C:/ArmAI/models', 'models'), ('C:/ArmAI/assets', 'assets'),
           (str(runtime_tcl), 'tcl'),
           (str(Path(SPECPATH) / 'ARM.ico'), '.')] + tkinter_source_files + dynamic_arch_files + dynamic_data_files + dynamic_scanned_files,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ArmAIImageEnhancer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(Path(SPECPATH) / 'ARM.ico'),
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='ArmAIImageEnhancer',
)
