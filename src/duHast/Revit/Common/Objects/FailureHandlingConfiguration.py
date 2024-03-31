"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
An implementation of Failur Handling Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Defines how to process warnings in Revit by storing the configuration for the failure handling.:
- Rolling back on warnings
- Printing warnings
- Rolling back on errors
- Printing errors
- Setting forced modal handling ( refer to autodesk documentation for more information )
- Setting clear after rollback ( refer to autodesk documentation for more information )

An output function is also provided to allow for custom output handling.

An instance of this class is passed to the failure handling function to determine how to handle failures.
"""

# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Peter Smith, Jan Christel
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

from duHast.Utilities.console_out import output
from duHast.Utilities.Objects.base import Base


class FailureHandlingConfig(Base):
    def __init__(
        self,
        roll_back_on_warning=False,
        print_warnings=False,
        roll_back_on_error=False,
        print_errors=False,
        set_forced_modal_handling=True,
        set_clear_after_rollback=True,
        output_function=output,
        **kwargs
    ):

        """
        Constructor for the FailureHandlingConfig class.

        :param roll_back_on_warning: Roll back the transaction on warnings.
        :type roll_back_on_warning: bool
        :param print_warnings: Print warnings.
        :type print_warnings: bool
        :param roll_back_on_error: Roll back the transaction on errors.
        :type roll_back_on_error: bool
        :param print_errors: Print errors.
        :type print_errors: bool
        :param set_forced_modal_handling: Set forced modal handling. ( refer to autodesk documentation for more information )
        :type set_forced_modal_handling: bool
        :param set_clear_after_rollback: Set clear after rollback. ( refer to autodesk documentation for more information )
        :type set_clear_after_rollback: bool
        :param output_function: A function to handle output.
        :type output_function: function
        :param kwargs: Additional keyword arguments.
        """

        super(FailureHandlingConfig, self).__init__(**kwargs)

        self.roll_back_on_warning = roll_back_on_warning
        self.print_warnings = print_warnings
        self.roll_back_on_error = roll_back_on_error
        self.print_errors = print_errors
        self.allowable_failures = None
        self.set_forced_modal_handling = set_forced_modal_handling
        self.set_clear_after_rollback = set_clear_after_rollback
        self.output_function = output_function
