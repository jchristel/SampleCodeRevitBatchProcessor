"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit MEP systems names (ENG). 
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

# Duct types are split into three major families
#: Built in family name for oval ducting
DUCT_OVAL_FAMILY_NAME = "Oval Duct"
#: Built in family name for round ducting
DUCT_ROUND_FAMILY_NAME = "Round Duct"
#: Built in family name for rectangular ducting
DUCT_RECTANGULAR_FAMILY_NAME = "Rectangular Duct"

#: List of all Built in ducting family names
BUILTIN_DUCT_TYPE_FAMILY_NAMES = [
    DUCT_OVAL_FAMILY_NAME,
    DUCT_ROUND_FAMILY_NAME,
    DUCT_RECTANGULAR_FAMILY_NAME,
]

# flex duct types are split into two major families
#: Built in family name for rectangular flex ducting
FLEX_DUCT_REC_FAMILY_NAME = "Flex Duct Rectangular"
#: Built in family name for round flex ducting
FLEX_DUCT_ROUND_FAMILY_NAME = "Flex Duct Round"

#: List of all Built in flex ducting family names
BUILTIN_FLEX_DUCT_TYPE_FAMILY_NAMES = [
    FLEX_DUCT_REC_FAMILY_NAME,
    FLEX_DUCT_ROUND_FAMILY_NAME,
]

# conduits types are split into two major families
#: Built in family name for conduits with fittings
CONDUIT_WITH_FITTING_FAMILY_NAME = "Conduit with Fittings"
#: Built in family name for conduits without fittings
CONDUIT_WITHOUT_FITTING_FAMILY_NAME = "Conduit without Fittings"

#: List of all Built in conduit family names
BUILTIN_CONDUIT_TYPE_FAMILY_NAMES = [
    CONDUIT_WITH_FITTING_FAMILY_NAME,
    CONDUIT_WITHOUT_FITTING_FAMILY_NAME,
]

# cable tray types are split into two major families
#: Built in family name for cable tray with fittings
CABLE_TRAY_WITH_FITTING_FAMILY_NAME = "Cable Tray with Fittings"
#: Built in family name for cable tray without fittings
CABLET_RAY_WITHOUT_FITTING_FAMILY_NAME = "Cable Tray without Fittings"

#: List of all Built in cable tray family names
BUILTIN_CABLE_TRAY_TYPE_FAMILY_NAMES = [
    CABLE_TRAY_WITH_FITTING_FAMILY_NAME,
    CABLET_RAY_WITHOUT_FITTING_FAMILY_NAME,
]

# pipe types exist in one major families
#: Built in family name for pipes
PIPE_FAMILY_NAME = "Pipe Types"

#: List of all Built in pipe family names
BUILTIN_PIPE_TYPE_FAMILY_NAMES = [PIPE_FAMILY_NAME]
