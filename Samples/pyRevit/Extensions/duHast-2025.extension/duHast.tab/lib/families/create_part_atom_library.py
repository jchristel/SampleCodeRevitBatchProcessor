# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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


from duHast.Utilities.Objects.result import Result
from duHast.Utilities.directory_io import get_child_directories
from duHast.pyRevit.Objects.ProgressPyRevit import ProgressPyRevit
from duHast.pyRevit.directory_picker import get_process_directories
from duHast.pyRevit.console_output import print_header
from duHast.Revit.Family.Utility.xml_create_atom_exports import create_family_xml_files


def create_part_atom_exports_in_library_entry(doc, output, forms):
    """
    Create part atom exports in library location based on family files in same library location.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output.
    :type output: pyRevit.output
    :param forms: pyRevit forms.
    :type forms: pyRevit.forms
    :return: Result object with status and message.
    :rtype: Result
    """

    # set up a status tracker
    return_value = Result()

    try:

        print_header("Getting directories")
        # get user to select library directories to process
        process_dirs_result = get_process_directories(forms)
        if not process_dirs_result.status:
            print(process_dirs_result.message)
            return_value.update_sep(False, process_dirs_result.message)
            return return_value

        process_dirs = process_dirs_result.result
        for d in process_dirs:
            print("Processing directories: {}".format(d))

        # set up a pyRevit progress bar
        with forms.ProgressBar(
            title="Creating XML files: {value} of {max_value}",
            cancellable=True,
        ) as pb:
            
            # set up a call back for pyRevit progressbar
            progress_callback = ProgressPyRevit(form=pb)

            print("Creating family xml exports in library:")

            # create the xml files
            create_result = create_family_xml_files(
                revit_application=doc.Application,
                process_directories=process_dirs,
                progress_callback=progress_callback
            )

            return_value.update(create_result)

    except Exception as e:
        return_value.update_sep(
            False, "Failed to create families exports exception: {}".format(e)
        )

    print("\n{}".format(return_value.message))
    print("Finished")

    return return_value

