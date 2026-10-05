import os
import sys
import zipfile


def main():
    source, destination = sys.argv[1:3]
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=1, allowZip64=True) as archive:
        for root, dirs, files in os.walk(source):
            dirs.sort()
            files.sort()
            for filename in files:
                path = os.path.join(root, filename)
                name = os.path.relpath(path, source).replace(os.sep, "/")
                archive.write(path, name)
    print(os.path.getsize(destination))


if __name__ == "__main__":
    main()
