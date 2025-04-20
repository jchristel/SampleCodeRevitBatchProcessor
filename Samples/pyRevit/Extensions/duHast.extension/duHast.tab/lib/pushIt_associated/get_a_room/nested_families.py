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

from duHast.Revit.Family.family_element_utils import get_all_curve_based_elements_in_family,get_all_generic_forms_in_family
from duHast.Utilities.Objects.result import Result
from duHast.Revit.Common.delete import delete_by_element_ids

from Autodesk.Revit.DB import Extrusion, ModelLine ,CurveLoop, Line, XYZ, ReferencePlane, CurveElement, ModelText, ElementId

def update_extrusion_outline(family_doc, curve_loops):
    # set up a status tracker
    return_value = Result()
    try:
        
        print("Updating extrusion outline in family")
        # get all (should be 1) extrusions in the family
        elements_col = get_all_generic_forms_in_family(doc=family_doc)
        
        # loop over elements and update outlines
        for el in elements_col:
            if isinstance(el, Extrusion):
                # store all existing curves in the extrusion
                extrusion_model_curve_ids = []
                
                # get the sketch
                sketch_extrusion = el.Sketch
                
                # get the sketch plane of the extrusion
                sketch_plane = sketch_extrusion.SketchPlane
                
                # get the element ids of elements in the sketch
                sketch_element_ids = sketch_extrusion.GetAllElements()
               
                # get the curves of the sketch elements
                for sketch_element_id in sketch_element_ids:
                    sketch_element = family_doc.GetElement(sketch_element_id)
                    if isinstance(sketch_element, ModelLine):
                        print("Found model line: {}".format(sketch_element.Id))
                        # get the curve of the sketch element
                        extrusion_model_curve_ids.append(sketch_element_id)
                
                # delete old curves and add new ones
                # delete old sketch elements
                result_delete = delete_by_element_ids(
                    doc=family_doc, 
                    ids=extrusion_model_curve_ids, 
                    transaction_name="Delete old sketch elements",
                    element_name= "model lines"
                )
                
                print("Deleted old sketch elements: {}".format(result_delete))
                
                # add new curves to the sketch
                for curve_loop in curve_loops:
                    # loop over the curves in the loop
                    for curve in curve_loop:
                        # create a new model line in the sketch plane
                        new_model_line = family_doc.NewModelCurve(curve, sketch_plane)
                        # set the model line to be part of the extrusion sketch
                        sketch_extrusion.AddElement(new_model_line)
                
            else:
                # ignore this element
                pass
                
            # get out of loop
            break
                
                
    except Exception as e:
        message = "Failed to update extrusion in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value

def add_2D_outline(family_doc, curve_loop):
    # set up a status tracker
    return_value = Result()
    try:
        return_value.append_message("Adding 2D outline to family")
    except Exception as e:
        message = "Failed to add 2D lines in family: {}".format(e)
        return_value.update_sep(False, message)
    return return_value