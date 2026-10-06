# ARM AI Image Enhancer

Windows desktop application for enlarging and preparing images for print.

## Project layout

- `app/` contains the application source.
- `assets/` contains the application logo, language icon, QR image, and icon.
- `installer/` contains the installer source and build scripts.
- `inference_realesrgan.py` contains the image inference entry point.

AI model weights, local Python environments, generated builds, user settings, and release installers are excluded from Git. The installer build script uses the configured Windows Python environment and writes generated files to the build output directory.

## Third-party licenses

Help > Third-party licenses and credits opens an offline component browser. The
source catalog is licenses/components.json; full upstream license and NOTICE
texts are kept under licenses/, and THIRD_PARTY_NOTICES.txt is the readable index.

To refresh versions and copied license files for the configured runtime, run
.venv\Scripts\python.exe tools\collect_third_party_licenses.py. This only updates
notices and does not build the application. The collector fails when a runtime
dependency has no available full license text. Upstream fallback license files
are checked in for packages that omit them from their wheels.

Model entries are separate from library entries. Their release tags and SHA-256
hashes identify the bundled files. Checkpoint terms that upstream has not stated
separately are identified explicitly. ParseNet's PSFR-GAN source credit retains
its CC-BY-NC-SA-4.0 text, separately from the facexlib MIT license.

Future packaging copies licenses/ and THIRD_PARTY_NOTICES.txt next to the
application executable. Refresh the catalog before building with a changed
runtime or replacing model files.
