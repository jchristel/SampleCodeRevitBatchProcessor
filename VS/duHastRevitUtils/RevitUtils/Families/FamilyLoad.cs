using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.DB;

namespace duHastNet.RevitUtils.Families
{
    public class FamilyLoad
    {

        public void LoadFamily(Document doc, string familyPath, bool overwriteExisting)
        {

            //set up a load option ( overwrite existing parameters, use nested shared families from the project )
            FamilyLoadOption loadOption = new FamilyLoadOption();

            // set up an action to run inside a Revit transaction
            //Func<bool> actionInTranny = () =>
            //{
            //    try
            //    {
            //        //update single family instance
            //        //return UpdateProperties(doc, familyInstance, roomData, pushOperationMode, AddMessage);
            //    }
            //    catch (Exception ex)
            //    {
            //        //log the exception
            //        //AddMessage($"Error updating family instance [{familyInstance.Id}] with room data [{roomData.Id.Value}]: {ex.Message}", Utils.WPF.Stores.MessageTypes.Error);
            //        return false;
            //    }
            //};


        }
    }
}
