"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Helper functions for benchmarking:. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- two values
- whether a text value starts or does not start with a given text value

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

import time


def measure_time(should_print=True):
    """
    Decorator function to measure the time a function takes to execute
    and then print it to the console.

    Use like:
    @measure_time(should_print = show_benchmarking_output_bool)
    def function_to_measure():
        pass

    :param should_print: Whether the elapsed time should be printed to the console
    :type should_print: bool
    """

    # Get the function name for the print statement
    def wrapper(func):
        func_name = func.__name__

        def wrapper_func(*args, **kwargs):
            # Get the start time
            start = time.time()
            # Execute the function
            result = func(*args, **kwargs)
            # Get the end time
            end = time.time()
            # Calculate the elapsed time
            elapsed = round(float(end - start), 5)
            # Print the elapsed time

            print("Elapsed time for {} is : {}".format(func_name, elapsed))
            # Return the result of the function
            return result

        if should_print:
            return wrapper_func
        else:
            return func

    return wrapper
