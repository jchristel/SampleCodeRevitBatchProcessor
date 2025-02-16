using Autodesk.Revit.DB;
using RevitUtils;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.Utilities.Revit
{
    public static class RevitRoomObjectsConverter
    {

        public static Models.RoomsRevit ConvertSingleFamilyToRevitRoom(FamilyInstance familyInstance, Models.RoomsDataModel sampleModelRoom, Dictionary<string, ElementId> sharedParameterIdsByGUIDs)
        {
            // get the parameters of the family instance
            IList<Parameter> parameters = familyInstance.GetOrderedParameters();

            // get the id value
            string id_value = SharedParaUtils.GetSharedParameterValueFromElementByElementId(familyInstance, sharedParameterIdsByGUIDs[sampleModelRoom.Id.ParameterGUID]);

            // ignore fam instance if id is null or empt
            if (id_value == null || id_value == "")
            {
                return null;
            }

            // convert area values from square feet to square meters
            string areaBriefed_value_string = SharedParaUtils.GetSharedParameterValueFromElementByElementId(familyInstance, sharedParameterIdsByGUIDs[sampleModelRoom.AreaBriefed.ParameterGUID]);
            double areaBriefed_value = 0;
            if (double.TryParse(areaBriefed_value_string, out double areaBriefed))
            {
                areaBriefed_value = areaBriefed * 0.092903; // Convert square feet to square meters
            }
            areaBriefed_value_string = areaBriefed_value.ToString();

            // convert area values from square feet to square meters
            string areaDesigned_value_string = SharedParaUtils.GetSharedParameterValueFromElementByElementId(familyInstance, sharedParameterIdsByGUIDs[sampleModelRoom.AreaDesigned.ParameterGUID]);

            double areaDesigned_value = 0;
            if (double.TryParse(areaDesigned_value_string, out double areaDesigned))
            {
                areaDesigned_value = areaDesigned * 0.092903; // Convert square feet to square meters
            }
            areaDesigned_value_string = areaDesigned_value.ToString();

            string nameShort_value = SharedParaUtils.GetSharedParameterValueFromElementByElementId(familyInstance, sharedParameterIdsByGUIDs[sampleModelRoom.NameShort.ParameterGUID]);
            string department_value = SharedParaUtils.GetSharedParameterValueFromElementByElementId(familyInstance, sharedParameterIdsByGUIDs[sampleModelRoom.Department.ParameterGUID]);
            string subDepartment_value = SharedParaUtils.GetSharedParameterValueFromElementByElementId(familyInstance, sharedParameterIdsByGUIDs[sampleModelRoom.SubDepartment.ParameterGUID]);

            // get the design set and option data
            var designSetAndOptionData = RevitUtils.DesignSetAndOptionsUtils.GetDesignSetOptionInfo(familyInstance.Document, familyInstance);

            // create a new revit room
            Models.RoomsRevit revitRoom = new Models.RoomsRevit(
                id: id_value,
                areaBriefed: areaBriefed_value_string,
                areaDesigned: areaDesigned_value_string,
                roomNameShort: nameShort_value,
                department: department_value,
                subDepartment: subDepartment_value,
                designSet: designSetAndOptionData[DesignSetAndOptionDefaultNames.DESIGN_SET_NAME].ToString(),
                designOption: designSetAndOptionData[DesignSetAndOptionDefaultNames.DESIGN_OPTION_NAME].ToString(),
                designOptionIsPrimary: (bool)designSetAndOptionData[DesignSetAndOptionDefaultNames.DESIGN_OPTION_IS_PRIMARY],
                familyInstance.Id.IntegerValue);

            return revitRoom;
        }
        public static List<PushIt.Models.RoomsRevit> ConvertFamiliesToRevitRooms(List<FamilyInstance> familyInstances, Models.RoomsDataModel sampleModelRoom)
        {
            // create a list of revit rooms
            List<Models.RoomsRevit> revitRooms = new List<PushIt.Models.RoomsRevit>();

            // get shared parameter ids by GUID
            Dictionary<string, ElementId> sharedParameterIdsByGUIDs = RevitUtils.SharedParaUtils.GetSharedParameterIdsByGUID(familyInstances[0].Document);

            foreach (FamilyInstance familyInstance in familyInstances)
            {
                // create a new revit room
                Models.RoomsRevit revitRoom = ConvertSingleFamilyToRevitRoom(familyInstance, sampleModelRoom, sharedParameterIdsByGUIDs);

                // add to list to be returned
                revitRooms.Add(revitRoom);
            }
            return revitRooms;
        }
    }
}
