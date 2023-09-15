"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Room separation lines solver class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Currently address room separation lines overlapping with other room separation lines only.
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

from duHast.Utilities.Objects import result as res

from duHast.Utilities.Objects import base


class RevitWarningsSolverRoomSepLinesOverlap(base.Base):
    def __init__(self):
        """
        Empty constructor this solver does not take any further arguments.
        """

        # ini super class to allow multi inheritance in children!
        super(RevitWarningsSolverRoomSepLinesOverlap, self).__init__()
        self.filter_name = "Room separation lines overlap."

    # --------------------------- room tag not in room ---------------------------
    #: guid identifying this specific warning
    GUID = ""

    def solve_warnings(self, doc, warnings):
        """
        Solver addressing overlapping room separation lines.

        - will ignore room separation lines in groups.

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param warnings: List of warnings to be solved.
        :type warnings: Autodesk.Revit.DB.FailureMessage

        :return:
            Result class instance.

            - .result = True if all room separation lines could be deleted / modified without an exception. Otherwise False.
            - .message will be 'moved tag to room xyz'

        :rtype: :class:`.Result`
        """

        return_value = res.Result()
        if len(warnings) > 0:
            pass
        else:
            return_value.update_sep(
                True, "No warnings of type: room separation lines overlap."
            )
        return return_value
