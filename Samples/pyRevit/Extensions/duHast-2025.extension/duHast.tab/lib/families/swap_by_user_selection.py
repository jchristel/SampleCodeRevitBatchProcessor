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
from duHast.Revit.Family.family_utils import get_family_instances_by_symbol_type_fast
from duHast.Revit.Family.Data.Objects.family_directive_swap_instances_of_type import FamilyDirectiveSwap
from duHast.Revit.Family.family_functions import get_name_and_category_to_family_dict
from duHast.pyRevit.UI.ui_element_selection import get_element_selection_from_user
from duHast.Revit.Family.family_swap_instances_of_types import _swap_loaded_family_instances
from families.util.print_table import print_result_table, get_table_data_from_swap_result

from duHast.Revit.Family.Data.Objects.family_base_data_processor_defaults import (
    NESTING_SEPARATOR,
)


from Autodesk.Revit.DB import (
    Element,
    FamilySymbol,
    FilteredElementCollector,
)


FAM_NAME_TYPE_NAME_CATEGORY_SEPARATOR = " {} ".format(NESTING_SEPARATOR)

def family_types_getter(doc):

    try:
        # get all family typres of fasmilies not in place
        col = FilteredElementCollector(doc).OfClass(FamilySymbol)

        # filter out types with no placed instances
        fam_types = [f for f in col if get_family_instances_by_symbol_type_fast(f).Count > 0]

        if fam_types is None or len(fam_types) == 0:
            return []

        return fam_types
    except Exception as e:
        print("Error getting family types", e)
        return []
    

def family_types_getter_target(doc, category_name_filter):
    try:
        # get all family typres of fasmilies not in place
        col = FilteredElementCollector(doc).OfClass(FamilySymbol)

        # filter out types by category name only
        fam_types = [f for f in col if f.Category.Name == category_name_filter]

        if fam_types is None or len(fam_types) == 0:
            return []

        return fam_types
    except Exception as e:
        print("Error getting family types", e)
        return []


def ui_data_builder(element):
    # element is a family type, UI to contain the family name , family type and category
    # in format "Family Name::Family Type :Category"
    try:
        return "{}{}{}{}{}".format(
            Element.Name.GetValue(element.Family),
            FAM_NAME_TYPE_NAME_CATEGORY_SEPARATOR,
            Element.Name.GetValue(element),
            FAM_NAME_TYPE_NAME_CATEGORY_SEPARATOR,
            element.Category.Name
        )
    except Exception as e:
        return "Unknown {}".format(e)
    
def get_target_category_name(doc, selection_id):

    fam_type = doc.GetElement(selection_id)
    return fam_type.Category.Name
    

def swap_instances_by_user_selection_entry(doc, output, forms):
    """
    Swaps instances of types based on user selection. This function is the entry point for the pyRevit command.

    :param doc: Revit Document
    :type doc: Document
    :param output: pyRevit output
    :type output: Output
    :param forms: pyRevit forms
    :type forms: Forms

    :return: Result
    """

    # set up a status tracker
    return_value = Result()

    # set up a table data ( for print out)
    table_data = None

    try:
        # get user to select the family source type
        selection_source_type_id = get_element_selection_from_user(
            doc=doc, 
            forms=forms, 
            element_getter=family_types_getter, 
            element_selection_description="Select the family type to swap from",
            multiselect=False,
            ui_element_name_builder=ui_data_builder,
        )

        if selection_source_type_id is None or len(selection_source_type_id) == 0:
            return_value.update_sep(False, "No family type selected")
            print("No family type selected. Exiting!")
            return return_value
        

        # get some source names
        source_type_id = selection_source_type_id[0]
        source_type_name = Element.Name.GetValue(doc.GetElement(source_type_id))
        source_fam_name = Element.Name.GetValue(doc.GetElement(source_type_id).Family)

        # separate the category name from the selection
        target_category_name = get_target_category_name(doc, selection_source_type_id[0])

        # set up warpper function to get the target family type filtered by category
        def getter_target_type (doc) :
            return family_types_getter_target(doc,  target_category_name)

        # get user to select the family target type
        selection_target_type = get_element_selection_from_user(
            doc=doc, 
            forms=forms, 
            element_getter=getter_target_type, 
            element_selection_description="Select the family type to swap to",
            multiselect=False,
            ui_element_name_builder=ui_data_builder,
        )

        # verify user selection
        if selection_target_type is None or len(selection_target_type) == 0:
            return_value.update_sep(False, "No target family type selected")
            print("No target family type selected. Exiting!")
            return return_value
        
        # get some target names
        target_type_id = selection_target_type[0]
        target_type_name = Element.Name.GetValue(doc.GetElement(target_type_id))
        target_fam_name = Element.Name.GetValue(doc.GetElement(target_type_id).Family)

        # create A swap directive from selection
        swap_directive = FamilyDirectiveSwap(
            name=source_fam_name,
            category=target_category_name,
            source_type_name = source_type_name,
            target_family_name=target_fam_name,
            target_family_type_name=target_type_name,
        )

        # get all family in file
        families = get_name_and_category_to_family_dict(doc)

        # swap the instances out
        swap_result = _swap_loaded_family_instances(doc, [swap_directive], families=families, progress_callback=None)
        # print logs
        print(swap_result.message)
        
        # get table data for printing tables at the end
        table_data = get_table_data_from_swap_result(doc, swap_result.result)
       
        # update return value
        return_value.update(swap_result)
        
    except Exception as e:
        print("An exception occurred: {}".format(e))
        return_value.update_sep(
            False, "Failed to swap families with exception: {}".format(e)
        )

    # print tables
    if table_data is not None and len(table_data[0]) >0:
        print_result_table(output, table_data[0], ["Host Family", "Instances not swapped"], "Host Families containing instances not swapped")
    if table_data is not None and len(table_data[1]) >0:
        print_result_table(output, table_data[1], ["Host Group", "Instances not swapped"], "Host Groups containing instances not swapped")

    print("Finished")

    return return_value