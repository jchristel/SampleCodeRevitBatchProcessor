"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Class for family line pattern data storage class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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

from duHast.Revit.Family.Data.Objects import ifamily_data_storage as IFamDataStorage


class FamilyLinePatternDataStorage(IFamDataStorage.IFamilyDataStorage):

    # data type for this class ( used in reports as first entry per row )
    data_type = "LinePattern"

    # number of properties in this class ( used in report reader function )
    number_of_properties = 9

    def __init__(
        self,
        root_name_path,
        root_category_path,
        family_name,
        family_file_path,
        use_counter,
        used_by,
        pattern_name,
        pattern_id,
        **kwargs
    ):
        
        # store args in base class
        super(FamilyLinePatternDataStorage, self).__init__(
            data_type=FamilyLinePatternDataStorage.data_type,
            root_name_path=root_name_path,
            root_category_path=root_category_path,
            family_name=family_name,
            family_file_path=family_file_path,
        )

        # store other args in this class
        self.use_counter = use_counter
        self.used_by = used_by
        self.pattern_name = pattern_name
        self.pattern_id = pattern_id