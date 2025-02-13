using PushIt.Models;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using CsvHelper;
using CsvHelper.Configuration;
using System.Globalization;

namespace PushIt.Utilities
{
    public static class MatchFamiliesToRoomData
    {
        public static List<Models.RoomsRevit> MatchFamiliesToRooms(List<Models.RoomsDataModel> roomsDataModel, List<Models.RoomsRevit> roomsRevit)
        {
            // build a dictionary of room revit id to store all rooms with the same id
            Dictionary<string, List<Models.RoomsRevit>> roomsRevitById = new Dictionary<string, List<Models.RoomsRevit>>();

            foreach (var revitRoom in roomsRevit)
            {
                if (roomsRevitById.Contains(revitRoom.Id))
                {
                    roomsRevitById[revitRoom.Id].Add(revitRoom)
                }
                else
                {
                    roomsRevitById
                }
            }
        }
    }
    {}
}