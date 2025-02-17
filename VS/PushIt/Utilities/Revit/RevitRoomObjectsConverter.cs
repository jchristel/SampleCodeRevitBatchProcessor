//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2025, Jan Christel
// All rights reserved.

// Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

// - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
// - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
// - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
//
// This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
// In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
// or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
//
//
//

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
                areaBriefed_value = Math.Round(areaBriefed * 0.092903,2); // Convert square feet to square meters and round to 2 decimal places
            }
            areaBriefed_value_string = areaBriefed_value.ToString();

            // convert area values from square feet to square meters
            string areaDesigned_value_string = SharedParaUtils.GetSharedParameterValueFromElementByElementId(familyInstance, sharedParameterIdsByGUIDs[sampleModelRoom.AreaDesigned.ParameterGUID]);

            double areaDesigned_value = 0;
            if (double.TryParse(areaDesigned_value_string, out double areaDesigned))
            {
                areaDesigned_value = Math.Round(areaDesigned * 0.092903,2); // Convert square feet to square meters and round to 2 decimal places
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
