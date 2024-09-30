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

from duHast.Revit.Common.parameter_get_utils import get_built_in_parameter_value
from duHast.Revit.Common.parameter_set_utils import (
    set_builtin_parameter_without_transaction_wrapper_by_name,
)
from duHast.Revit.Common.Objects.FailureHandlingConfiguration import (
    FailureHandlingConfig,
)
from duHast.Revit.Common.transaction import in_transaction_with_failure_handling
from duHast.Utilities.Objects import result as res
from duHast.Revit.Warnings.warning_guids import DUPLICATE_MARK_VALUE
from duHast.Utilities.Objects import base

# import Autodesk
from Autodesk.Revit.DB import BuiltInParameter, Element, Transaction


class RevitWarningsSolverDuplicateMark(base.Base):
    def __init__(
        self,
        filter_func,
        filter_values=None,
        callback=None,
    ):
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
        # check if default value
        if filter_values == None:
            self.filter_values = []
        else:
            self.filter_values = filter_values

        self.filter_name = "Duplicate mark value."
        self.callback = callback

    # --------------------------- duplicate mark guid ---------------------------
    #: guid identifying this specific warning
    GUID = DUPLICATE_MARK_VALUE

    IGNORED_WARNINGS = ["Type Mark"]

    def _setup_failure_handling_config(self):
        # define failure handling for the transaction ( push through on any warnings or errors )
        failure_handling_settings = FailureHandlingConfig(
            roll_back_on_warning=False,
            print_warnings=False,
            roll_back_on_error=False,
            print_errors=False,
        )
        return failure_handling_settings

    def solve_warnings(self, doc, warnings):
        """
        Solver setting element mark to nothing, provided it passes the filter.

        :param doc: Current Revit model document.
        :type doc: Autodesk.Revit.DB.Document
        :param warnings: List of warnings to be solved.
        :type warnings: Autodesk.Revit.DB.FailureMessage

        :return:
            Result class instance.

            - .status True if all duplicate mark warnings could be solved. Otherwise False.
            - .message will contain stats in format parameter value set to ''

        :rtype: :class:`.Result`
        """

        return_value = res.Result()
        if len(warnings) > 0:

            # report progress to call back if required
            counter = 0

            for warning in warnings:

                # report progress to call back if required
                if self.callback:
                    self.callback.update(counter, len(warnings))

                # Flag to indicate if we should continue the outer loop
                # ignoring this warning
                should_continue_outer = False

                # check for any duplicate Type Mark warnings...which are not to be addressed!
                for ignore in self.IGNORED_WARNINGS:
                    if ignore in warning.GetDescriptionText():
                        element_ids = warning.GetFailingElements()
                        for el_id in element_ids:
                            element = doc.GetElement(el_id)
                            return_value.update_sep(
                                True,
                                "{} Warning of type: duplicate {}. {} will be ignored.".format(
                                    self.filter_name,
                                    Element.Name.GetValue(element),
                                    ignore,
                                ),
                            )
                        should_continue_outer = True
                        break  # Break out of the inner loop (ignore this warning)
                if should_continue_outer:
                    continue  # Continue the outer loop

                # loop over elements in warning and set mark to an empty value
                element_ids = warning.GetFailingElements()
                # set up a failure handling config ignoring all warnings and errors
                failure_handling_config = self._setup_failure_handling_config()

                for el_id in element_ids:
                    element = doc.GetElement(el_id)
                    # check whether element passes filter
                    if self.filter(doc, el_id, self.filter_values):

                        try:
                            p_value = get_built_in_parameter_value(
                                element, BuiltInParameter.ALL_MODEL_MARK
                            )
                            if p_value != None:
                                # set up an action to run in a transaction with custom failure handling
                                def action():
                                    action_return_value = res.Result()
                                    try:
                                        action_return_value = set_builtin_parameter_without_transaction_wrapper_by_name(
                                            element=element,
                                            parameter_definition=BuiltInParameter.ALL_MODEL_MARK,
                                            parameter_value="",
                                        )
                                    except Exception as e:
                                        action_return_value.update_sep(
                                            False, "Failed with exception: {}".format(e)
                                        )
                                    return action_return_value

                                # set up the revit transaction
                                transaction = Transaction(
                                    doc, "Updating mark value to empty"
                                )
                                # run the action in the transaction
                                result = in_transaction_with_failure_handling(
                                    transaction=transaction,
                                    action=action,
                                    failure_config=failure_handling_config,
                                )
                                # setup return object message
                                message_prefix = "Updated mark on: {} [id:{}]".format(
                                    Element.Name.GetValue(element),
                                    element.Id.IntegerValue,
                                )
                                return_value.update_sep(
                                    result.status,
                                    "{} : {}".format(message_prefix, result.message),
                                )
                            else:
                                return_value.update_sep(
                                    True,
                                    "{}:  Element has no mark value: {}".format(
                                        self.filter_name,
                                        Element.Name.GetValue(element),
                                    ),
                                )
                        except Exception as e:
                            return_value.update_sep(
                                False,
                                "{}: Failed to solve warning duplicate mark with exception: {}".format(
                                    self.filter_name, e
                                ),
                            )
                    else:
                        return_value.update_sep(
                            True,
                            "{}: Element removed by filter: {}".format(
                                self.filter_name, Element.Name.GetValue(element)
                            ),
                        )

                # increase progress counter
                counter = counter + 1

                # check if cancelled
                if self.callback:
                    if self.callback.is_cancelled():
                        return_value.append_message("User cancelled!")
                        break
        else:
            return_value.update_sep(
                True,
                "{}: No warnings of type: duplicate mark in model.".format(
                    self.filter_name
                ),
            )
        return return_value
