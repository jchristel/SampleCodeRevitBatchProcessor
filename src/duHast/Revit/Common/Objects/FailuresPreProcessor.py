"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
An implementation of the Revit IFailuresProcessor interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Helps to pre process warnings in Revit.

"""

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


from Autodesk.Revit.DB import IFailuresPreprocessor

from duHast.Utilities.Objects.result import Result
from duHast.Revit.Common.failure_handling import process_failures
from duHast.Revit.Common.Objects.FailureHandlingConfiguration import (
    FailureHandlingConfig,
)


class FailuresPreprocessor(IFailuresPreprocessor):
    def __init__(
        self,
        failure_processor=process_failures,
        result=Result(),
        fail_config=FailureHandlingConfig(),
    ):
        """
        Constructor for the FailuresPreprocessor class.

        :param failure_processor: The function to be used to process failures.
        :type failure_processor: function
        :param result: The result of the operation.
        :type result: duHast.Utilities.Objects.result.Result
        :param fail_config: The failure handling configuration.
        :type fail_config: duHast.Revit.Common.Objects.FailureHandlingConfiguration.FailureHandlingConfig

        """

        # some checking of the input parameters
        if callable(failure_processor):
            self.failure_processor = failure_processor
        else:
            raise TypeError("failure_processor must be a callable function")

        if isinstance(fail_config, FailureHandlingConfig):
            self.failure_handling_config = fail_config
        else:
            raise TypeError(
                "fail_config must be an instance of duHast.Revit.Common.Objects.FailureHandlingConfiguration.FailureHandlingConfig"
            )

        if isinstance(result, Result):
            self.result = result
        else:
            raise TypeError(
                "result must be an instance of duHast.Utilities.Objects.result.Result"
            )

        return

    def PreprocessFailures(self, failures_accessor):
        # If the failure processing function is the default from the failure_handling module
        # Then we need to pass the failure handling configuration to the function
        if self.failure_processor == process_failures:
            try:
                result = self.failure_processor(
                    failures_accessor,
                    self.failure_handling_config,
                )
            except Exception as e:
                print("exception in failure preprocessor: {}".format(e))
        else:
            result = self.failure_processor(failures_accessor, self.result)
        return result
