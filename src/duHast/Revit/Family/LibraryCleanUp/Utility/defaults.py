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

# the parameter containing the grouping code in each family
GROUPING_CODE_PARAMETER_NAME = "HSL_AHFG_CODE"

# prefix for the file name of swap directives
SWAP_DIRECTIVE_FILE_NAME_PREFIX = "SwapDirective"
# file name of swap directives
SWAP_DIRECTIVE_FILE_NAME = "{} {}.csv".format(SWAP_DIRECTIVE_FILE_NAME_PREFIX, get_date_stamp(FILE_DATE_STAMP_YYYY_MM_DD))

# prefix for the file name of maintain family types by family directives
MAINTAIN_TYPES_BY_FAMILY_FILE_NAME_PREFIX = "maintain_types_by_family"
# file name of maintain family types by family directives
MAINTAIN_TYPES_BY_FAMILY_FILE_NAME = "{} {}.csv".format(MAINTAIN_TYPES_BY_FAMILY_FILE_NAME_PREFIX, get_date_stamp(FILE_DATE_STAMP_YYYY_MM_DD))
