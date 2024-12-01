"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Family Base data processing utility module.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Processes family_data_family objects using multi threading ( testing has shown results in multi threading are not as expected, so single core processing is used for now)

"""

#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2024, Jan Christel
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

import threading
import os
import queue

from duHast.Utilities.Objects import result as res
from duHast.Revit.Family.Data.family_report_reader import read_data_into_families


# def process_data(family_base_data_report_file_path, do_this):
#     """
#     Process family data using multi threading

#     :param family_base_data_report_file_path: str: path to directory containing family report files
#     :param do_this: function: function taking two args: list of family_data_family and result list

#     :return:
#         Result class instance.

#         - result.status. True if processing completed without an exception occurring.
#         - result.message will contain the summary messages of the process including time stamps.
#         - result.result [:class:`.FamilyDataFamily`]

#         On exception:

#         - result.status (bool) will be False.
#         - result.message will contain generic exception message.
#         - result.result will be empty

#     :rtype: :class:`.Result`
#     """

#     # do_this: function taking two args: list of family_data_family and result list
    

#     return_value = res.Result()
#     # results will be stored in here:
#     processing_result = []

#     try:
#         # read families into data
#         read_result = read_data_into_families(family_base_data_report_file_path)

#         return_value.update(read_result)
#         return_value.append_message(
#             "Number of family instances: {} read.".format(
#                 len(read_result.result),
#             )
#         )

#         # check if something went wrong
#         if not read_result.status:
#             raise ValueError(read_result.message)
#         elif len(read_result.result) == 0:
#             raise ValueError(
#                 "No family data found in file: {}".format(
#                     family_base_data_report_file_path
#                 )
#             )

#         # read results
#         return_value.result.append(read_result.result)

#         # set up some multithreading
#         core_count = int(os.environ["NUMBER_OF_PROCESSORS"])
#         return_value.append_message("cores: {}".format(core_count))

#         if core_count > 2:
#             # leave some room for other processes
#             core_count = core_count - 1
#             return_value.append_message("using threads: {}".format(core_count))
#             # attempt int division
#             chunk_size = len(read_result.result) // core_count
#             return_value.append_message("...chunk size: {}".format(chunk_size))
#             threads = []
#             start_value = 0
#             end_value = start_value + chunk_size
#             # set up threads
#             for i in range(core_count):
#                 if start_value + chunk_size <= len(read_result.result) - 1:
#                     end_value = start_value + chunk_size
#                 else:
#                     end_value = len(read_result.result)
#                 return_value.append_message(
#                     "......assigning chunk {} : {} of {}".format(
#                         start_value, end_value, len(read_result.result)
#                     )
#                 )
#                 t = threading.Thread(
#                     target=do_this,
#                     args=(
#                         read_result.result[start_value:end_value],
#                         processing_result,
#                     ),
#                 )
#                 threads.append(t)

#                 # increase the start value for the next processing chunk by 1 to avoid duplicate processing
#                 start_value = end_value + 1

#             # start up threads
#             for t in threads:
#                 t.start()
#             # wait for results
#             for t in threads:
#                 t.join()
#         else:
#             # no threading
#             processing_result = do_this(read_result.result, processing_result)
#     except Exception as e:
#         return_value.update_sep(
#             False, "Failed to read and process families with exception: {}".format(e)
#         )

#     return_value.result = processing_result
#     return return_value

def process_data(family_base_data_report_file_path, do_this):
    return_value = res.Result()
    processing_results = []

    try:
        read_result = read_data_into_families(family_base_data_report_file_path)
        return_value.update(read_result)
        return_value.append_message(
            "Number of family instances: {} read.".format(len(read_result.result))
        )

        if not read_result.status:
            raise ValueError(read_result.message)
        elif len(read_result.result) == 0:
            raise ValueError(
                "No family data found in file: {}".format(family_base_data_report_file_path)
            )

        return_value.result.append(read_result.result)
        core_count = int(os.environ.get("NUMBER_OF_PROCESSORS", 1))
        return_value.append_message("cores: {}".format(core_count))

        # if core_count > 2:
        #     core_count -= 1
        #     return_value.append_message("using threads: {}".format(core_count))
        #     chunk_size = len(read_result.result) // core_count
        #     return_value.append_message("...chunk size: {}".format(chunk_size))
        #     threads = []
        #     start_value = 0

        #     for i in range(core_count):
        #         end_value = min(start_value + chunk_size, len(read_result.result))
        #         return_value.append_message(
        #             "......assigning chunk {} : {} of {}".format(start_value, end_value, len(read_result.result))
        #         )
        #         thread_result = []
        #         t = threading.Thread(
        #             target=do_this,
        #             args=(read_result.result[start_value:end_value], thread_result)
        #         )
        #         threads.append((t, thread_result))
        #         t.start()
        #         start_value = end_value + 1

        #     for t, thread_result in threads:
        #         t.join()
        #         processing_results.extend(thread_result)
        # else:
        
        # go single core for now only...multi thread processing is not working
        result = do_this(read_result.result, processing_results)
        return_value.result = result
    except Exception as e:
        return_value.update_sep(False, "Failed to read and process families with exception: {}".format(e))

    return_value.result = processing_results
    return return_value