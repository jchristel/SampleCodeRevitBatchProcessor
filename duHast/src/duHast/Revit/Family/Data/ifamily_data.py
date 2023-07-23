"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Interface for family data storage / processing class.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""

#
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
#

from duHast.Utilities.Objects import base

# common data dictionary keys
ROOT = "root"
ROOT_CATEGORY = "rootCategory"
FAMILY_NAME = "familyName"
FAMILY_FILE_PATH = "familyFilePath"
USAGE_COUNTER = "usageCounter"
USED_BY = "usedBy"


class IFamilyData(base.Base):
    def __init__(self, root_path, root_category_path=None, data_type=None, **kwargs):

        # forwards all unused arguments
        # ini super class to allow multi inheritance in children!
        super(IFamilyData, self).__init__(**kwargs)

        self.data = []

        if data_type != None:
            self.data_type = data_type
        else:
            self.data_type = "not declared"

        if root_path != None:
            self.root_path = root_path
        else:
            self.root_path = "-"

        if root_category_path != None:
            self.root_category_path = root_category_path
        else:
            self.root_category_path = "-"

    def process(self, doc):
        pass

    def get_data(self):
        pass

    def update_data(
        self,
        identify_by_this_property_name,
        identify_by_this_property_value,
        update_dic,
    ):
        match = False
        match_update = True
        for d in self.data:
            # print(identifyByThisPropertyName, d)
            if identify_by_this_property_name in d:
                # print('identify by property found')
                if d[identify_by_this_property_name] == identify_by_this_property_value:
                    # print ('dic', updateDic)
                    for update_prop in update_dic:
                        if update_prop in d:
                            old_value = d[update_prop]
                            d[update_prop] = update_dic[update_prop]
                            # print ('updated:', update_prop, ' from value ', old_value, ' to value ', d[update_prop])
                            match_update = match_update and True

        if match_update:
            return match_update
        else:
            return match

    def add_data(self):
        pass

    def _strip_file_extension(self, fam_name):
        """
        Strips the file extension '.rfa. , if exists, of the family  name.

        :param famName: The family name.
        :type famName: str
        :return: The truncated family name.
        :rtype: str
        """

        if fam_name.lower().endswith(".rfa"):
            fam_name = fam_name[:-4]
        return fam_name
