"""
Builds a ready to install copy of the duHast pyRevit extension.

- copies the extension folder from Samples/pyRevit/Extensions into an output folder
- bundles the duHast library from src/duHast (including its lib DLLs) into the extension lib folder
- fills the extension bin folder with the DLLs built by Visual Studio (VS/**/bin/x64/<configuration>)
- writes the version into extension.json and lib/duHast/_bundled_version.txt
- zips the result

Usage (from anywhere, Python 3):

    python Samples/pyRevit/installer/build_extension.py
    python Samples/pyRevit/installer/build_extension.py --version 1.0.5 --configuration Release
    python Samples/pyRevit/installer/build_extension.py --bin-from committed

"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2026, Jan Christel
# All rights reserved.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

# - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
#
# This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
# In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
# or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
#
#
#

import argparse
import fnmatch
import json
import os
import re
import shutil
import sys
import zipfile

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(SCRIPT_DIR, "..", "..", ".."))

EXTENSIONS_DIR = os.path.join(REPO_ROOT, "Samples", "pyRevit", "Extensions")
DUHAST_SRC_DIR = os.path.join(REPO_ROOT, "src", "duHast")
VS_ROOT = os.path.join(REPO_ROOT, "VS")
PYPROJECT = os.path.join(REPO_ROOT, "pyproject.toml")
BIN_MANIFEST = os.path.join(SCRIPT_DIR, "bin_manifest.txt")

DEFAULT_EXTENSION = "duHast-2025.extension"
DEFAULT_OUTPUT_DIR = os.path.join(REPO_ROOT, "dist", "pyRevit")

# files and folders never copied into the extension
EXCLUDE_PATTERNS = ["__pycache__", "*.pyc", ".DS_Store", "Thumbs.db"]

# additionally excluded when copying duHast (sphinx sources and notes, not needed at run time)
DUHAST_EXCLUDE_PATTERNS = EXCLUDE_PATTERNS + ["*.rst", "*.md"]

# VS projects whose output is never shipped
VS_EXCLUDE_PROJECT_PATTERNS = ["*Test", "*Tester", "*Tests"]

# file name written into lib/duHast holding the bundled version
BUNDLED_VERSION_FILE = "_bundled_version.txt"


class BuildError(Exception):
    pass


def read_version_from_pyproject(pyproject_path=PYPROJECT):
    """
    Reads the version from pyproject.toml (the release workflow keeps it in sync with the release tag).

    :param pyproject_path: Fully qualified path to pyproject.toml
    :type pyproject_path: str

    :return: The version, e.g. 1.0.5
    :rtype: str
    """
    with open(pyproject_path, "r", encoding="utf-8") as f:
        for line in f:
            match = re.match(r'^version\s*=\s*"([^"]+)"', line)
            if match:
                return match.group(1)
    raise BuildError("No version found in {}".format(pyproject_path))


def read_bin_manifest(manifest_path=BIN_MANIFEST):
    """
    Reads the names of the DLLs the extension bin folder needs.

    A name may be given without its version suffix: PushIt matches PushIt.dll and PushIt.25.0.1.2.dll

    :param manifest_path: Fully qualified path to the manifest file
    :type manifest_path: str

    :return: List of DLL base names
    :rtype: [str]
    """
    names = []
    with open(manifest_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].strip()
            if line:
                names.append(line)
    return names


def _is_excluded(name, patterns):
    return any(fnmatch.fnmatch(name, pattern) for pattern in patterns)


def _ignore(patterns):
    def ignore(directory, names):
        return [name for name in names if _is_excluded(name, patterns)]

    return ignore


def _version_key(version_string):
    return tuple(int(part) for part in version_string.split(".")) if version_string else ()


def find_vs_output_dlls(vs_root, configuration):
    """
    Finds all DLLs in the Visual Studio output folders (<project>/bin/x64/<configuration>, including sub folders
    such as runtimes/win-x64/native), skipping test projects.

    :param vs_root: Root folder of the Visual Studio solutions
    :type vs_root: str
    :param configuration: The build configuration, e.g. Release
    :type configuration: str

    :return: List of fully qualified DLL paths
    :rtype: [str]
    """
    found = []
    output_marker = os.path.join("bin", "x64", configuration)
    for root, dirs, files in os.walk(vs_root):
        # don't descend into intermediate build folders or test projects
        dirs[:] = [
            d
            for d in dirs
            if d != "obj" and not _is_excluded(d, VS_EXCLUDE_PROJECT_PATTERNS)
        ]
        if output_marker not in root:
            continue
        for file_name in files:
            if file_name.lower().endswith(".dll"):
                found.append(os.path.join(root, file_name))
    return found


def select_dll(base_name, dll_paths):
    """
    Picks the DLL for a manifest entry: the highest version suffix wins, then the most recently built file.

    :param base_name: Manifest entry, e.g. PushIt or Newtonsoft.Json
    :type base_name: str
    :param dll_paths: Candidate DLL paths
    :type dll_paths: [str]

    :return: The selected DLL path or None if no match was found
    :rtype: str or None
    """
    pattern = re.compile(
        r"^{}(?:\.(\d+(?:\.\d+)*))?\.dll$".format(re.escape(base_name)), re.IGNORECASE
    )
    matches = []
    for path in dll_paths:
        match = pattern.match(os.path.basename(path))
        if match:
            matches.append((_version_key(match.group(1)), os.path.getmtime(path), path))
    if not matches:
        return None
    return max(matches)[2]


def fill_bin_from_vs_output(bin_dir, manifest_names, vs_root, configuration):
    """
    Copies the DLLs listed in the manifest from the Visual Studio output folders into the extension bin folder.

    :return: List of copied DLL paths (source)
    :rtype: [str]
    """
    dll_paths = find_vs_output_dlls(vs_root, configuration)
    selected = []
    missing = []
    for name in manifest_names:
        dll = select_dll(name, dll_paths)
        if dll is None:
            missing.append(name)
        else:
            selected.append(dll)
    if missing:
        raise BuildError(
            "No Visual Studio build output ({}) found for: {}\n"
            "Build the solutions in {} first, or use --bin-from committed.".format(
                configuration, ", ".join(missing), vs_root
            )
        )
    os.makedirs(bin_dir, exist_ok=True)
    for dll in selected:
        shutil.copy2(dll, os.path.join(bin_dir, os.path.basename(dll)))
    return selected


def check_bin_against_manifest(bin_dir, manifest_names):
    """
    Checks the committed bin folder holds every DLL in the manifest.
    """
    dll_paths = [
        os.path.join(bin_dir, f) for f in os.listdir(bin_dir) if f.lower().endswith(".dll")
    ]
    missing = [name for name in manifest_names if select_dll(name, dll_paths) is None]
    if missing:
        raise BuildError(
            "Committed bin folder {} is missing: {}".format(bin_dir, ", ".join(missing))
        )


def write_version(extension_dir, duhast_dir, version):
    """
    Writes the version into extension.json and the bundled duHast version file.
    """
    extension_json = os.path.join(extension_dir, "extension.json")
    with open(extension_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["version"] = version
    with open(extension_json, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    with open(os.path.join(duhast_dir, BUNDLED_VERSION_FILE), "w", encoding="utf-8") as f:
        f.write(version + "\n")


def zip_extension(extension_dir, zip_path):
    """
    Zips the extension folder, keeping the extension folder as the top level entry.
    """
    parent = os.path.dirname(extension_dir)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(extension_dir):
            dirs.sort()
            for file_name in sorted(files):
                full_path = os.path.join(root, file_name)
                zf.write(full_path, os.path.relpath(full_path, parent))


def build(
    extension_name=DEFAULT_EXTENSION,
    version=None,
    output_dir=DEFAULT_OUTPUT_DIR,
    bin_from="vs",
    configuration="Release",
    vs_root=VS_ROOT,
    make_zip=True,
):
    """
    Builds the extension. Returns the path of the built extension folder and the zip file (or None).
    """
    source_extension_dir = os.path.join(EXTENSIONS_DIR, extension_name)
    if not os.path.isdir(source_extension_dir):
        raise BuildError("Extension not found: {}".format(source_extension_dir))

    version = version or read_version_from_pyproject()
    manifest_names = read_bin_manifest()

    # start from a clean output folder for this extension
    os.makedirs(output_dir, exist_ok=True)
    extension_dir = os.path.join(output_dir, extension_name)
    if os.path.exists(extension_dir):
        shutil.rmtree(extension_dir)

    print("Copying extension {}".format(extension_name))
    shutil.copytree(
        source_extension_dir,
        extension_dir,
        ignore=_ignore(EXCLUDE_PATTERNS + (["bin"] if bin_from == "vs" else [])),
    )

    # extension wide lib folder: replace whatever is there with the bundled duHast
    lib_dir = os.path.join(extension_dir, "lib")
    duhast_dir = os.path.join(lib_dir, "duHast")
    if os.path.exists(duhast_dir):
        shutil.rmtree(duhast_dir)
    print("Bundling duHast from {}".format(DUHAST_SRC_DIR))
    shutil.copytree(DUHAST_SRC_DIR, duhast_dir, ignore=_ignore(DUHAST_EXCLUDE_PATTERNS))

    bin_dir = os.path.join(extension_dir, "bin")
    if bin_from == "vs":
        print("Filling bin from Visual Studio output ({})".format(configuration))
        copied = fill_bin_from_vs_output(bin_dir, manifest_names, vs_root, configuration)
        for dll in copied:
            print("  {}".format(os.path.relpath(dll, vs_root)))
    else:
        print("Using committed bin folder")
        check_bin_against_manifest(bin_dir, manifest_names)

    write_version(extension_dir, duhast_dir, version)

    zip_path = None
    if make_zip:
        zip_path = os.path.join(
            output_dir, "{}-v{}.zip".format(extension_name, version)
        )
        if os.path.exists(zip_path):
            os.remove(zip_path)
        zip_extension(extension_dir, zip_path)

    return extension_dir, zip_path


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Build the duHast pyRevit extension with duHast bundled."
    )
    parser.add_argument(
        "--extension",
        default=DEFAULT_EXTENSION,
        help="Extension folder name in Samples/pyRevit/Extensions (default: %(default)s)",
    )
    parser.add_argument(
        "--version", help="Version to write into the extension (default: pyproject.toml)"
    )
    parser.add_argument(
        "--output", default=DEFAULT_OUTPUT_DIR, help="Output folder (default: %(default)s)"
    )
    parser.add_argument(
        "--bin-from",
        choices=["vs", "committed"],
        default="vs",
        help="vs: fill bin from the Visual Studio build output (default); "
        "committed: use the bin folder committed with the extension",
    )
    parser.add_argument(
        "--configuration",
        default="Release",
        help="Visual Studio build configuration (default: %(default)s)",
    )
    parser.add_argument(
        "--vs-root", default=VS_ROOT, help="Visual Studio solutions root (default: %(default)s)"
    )
    parser.add_argument("--no-zip", action="store_true", help="Do not create the zip file")
    args = parser.parse_args(argv)

    try:
        extension_dir, zip_path = build(
            extension_name=args.extension,
            version=args.version,
            output_dir=args.output,
            bin_from=args.bin_from,
            configuration=args.configuration,
            vs_root=args.vs_root,
            make_zip=not args.no_zip,
        )
    except BuildError as e:
        print("Build failed: {}".format(e), file=sys.stderr)
        return 1

    print("Extension: {}".format(extension_dir))
    if zip_path:
        print("Zip:       {}".format(zip_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
