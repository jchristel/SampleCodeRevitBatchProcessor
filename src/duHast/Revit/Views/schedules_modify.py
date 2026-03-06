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
from duHast.Revit.Common.element_id import get_el_id_int
from duHast.UI.Objects.ProgressBase import ProgressBase

from Autodesk.Revit.DB import (
    Element,
    UnitUtils,
    UnitTypeId,
    Transaction
    )


def adjust_column_width(doc, schedules, field_data, callback_progress=None):
	"""
	Adjusts the column width of a specified field in a list of schedules.

	:param doc: The Revit document object.
	:type doc: Autodesk.Revit.DB.Document
	:param schedules: A list of Revit schedule objects to adjust.
	:type schedules: list of Autodesk.Revit.DB.ViewSchedule
	:param field_data: A dictionary where the key is the schedule id and the values are another dictionary with the field name (key) and column width (value) to set.
	:type field_data: dict[int, dict[str, int]]
	:param callback_progress: An optional callback function to update the progress of the operation. The function should accept two parameters: the current progress (int) and the maximum progress (int).
	:type callback_progress: function, optional
	
	:return: A Result object containing a list of schedules that were skipped because they did not contain the specified field.
	:rtype: duHast.Utilities.Objects.result.Result
	"""

	return_value = Result()
	irregular_schedules = []

	if isinstance(callback_progress, ProgressBase) == False and callback_progress is not None:
		raise ValueError("callback_progress is not a ProgressBase: {}".format(type(callback_progress)))
	

	# progress bar data
	max = len(schedules)
	counter = 1

	for s in schedules:
		# update the progress bar
		counter += 1
		if callback_progress:
			callback_progress.update(counter, max)

		schedule_name = Element.Name.GetValue(s)
		return_value.append_message ("Adjusting schedule: {}".format(schedule_name))
		field_names_in_schedule = get_field_names_from_schedule(s)
		
		schedule_field_data = field_data.get(int(get_el_id_int(s.Id)), None)

		if schedule_field_data is None:
			return_value.append_message ("No field data found for schedule {}...skipping it".format(schedule_name))
			irregular_schedules.append(s)
			continue

		# set all field widths within one transaction
		# set the width in an action
		def action():
			action_return_value = Result()
			try:
				# loop over all fields and widths to set for the schedule
				for field_name, field_width in schedule_field_data.items():

					# check if field is in schedule
					if field_name not in field_names_in_schedule:
						#print(",".join(field_names))
						action_return_value.append_message ("{} not in schedule...skipping schedule: {}".format(field_name, schedule_name))
						irregular_schedules.append(s)
						continue
				
					# get the field of interest
					field_of_interest =  get_field_from_schedule_by_field_name(s, field_name)
				
					# check if we got something...we definitely should have since we checked the field names but just in case
					if field_of_interest is None:
						action_return_value.append_message ("{} not in schedule...skipping it".format(field_name))

					#convert mm to internal units (feet) since the API expects the width to be set in feet, even though we want to work with mm
					column_width_in_feet = UnitUtils.ConvertToInternalUnits(field_width, UnitTypeId.Millimeters)
					# set the desired column width in inches
					field_of_interest.SheetColumnWidth = column_width_in_feet
					# all good, report back what we did
					action_return_value.append_message ("Set column width for field {} to {} mm in schedule {}".format(field_name, field_width, schedule_name))

			except Exception as e:
				action_return_value.update_sep(False, "Failed to set column width: {}".format(e))
		
			return action_return_value
		
		# set up a transaction to set the width
		tranny = Transaction(doc, "Schedule {} Set fields".format(schedule_name))
		tranny_result = in_transaction(tranny, action)
	
		# check what came back
		if tranny_result.status:
			return_value.append_message ("...Set column width successfully")
		else:
			return_value.update_sep(False,"Failed to set column schedule width:{}".format(tranny_result.message))

		if callback_progress and callback_progress.is_cancelled() == True:
			return_value.append_message("Cancelled by user")
			break
	
	return_value.result = irregular_schedules
	return return_value