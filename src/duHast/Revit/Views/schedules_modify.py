"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit view schedule modifications. 
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

from duHast.Revit.Views.schedules_fields import get_field_names_from_schedule, get_field_from_schedule_by_field_name
from duHast.Revit.Common.transaction import in_transaction

from Autodesk.Revit.DB import (
    Element,
    UnitUtils,
    UnitTypeId,
    Transaction
    )


def adjust_column_width(doc, schedules, field_name, column_width_in_mm=6.35):
	"""
	Adjusts the column width of a specified field in a list of schedules.

	:param doc: The Revit document object.
	:type doc: Autodesk.Revit.DB.Document
	:param schedules: A list of Revit schedule objects to adjust.
	:type schedules: list of Autodesk.Revit.DB.ViewSchedule
	:param field_name: The human readable name of the field to adjust the column width for.
	:type field_name: str
	:param column_width_in_inches: The desired column width in inches (default is 0.25 inches).
	:type column_width_in_inches: float

	:return: A Result object containing a list of schedules that were skipped because they did not contain the specified field.
	:rtype: duHast.Utilities.Objects.result.Result
	"""

	return_value = Result()
	irregular_schedules = []
	
	column_width_in_feet = UnitUtils.ConvertToInternalUnits(column_width_in_mm, UnitTypeId.Millimeters)

	for s in schedules:
		schedule_name = Element.Name.GetValue(s)
		return_value.append_message ("Adjusting schedule: {}".format(schedule_name))
		field_names = get_field_names_from_schedule(s)
		
		# check if field is in schedule
		if field_name not in field_names:
			#print(",".join(field_names))
			return_value.append_message ("{} not in schedule...skipping schedule: {}".format(field_name, schedule_name))
			irregular_schedules.append(s)
			continue
		
		# get the field of interest
		field_of_interest =  get_field_from_schedule_by_field_name(s, field_name)
		
		# check if we got something...we definitely should have since we checked the field names but just in case
		if field_of_interest is None:
			return_value.append_message ("{} not in schedule...skipping it".format(field_name))
		
		# set the width in an action
		def action():
			action_return_value = Result()
			try:
				# set the desired column width in inches
				field_of_interest.SheetColumnWidth = column_width_in_feet

			except Exception as e:
				action_return_value.update_sep(False, "Failed to set column width: {}".format(e))
		
			return action_return_value
		
		# set up a transaction to set the width
		tranny = Transaction(doc, "Schedule {} Set field {} width to: {}".format(schedule_name, field_name, column_width_in_mm))
		tranny_result = in_transaction(tranny, action)
		
		# check what came back
		if tranny_result.status:
			return_value.append_message ("...Set column width successfully")
		else:
			return_value.update_sep(False,"Failed to set column schedule width:{}".format(tranny_result.message))
	
	return_value.result = irregular_schedules
	return return_value