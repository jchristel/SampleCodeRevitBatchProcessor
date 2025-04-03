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
from Autodesk.Revit.DB import Element, FamilyInstance, FilteredElementCollector

from families.util.print_table import print_result_table

# family name prefix to identify the elements to be processed
PUSH_IT_COMMAND_NAME = "WLL"


def basic_stats_entry(doc,  uiapp, output, forms):
    """
    This function will give you a basic statistics of the elements in the document.
    """

    # set up a status tracker
    return_value = Result()

    # Get all family instances in the document
    col = FilteredElementCollector(doc).OfClass(FamilyInstance)
    stats = {}
    for c in col:
        fam_name = Element.Name.GetValue(c.Symbol.Family)
        if (fam_name.startswith(PUSH_IT_COMMAND_NAME)):
            if not fam_name in stats:
                stats[fam_name] = []
            stats[fam_name].append(c.Id.IntegerValue)


    # check if there are any elements in the document
    if len(stats) == 0:
        print("No PushIt elements found in the document.")
        return_value.update_sep(True,"No PushIt elements found in the document.")
        return return_value
    
    # reformat data for printing
    data = []

    # get the list of keys sorted by family name
    keys = sorted(stats.keys())

    # iterate over the keys and get the data
    for key in keys:
        data.append([key, len(stats[key])])

    # print the data
    print_result_table(output=output, data=data, header= ["Family Name", "Count"], table_title= "Basic Statistics of PushIt Elements")

    # set the return value
    return_value.update_sep(True,"Successfully processed the elements in the document.")

    return return_value