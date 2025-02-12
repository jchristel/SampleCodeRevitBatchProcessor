using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.DB;

namespace RevitUtils
{
    public static class Families
    {

        // get all family instances by category
        public static List<FamilyInstance> GetFamilyInstancesByBuiltInCategories(Document doc, List<BuiltInCategory> categories)
        {
            List<FamilyInstance> familyInstances = new List<FamilyInstance>();
            ElementMulticategoryFilter filter = new ElementMulticategoryFilter(categories);
            FilteredElementCollector col = new FilteredElementCollector(doc).OfClass(typeof(FamilyInstance)).WherePasses(filter);
            
            foreach (Element instance in col)
            {
                familyInstances.Add(instance as FamilyInstance);
            }

            return familyInstances;
        }


    }
}
