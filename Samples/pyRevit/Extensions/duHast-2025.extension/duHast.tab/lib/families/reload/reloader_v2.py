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

import clr
import System
import sys
import os

from System import Int64 # revit element Id expects 64 bit integer

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Family.family_reload_single import reload_family
from duHast.Revit.NetSupport.dll_names import FAMILY_RELOADER_UI

from duHast.pyRevit.console_output import print_header, print_error
from duHast.pyRevit.net_dll_loader import load_net_dll_path, get_bin_path_from_script_path_within_extension

from families.reload.get_families import get_families_in_model_net
from duHast.Revit.NetSupport.dll_names import UTILITY,WPF_CUSTOM_CONTROLS,FAMILY_RELOADER_UI

from Autodesk.Revit.DB import ElementId

DEBUG = False

# .net dlls to load for this script, these need to be in the bin folder of the extension
DLL_LIST = [UTILITY,WPF_CUSTOM_CONTROLS,FAMILY_RELOADER_UI]


def reload_families(doc, families, forms, load_all_family_types=False):
    """
    Reloads families in the Revit model.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param families: List of families to reload.
    :type families: list of Family objects
    :param forms: pyRevit forms module.
    :type forms: pyRevit forms module
    :param load_all_family_types: If True, family types introduced by the library file are kept
        ( the UI's "Import All Types On Reload" ). If False, only types already in the document
        are updated and any new type is deleted again after the reload.
    :type load_all_family_types: bool
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
                revit_family = doc.GetElement(ElementId(Int64(fam.RevitElementId)))
                reload_result = reload_family(
                    doc=doc,
                    family=revit_family,
                    family_file_path=fam.FamilyFilePath,
                    # keeping new types is the inverse of deleting them
                    delete_new_types=not load_all_family_types,
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
        
        print_header("Starting ...")
        # get the bin directory for the extension, this is where the required dlls should be located
        bin_directory = get_bin_path_from_script_path_within_extension(__file__)   
        if bin_directory is None:
            message = "Failed to determine bin directory for dlls."
            print_error(message)
            return_value.update_sep(False, message)
            return return_value

        # load the required dlls for the UI
        load_result = load_net_dll_path(DLL_LIST, bin_directory=bin_directory, exact_match=True)
        print(load_result.message)

        # # Find the already-loaded assembly
        # assembly = None
        # for asm in System.AppDomain.CurrentDomain.GetAssemblies():
        #     if "FamilyReloaderUI" in asm.FullName:
        #         assembly = asm
        #         break
        # if assembly:
        #     # Register it with IronPython using the assembly object
        #     # the loader will have already loaded the assembly, so we can just reference it here without loading it again
        #     clr.AddReference(assembly)
        #     from duHastNet.UI.FamilyReloaderUI import Main
        # else:
        #     print_error("Failed to find FamilyReloaderUI assembly.")
        #     return_value.update_sep(False, "Failed to find FamilyReloaderUI assembly.")

        print_header("Reloading families in the model {}...".format(doc.Title))
        
        
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
        print("Will reload {} families".format(families_reload.FamiliesToReload.Count))

        # honour the reload mode picked in the UI: "Import All Types On Reload" keeps any
        # type the library file introduces, otherwise only existing types are updated
        load_all_family_types = families_reload.LoadAllFamilyTypesOnReload
        print(
            "Reload mode: {}".format(
                "import all types"
                if load_all_family_types
                else "reload existing types only"
            )
        )

        reloader_result = reload_families(
            doc=doc,
            families=families_reload.FamiliesToReload,
            forms=forms,
            load_all_family_types=load_all_family_types,
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
