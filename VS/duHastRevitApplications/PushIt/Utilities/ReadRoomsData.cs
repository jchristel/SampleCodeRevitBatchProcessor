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


using CsvHelper;
using CsvHelper.Configuration;
using duHastNet.PushIt.Models;
using System.Collections.Generic;
using System.Globalization;
using System.IO;

namespace duHastNet.PushIt.Utilities
{
    public static class ReadRoomsData
    {

        /// <summary>
        /// get the header rows from the file as properties
        /// </summary>
        public static List<RoomDataProperty> GetRoomsDataHeaderRows(string filePath, int headerRowsCount = 4)
        {
            List<List<string>> headerRows = new List<List<string>>();

            //check if valid path
            if (!File.Exists(filePath))
            {
                System.Windows.Forms.MessageBox.Show(
                            $"Schedule of accomodation file does not exist at: {filePath}",
                            "Attention",
                            System.Windows.Forms.MessageBoxButtons.OK, System.Windows.Forms.MessageBoxIcon.Information);
                return null;
            }

            //read data from comma separated file
            using (StreamReader sr = new StreamReader(filePath))
            {
                for (int i = 0; i < headerRowsCount; i++)
                {
                    // Read the header row
                    var headerRow = sr.ReadLine().Split(',');
                    headerRows.Add(new List<string>(headerRow));
                }
            }

            if (headerRows.Count == 0)
            {
                return null;
            }

            //build properties from the header rows
            var properties = new List<RoomDataProperty>();
            for (int i = 0; i < headerRows[0].Count; i++)
            {
                bool isId = false ? i == 0 : true;
                var property = new RoomDataProperty(
                    name: headerRows[0][i],
                    parameterGUID: headerRows[1][i],
                    parameterName: "",
                    value: "empty",
                    showInUI: bool.Parse(headerRows[3][i].ToLower()),
                    isReadOnly: bool.Parse(headerRows[2][i].ToLower()),
                    isUniqueId:isId
                );
                properties.Add(property);
            }

            // return list of properties
            return properties;
        }


        public static List<Models.RoomDataModel> GetRoomsData(string filePath, int rowsToSkip = 4)
        {
            //Console.WriteLine("Reading Rooms Data from file: " + filePath);
            // read data from comma separated file
            List<Models.RoomDataModel> roomsData = new List<Models.RoomDataModel>();

            //check if valid path
            if (!File.Exists(filePath))
            {
                System.Windows.Forms.MessageBox.Show(
                            $"Schedule of accomodation file does not exist at: {filePath}",
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
                //Read the first 4 lines as headers
                var header1 = sr.ReadLine().Split(','); //name row
                var header2 = sr.ReadLine().Split(','); //guid row
                var header3 = sr.ReadLine().Split(','); //isReadOnly row
                var header4 = sr.ReadLine().Split(','); //showInUI row

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
                        // read the data to the right of the first column into property objects
                        var properties = new List<RoomDataProperty>();
                        for (int i = 1; i < csv.HeaderRecord.Length; i++)
                        {
                            var property = new RoomDataProperty(
                                name: header1[i],
                                parameterGUID: header2[i],
                                parameterName: "",
                                value: csv.GetField(i),
                                showInUI: bool.Parse(header4[i].ToLower()),
                                isReadOnly: bool.Parse(header3[i].ToLower()),
                                isUniqueId: false
                            );
                            properties.Add(property);
                        }

                        // create a new RoomDataModel object
                        var record = new RoomDataModel(
                             id: new RoomDataProperty(
                                name: header1[0],
                                parameterGUID: header2[0],
                                parameterName: "",
                                value: csv.GetField(0),
                                showInUI: bool.Parse(header4[0].ToLower()),
                                isReadOnly: bool.Parse(header3[0].ToLower()),
                                isUniqueId: true
                             ),
                            otherProperties: properties);

                        roomsData.Add(record);
                    }
                }
            }

            // return list of RoomsDataModel
            return roomsData;
        }
    }
}