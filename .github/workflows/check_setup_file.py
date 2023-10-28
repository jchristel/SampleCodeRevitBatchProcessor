import os
import re

def set_action_output(value):
    """Sets the GitHub Action output.

    Keyword arguments:
    output_name - The name of the output
    value - The value of the output
    """
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            print("changed_files={0}".format(value), file=f)
    else:
        print("GITHUB_OUTPUT environment variable not set. Output not set.")

def check_setup_cfg_file():
    modified_files = []
    # Get the root directory of the repo in the workflow 
    root_dir = os.getenv("GITHUB_WORKSPACE")

    # Setup.cfg version number is not enclosed by quptation marks
    setup_cfg_file = os.path.join(root_dir, "setup.cfg")

    with open(setup_cfg_file, "r") as fr:
        content = fr.read()

        setup_cfg_ver_num = content.split("version = ")[1].split('\n')[0]
        print("setup.cfg version number is: " + setup_cfg_ver_num)

    # files which contain a version string
    # first value entry is the string preceding the version number,
    # second value entry is the file path of the file in the repo
    tag_locations = {
        "conf.py":("release",os.path.join(root_dir, "docsource", "conf.py")),
        "pyproject.toml":("current_version" ,os.path.join(root_dir, "pyproject.toml")),
    }

    # loop over files and update version number 
    for key, value in tag_locations.items():
        # read file content and replace version string
        with open(value[1], "r") as fr:
            content = fr.read()

            ver_num = content.split(value[0])[1].split('\n')[0]
            print("{} version number is: {}".format(key, ver_num))

            if str(setup_cfg_ver_num) in ver_num:
                print("Version number in {} is up to date".format(key))
            else:
                content = re.sub(
                            r'{} = "\d*.\d*.\d*"'.format(value[0]),
                            '{} = "{}"'.format(value[0], setup_cfg_ver_num),
                            content,
                        )
                print("Version number updated for {}".format(key))
                modified_files.append(value[1])
                
        # write file content out
        with open(value[1], "w") as fw:
            fw.write(content)

    # Set the changed files output of the action
    if len(modified_files) == 0:
        set_action_output("No files changed")
    else:
        set_action_output("{} files changed".format(len(modified_files)))

    return modified_files

if __name__ == "__main__":
    check_setup_cfg_file()
    
    