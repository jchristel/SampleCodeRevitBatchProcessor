"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit transaction wrapper utility functions.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#!/usr/bin/python
# -*- coding: utf-8 -*-
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright © 2023, Jan Christel
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

# class used for stats reporting
from duHast.Utilities.Objects import result as res

# type checker
# from typing import List, Callable

# --------------------------------------------Transactions-----------------------------------------


def in_transaction(
    tranny,  #
    action,  # type: Callable[[], res.Result]
    doc=None,  # used as placeholder...
):
    # type: (...) -> res.Result
    """
    Revit transaction wrapper.

    This function is used to execute any actions requiring a transaction in the Revit api. On exception this will roll back the transaction.

    :param tranny: The transaction to be executed.
    :type tranny: Autodesk.Revit.DB.Transaction
    :param doc: The current model document. (not used in this function)
    :type doc: Autodesk.Revit.DB.Document
    :param action: The action to be nested within the transaction. This needs to return a Result class instance!
    :type action: action().

    :return:
        Result class instance.

        - .result = True if successfully executed transaction, otherwise False.

    :rtype: :class:`.Result`
    """

    return_value = res.Result()
    try:
        tranny.Start()
        try:
            tranny_result = action()
            tranny.Commit()
            # check what came back
            if tranny_result != None:
                # store false value
                return_value = tranny_result
        except Exception as e:
            tranny.RollBack()
            return_value.update_sep(False, "Failed with exception: {}".format(e))
    except Exception as e:
        return_value.update_sep(False, "Failed with exception: {}".format(e))
    return return_value
