"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit family type helper functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2023, Jan Christel
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
from duHast.Revit.Common.transaction import in_transaction

from Autodesk.Revit.DB import Transaction

def create_family_type(doc, type_name):
    """
    Creates a new family type in the family document.

    :param doc: The family document
    :type doc: Document
    :param type_name: The name of the family type
    :type type_name: str
    :return: Result object
    :rtype
    """

    return_value = Result()

    try:
        # check this is a family document
        if not doc.IsFamilyDocument:
            return_value.update_sep(False, "Document is not a family document.")
            return return_value
        
        # Get the FamilyManager
        family_manager = doc.FamilyManager

        def action():
            action_return_value = Result()
            try:
                # create new type
                new_fam_type = family_manager.NewType(type_name)
                action_return_value.update_sep(True, "Created new family type: {}".format(type_name))
                action_return_value.result.append(new_fam_type)
            except Exception as e:
                action_return_value.update_sep(False, "Failed to create family type with exception: {}".format(e))
            return action_return_value
        
        tranny = Transaction(doc, "Creating type: {}".format(type_name))
        create_type_result = in_transaction(tranny=tranny, action=action)
        return_value.update(create_type_result)

        return return_value

    except Exception as e:
        return_value.update_sep(False, "Failed to create family type with exception: {}".format(e))
    
    return return_value


def delete_family_type(doc, type_name):
    """
    Deletes a family type from the family document.

    :param doc: The family document
    :type doc: Document
    :param type_name: The name of the family type
    :type type_name: str
    :return: Result object
    :rtype
    """

    return_value = Result()

    try:

        # check this is a family document
        if not doc.IsFamilyDocument:
            return_value.update_sep(False, "Document is not a family document.")
            return return_value
        
        # Get the FamilyManager
        family_manager = doc.FamilyManager

        # get all the types in the family
        familyTypes = family_manager.Types

        # flag checking if anything got deleted at all
        deleted_type = False

        # iterate over family types
        familyTypesItor = familyTypes.ForwardIterator()
        familyTypesItor.Reset()
        while (familyTypesItor.MoveNext()):
        
            familyType = familyTypesItor.Current
            if familyType.Name == type_name:
                
                def action():
                    action_return_value = Result()
                    try:
                        # delete the current type
                        family_manager.RemoveType(familyType)
                        action_return_value.update_sep(True, "Deleted family type: {}".format(type_name))
                        deleted_type = True
                    except Exception as e:
                        action_return_value.update_sep(False, "Failed to delete family type with exception: {}".format(e))
                    return action_return_value
                
                tranny = Transaction(doc, "Deleting type: {}".format(type_name))
                delete_type_result = in_transaction(tranny=tranny, action=action)
                return_value.update(delete_type_result)

                break
       
        if not deleted_type:
            return_value.update_sep("No matching type {} in family found.".format(type_name))

    except Exception as e:
        return_value.update_sep(False, "Failed to delete family type with exception: {}".format(e))
    
    return return_value