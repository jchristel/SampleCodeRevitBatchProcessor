import os
import re


def update_package_config():
    """
    Update version and package name based on tag and branch.
    """
    # Get the version number from the tag on the newly published release
    tag_num = os.environ.get("TAG_NUM", "")
    package_name = os.environ.get("PACKAGE_NAME", "")
    
    print(f"Tag num environment variable is: {tag_num}")
    print(f"Package name environment variable is: {package_name}")

    # If the tag number is not set, then exit
    if not tag_num:
        print("TAG_NUM environment variable not set. Version not set.")
        return
    
    # If the package name is not set, then exit
    if not package_name:
        print("PACKAGE_NAME environment variable not set. Package name not set.")
        return

    # If the tag number starts with a "v", then remove it so it's numbers only
    if tag_num.startswith("v"):
        tag_num = tag_num[1:]

    print(f"Tag number is: {tag_num}")
    print(f"Package name is: {package_name}")

    # Get the root directory of the repo in the workflow
    root_dir = os.getenv("GITHUB_WORKSPACE")

    # Files which contain a version string
    # First value entry is the string preceding the version number,
    # Second value entry is the file path of the file in the repo
    tag_locations = {
        "conf.py": ("release", os.path.join(root_dir, "docsource", "conf.py")),
        "pyproject.toml": ("current_version", os.path.join(root_dir, "pyproject.toml")),
    }

    # Loop over files and update version number
    for key, value in tag_locations.items():
        # Read file content and replace version string
        try:
            with open(value[1], "r") as fr:
                content = fr.read()

            ver_num = content.split(value[0])[1].split("\n")[0]
            print(f"{key} version number is: {ver_num}")
            
            # Update version using more flexible regex pattern
            content = re.sub(
                rf'{re.escape(value[0])} = "\d+\.\d+\.\d+"',
                f'{value[0]} = "{tag_num}"',
                content,
            )
            print(f"Updated {key} version number to: {tag_num}")
            
            # For pyproject.toml, also update the project version
            if key == "pyproject.toml":
                content = re.sub(
                    r'version = "\d+\.\d+\.\d+"',
                    f'version = "{tag_num}"',
                    content,
                )
                print(f"Updated {key} project version to: {tag_num}")
                
        except Exception as e:
            print(f"Failed to update {key} version number: {e}")
            continue

        # Write file content out
        try:
            with open(value[1], "w") as fw:
                fw.write(content)
        except Exception as e:
            print(f"Failed to write {key}: {e}")

    # Update setup.cfg with both version and package name
    setup_cfg_file = os.path.join(root_dir, "setup.cfg")

    try:
        with open(setup_cfg_file, "r") as fr:
            content = fr.read()

        setup_cfg_ver_num = content.split("version = ")[1].split("\n")[0]
        print(f"setup.cfg version number is: {setup_cfg_ver_num}")
        
        # Update version
        content = re.sub(
            r"version = \d+\.\d+\.\d+",
            f"version = {tag_num}",
            content,
        )
        print(f"Updated setup.cfg version number to: {tag_num}")
        
        # Update package name
        content = re.sub(
            r"name = \w+",
            f"name = {package_name}",
            content,
        )
        print(f"Updated setup.cfg package name to: {package_name}")
        
    except Exception as e:
        print(f"Failed to update setup.cfg: {e}")
        return

    try:
        with open(setup_cfg_file, "w") as fw:
            fw.write(content)
        print("Successfully wrote setup.cfg")
    except Exception as e:
        print(f"Failed to write setup.cfg: {e}")

    # Update pyproject.toml package name as well
    pyproject_file = os.path.join(root_dir, "pyproject.toml")
    try:
        with open(pyproject_file, "r") as fr:
            content = fr.read()
        
        # Update package name in project section (supports any package name)
        content = re.sub(
            r'name = "[^"]+"',
            f'name = "{package_name}"',
            content,
        )
        print(f"Updated pyproject.toml package name to: {package_name}")
        
        with open(pyproject_file, "w") as fw:
            fw.write(content)
        print("Successfully updated pyproject.toml package name")
        
    except Exception as e:
        print(f"Failed to update pyproject.toml package name: {e}")


if __name__ == "__main__":
    update_package_config()