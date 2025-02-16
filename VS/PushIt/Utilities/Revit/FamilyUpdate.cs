using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.DB;

namespace PushIt.Utilities.Revit
{
    public static class FamilyUpdate
    {

        public static bool updateSingleFamilyInstance(Document doc, FamilyInstance familyInstance, Models.RoomsDataModel roomData, bool safetyOff )
        {

            // set up an action to run inside a Revit transaction
            Func<bool> actionInTranny = () =>
            {
                try
                {
                    string room_id = roomData.Id.Value;
                    if (safetyOff)
                    {
                        string userName = doc.Application.Username;
                        string dateStamp = DateTime.Now.ToString("yyyy_MM_dd_HH_mm_ss");
                        room_id = $"{room_id}::{userName}<{dateStamp}>";
                    }

                    // set the room id parameter
                    bool flag_Id = RevitUtils.SharedParaUtils.SetSharedParameterValueByGUID(doc, familyInstance, roomData.Id.ParameterGUID, room_id);

                    // set the room area parameter
                    bool flag_AreaBriefed = RevitUtils.SharedParaUtils.SetSharedParameterValueByGUID(doc, familyInstance, roomData.AreaBriefed.ParameterGUID, roomData.AreaBriefed.Value);
                    bool flag_AreaDesigned = RevitUtils.SharedParaUtils.SetSharedParameterValueByGUID(doc, familyInstance, roomData.AreaDesigned.ParameterGUID, roomData.AreaDesigned.Value);
                    bool flag_NameShort = RevitUtils.SharedParaUtils.SetSharedParameterValueByGUID(doc, familyInstance, roomData.NameShort.ParameterGUID, roomData.NameShort.Value);
                    bool flag_Department = RevitUtils.SharedParaUtils.SetSharedParameterValueByGUID(doc, familyInstance, roomData.Department.ParameterGUID, roomData.Department.Value);
                    bool flag_SubDepartment = RevitUtils.SharedParaUtils.SetSharedParameterValueByGUID(doc, familyInstance, roomData.SubDepartment.ParameterGUID, roomData.SubDepartment.Value);

                    return flag_Id && flag_AreaBriefed && flag_AreaDesigned && flag_NameShort && flag_Department && flag_SubDepartment;
                }
                catch (Exception)
                {
                    return false;
                }
            };

            bool transactionFlag =  RevitUtils.TransactionUtils.inTransaction(
                doc, $"Pushing room {roomData.Id.Value}", actionInTranny);

            return transactionFlag;

        }
    }
}
