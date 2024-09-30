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
# Copyright 2023, Jan Christel
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

from Autodesk.Revit.DB import BuiltInParameterGroup

PRAMETER_GROPUING_TO_BUILD_IN_PARAMETER_GROUPS = {
    "Analysis Results": BuiltInParameterGroup.PG_ANALYSIS_RESULTS,
    "Analytical Alignment": BuiltInParameterGroup.PG_ANALYTICAL_ALIGNMENT,
    "Analytical Model": BuiltInParameterGroup.PG_ANALYTICAL_MODEL,
    "Constraints": BuiltInParameterGroup.PG_CONSTRAINTS,
    "Construction": BuiltInParameterGroup.PG_CONSTRUCTION,
    "Data": BuiltInParameterGroup.PG_DATA,
    "Dimensions": BuiltInParameterGroup.PG_GEOMETRY,
    "Electrical": BuiltInParameterGroup.PG_ELECTRICAL,
    "Electrical-Circuiting": BuiltInParameterGroup.PG_ELECTRICAL_CIRCUITING,
    "Electrical-Lighting": BuiltInParameterGroup.PG_ELECTRICAL_LIGHTING,
    "Electrical-Loads": BuiltInParameterGroup.PG_ELECTRICAL_LOADS,
    "Electrical Engineering": BuiltInParameterGroup.PG_ELECTRICAL,
    "Energy Analysis": BuiltInParameterGroup.PG_ENERGY_ANALYSIS,
    "Fire Protection": BuiltInParameterGroup.PG_FIRE_PROTECTION,
    "General": BuiltInParameterGroup.PG_GENERAL,
    "Graphics": BuiltInParameterGroup.PG_GRAPHICS,
    "Green Building Properties": BuiltInParameterGroup.PG_GREEN_BUILDING,
    "Identity Data": BuiltInParameterGroup.PG_IDENTITY_DATA,
    "IFC Parameters": BuiltInParameterGroup.PG_IFC,
    "Layers": BuiltInParameterGroup.PG_REBAR_SYSTEM_LAYERS,
    "Materials": BuiltInParameterGroup.PG_MATERIALS,
    "Mechanical": BuiltInParameterGroup.PG_MECHANICAL,
    "Mechanical-Flow": BuiltInParameterGroup.PG_MECHANICAL_AIRFLOW,
    "Mechanical-Loads": BuiltInParameterGroup.PG_MECHANICAL_LOADS,
    "Model Properties": BuiltInParameterGroup.PG_ADSK_MODEL_PROPERTIES,
    "Other": BuiltInParameterGroup.INVALID,
    "Overall Legend": BuiltInParameterGroup.PG_OVERALL_LEGEND,
    "Phasing": BuiltInParameterGroup.PG_PHASING,
    "Photometric": BuiltInParameterGroup.PG_LIGHT_PHOTOMETRICS,
    "Plumbing": BuiltInParameterGroup.PG_PLUMBING,
    "Rebar Set": BuiltInParameterGroup.PG_REBAR_ARRAY,
    "Segments and Fittings": BuiltInParameterGroup.PG_SEGMENTS_FITTINGS,
    "Slab Shape Edit": BuiltInParameterGroup.PG_SLAB_SHAPE_EDIT,
    "Structural": BuiltInParameterGroup.PG_STRUCTURAL,
    "Structural Analysis": BuiltInParameterGroup.PG_STRUCTURAL_ANALYSIS,
    "Text": BuiltInParameterGroup.PG_TEXT,
    "Title Text": BuiltInParameterGroup.PG_TITLE,
    "Visibility}": BuiltInParameterGroup.PG_VISIBILITY,
}
