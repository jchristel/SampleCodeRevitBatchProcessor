"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
area separation lines solver class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Currently address' area separation lines overlapping with other area separation lines only.
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
from duHast.Revit.Warnings.Utility.curves_util import (
    get_curves_from_failure_messages,
    check_curves_overlaps,
    delete_curves,
    modify_curves_by_lengthening,
    modify_curves_by_shortening,
)
from duHast.Revit.Common.transaction import in_transaction
from duHast.Revit.Warnings.warning_guids import AREA_SEPARATION_LINES_OVERLAP


class RevitWarningsSolverAreaSepLinesOverlap(base.Base):
    """
    A solver that addresses overlapping area separation lines in a Revit model.
    It can delete or modify these lines to resolve the overlap issue.

    Example Usage:
    solver = RevitWarningsSolverAreaSepLinesOverlap()
    result = solver.solve_warnings(doc, warnings)
    print(result.status)
    print(result.message)

    Main functionalities:
    - Solving overlapping area separation lines by deleting or modifying them.
    - Ignoring area separation lines that overlap when they are in group instances.
    """

    def __init__(
        self,
        solve_by_lengthening_curves=True,
        group_id=-1,
        transaction_manager=in_transaction,
        callback=None,
    ):
        """
        Class constructor.

        :param solve_by_lengthening_curves: Whether to solve the overlapping curves by lengthening or shortening. Defaults to True.
        :type solve_by_lengthening_curves: bool, optional
        :param group_id: The group ID that the curves need to belong to for processing. Defaults to -1.
        :type group_id: int, optional
        :param transaction_manager: The transaction manager function used to perform the modifications. Defaults to in_transaction.
        :type transaction_manager: function, optional
        :param callback: An optional callback function.
        :type callback: function, optional
        """

        # ini super class to allow multi inheritance in children!
        super(RevitWarningsSolverAreaSepLinesOverlap, self).__init__()
        self.filter_name = "Area separation lines overlap."
        self.solve_by_lengthening_curves = solve_by_lengthening_curves
        self.transaction_manager = transaction_manager
        self.group_id = group_id
        self.callback = callback

    # --------------------------- area separation lines ---------------------------
    #: guid identifying this specific warning
    GUID = AREA_SEPARATION_LINES_OVERLAP

    def solve_warnings(self, doc, warnings):
        """
        Solver addressing overlapping area separation lines.

        - will ignore area separation lines overlapping when in different group instances.

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param warnings: List of warnings to be solved.
        :type warnings: Autodesk.Revit.DB.FailureMessage

        :return:
            Result class instance.

            - .status True if all area separation lines could be deleted / modified without an exception. Otherwise False.
            - .message will be 'moved tag to area xyz'

        :rtype: :class:`.Result`
        """

        return_value = res.Result()
        if len(warnings) > 0:
            # extract model lines and geometry from failure messages
            curve_storage_sets = get_curves_from_failure_messages(
                doc=doc, failure_messages=warnings, group_id=self.group_id
            )
            # get curves which are completely within other curves
            curves_to_delete = check_curves_overlaps(
                curves=curve_storage_sets, group_id=self.group_id
            )
            # delete those curves
            delete_curves_status = delete_curves(
                doc=doc, curves_to_delete=curves_to_delete, curve_descriptor="area"
            )
            return_value.update(delete_curves_status)
            if self.solve_by_lengthening_curves:
                # attempt to modify overlapping curves by lengthening the longer curve to
                # the length of the shorter curve and thereby completely overlapping the shorter curve
                modify_curves_status = modify_curves_by_lengthening(
                    doc=doc,
                    guid=self.GUID,
                    group_id=self.group_id,
                    transaction_manager=self.transaction_manager,
                    callback=self.callback,
                )
                return_value.update(modify_curves_status)
            else:
                # attempt to modify overlapping curves by shortening the longer curve to
                # the point of overlap with the shorter curve
                modify_curves_status = modify_curves_by_shortening(
                    doc=doc,
                    guid=self.GUID,
                    group_id=self.group_id,
                    transaction_manager=self.transaction_manager,
                    callback=self.callback,
                )
                return_value.update(modify_curves_status)
        else:
            return_value.update_sep(
                True,
                "{}: No warnings of type: area separation lines overlap in model.".format(
                    self.filter_name
                ),
            )
        return return_value
