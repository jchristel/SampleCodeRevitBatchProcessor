import clr

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

# import Autodesk
from Autodesk.Revit.DB import BuiltInCategory, BuiltInParameter, Element
from System.Collections.Generic import List


from duHast.Revit.Family.family_functions import get_name_to_family_dict

from test.UI.PushIt.Models.Room import Room
from duHast.Revit.Categories.categories_model import get_category_from_builtInCategory
from test.UI.PushIt.Models.RoomId import RoomID



def get_families_in_model(doc,  library_path = None):
    family_data = []
    families = get_name_to_family_dict(doc)
    
    # TODO:
    # 1. get the families in the model of all categories required
    
    return family_data

