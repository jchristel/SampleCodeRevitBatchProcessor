import clr, os, sys, getopt

clr.AddReferenceByPartialName("PresentationCore")
clr.AddReferenceByPartialName("PresentationFramework")
clr.AddReferenceByPartialName("WindowsBase")
clr.AddReferenceByPartialName("IronPython")
clr.AddReferenceByPartialName("Microsoft.Scripting")

from System.Windows import Application

# define path to duHast
# to get to the root folder of this repo if this script is called directly from a powershell, batch or similar
ROOT_REPO_DIRECTORY = os.path.join(
    os.path.realpath(__file__), os.pardir, os.pardir, os.pardir, os.pardir
)
sys.path.insert(0, ROOT_REPO_DIRECTORY)


# import UI helper
from duHast.UI import file_list as fl
from duHast.UI.Objects.file_select_settings import FileSelectionSettings
from duHast.UI.file_list import get_revit_files_for_processing
from duHast.UI.Objects.XamlLoader import XamlLoader
from duHast.UI import workloader as wl

from duHast.Utilities.files_io import file_exist
from duHast.Utilities.directory_io import directory_exists
from duHast.Utilities.console_out import output_with_time_stamp

# xaml helper classes
from ViewModel import ViewModel

# Define the path to your XAML file
CURRENT_SCRIPT_DIRECTORY = os.path.dirname(__file__)
XAML_FILE = "ui_v2.xaml"  # Replace with your XAML file name
XAML_FULL_FILE_NAME = os.path.join(CURRENT_SCRIPT_DIRECTORY, XAML_FILE)


def main(argv):
    """
    Entry point.

    :param argv: A list of string representing arguments past in.
    :type argv: [str]
    """

    # get arguments
    got_args, settings = process_args(argv)
    if got_args:
        # retrieve revit file data
        revit_files = get_revit_files_for_processing(
            settings.input_directory,
            settings.incl_sub_dirs,
            settings.revit_file_extension,
        )
        # check whether this is a BIM360 project or file system and assign
        # data retriever method accordingly
        if is_bim_360_file(revit_files):
            get_data = fl.bucket_to_task_list_bim_360
        else:
            get_data = fl.bucket_to_task_list_file_system

        # check if anything came back
        if len(revit_files) > 0:
            # load xaml
            xaml = XamlLoader(XAML_FULL_FILE_NAME)
            # forms window
            window = xaml.Root

            # view model initialise
            view_model = ViewModel(
                window,
                settings.input_directory,
                settings.output_dir,
                settings.revit_file_extension,
                settings.output_file_num,
                settings.incl_sub_dirs,
                settings.filters,
                settings.filter_type,
            )
            # assign view model to xaml
            xaml.Root.DataContext = view_model

            # show application
            Application().Run(xaml.Root)

            # debugging
            """
            print("Destination Path {}".format(xaml.Root.DataContext.destination_path))
            print("Source Path {}".format(xaml.Root.DataContext.source_path))
            print(
                "Source File Extension {}".format(
                    xaml.Root.DataContext.source_file_extension
                )
            )
            print(
                "Include sub dirs {}\n".format(xaml.Root.DataContext.include_sub_dirs)
            )
            print("selected files {}\n".format(len(view_model.selected_files)))
            print("filter {}\n".format(view_model.filter_text))
            for rf in view_model.revit_files:
                print("file {}".format(rf.name))
            for frf in view_model.filtered_revit_files:
                print("filtered files: {}".format(frf.name))
            print("debug {}".format("\n".join(view_model.debug)))
            """

            # get the dialog result (ok vs cancel buttons)
            ui_result = view_model.DialogResult
            if ui_result:
                # build bucket list
                buckets = wl.distribute_workload(
                    settings.output_file_num,
                    view_model.selected_files,
                    fl.get_file_size,
                )
                # write out file lists
                counter = 0
                for bucket in buckets:
                    file_name = os.path.join(
                        settings.output_dir, "Tasklist_" + str(counter) + ".txt"
                    )
                    status_write = fl.write_revit_task_file(file_name, bucket, get_data)
                    output_with_time_stamp(status_write.message)
                    counter += 1
                output_with_time_stamp("Finished writing out task files")
                sys.exit(0)
            else:
                # do nothing...
                output_with_time_stamp("No files selected!")
                sys.exit(2)
        else:
            # show message box
            output_with_time_stamp(
                "No files found matching extension: {} in location: {}!".format(
                    settings.revit_file_extension, settings.input_directory
                )
            )
            sys.exit(2)
    else:
        # invalid or no args provided... get out
        sys.exit(1)


def process_args(argv):
    """
    Processes past in arguments and checks whether inputs are valid.

    :param argv: List of arguments
    :type argv: _type_

    :return:
        - True if arguments past in are valid, otherwise False.
        - FIle select settings object instance.
    :rtype: bool, :class:`.FileSelectionSettings`
    """

    input_dir_file = ""
    output_directory = ""
    output_file_number = 1
    revit_file_extension = ".rvt"
    include_sub_dirs_in_search = False
    got_args = False
    try:
        opts, args = getopt.getopt(
            argv,
            "hsxi:o:n:e:f:",
            [
                "subDir",
                "TextFilterIsOR",
                "inputDirectory=",
                "outputDirectory=",
                "numberOfOutputFiles=",
                "fileExtension=",
                "filterText=",
            ],
        )
    except getopt.GetoptError as e:
        output_with_time_stamp(
            "file_select_ui.py -s -x <TextFilterIsOR> -i <inputDirectory> -o <outputDirectory> -n <numberOfOutputFiles> -e <fileExtension> -f <filterText> failed with exception: {}".format(
                e
            )
        )

    # set a default value (True) for the filter type
    filter_is_and = True
    # set default value for text filters
    filter_rules = []

    # check what args have been provided
    for opt, arg in opts:
        if opt == "-h":
            output_with_time_stamp(
                "file_select_ui.py -s <include sub dir> -x <TextFilterIsOR> -i <inputPath> -o <outputDirectory> -n <numberOfOutputFiles> -e <fileExtension> -f <filterText>"
            )
        elif opt in ("-s", "--subDir"):
            include_sub_dirs_in_search = True
        elif opt in ("-x", "--TextFilterIsOR"):
            filter_is_and = False
        elif opt in ("-i", "--inputDirectory"):
            input_dir_file = arg
            got_args = True
        elif opt in ("-o", "--outputDirectory"):
            output_directory = arg
            got_args = True
        elif opt in ("-n", "--numberOfOutputFiles"):
            try:
                value = int(arg)
                output_file_number = value
                got_args = True
            except ValueError:
                output_with_time_stamp("{}: value is not an integer".format(arg))
                got_args = False
        elif opt in ("-e", "--fileExtension"):
            revit_file_extension = arg.strip()
            got_args = True
        elif opt in ("-f", "--filterText"):
            filter_text = arg.strip()
            filter_rules = [rule.strip() for rule in filter_text.split(";")]

    # check if input values are valid
    if output_file_number < 0 or output_file_number > 100:
        got_args = False
        output_with_time_stamp(
            "The number of output files must be bigger then 0 and smaller then 100"
        )

    # need to check if path provided is a directory or a file path
    if os.path.isdir(input_dir_file):
        if not directory_exists(input_dir_file):
            got_args = False
            output_with_time_stamp(
                "Invalid input directory or file path: {}".format(input_dir_file)
            )
    elif os.path.isfile(input_dir_file):
        if not file_exist(input_dir_file):
            got_args = False
            output_with_time_stamp("Invalid input file path: {}".format(input_dir_file))
    else:
        got_args = False
        output_with_time_stamp("Invalid input path: {}".format(input_dir_file))

    # check output directory
    if not directory_exists(output_directory):
        got_args = False
        output_with_time_stamp("Invalid output directory: {}".format(output_directory))
    if (
        revit_file_extension.lower() != ".rvt"
        and revit_file_extension.lower() != ".rfa"
    ):
        got_args = False
        output_with_time_stamp(
            "Invalid file extension: [{}] expecting: .rvt or .rfa".format(
                revit_file_extension
            )
        )

    return got_args, FileSelectionSettings(
        input_dir_file,
        include_sub_dirs_in_search,
        output_directory,
        output_file_number,
        revit_file_extension,
        filter_rules,
        filter_is_and,
    )


def is_bim_360_file(revit_files):
    """
    Checks whether the first item in a file item list belongs to a BIM 360 project.

    Checks whether Project GUID property on file item object is None.

    :param revit_files: List of file items.
    :type revit_files: [:class:`.FileItem`]
    :return: True if BIM360 file, otherwise False.
    :rtype: bool
    """

    bim_360_file = False
    for revit_file in revit_files:
        if revit_file.bim_360_project_guid != None:
            bim_360_file = True
            break
    return bim_360_file


#: module entry
if __name__ == "__main__":
    main(sys.argv[1:])
