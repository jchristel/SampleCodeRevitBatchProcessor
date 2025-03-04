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
from duHast.Revit.BIM360.bim_360 import get_model_bim_360_ids, get_model_file_size_from_GUID, get_model_file_size
from duHast.Revit.Links.links import get_all_revit_link_instances
from duHast.pyRevit.console_output import print_header
from duHast.Revit.Common.revit_version import get_revit_version_number
from duHast.Utilities.files_csv import write_report_data_as_csv

from pyrevit.framework import Forms

def get_cloud_guids_entry(doc, output, forms):
    """
    Prints out all cloud guid data of the active document and any links

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

        data = []
        print_header("Getting cloud GUIDs")

        revit_version = get_revit_version_number(doc=doc)
        file_size = get_model_file_size(doc)
        # main document
        main_doc = get_model_bim_360_ids(doc)

        # build string for root model
        data_root = ["{}".format(revit_version), "{}".format(main_doc[0]),"{}".format(main_doc[1]),"{}".format(file_size), main_doc[2]]
        data.append(data_root)

        print("version, project guid, file guid, file size, file name")
        print (str.join(",", data_root))
        
        # get all links
        links = get_all_revit_link_instances(doc)
        for link in links:
            # get link document
            link_doc = link.GetLinkDocument()
            try:
                cloud_data =  get_model_bim_360_ids(link_doc)
                file_size_link = get_model_file_size_from_GUID(revit_version=revit_version, file_guid=cloud_data[1])
                data_cloud_link = ["{}".format(revit_version),"{}".format(cloud_data[0]),"{}".format(cloud_data[1]),"{}".format(file_size_link),cloud_data[2]]
                data.append(data_cloud_link)
                print (str.join(",", data_cloud_link))
            except Exception as e:
                print ("An exception occured when retrieving cloud data for links: {}".format(e))
    
        # offer to safe data
        file_name = None
        sf_dlg = Forms.SaveFileDialog()  # (file_ext="json", title="Save template data")
        sf_dlg.Filter = "Text files (*.csv)|*.csv|All files (*.*)|*.*"
        if sf_dlg.ShowDialog() == Forms.DialogResult.OK:
            file_name = sf_dlg.FileName

        if file_name is None:
            print("No file name for data file selected. Exiting.")
            return_value.update_sep(False, "No file name for data file selected. Exiting.")
            return return_value
        
        try:
            # write data to file
            write_result = write_report_data_as_csv(
                file_name=file_name, header="", data=data
            )
            if write_result.status == False:
                raise ValueError(write_result.message)
            
            return_value.append_message("Wrote file to: {}".format(file_name))
        except Exception as e:
            return_value.update_sep(
                False, "Failed to write data file with exception: {}".format(e)
            )
    except Exception as e:
        return_value.update_sep(
            False, "Failed to retrieve cloud guids with exception: {}".format(e)
        )

    print("\n{}".format(return_value.message))

    return return_value