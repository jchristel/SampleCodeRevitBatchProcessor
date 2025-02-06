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

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A module containing event names used by the view model and the Revit model. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

# Event names

# safety off mode
VIEW_MODEL_SAFETY_OFF_MODE = "ViewModelSafetyOffMode"

# safety off button text
VIEW_MODEL_SAFETY_BUTTON_TEXT="SafetyButtonText"

# filter column changed
VIEW_MODEL_SELECTED_FILTER_BY_COLUMN ="SelectedColumnFilterItem"

# filter value changed
VIEW_MODEL_SELECTED_FILTER_BY_VALUE = "SelectedValueFilterItem"

# selected row changed
VIEW_MODEL_SELECTED_ROW = "SelectedRow"

# data file path change
VIEW_MODEL_DATA_FILE_PATH = "DataFilePath"

# view data has been updated
VIEW_MODEL_DATA_VIEW_UPDATED = "DataView"

# selected file path has changed and the valid file path flag has been updated
VIEW_MODEL_SELECTED_FILE_PATH = "SelectedFilePath"

# event raised when the selected file path is valid flag has been updated
VIEW_MODEL_SELECTED_FILE_PATH_IS_VALID = "SelectedFilePathIsValid"

# event raised when a row filter is applied to the data view
VIEW_MODEL_IS_FILTER_APPLIED = "IsFilterApplied"

# view model active design set and option changed
VIEW_MODEL_ACTIVE_DESIGN_SET_AND_OPTION = "ActiveDesignSetAndOptionName"

# rooms in the model have been updated
REVIT_MODEL_ROOMS_UPDATED = "RoomsUpdated"