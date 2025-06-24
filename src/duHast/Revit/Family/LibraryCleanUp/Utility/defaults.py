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



from duHast.Utilities.date_stamps import FILE_DATE_STAMP_YYYY_MM_DD, get_date_stamp
from duHast.Revit.Family.Data.Objects.family_directive_copy import FamilyDirectiveCopy
from duHast.Revit.Family.Data.Objects.family_directive_swap_instances_of_type import FamilyDirectiveSwap

# the parameter containing the grouping code in each family
GROUPING_CODE_PARAMETER_NAME = "HSL_AHFG_CODE"

# file name of swap directives
SWAP_DIRECTIVE_FILE_NAME = "{} {}{}".format(
    FamilyDirectiveSwap.SWAP_DIRECTIVE_FILE_NAME_PREFIX, 
    get_date_stamp(FILE_DATE_STAMP_YYYY_MM_DD),
    FamilyDirectiveSwap.SWAP_DIRECTIVE_FILE_EXTENSION
)

# prefix for the file name of maintain family types by family directives
MAINTAIN_TYPES_BY_FAMILY_FILE_NAME_PREFIX = "maintain_types_by_family"
# file name of maintain family types by family directives
MAINTAIN_TYPES_BY_FAMILY_FILE_NAME = "{} {}.csv".format(MAINTAIN_TYPES_BY_FAMILY_FILE_NAME_PREFIX, get_date_stamp(FILE_DATE_STAMP_YYYY_MM_DD))

# file name for copy directive
COPY_DIRECTIVE_FILE_NAME = "{} {}{}".format(
    FamilyDirectiveCopy.COPY_DIRECTIVE_FILE_NAME_PREFIX, 
    get_date_stamp(FILE_DATE_STAMP_YYYY_MM_DD), 
    FamilyDirectiveCopy.COPY_DIRECTIVE_FILE_EXTENSION
)

# file name for duplicate copy directives
DUPLICATE_COPY_DIRECTIVE_FILE_NAME = "{} {}{}".format(
    "duplicate__"+FamilyDirectiveCopy.COPY_DIRECTIVE_FILE_NAME_PREFIX, 
    get_date_stamp(FILE_DATE_STAMP_YYYY_MM_DD), 
    FamilyDirectiveCopy.COPY_DIRECTIVE_FILE_EXTENSION
)

# file name for families with missing group codes
FAMILIES_WITH_MISSING_GROUP_CODES_FILE_NAME = "missing_group_codes {}.csv".format(get_date_stamp(FILE_DATE_STAMP_YYYY_MM_DD))

# file name prefix depending on the family category
CATEGORY_FILE_NAME_PREFIX_MAPPER = {
    "Audio Visual Devices": "AVD",
    "Casework": "CSW",
    "Data Devices": "DAT",
    "Electrical Equipment": "ELE",
    "Electrical Fixtures": "ELF",
    "Fire Alarm Devices": "FIR",
    "Furniture": "FRN",
    "Furniture Systems": "FRS",
    "Generic Models": "GEN",
    "Lighting Devices": "LGD",
    "Lighting Fixtures": "LGF",
    "Mechanical Equipment": "MEC",
    "Medical Equipment": "MEF",
    "Nurse Call Devices": "NRS",
    "Plumbing Fixtures": "PLM",
    "railings": "RLG",
    "Security Devices": "SEC",
    "Specialty Equipment": "SPC",
    "Sprinklers": "SPR",
    "Telephone Devices": "TEL",
    "Windows": "WDW",
}