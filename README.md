# ARM AI Image Enhancer

Windows desktop application for enlarging and preparing images for print.

## Project layout

- `app/` contains the application source.
- `assets/` contains the application logo, language icon, QR image, and icon.
- `installer/` contains the installer source and build scripts.
- `inference_realesrgan.py` contains the image inference entry point.

AI model weights, local Python environments, generated builds, user settings, and release installers are excluded from Git. The installer build script uses the configured Windows Python environment and writes generated files to the build output directory.
