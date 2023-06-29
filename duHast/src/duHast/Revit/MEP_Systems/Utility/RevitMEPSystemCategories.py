"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Revit MEP built-in categories. 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- useful for filtering out families which can be used in MEP system types

"""
#
# License:
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

#: List of loadable built in family categories for duct related elements.
import Autodesk.Revit.DB as rdb
from System.Collections.Generic import List


CATS_LOADABLE_DUCTS = List[rdb.BuiltInCategory](
    [
        rdb.BuiltInCategory.OST_DuctAccessory,
        rdb.BuiltInCategory.OST_DuctTerminal,
        rdb.BuiltInCategory.OST_DuctFitting,
    ]
)


#: List of loadable built in family categories for cable tray related elements.
CATS_LOADABLE_CABLE_TRAYS = List[rdb.BuiltInCategory](
    [rdb.BuiltInCategory.OST_CableTrayFitting]
)


#: List of loadable built in family categories for conduit related elements.
CATS_LOADABLE_CONDUITS = List[rdb.BuiltInCategory](
    [rdb.BuiltInCategory.OST_ConduitFitting]
)


#: List of loadable built in family categories for pipe related elements.
CATS_LOADABLE_PIPES = List[rdb.BuiltInCategory](
    [rdb.BuiltInCategory.OST_PipeAccessory, rdb.BuiltInCategory.OST_PipeFitting]
)


#: List of routing reference rule group types
ROUTING_PREF_RULE_GROUP_TYPES = [
    rdb.RoutingPreferenceRuleGroupType.Segments,
    rdb.RoutingPreferenceRuleGroupType.Elbows,
    rdb.RoutingPreferenceRuleGroupType.Junctions,
    rdb.RoutingPreferenceRuleGroupType.Crosses,
    rdb.RoutingPreferenceRuleGroupType.Transitions,
    rdb.RoutingPreferenceRuleGroupType.Unions,
    rdb.RoutingPreferenceRuleGroupType.MechanicalJoints,
    rdb.RoutingPreferenceRuleGroupType.TransitionsRectangularToRound,
    rdb.RoutingPreferenceRuleGroupType.TransitionsRectangularToOval,
    rdb.RoutingPreferenceRuleGroupType.TransitionsOvalToRound,
    rdb.RoutingPreferenceRuleGroupType.Caps,
]
