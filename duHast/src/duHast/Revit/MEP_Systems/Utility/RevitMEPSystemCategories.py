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
