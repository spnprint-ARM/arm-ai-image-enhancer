# Installer V2.2.7 fixes

- Uninstall confirmation uses the embedded lang.png icon; the selector is 6 pixels from the icon.
- Disk-space details use the label's preferred wrapped height; status, progress, options, and buttons move down by the added height. The form supports scrolling.
- Staging is a unique sibling of the installation directory, rather than the elevated user's Temp directory. Directory moves and cleanup retry transient I/O/access failures. A failed staging rename falls back to copying, checking additional free space first.
- Partial copy destinations are marked for rollback before copying starts. Existing installation backup/restore remains active. Staging cleanup after commit cannot roll back a valid installation.

## Outputs

The corrected distribution is in C:\ArmAI\installer\fixed-v227. Keep setup-V.2.2.7.exe and both matching .dat parts together. The old distribution in the installer directory has been preserved.

The new Uninstall.exe is included in the corrected payload; existing installed V2.2.6 uninstallers change only after an upgrade.

## Validation

The source compiles with the .NET Framework C# compiler. installer/tests/InstallerTests.cs exercises all four language layouts, the uninstall icon spacing, transient operation retry, a synthetic upgrade, copying with an open staging handle, empty directory preservation, staging cleanup, invalid archive rejection, and cancellation. These tests use workspace destinations without writing system registration.

The final executable's InspectPayload was also invoked against both split data files and its English page rendered for visual inspection. This does not reproduce every administrator account or antivirus policy on the user's installation machine.

To compile the test harness, include Setup.cs, the test source, and a generated assembly version file; use /main:InstallerTests /target:exe /platform:x64, references to System.Windows.Forms, System.Drawing, System.IO.Compression, System.IO.Compression.FileSystem, and embed assets/lang.png as lang.png.

The payload was assembled from the original V2.2.7 .dat parts, retaining application files and replacing the central-directory entry for Uninstall.exe with the newly compiled binary. ZIP entries contain one Uninstall.exe.
Final verification passed: SHA-256 of the concatenated split data matches the assembled payload; CRC verification passed for all 5,184 ZIP entries; the bundled Uninstall.exe matches the rebuilt binary.
