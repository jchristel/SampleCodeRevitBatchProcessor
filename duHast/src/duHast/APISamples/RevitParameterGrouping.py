'''
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
built in parameter grouping to human readable names.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

'''
#
#License:
#
#
# Revit Batch Processor Sample Code
#
# Copyright (c) 2022  Jan Christel
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

import Autodesk.Revit.DB as rdb


ParameterGroupingToBuiltInParameterGroups = {
    'Analysis Results' : rdb.BuiltInParameterGroup.PG_ANALYSIS_RESULTS,
    'Analytical Alignment' : rdb.BuiltInParameterGroup.PG_ANALYTICAL_ALIGNMENT,
    'Analytical Model': rdb.BuiltInParameterGroup.PG_ANALYTICAL_MODEL,
    'Constraints': rdb.BuiltInParameterGroup.PG_CONSTRAINTS,
    'Construction': rdb.BuiltInParameterGroup.PG_CONSTRUCTION,
    'Data':rdb.BuiltInParameterGroup.PG_DATA,
    'Dimensions':rdb.BuiltInParameterGroup.PG_GEOMETRY,
    'Electrical':rdb.BuiltInParameterGroup.PG_ELECTRICAL,
    'Electrical-Circuiting':rdb.BuiltInParameterGroup.PG_ELECTRICAL_CIRCUITING,
    'Electrical-Lighting':rdb.BuiltInParameterGroup.PG_ELECTRICAL_LIGHTING,
    'Electrical-Loads':rdb.BuiltInParameterGroup.PG_ELECTRICAL_LOADS,
    'Electrical Engineering':rdb.BuiltInParameterGroup.PG_ELECTRICAL,
    'Energy Analysis':rdb.BuiltInParameterGroup.PG_ENERGY_ANALYSIS,
    'Fire Protection':rdb.BuiltInParameterGroup.PG_FIRE_PROTECTION,
    'General':rdb.BuiltInParameterGroup.PG_GENERAL,
    'Graphics':rdb.BuiltInParameterGroup.PG_GRAPHICS,
    'Green Building Properties':rdb.BuiltInParameterGroup.PG_GREEN_BUILDING,
    'Identity Data':rdb.BuiltInParameterGroup.PG_IDENTITY_DATA,
    'IFC Parameters':rdb.BuiltInParameterGroup.PG_IFC,
    'Layers':rdb.BuiltInParameterGroup.PG_REBAR_SYSTEM_LAYERS,
    'Materials':rdb.BuiltInParameterGroup.PG_MATERIALS,
    'Mechanical':rdb.BuiltInParameterGroup.PG_MECHANICAL,
    'Mechanical-Flow':rdb.BuiltInParameterGroup.PG_MECHANICAL_AIRFLOW,
    'Mechanical-Loads':rdb.BuiltInParameterGroup.PG_MECHANICAL_LOADS,
    'Model Properties':rdb.BuiltInParameterGroup.PG_ADSK_MODEL_PROPERTIES,
    'Other':rdb.BuiltInParameterGroup.INVALID,
    'Overall Legend':rdb.BuiltInParameterGroup.PG_OVERALL_LEGEND,
    'Phasing':rdb.BuiltInParameterGroup.PG_PHASING,
    'Photometric':rdb.BuiltInParameterGroup.PG_LIGHT_PHOTOMETRICS,
    'Plumbing':rdb.BuiltInParameterGroup.PG_PLUMBING,
    'Rebar Set':rdb.BuiltInParameterGroup.PG_REBAR_ARRAY,
    'Segments and Fittings':rdb.BuiltInParameterGroup.PG_SEGMENTS_FITTINGS,
    'Slab Shape Edit':rdb.BuiltInParameterGroup.PG_SLAB_SHAPE_EDIT,
    'Structural':rdb.BuiltInParameterGroup.PG_STRUCTURAL,
    'Structural Analysis':rdb.BuiltInParameterGroup.PG_STRUCTURAL_ANALYSIS,
    'Text':rdb.BuiltInParameterGroup.PG_TEXT,
    'Title Text':rdb.BuiltInParameterGroup.PG_TITLE,
    'Visibility}':rdb.BuiltInParameterGroup.PG_VISIBILITY
}