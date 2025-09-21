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
from duHast.Revit.Family.family_reload_single import reload_family
from duHast.Revit.NetSupport.dll_names import FAMILY_RELOADER_UI

from duHast.pyRevit.console_output import print_header, print_error
from duHast.pyRevit.net_dll_loader import load_net_dll_path

from families.reload.get_families import get_families_in_model_net


from Autodesk.Revit.DB import ElementId

DEBUG = False



def reload_families(doc, families, forms):
    """
    Reloads families in the Revit model.
    
    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param families: List of families to reload.
    :type families: list of Family objects
    :param forms: pyRevit forms module.
    :type forms: pyRevit forms module
    :return: Result class instance.
        - `result` (bool): True if families were reloaded successfully, otherwise False.
        - `message` (str): details about the reloading process.
    :rtype: :class:`.Result`
    """
    
    return_value = Result()

    fam_counter = 0
    # set up a pyRevit progress bar
    with forms.ProgressBar(
        title="Reloading families: {value} of {max_value}", cancellable=True
    ) as pb:
        try:
            for fam in families:
                # reload_family(doc, family, family_file_path):
                revit_family = doc.GetElement(ElementId(fam.RevitElementId))
                reload_result = reload_family(
                    doc=doc, 
                    family=revit_family, 
                    family_file_path=fam.FamilyFilePath
                )
                return_value.update(reload_result)

                # check for cancel
                if pb.cancelled:
                    return_value.update_sep(False, "User cancelled.")
                    # get out of loop
                    break

                fam_counter = fam_counter + 1
                pb.update_progress(fam_counter, len(families))

        except Exception as e:
            print(e)
    return return_value


def reloaded_families_entry(doc, output, forms):
    """
    Reports on loaded families in a project file.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param output: pyRevit output
    :type output: pyRevit output module
    :param forms: pyRevit forms
    :type forms: pyRevit forms module

    :return: Result class instance.
        - `result` (bool): True if warnings where reported without an exception, otherwise False.
        - `message` (str): details how many warnings where retrieved.
    :rtype: :class:`.Result`
    """

    # set up a status tracker
    return_value = Result()

    try:
        
        print_header("Reloading families in the model {}...".format(doc.Title))
        # load .net interface dlls
        set_dll_path_result = load_net_dll_path([FAMILY_RELOADER_UI])

        # check if the dlls were loaded successfully
        if not set_dll_path_result.status:
            print_error(set_dll_path_result.message)
            return_value.update_sep(False, set_dll_path_result.message)
            return return_value
        
        # get all families in file as a list of .net RevitFamily objects
        families_net = get_families_in_model_net(doc=doc)
        
        # check if families were found
        if not families_net or families_net.Count == 0:
            print_header("No families found in the model.")
            return_value.update_sep(True, "No families found in the model.")
            return return_value
        
        # import the UI class from the FamilyReloaderUI namespace
        from duHastNet.UI.FamilyReloaderUI import Main
       
        # create an instance of the Main class
        main = Main(families_net)
        
        # show the output window
        families_reload = main.Execute()
        
        #check what came back from the UI
        if not families_reload or not families_reload.FamiliesToReload or families_reload.FamiliesToReload.Count == 0:
            print("No families to reload selected.")
            return_value.append_message("No families to reload selected.")
            return return_value
        
        
        # reload the families
        print("Will {} reload families").format(families_reload.FamiliesToReload.Count)
        
        reloader_result = reload_families(
            doc=doc, families=families_reload.FamiliesToReload, forms=forms
        )
        return_value.update(reloader_result)
        print(reloader_result.message)
        

        print("Finished.")
        return return_value

    
    except Exception as e:
        # handle any exceptions that occur during the reload process
        message = "An error occurred while reloading families: {}".format(e)
        return_value.update_sep(
            False, "Failed to reload families with exception: {}".format(e)
        )
        print(message)
        return return_value
