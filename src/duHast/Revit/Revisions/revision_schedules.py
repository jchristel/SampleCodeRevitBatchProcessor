"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit revision schedules.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2026, Jan Christel
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

from Autodesk.Revit.DB import (
    ElementClassFilter,
    ScheduleSheetInstance
)

def get_revision_schedule_from_sheet(doc, sheet):
    """
    Gets the revision schedule instance from a given sheet. 
    
    If no revision schedule is found, None is returned.
    If multiple are fopund, the first one is returned.

    :param doc: Current Revit model document.
    :type doc: Autodesk.Revit.DB.Document
    :param sheet: Sheet to get revision schedule from.
    :type sheet: Autodesk.Revit.DB.ViewSheet
    
    :return: Revision schedule instance or None if not found.
    :rtype: Autodesk.Revit.DB.ScheduleSheetInstance or None
    """
    
    filter = ElementClassFilter(ScheduleSheetInstance)
    schedules_on_sheet_ids = sheet.GetDependentElements(filter)
	
	# note: there is a chance that there is no revision schedule:
	# sheet has no title block, or titleblock has no revision schedule
	
    if len(schedules_on_sheet_ids) == 0:
        return None
    
    for schedule_instance_id in schedules_on_sheet_ids:
        schedule_instance = doc.GetElement(schedule_instance_id)
        if schedule_instance.IsTitleblockRevisionSchedule:
            # found a revision schedule
            return schedule_instance
    
    return None