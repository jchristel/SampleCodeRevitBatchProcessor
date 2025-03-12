"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A module with helper function around family types catalogue files.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Family types can be filtered ( removed from the export ) by providing a list of filters.
For available filters see the documentation in the module duHast.Utilities.compare



"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

from duHast.Revit.Family.family_types_get_data_from_xml import get_type_data_via_XML_from_family_file
from duHast.Revit.Family.Data.Objects.family_type_data_storage_manager import FamilyTypeDataStorageManager
from duHast.Utilities.Objects.result import Result



def export_catalogue_file(doc, file_path = None, filters = None):
    """
    Export the family types catalogue file.

    :param doc: The family document to extract the type data from.
    :type doc: rdb.Family
    :param file_path: The path to save the catalogue file. If None, the file will be saved in the same location as the family with the same name as the family.
    :type file_path: str
    :param filters: 
        
            The filters to apply to the types to be added to the catalogue file. If None, no filters will be applied and all types will be added. If more then one filter is provided, the types must pass all filters to be added.
            Filter format:

                [[ does_not_equal, "my check value"],...]

    :type filters: list(function(value1,value2))
    """

    return_value = Result()

    try:

        # check if a family document...
        if not doc.IsFamilyDocument:
            return_value.update_sep(False, "The document is not a family document.")
            return return_value

        # get the family name
        family_name = doc.Name

        # remove the file extension
        if family_name.lower().endswith(".rfa"):
            family_name = family_name[:-4]

        # get the family path
        family_path = doc.PathName

        # get the root path (same as the family name)
        root_path = doc.Name

        # get the root category path (same as the family category)
        root_category_path = doc.FamilyCategory.Name

        # get the family type data
        family_type_data_result = get_type_data_via_XML_from_family_file(doc, family_name, family_path, root_path, root_category_path)

        # check if the family type data was successfully extracted
        if not family_type_data_result.success:
            return_value.update_sep(False, "Failed to get the family type data: {}".format(family_type_data_result.message))
            return return_value
        
        if family_type_data_result.result is None or len(family_type_data_result.result) == 0:
            return_value.update_sep(False, "No family type data was extracted.")
            return return_value
        
        # get the family type data
        fam_type_manager = family_type_data_result.result[0]

        if not isinstance(fam_type_manager, FamilyTypeDataStorageManager):
            return_value.update_sep(False, "Failed to get the family type manager. Got {} instead.".format(type(fam_type_manager)))
            return return_value
        
        # check if family has any types
        if not fam_type_manager.family_has_types:
            return_value.update_sep(False, "No family types found in family.")
            return return_value

        # go over filters and remove types that do not pass the filter
        if filters is not None:

            # loop over filters
            for filter_instance in filters:

                # do some sanity checks
                if not isinstance(filter_instance, list):
                    return_value.update_sep(False, "Filter is not a list: {}".format(filter_instance))
                    continue

                if len(filter_instance) != 2:
                    return_value.update_sep(False, "Filter does not contain two elements: {}".format(filter_instance))
                    continue

                # get the filter function
                filter_func = filter_instance[0]
                filter_value = filter_instance[1]

                # check if the filter function is callable
                if not callable(filter_func):
                    return_value.update_sep(False, "Filter function is not callable: {}".format(filter_func))
                    continue
            
                

                # loop over family types
                for fam_type in fam_type_manager.family_type_data_storage:
                    pass


               




        # convert type data into catalogue file
    
    except Exception as e:
        return_value.update_sep(False, str(e))

    return return_value
    