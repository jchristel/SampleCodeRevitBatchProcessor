import os
import re


def set_version_from_tag():
    # Get the version number from the tag on the newly published release
    tag_num = os.environ["TAG_NUM"]
    print("Tag num environment variable is: " + tag_num)

    # If the tag number is not set, then exit
    if tag_num is None or tag_num == "":
        print("TAG_NUM environment variable not set. Version not set.")
        return

    # If the tag number starts with a "v", then remove it so it's numbers only
    if tag_num.startswith("v"):
        tag_num = tag_num[1:]

    print("Tag number is: " + tag_num)

    # Get the root directory of the repo in the workflow
    root_dir = os.getenv("GITHUB_WORKSPACE")

    # files which contain a version string
    # first value entry is the string preceding the version number,
    # second value entry is the file path of the file in the repo
    tag_locations = {
        "conf.py": ("release", os.path.join(root_dir, "docsource", "conf.py")),
        "pyproject.toml": ("current_version", os.path.join(root_dir, "pyproject.toml")),
    }

    # loop over files and update version number
    for key, value in tag_locations.items():
        # read file content and replace version string
        with open(value[1], "r") as fr:
            content = fr.read()

            ver_num = content.split(value[0])[1].split("\n")[0]
            print("{} version number is: {}".format(key, ver_num))
            try:
                content = re.sub(
                    r'{} = "\d.\d.\d"'.format(value[0]),
                    '{} = "{}"'.format(value[0], tag_num),
                    content,
                )
                print("Updated {} version number to: {}".format(key, tag_num))
            except:
                print("Failed to update {} version number".format(key))

        # write file content out
        with open(value[1], "w") as fw:
            fw.write(content)

    # Setup.cfg version number is not enclosed by quptation marks
    setup_cfg_file = os.path.join(root_dir, "setup.cfg")

    with open(setup_cfg_file, "r") as fr:
        content = fr.read()

        setup_cfg_ver_num = content.split("version = ")[1].split("\n")[0]
        print("setup.cfg version number is: " + setup_cfg_ver_num)
        try:
            content = re.sub(
                r"version = \d.\d.\d",
                "version = {}".format(tag_num),
                content,
            )
            print("Updated setup.cfg version number to: " + tag_num)
        except:
            print("Failed to update setup.cfg version number")

    with open(setup_cfg_file, "w") as fw:
        fw.write(content)


if __name__ == "__main__":
    set_version_from_tag()
