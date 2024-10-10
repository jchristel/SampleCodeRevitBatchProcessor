"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A number of helper functions relating to py pyrevit output to console duHast result class.
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

from pyrevit import script
from duHast.Utilities.Objects.result import Result


def print_result(result, header=None):
    """
    Prints a result class instance to the pyRevit console.



    :param result: The result instance to be printed.
    :type result: Result
    :param header: The header to be printed before the result.
    :type header: str
    """

    # check if result is of type Result
    if not isinstance(result, Result):
        raise TypeError("result must be of type Result")

    # print header if it exists
    if header != None:
        print_header(header)

    # print the results message property
    # split the message by new line and print each line
    messages = result.message.split("\n")
    for m in messages:
        print("...{}".format(m))

    # print the status of the result
    print("Finished with status: {}!".format(result.status))


def print_header(header):
    """
    Prints a header to the pyRevit console.

    :param header: The header to be printed.
    :type header: str
    """

    output = script.get_output()
    if header != None:
        output.print_md("### {}".format(header))
