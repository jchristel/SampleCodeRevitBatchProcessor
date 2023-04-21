'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit MEP systems names (ENG). 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2023  Jan Christel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

# Duct types are split into three major families
#: Built in family name for oval ducting
DUCT_OVAL_FAMILY_NAME = 'Oval Duct'
#: Built in family name for round ducting
DUCT_ROUND_FAMILY_NAME = 'Round Duct'
#: Built in family name for rectangular ducting
DUCT_RECTANGULAR_FAMILY_NAME = 'Rectangular Duct'

#: List of all Built in ducting family names
BUILTIN_DUCT_TYPE_FAMILY_NAMES = [
    DUCT_OVAL_FAMILY_NAME,
    DUCT_ROUND_FAMILY_NAME,
    DUCT_RECTANGULAR_FAMILY_NAME
]

# flex duct types are split into two major families
#: Built in family name for rectangular flex ducting
FLEX_DUCT_REC_FAMILY_NAME = 'Flex Duct Rectangular'
#: Built in family name for round flex ducting
FLEX_DUCT_ROUND_FAMILY_NAME = 'Flex Duct Round'

#: List of all Built in flex ducting family names
BUILTIN_FLEX_DUCT_TYPE_FAMILY_NAMES = [
    FLEX_DUCT_REC_FAMILY_NAME,
    FLEX_DUCT_ROUND_FAMILY_NAME
]

# conduits types are split into two major families
#: Built in family name for conduits with fittings
CONDUIT_WITH_FITTING_FAMILY_NAME = 'Conduit with Fittings'
#: Built in family name for conduits without fittings
CONDUIT_WITHOUT_FITTING_FAMILY_NAME = 'Conduit without Fittings'

#: List of all Built in conduit family names
BUILTIN_CONDUIT_TYPE_FAMILY_NAMES = [
    CONDUIT_WITH_FITTING_FAMILY_NAME,
    CONDUIT_WITHOUT_FITTING_FAMILY_NAME
]

# cable tray types are split into two major families
#: Built in family name for cable tray with fittings
CABLE_TRAY_WITH_FITTING_FAMILY_NAME = 'Cable Tray with Fittings'
#: Built in family name for cable tray without fittings
CABLET_RAY_WITHOUT_FITTING_FAMILY_NAME = 'Cable Tray without Fittings'

#: List of all Built in cable tray family names
BUILTIN_CABLE_TRAY_TYPE_FAMILY_NAMES = [
    CABLE_TRAY_WITH_FITTING_FAMILY_NAME,
    CABLET_RAY_WITHOUT_FITTING_FAMILY_NAME
]

# pipe types exist in one major families
#: Built in family name for pipes
PIPE_FAMILY_NAME = 'Pipe Types'

#: List of all Built in pipe family names
BUILTIN_PIPE_TYPE_FAMILY_NAMES = [
    PIPE_FAMILY_NAME
]