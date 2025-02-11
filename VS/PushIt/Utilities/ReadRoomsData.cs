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
    public static class ReadRoomsData
    {
        public static List<Models.RoomsDataModel> GetRoomsData(string filePath, int rowsToSkip = 2)
        {
            Console.WriteLine("Reading Rooms Data from file: " + filePath);
            // read data from comma separated file
            List<Models.RoomsDataModel> roomsData = new List<Models.RoomsDataModel>();

            var config = new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                HasHeaderRecord = true
            };

            using (StreamReader sr = new StreamReader(filePath))
            {
                //Read the first two lines as headers
                var header1 = sr.ReadLine().Split(',');
                var header2 = sr.ReadLine().Split(',');

                // Reset the stream position to the beginning
                sr.BaseStream.Seek(0, SeekOrigin.Begin);
                sr.DiscardBufferedData();

                using (var csv = new CsvReader(sr, config))
                {
                    csv.Read();
                    csv.ReadHeader();
                    // Read the first row as header not required in the moment
                    //string id = csv.GetField(0);

                    // Skip the specified number of rows (minus 1 since one row is already read)
                    for (int i = 0; i < rowsToSkip - 1; i++)
                    {
                        csv.Read();
                    }

                    // read the rest of the file
                    while (csv.Read())
                    {
                        var record = new RoomsDataModel
                        {
                            Id = new RoomDataProperty("Id", header2[0], "", csv.GetField(0)),
                            AreaBriefed = new RoomDataProperty("AreaBriefed", header2[1], "", csv.GetField(1)),
                            AreaDesigned = new RoomDataProperty("AreaDesigned", header2[2], "", csv.GetField(2)),
                            NameShort = new RoomDataProperty("NameShort", header2[3], "", csv.GetField(3)),
                            Department = new RoomDataProperty("Department", header2[4], "", csv.GetField(4)),
                            SubDepartment = new RoomDataProperty("SubDepartment", header2[5], "", csv.GetField(5)),
                        };
                        roomsData.Add(record);
                    }
                }
            }

            // return list of RoomsDataModel
            return roomsData;
        }
    }
}