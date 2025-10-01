"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions to swap instances of a duplicated family to instances of the original family in a revit document.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This function will identify duplicated families in the current Revit document based on their names. It will then swap all instances of the duplicated families with instances of the original family, ensuring that the document maintains consistency and avoids redundancy.

Potential issues: 

- the source family does not include the type of the duplicate family

"""


#
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

from duHast.Revit.Common import transaction as rTran
from duHast.Utilities.Objects import result as res
from family_find_duplicate import *
from duHast.UI.Objects.ProgressBase import ProgressBase

from Autodesk.Revit.DB import Element, ElementId, Transaction

DEBUG = True

def swap_family_instances_of_duplicates(doc, progress_callback=None):
    """
    Entry point for this module. 

    :return:
        Result class instance.

        - result.status. True if a single families was swapped successfully, otherwise False.
        - result.message will contain each swap message
        - result.result empty list

        On exception:

        - result.status (bool) will be False.
        - result.message will contain an exception message in format: 'Failed to swap family from :' + currentName + ' to ' + newName
        - result.result will be empty

    :rtype: :class:`.Result`
    """

    return_value = res.Result()

    # check callback class
    if progress_callback and isinstance(progress_callback, ProgressBase) == False:
        raise TypeError(
            "progress_callback needs to be inherited from ProgressBase. Got : {} instead.".format(
                type(progress_callback)
            )
        )
    
    try:
        print ("here...")
        # attempt to find duplicate families
        duplicate_families = find_duplicate_families(doc)
        
        if DEBUG:
            print ("there...{}".format(len(duplicate_families)))
            for fam_id, families in duplicate_families.items():
                print ("fam_id: {}: {}".format(fam_id, families))

        # check if any duplicates found
        if len(duplicate_families) == 0:
            return_value.update_sep(True, "No duplicate families found.", [])
            return return_value
        
        # find duplicate types in families

        for fam_id, families in duplicate_families.items():
            
            if DEBUG:
                print ("Processing family id: {}".format(fam_id))
            
            target_family = doc.GetElement(fam_id)

            if DEBUG:
                print ("target_family: {}".format(target_family.Name))

            # get the duplicate families
            for duplicate_family in families:
                if DEBUG:
                    print ("duplicate_family: {}".format(duplicate_family.Name))
                target_mapper = find_matching_types_between_families (duplicate_family, target_family)
                print ("target_mapper: {}".format(target_mapper))
    except Exception as e:
        return_value.update_sep(
            False,
            "Failed to swap family instances due to exception: {}".format(e)
        )
    
    return return_value