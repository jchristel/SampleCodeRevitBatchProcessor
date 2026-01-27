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

from Autodesk.Revit.DB import GroupTypeId

PARAMETER_GROUPING_TO_GROUP_TYPE_ID = {
    "Analysis Results": GroupTypeId.AnalysisResults,
    "Analytical Alignment": GroupTypeId.AnalyticalAlignment,
    "Analytical Model": GroupTypeId.AnalyticalModel,
    "Constraints": GroupTypeId.Constraints,
    "Construction": GroupTypeId.Construction,
    "Data": GroupTypeId.Data,
    "Dimensions": GroupTypeId.Geometry,
    "Electrical": GroupTypeId.Electrical,
    "Electrical-Circuiting": GroupTypeId.ElectricalCircuiting,
    "Electrical-Lighting": GroupTypeId.ElectricalLighting,
    "Electrical-Loads": GroupTypeId.ElectricalLoads,
    "Electrical Engineering": GroupTypeId.Electrical,
    "Energy Analysis": GroupTypeId.EnergyAnalysis,
    "Fire Protection": GroupTypeId.FireProtection,
    "General": GroupTypeId.General,
    "Graphics": GroupTypeId.Graphics,
    "Green Building Properties": GroupTypeId.GreenBuilding,
    "Identity Data": GroupTypeId.IdentityData,
    "IFC Parameters": GroupTypeId.Ifc,
    "Layers": GroupTypeId.RebarSystemLayers,
    "Materials": GroupTypeId.Materials,
    "Mechanical": GroupTypeId.Mechanical,
    "Mechanical-Flow": GroupTypeId.MechanicalAirflow,
    "Mechanical-Loads": GroupTypeId.MechanicalLoads,
    "Model Properties": GroupTypeId.AdskModelProperties,
    "Overall Legend": GroupTypeId.OverallLegend,
    "Phasing": GroupTypeId.Phasing,
    "Photometric": GroupTypeId.LightPhotometrics,
    "Plumbing": GroupTypeId.Plumbing,
    "Rebar Set": GroupTypeId.RebarArray,
    "Segments and Fittings": GroupTypeId.SegmentsFittings,
    "Slab Shape Edit": GroupTypeId.SlabShapeEdit,
    "Structural": GroupTypeId.Structural,
    "Structural Analysis": GroupTypeId.StructuralAnalysis,
    "Text": GroupTypeId.Text,
    "Title Text": GroupTypeId.Title,
    "Visibility}": GroupTypeId.Visibility,
}
