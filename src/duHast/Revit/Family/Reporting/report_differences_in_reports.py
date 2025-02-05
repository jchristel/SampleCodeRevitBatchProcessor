"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Module containing comparison reporting of family reports.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This mimicks an outer join between any number of reports. 

The reports are compared based on the family name, type name, parameter name:, 


family Name,    Type name,  parmater name,  report 1,   report 2,   report 3,   ...
family 1,       type 1,     parameter 1,    value 1,   N/A,        value 1,     ...
family 2,       type 2,     parameter 2,    N/A,       value 2,    value 3,     ...
family 3,       type 3,     parameter 3,    value 3,       N?A      N/A         ...


N/A = not available in that report
"""

# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2025, Jan Christel
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

from duHast.Utilities.Objects.result import Result
from duHast.Utilities.files_csv import read_csv_file
from duHast.Utilities.files_io import get_file_name_without_ext


def _build_report_dict(reports):
    # build a dictionary of the report
    report_dic = {}
    for report in reports:
        for report_name, report_content in report.items():
            for row in report_content [1:]:
                family_name = row[1]
                family_category = row[2]
                type_name = row[3]
                parameter_name = row[6]
                value = row[10]
                report_dic[(family_name, family_category, type_name, parameter_name)] = value
    
    return report_dic

        
def outer_join_report_a_vs_b(report_a, report_b):

    # this will compare initial a vs b and b vs a as well
    # the return will be a list of lists:
    # [ family Name,    Type name,  parmater name,  value report 1,   value report 2]
    
    # build a dictionary for each report:
    report_a_dict = _build_report_dict(report_a)
    report_b_dict = _build_report_dict(report_b)

    # Get all unique keys from both reports
    all_keys = set(report_a_dict.keys()).union(set(report_b_dict.keys()))
    
    # Perform the outer join
    outer_join = {}
    for key in all_keys:
        outer_join[key] = [report_a_dict.get(key), report_a_dict.get(key)]
    
    return outer_join


def compare_outer_join_result_with_report(report, outer_join_result):
    
    # build a dictionary from the report:
    report_dict = _build_report_dict(report)

    # Get all unique keys from both reports
    all_keys = set(report_dict.keys()).union(set(outer_join_result.keys()))

    # get the number of paddings required for the outer join result
    n_a_value = "N/A"
    padding_length = 2
    for key in outer_join_result:
        padding_length = len(outer_join_result[key])
        break

    # Perform the outer join:
    # if there is a match for a key in both dictionaries, then the value of the report need to be added to the outer join result for that key, which is a tuple of values
    # if there is no match for a key from the outer join result in the report, then N?A needs to be added to the outer join result for that key
    # if there is no match for a key from the report in the outer join result, then the key needs to be added to the outer join result and the value of the report need to be added
    # but the value needs to be padded with N/A for the other reports

    for key in all_keys:
        if key in report_dict:
            if key in outer_join_result:
                outer_join_result[key] = outer_join_result[key] + [report_dict[key],]
            else:
                outer_join_result[key] = [n_a_value for _ in range(padding_length)] + [report_dict[key],]
        else:
            outer_join_result[key] = outer_join_result[key] + [n_a_value,]
    
    return outer_join_result
   

def read_report(file_path):

    return_value = Result()
    data = {}

    try:
        # get the report name
        report_name = get_file_name_without_ext(file_path)
        # read the report
        read_result = read_csv_file(file_path)
        # check if the read was successful
        if read_result.status:
            data[report_name] = read_result.result
            return_value.append_message("Report read successfully: {}".format(report_name))
            return_value.result.append(data)
        else:
            # something went wrong...
            return_value.update_sep(False, read_result.message)
            return return_value
    except Exception as e:
        return_value.update_sep(False, str(e))
    return return_value


def compare_family_reports_outer_join(file_paths):

    return_value = Result()
    # make sure there at least two reports
    if len(file_paths) < 2:
        raise ValueError("At least two reports are required")
    
    # read reports into memory
    reports = []
    for file_path in file_paths:
        # get the report
        read_report_result = read_report(file_path)
        # check if reead ok, otherwise get out
        if not read_report_result.status:
            return read_report_result
        reports.append(read_report_result.result)
    
    #l og updates
    return_value.append_message("read {} reports.".format(len(reports)))
    
    # compare reports
    # do the initial report comparison
    outer_join_results = outer_join_report_a_vs_b(report_a= reports[0], report_b= reports[1])

    # get out if there are only 2 reports to compare
    if len(reports) == 2:
        return_value.result = outer_join_results
        return return_value
    
    # compare the outer join results with the remaining reports
    for report in reports[2:]:
        outer_join_results = compare_outer_join_result_with_report(report, outer_join_results)
    
    return_value.result = outer_join_results
    return  return_value

    
