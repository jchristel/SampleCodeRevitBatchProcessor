


from duHast.Revit.DetailItems.curve_create import draw_2D_lines_on_bounding_box_and_separate_point

from Autodesk.Revit.DB import ElementId, Options, Solid, XYZ





def draw_bounding_box_and_centroid(doc, family_instances):
    for fam in family_instances:

        revit_family_instance = doc.GetElement(ElementId(fam.revit_element_id_integer_value))
        # get the bounding box of the family instance
        bounding_box = revit_family_instance.get_BoundingBox(doc.ActiveView)
        if bounding_box is not None:
            
            
            if fam.centroid is not None:
                result_draw = draw_2D_lines_on_bounding_box_and_separate_point(
                    doc,
                    bounding_box,
                    XYZ (fam.centroid[0], fam.centroid[1], fam.centroid[2]),
                    doc.ActiveView,
                )
            else:
                print("Centroid is None: {}".format(fam.revit_element_id_integer_value))


def draw_bounding_box_and_centroid_linked_model(doc_host, doc_link, family_instances):
    for fam in family_instances:

        revit_family_instance = doc_link.GetElement(ElementId(fam.revit_element_id_integer_value))
        # get the bounding box of the family instance
        bounding_box = revit_family_instance.get_BoundingBox(None)
        if bounding_box is not None:
            
            
            if fam.centroid is not None:
                result_draw = draw_2D_lines_on_bounding_box_and_separate_point(
                    doc_host,
                    bounding_box,
                    XYZ (fam.centroid[0], fam.centroid[1], fam.centroid[2]),
                    doc_host.ActiveView,
                )
            else:
                print("Centroid is None: {}".format(fam.revit_element_id_integer_value))