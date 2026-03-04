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

from duHast.Utilities.Objects.result import Result

from System import Int64 # revit element Id expects 64 bit integer

from Autodesk.Revit.DB import Element, ElementId, SectionType

# the sheet number parameter id
SHEET_NUMBER_PARAMETER_ID = ElementId(Int64(-1007401))

def schedule_contains_field_by_parameter_id(schedule, parameter_id, ignore_hidden_field=False):
    """
    Checks if the given schedule contains a specific field identified by the parameter Id.

    :param schedule: The schedule to check.
    :type schedule: Autodesk.Revit.DB.ViewSchedule
    :param parameter_id: The parameter Id of the field to check for.
    :type parameter_id: Autodesk.Revit.DB.ElementId
    :param ignore_hidden_field: If True, a hidden field returns false.
    :type ignore_hidden_field: bool, optional
    
    :return: True if the schedule contains the sheet number field, False otherwise.
    :rtype: bool
    """

    # get the schedule definition
    schedule_definition = schedule.Definition

    # get the number of fields in the schedule
    num_fields = schedule_definition.GetFieldCount()

    # loop through the fields and get their names
    for i in range(num_fields):
        field = schedule_definition.GetField(i)
        field_id = field.ParameterId
        # check if the field id matches the parameter id
        if field_id == parameter_id:
            if ignore_hidden_field is True and field.IsHidden:
                # if the field is hidden, return false
                return False
            # return True 
            return True
       
    # field not found, return False
    return False


def schedule_contains_sheet_number_field(schedule, ignore_hidden_field=False):
    """
    Checks if the given schedule contains the sheet number field.

    :param schedule: The schedule to check.
    :type schedule: Autodesk.Revit.DB.ViewSchedule
    :param ignore_hidden_field: If True, a hidden sheet number field returns false.
    :type ignore_hidden_field: bool, optional

    :return: True if the schedule contains the sheet number field, False otherwise.
    :rtype: bool
    """

    return schedule_contains_field_by_parameter_id(schedule, SHEET_NUMBER_PARAMETER_ID, ignore_hidden_field=ignore_hidden_field)


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
    field_names_to_id = {}

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
    
    return field_names_to_id


def get_field_column_index_from_schedule_by_parameter_id(schedule, parameter_id):
    """
    Returns the index of a field in a Revit schedule based on the parameter ID.

    If the field is hidden or not found will return -1.

    Takes into account if other fields are hidden or not, so the index is based on visible fields only.

    :param schedule: The Revit schedule object from which to extract the field index.
    :type schedule: Autodesk.Revit.DB.ViewSchedule
    :param parameter_id: The parameter ID of the field to find.
    :type parameter_id: Autodesk.Revit.DB.ElementId

    :return: The index of the field in the schedule, or -1 if not found or hidden.
    :rtype: int 
    """


    # get the schedule definition
    schedule_definition = schedule.Definition

    # get the number of fields in the schedule
    num_fields = schedule_definition.GetFieldCount()
    
    # ordered field list:
    sorted_field_ids = schedule_definition.GetFieldOrder()

    # get the column index
    column_index = 0

    # if the parameter ID is not provided, return -1
    field_found = False

    # loop through the fields in order of appearance in schedule to find the column index for the specified parameter ID
    for i in range(num_fields):
        field_id = sorted_field_ids[i]

        # get the field
        field_by_field_id = schedule_definition.GetField(field_id)

        # check if the field is hidden
        if field_by_field_id.IsHidden:
            # if the field is hidden, skip it
            continue

        # check if the field parameter ID matches the specified parameter ID
        if field_by_field_id.ParameterId == parameter_id:
            field_found = True
            break

        # increase the column index if the field is not hidden
        column_index += 1
    
    # if the field was found, return the column index
    if not field_found:
        column_index = -1

    return column_index


def get_field_from_schedule_by_field_name(schedule, field_name):
    """
    Returns the field matching the given name.

    :param schedule: The Revit schedule object from which to extract the field index.
    :type schedule: Autodesk.Revit.DB.ViewSchedule
    :param  field_name: The human readable field name
    :type  field_name: str

    :return: The field or None if no match was found.
    :rtype: Autodesk.Revit.DB.ScheduleField
    """


    # get the schedule definition
    schedule_definition = schedule.Definition

    # get the number of fields in the schedule
    num_fields = schedule_definition.GetFieldCount()
    
    # ordered field list:
    sorted_field_ids = schedule_definition.GetFieldOrder()

    # field place holder
    schedule_field = None

    # loop through the fields in order of appearance in schedule to find the column index for the specified parameter ID
    for i in range(num_fields):
        field_id = sorted_field_ids[i]
        
        # get the field by field ID
        field_by_field_id = schedule_definition.GetField(field_id)

        # check if the field parameter ID matches the specified parameter ID
        if field_by_field_id.GetName() == field_name:
            #print(field_by_field_id)
            return field_by_field_id
    return schedule_field


def get_field_values_from_schedule_by_parameter_id(schedule, parameter_id=None):
    """
    Get a list of all field values from a Revit schedule based on the parameter id.

    
    :param schedule: The Revit schedule object from which to extract field values.
    :type schedule: Autodesk.Revit.DB.ViewSchedule
    
    :return: A list of field values in the schedule.
    :rtype: list of str
    """

    # get the schedule definition
    schedule_definition = schedule.Definition

    # get the number of fields in the schedule
    num_fields = schedule_definition.GetFieldCount()
    
    # ordered field list:
    sorted_field_ids = schedule_definition.GetFieldOrder()

    # get the column index
    column_index = -1

    # loop through the fields in order of appearance in schedule to find the column index for the specified parameter ID
    for i in range(num_fields):
        field_id = sorted_field_ids[i]

        field_by_field_id = schedule_definition.GetField(field_id)
        #print("field by field ID",field_by_field_id.GetName())

        field_index = schedule_definition.GetField(i)

        if field_by_field_id.ParameterId == parameter_id and field_by_field_id.IsHidden == False:
            column_index = i
            break

    if column_index == -1:
        raise ValueError("The specified parameter ID is not found in the schedule fields.")

    # get the table data
    table = schedule.GetTableData()

    # get the body table data
    table_body = table.GetSectionData(SectionType.Body)
  
    # get the number of rows in the body table 
    num_rows = table_body.NumberOfRows

    # create a list to hold the field values
    field_values = []

    for row in range(num_rows):
        # get the cell text for the specified row and column
        # get cell text expects the row number first, followed by the column number
        cell_text = table_body.GetCellText(row, column_index)
        print("Row: {row}, Column: {column_index}, Cell Text: {cell_text}".format(
            row=row,
            column_index=column_index,
            cell_text=cell_text
        ))
        # append the cell text to the field values list
        field_values.append(cell_text)
    
    print (field_values)
    return field_values


def get_schedules_column_widths (schedules, field_names_of_interest=[]):
    """
    Returns a list of lists with schedule id and column data for the specified field names of interest. If no field names of interest are provided, will return column data for all fields in the schedule.

    Each row starts with the schedule id followed by tuples of field name and column width in inches for each field of interest.

    :param schedules: A list of Revit schedule objects to extract column width data from.
    :type schedules: list of Autodesk.Revit.DB.ViewSchedule
    :param field_names_of_interest: A list of field names to extract column width data for. If empty, will extract column width data for all fields in the schedule.
    :type field_names_of_interest: list of str, optional

    :return: A Result object containing a list of lists with schedule id and column data for the specified field names of interest, or an error message if the operation fails.
    :rtype: duHast.Utilities.Objects.result.Result
    """

    return_value = Result()

    schedules_data = []
    try:
        for s in schedules:
            row_data = [s.Id.IntegerValue]
            schedule_name = Element.Name.GetValue(s)
            return_value.append_message ("Getting columns: {}".format(schedule_name))
            field_names = get_field_names_from_schedule(s)

            # check if we need to filter schedules based on field names of interest:
            if len(field_names_of_interest) > 0:

                # do we have all  fields of interest in the schedule?
                for field_of_interest_name in field_names_of_interest:
                    if field_of_interest_name not in field_names:
                        return_value.append_message ("{} not in schedule...skipping schedule: {}".format(field_of_interest_name, schedule_name))
                        continue

            # check if we have any field names of interest in the schedule, if not assume we want all fields:
            if len(field_names_of_interest) == 0:
                # assume we want all fields if no field names of interest were provided
                field_names_of_interest = field_names

            # get the column width for each field of interest:
            for field_of_interest_name in field_names_of_interest:
                # get the field of interest
                field_of_interest =  get_field_from_schedule_by_field_name(s, field_of_interest_name)
            
                # check if we got something...we definitely should have since we checked the field names but just in case
                if field_of_interest is None:
                    return_value.append_message ("{} not in schedule...skipping it".format(field_of_interest_name))
                
                # get the column width in inches for the field of interest
                column_width = field_of_interest.SheetColumnWidth
               
                # store the column data as a tuple of field name and column width
                column_data = (field_of_interest_name, column_width)

                # append the column data to the row data
                row_data.append(column_data)
            
            schedules_data.append(row_data)
    except Exception as e:
        return_value.append_message("Error getting column data: {}".format(str(e)))
        return_value.status = False
        return return_value

    return_value.result = schedules_data
    return return_value