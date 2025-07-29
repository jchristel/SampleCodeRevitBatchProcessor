"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to fields in Revit view schedules. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

def get_field_names_from_schedule(schedule):
    """
    Get a list of all field names from a Revit schedule.
    :param schedule: The Revit schedule object from which to extract field names.
    :type schedule: Autodesk.Revit.DB.ViewSchedule

    :return: A list of field names in the schedule.
    :rtype: list of str
    """

    # get the schedule definition
    schedule_definition = schedule.Definition

    # get the number of fields in the schedule
    num_fields = schedule_definition.GetFieldCount()

    # create a list to hold the field names
    field_names = []

    # loop through the fields and get their names
    for i in range(num_fields):
        field = schedule_definition.GetField(i)
        field_name = field.GetName()
        field_names.append(field_name)
    
    return field_names


def get_field_names_to_parameters(schedule):
    """
    Get a dictionary of field names to their corresponding parameters in a Revit schedule.
    
    :param schedule: The Revit schedule object from which to extract field names and parameters.
    :type schedule: Autodesk.Revit.DB.ViewSchedule
    
    :return: A dictionary where keys are field names and values are the corresponding parameter IDs.
    """

    # create a dictionary to hold field names and their corresponding parameter IDs
    field_name_to_id

    # get the schedule definition
    schedule_definition = schedule.Definition

    # get the number of fields in the schedule
    num_fields = schedule_definition.GetFieldCount()

    # loop through the fields and get their names
    for i in range(num_fields):
        field = schedule_definition.GetField(i)
        field_name = field.GetName()
        parameter_id = field.ParameterId

        # add the field name and parameter ID to the dictionary
        field_names_to_id[field_name]= parameter_id
    
    return field_name_to_id
