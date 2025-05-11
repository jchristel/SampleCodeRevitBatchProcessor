using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.DB;

namespace duHastNet.RevitUtils.Families
{
    public static class FamilyLoad
    {

        public static void LoadFamily(Document doc, string familyPath, bool overwriteExisting)
        {

            //set up a load option ( overwrite existing parameters, use nested shared families from the project )
            FamilyLoadOption loadOption = new FamilyLoadOption();
            
            
        }
    }
}
