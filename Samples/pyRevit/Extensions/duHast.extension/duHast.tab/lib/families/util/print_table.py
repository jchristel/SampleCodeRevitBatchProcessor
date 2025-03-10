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

from Autodesk.Revit.DB import Element, ElementId

def print_result_table(output, data, header, table_title):

    # pad data rows to match header by appending empty strings
    # to end of individual rows

    # set a max row value to display
    max_row_number = 100

    # safety check
    if len(header) == 0:
        print("Header is empty. Cannot print table")
        return

    rows = []
    print("Data contains {} rows.".format(len(data)))
    for row in data:
        if len(row) < len(header):
            # pad row with empty strings
            row = row + [""] * (len(header) - len(row))
        rows.append(row)

    if len(rows) > max_row_number:
        print(
            "Table has too many rows to display. Printing only first {} rows".format(
                max_row_number
            )
        )
        rows = rows[:max_row_number]

    # print( "Printing table with {} rows and {} columns".format(len(rows), len(header)))

    # return
    output.print_table(
        table_data=rows,
        title=table_title,
        columns=header,
        last_line_style="color:red;",
    )


def get_table_data_from_swap_result(doc, result_list):
    """
    Extracts data from the result list of the swap family instances function
    and returns a list of host families and host groups that could not be swapped
    because they host other instances

    :param doc: Revit Document
    :param result_list: list of tuples containing swap result data
    :return: a tuple containing two lists
    """

    # the result lit is made up of tuples containing three entries

    # 1. the id's of family instances swapped out
    # 2. a dictioanry in format (Host Family Id:[list of instances not swapped because they are hosted in this family])
    # 3. a dictionary in format (Group Type Id:[list of instances not swapped because they are hosted in this group])

    host_fams = []
    host_groups = []
    for data in result_list:
        if (isinstance(data, tuple)):

            if len(data) != 3:
                continue

            for fam_id, instance_count in data[1].items():
                host_fams.append([Element.Name.GetValue(doc.GetElement(ElementId(fam_id))), instance_count])
            
            for group_id, instance_count in data[2].items():
                host_groups.append([Element.Name.GetValue(doc.GetElement(ElementId(group_id))), instance_count])
    
    return host_fams, host_groups