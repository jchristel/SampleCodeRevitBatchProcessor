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

import System

from duHast.Utilities.Objects.result import Result
from duHast.Revit.ColourFillSchemes.colour_fill_scheme_entry import get_entry_value_as_string, set_entry_value
from duHast.Revit.Common.transaction import in_transaction

from Autodesk.Revit.DB import ColorFillScheme, ColorFillSchemeEntry,Color,  ElementId, Transaction, StorageType

def update_by_values(doc, colour_fill_scheme, colour_fill_scheme_data, transaction_manager = in_transaction):
    """
    Updates the colours and fill patterns of a colour fill scheme by values.

    :param colour_fill_scheme: The colour fill scheme.
    :type colour_fill_scheme: ColourFillScheme
    :param colour_fill_scheme_data: The colour fill scheme data.
    :type colour_fill_scheme_data: dict
    
    :return: The result of the update operation.
    :rtype: Result
    """

    return_value = Result()

    try:
        # Check types

        if not isinstance(colour_fill_scheme, ColorFillScheme):
            raise TypeError("colour_fill_scheme must be of type ColourFillScheme. Got {}".format(type(colour_fill_scheme)))
        
        if not isinstance(colour_fill_scheme_data, list):
            raise TypeError("colour_fill_scheme_data must be of type list. Got {}".format(type(colour_fill_scheme_data)))


        def action():
            action_return_value = Result()

            try:
                # get all entries in the colour fill scheme
                entries = colour_fill_scheme.GetEntries()

                # loop over the entries and get the report data
                for entry in entries:

                    # get the value as string
                    parameter_value = get_entry_value_as_string(entry=entry)
                    
                    # set update flag to default
                    entry_requires_update = False

                    # loop over the colour fill scheme data and get the matching entry
                    for colour_fill_scheme_entry in colour_fill_scheme_data:
                        if parameter_value.lower() == colour_fill_scheme_entry.parameter_value.lower():
                            # create a color instance
                            new_colour = Color(
                                System.Convert.ToByte(colour_fill_scheme_entry.colour_red),
                                System.Convert.ToByte(colour_fill_scheme_entry.colour_green),
                                System.Convert.ToByte(colour_fill_scheme_entry.colour_blue),
                            )

                            # check if the colour is the same
                            if entry.Color.Red != new_colour.Red or entry.Color.Green != new_colour.Green or entry.Color.Blue != new_colour.Blue:
                                action_return_value.append_message("Colour is different: {} != {}".format(entry.Color, new_colour))
                                # update the entry with the new colour
                                entry.Color = new_colour
                                entry_requires_update = True


                            # check if the fill pattern is the same
                            if entry.FillPatternId.IntegerValue != colour_fill_scheme_entry.fill_pattern_id:
                                action_return_value.append_message("Fill pattern is different: {} != {}".format(entry.FillPatternId.IntegerValue, colour_fill_scheme_entry.fill_pattern_id))
                                # update the entry with the new fill pattern
                                entry.FillPatternId = ElementId(colour_fill_scheme_entry.fill_pattern_id)
                                entry_requires_update = True

                           
                            break

                    # this can throw an exception if the entry values are the same...
                    if entry_requires_update == False:
                        action_return_value.append_message("No update required for entry: {}".format(parameter_value))
                        continue
                    
                    # update the entry
                    colour_fill_scheme.UpdateEntry(entry)

                    # reset the update flag
                    entry_requires_update = False

                    # if the entry was updated, append the message
                    action_return_value.append_message("Updated entry: {} with colour: {},{},{} and fill pattern: {}".format(
                        parameter_value, 
                        colour_fill_scheme_entry.colour_red, 
                        colour_fill_scheme_entry.colour_green, 
                        colour_fill_scheme_entry.colour_blue, 
                        colour_fill_scheme_entry.fill_pattern_id)
                        )

                action_return_value.append_message("Colour fill scheme entries updated successfully.")
                return action_return_value
            except Exception as e:
                action_return_value.update_sep(False, "Error in action: {}".format(e))
                return action_return_value
        
        if transaction_manager is None:
           action_result =  action()
           return action_result
        else:
            tranny = Transaction(doc, "Updating colour fill scheme")
            result_delete = transaction_manager(tranny, action)
            return_value.update(result_delete)
            return return_value
       
    except Exception as e:
        return_value.update_sep(False, "Error updating colour fill scheme: {}".format(e))
        return return_value
   

def update_existing_and_add_new_values (doc, colour_fill_scheme, colour_fill_scheme_data, transaction_manager = in_transaction):
    """
    Updates the colours and fill patterns of a colour fill scheme by values and adds new values if provided in colour fill scheme data.

    :param colour_fill_scheme: The colour fill scheme.
    :type colour_fill_scheme: ColourFillScheme
    :param colour_fill_scheme_data: The colour fill scheme data.
    :type colour_fill_scheme_data: dict
    
    :return: The result of the update operation.
    :rtype: Result
    """

    return_value = Result()

    try:
        # Check types
        if not isinstance(colour_fill_scheme, ColorFillScheme):
            raise TypeError("colour_fill_scheme must be of type ColourFillScheme. Got {}".format(type(colour_fill_scheme)))
        
        if not isinstance(colour_fill_scheme_data, list):
            raise TypeError("colour_fill_scheme_data must be of type list. Got {}".format(type(colour_fill_scheme_data)))

        # define action to run inside a transaction
        def action():
            action_return_value = Result()

            try:
                # update existing values first
                update_existing_values_result = update_by_values(doc, colour_fill_scheme, colour_fill_scheme_data, transaction_manager = None)
                action_return_value.update(update_existing_values_result)

                # add new values
                # get all entries in the colour fill scheme
                entries = colour_fill_scheme.GetEntries()

                # loop over the colour fill scheme data and get the matching entry
                for colour_fill_scheme_entry in colour_fill_scheme_data:

                    entry_exists = False
                    # loop over the entries and get the report data
                    for entry in entries:

                        # get the value
                        parameter_value = get_entry_value_as_string(entry=entry)
                       
                        # check if the entry is already in the colour fill scheme
                        if parameter_value.lower() == colour_fill_scheme_entry.parameter_value.lower():
                            # skip this value as already updated in first step
                            entry_exists = True
                            break

                    # if the entry is in the colour fill scheme, skip it
                    if entry_exists == True:
                        entry_exists = False
                        continue

                    # create a new entry
                    new_entry = ColorFillSchemeEntry(StorageType(colour_fill_scheme_entry.storage_type))
                    
                    # set the value
                    new_entry = set_entry_value(new_entry, colour_fill_scheme_entry.parameter_value)

                    
                    # create a color instance
                    new_colour = Color(
                        System.Convert.ToByte(colour_fill_scheme_entry.colour_red),
                        System.Convert.ToByte(colour_fill_scheme_entry.colour_green),
                        System.Convert.ToByte(colour_fill_scheme_entry.colour_blue),
                    )
                   
                    # set the fill color
                    new_entry.Color = new_colour
                    
                    # set the fill pattern id
                    new_entry.FillPatternId = ElementId(colour_fill_scheme_entry.fill_pattern_id)
                    

                    # add the entry to the colour fill scheme
                    colour_fill_scheme.AddEntry(new_entry)
                    
                    action_return_value.append_message("Added new entry: {} with colour: {},{},{} and fill pattern: {}".format(
                        colour_fill_scheme_entry.parameter_value, 
                        colour_fill_scheme_entry.colour_red, 
                        colour_fill_scheme_entry.colour_green, 
                        colour_fill_scheme_entry.colour_blue, 
                        colour_fill_scheme_entry.fill_pattern_id)
                    )

                action_return_value.append_message("Colour fill scheme entries updated successfully.")
                return action_return_value
            except Exception as e:
                action_return_value.update_sep(False, "Error in action: {}".format(e))
                return action_return_value
            
        if transaction_manager is None:
           action_result =  action()
           return action_result
        else:
            tranny = Transaction(doc, "Updating colour fill scheme")
            result_delete = transaction_manager(tranny, action)
            return_value.update(result_delete)
            return return_value
       
    except Exception as e:
        return_value.update_sep(False, "Error updating colour fill scheme: {}".format(e))
        return return_value
   