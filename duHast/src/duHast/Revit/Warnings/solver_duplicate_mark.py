"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Duplicate mark warnings solver class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2020  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

from duHast.Revit.Common import parameter_get_utils as rParaGet
from duHast.Revit.Common import parameter_set_utils as rParaSet
from duHast.Utilities.Objects import result as res


# import Autodesk
import Autodesk.Revit.DB as rdb
from duHast.Utilities.Objects import base


class RevitWarningsSolverDuplicateMark(base.Base):
    def __init__(self, filter_func, filter_values=[]):
        """
        Constructor: this solver takes two arguments: a filter function and a list of values to filter by

        :param filter_func: A function to filter elements in warnings by
        :type filter_func: func(document, elementId, list of filter values)
        :param filter_values: A list of filter values, defaults to []
        :type filter_values: list, optional
        """

        # ini super class to allow multi inheritance in children!
        super(RevitWarningsSolverDuplicateMark, self).__init__()

        self.filter = filter_func
        self.filter_values = filter_values
        self.filter_name = "Duplicate mark value."

    # --------------------------- duplicate mark guid ---------------------------
    #: guid identifying this specific warning
    GUID = "6e1efefe-c8e0-483d-8482-150b9f1da21a"

    def solve_warnings(self, doc, warnings):
        """
        Solver setting element mark to nothing, provided it passes the filter.

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param warnings: List of warnings to be solved.
        :type warnings: Autodesk.Revit.DB.FailureMessage

        :return:
            Result class instance.

            - .result = True if all duplicate mark warnings could be solved. Otherwise False.
            - .message will contain stats in format parameter value set to ''

        :rtype: :class:`.Result`
        """

        return_value = res.Result()
        if len(warnings) > 0:
            for warning in warnings:
                element_ids = warning.GetFailingElements()
                for el_id in element_ids:
                    element = doc.GetElement(el_id)
                    # check whether element passes filter
                    if self.filter(doc, el_id, self.filter_values):
                        try:
                            p_value = rParaGet.get_built_in_parameter_value(
                                element, rdb.BuiltInParameter.ALL_MODEL_MARK
                            )
                            if p_value != None:
                                result = rParaSet.set_built_in_parameter_value(
                                    doc,
                                    element,
                                    rdb.BuiltInParameter.ALL_MODEL_MARK,
                                    "",
                                )
                                return_value.update(result)
                        except Exception as e:
                            return_value.update_sep(
                                False,
                                "Failed to solve warning duplicate mark with exception: {}".format(
                                    e
                                ),
                            )
                    else:
                        return_value.update_sep(
                            True,
                            "Element removed by filter: {} : {}".format(
                                self.filter_name, rdb.Element.Name.GetValue(element)
                            ),
                        )
        else:
            return_value.update_sep(
                True, "No warnings of type: duplicate mark in model."
            )
        return return_value
