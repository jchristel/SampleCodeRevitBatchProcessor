"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module contains a number of helper functions relating to Revit revisions on sheets.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


To get the complete revision history of a sheet, without using a revision schedule, use this module.

The flow is as follows if revisions vary by sheet:
- from a sheet, get the revisions on the sheet using ViewSheet.GetAllRevisionIds()
- loop over each revision id and get the revision element using Document.GetElement(revisionId)
    - for each revision element, you can access its properties such as Description ,issue date etc 
    - for each revision get the revision sequence id using Revision.GetRevisionSequenceId()
    - build a dictionary with revision sequence id as key and revision element id and index of revision on the sheet as value pair list, this will allow you to get the actual revision value from the sequence:
        - 1.st entry in list has the matching sequence entry of index 0 etc
        - keeping the index allows to rebuild the original order of revisions on the sheet with their appropriate sequence values

        
loop over revision sequence id dictionary:
- find the sequential index value (starting with 0) and get the sequence id
- from the sequence id get the revision sequence element using Document.GetElement(revisionSequenceId)
- from the revision sequence element get the actual sequence
- from the sequence get the actual revision value using the index of the revision and index value pair list built earlier

return the list of revision values, revision Id' in the order of the sheet revisions


The flow is as follows if revisions are the same for all sheets:
- from a sheet, get the revisions on the sheet using ViewSheet.GetAllRevisionIds()
- loop over each revision id and get the revision element using Document.GetElement(revisionId)
    - get the revisionNumberProperty from the revision element
    - add  the revision number to a list together with the revision element id as a tuple

return the list of revision values, revision Id' in the order of the sheet revisions


general notes:

in alphanumeric mode: if the number of revisions exceeds the number of entries in the predefined sequence, the sequence continues with A,B,C...Z,AA,BB,CC,AAA,BBB,CCC and so on.
"""
#
# License:
#
#
# Revit Batch Processor Sample Code
#
# BSD License
# Copyright 2026, Jan Christel
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