"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
built in parameter grouping to human readable names.
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

import Autodesk.Revit.DB as rdb


PRAMETER_GROPUING_TO_BUILD_IN_PARAMETER_GROUPS = {
    "Analysis Results": rdb.BuiltInParameterGroup.PG_ANALYSIS_RESULTS,
    "Analytical Alignment": rdb.BuiltInParameterGroup.PG_ANALYTICAL_ALIGNMENT,
    "Analytical Model": rdb.BuiltInParameterGroup.PG_ANALYTICAL_MODEL,
    "Constraints": rdb.BuiltInParameterGroup.PG_CONSTRAINTS,
    "Construction": rdb.BuiltInParameterGroup.PG_CONSTRUCTION,
    "Data": rdb.BuiltInParameterGroup.PG_DATA,
    "Dimensions": rdb.BuiltInParameterGroup.PG_GEOMETRY,
    "Electrical": rdb.BuiltInParameterGroup.PG_ELECTRICAL,
    "Electrical-Circuiting": rdb.BuiltInParameterGroup.PG_ELECTRICAL_CIRCUITING,
    "Electrical-Lighting": rdb.BuiltInParameterGroup.PG_ELECTRICAL_LIGHTING,
    "Electrical-Loads": rdb.BuiltInParameterGroup.PG_ELECTRICAL_LOADS,
    "Electrical Engineering": rdb.BuiltInParameterGroup.PG_ELECTRICAL,
    "Energy Analysis": rdb.BuiltInParameterGroup.PG_ENERGY_ANALYSIS,
    "Fire Protection": rdb.BuiltInParameterGroup.PG_FIRE_PROTECTION,
    "General": rdb.BuiltInParameterGroup.PG_GENERAL,
    "Graphics": rdb.BuiltInParameterGroup.PG_GRAPHICS,
    "Green Building Properties": rdb.BuiltInParameterGroup.PG_GREEN_BUILDING,
    "Identity Data": rdb.BuiltInParameterGroup.PG_IDENTITY_DATA,
    "IFC Parameters": rdb.BuiltInParameterGroup.PG_IFC,
    "Layers": rdb.BuiltInParameterGroup.PG_REBAR_SYSTEM_LAYERS,
    "Materials": rdb.BuiltInParameterGroup.PG_MATERIALS,
    "Mechanical": rdb.BuiltInParameterGroup.PG_MECHANICAL,
    "Mechanical-Flow": rdb.BuiltInParameterGroup.PG_MECHANICAL_AIRFLOW,
    "Mechanical-Loads": rdb.BuiltInParameterGroup.PG_MECHANICAL_LOADS,
    "Model Properties": rdb.BuiltInParameterGroup.PG_ADSK_MODEL_PROPERTIES,
    "Other": rdb.BuiltInParameterGroup.INVALID,
    "Overall Legend": rdb.BuiltInParameterGroup.PG_OVERALL_LEGEND,
    "Phasing": rdb.BuiltInParameterGroup.PG_PHASING,
    "Photometric": rdb.BuiltInParameterGroup.PG_LIGHT_PHOTOMETRICS,
    "Plumbing": rdb.BuiltInParameterGroup.PG_PLUMBING,
    "Rebar Set": rdb.BuiltInParameterGroup.PG_REBAR_ARRAY,
    "Segments and Fittings": rdb.BuiltInParameterGroup.PG_SEGMENTS_FITTINGS,
    "Slab Shape Edit": rdb.BuiltInParameterGroup.PG_SLAB_SHAPE_EDIT,
    "Structural": rdb.BuiltInParameterGroup.PG_STRUCTURAL,
    "Structural Analysis": rdb.BuiltInParameterGroup.PG_STRUCTURAL_ANALYSIS,
    "Text": rdb.BuiltInParameterGroup.PG_TEXT,
    "Title Text": rdb.BuiltInParameterGroup.PG_TITLE,
    "Visibility}": rdb.BuiltInParameterGroup.PG_VISIBILITY,
}
