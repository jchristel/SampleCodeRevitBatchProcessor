import clr

clr.AddReference("System.Core")
from System import Linq

clr.ImportExtensions(Linq)

# import Autodesk
from Autodesk.Revit.DB import BuiltInCategory, BuiltInParameter, Element
from System.Collections.Generic import List

from duHast.Revit.Common.revit_version import get_revit_version_number
from duHast.Revit.Family.Utility import loadable_family_categories as rFamUtilCats
from duHast.Revit.Family.family_functions import get_name_to_family_dict
from duHast.Revit.Family.family_utils import (
    get_family_symbols,
    is_shared_from_family
)

from duHast.Revit.Family.Reporting.Objects.family_report_data import (
    FamilyReportData,
)
from Models.RevitFamily import RevitFamily

from duHast.Revit.Categories.categories_model import get_category_from_builtInCategory
from duHast.Utilities.benchmarking import measure_time_wrapper
from duHast.pyRevit.console_output import print_header

from Objects.match_status_names import MatchStatusNames
from Models.RevitFamilyId import FamilyID



def get_families_in_model(doc,  library_path = None):
    family_data = []
    families = get_name_to_family_dict(doc)
    
    cat_mullion = get_category_from_builtInCategory(doc, BuiltInCategory.OST_CurtainWallMullions)
    #print("mullion_cat",cat_mullion, cat_mullion.Name)
    
    for revit_family_name, revit_family in families.items():
        # check if in place or mullion
        if revit_family.IsInPlace == False and revit_family.FamilyCategory.Name != cat_mullion.Name:

            # build new data entry
            family_container = RevitFamily(
                id=FamilyID(revit_family.Id.IntegerValue),
                family_name= revit_family_name,
                family_category=revit_family.FamilyCategory.Name,
                is_shared=is_shared_from_family(revit_family),
                match_status=MatchStatusNames.MATCH_OK.value)
            
            family_data.append(family_container)
    
    return family_data

