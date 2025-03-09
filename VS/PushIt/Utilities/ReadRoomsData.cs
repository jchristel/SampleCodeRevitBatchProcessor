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


using duHast.PushIt.Models;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using CsvHelper;
using CsvHelper.Configuration;
using System.Globalization;

namespace duHast.PushIt.Utilities
{
    public static class ReadRoomsData
    {
        public static List<Models.RoomDataModel> GetRoomsData(string filePath, int rowsToSkip = 2)
        {
            //Console.WriteLine("Reading Rooms Data from file: " + filePath);
            // read data from comma separated file
            List<Models.RoomDataModel> roomsData = new List<Models.RoomDataModel>();

            //check if valid path
            if (!File.Exists(filePath))
            {
                System.Windows.Forms.MessageBox.Show(
                            $"Invalid data file path: {filePath}",
                            "Attention",
                            System.Windows.Forms.MessageBoxButtons.OK, System.Windows.Forms.MessageBoxIcon.Information);
                return null;
            }

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
                        var record = new RoomDataModel
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