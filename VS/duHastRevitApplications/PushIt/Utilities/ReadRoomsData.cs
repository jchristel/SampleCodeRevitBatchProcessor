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
        public static List<RoomDataProperty> GetRoomsDataHeaderRows(string filePath, int headerRowsCount = 5)
        {
            List<List<string>> headerRows = [];

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
            using (StreamReader sr = new(filePath))
            {
                for (int i = 0; i < headerRowsCount; i++)
                {
                    var line = sr.ReadLine();
                    if (line == null) break; // legacy file has fewer rows — stop early
                    var headerRow = line.Split(',');
                    headerRows.Add([.. headerRow]);
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
                bool isId = true && i == 0;

                // row 4 (index 4): isRevitTakesPrecedenceAfterInitialPush — default false for legacy files
                bool revitTakesPrecedence = false;
                if (headerRows.Count > 4 && i < headerRows[4].Count)
                {
                    bool.TryParse(headerRows[4][i].ToLower(), out revitTakesPrecedence);
                }

                var property = new RoomDataProperty(
                    name: headerRows[0][i],
                    parameterGUID: headerRows[1][i],
                    parameterName: "",
                    value: "empty",
                    showInUI: bool.Parse(headerRows[3][i].ToLower()),
                    isReadOnly: bool.Parse(headerRows[2][i].ToLower()),
                    isUniqueId: isId,
                    revitTakesPrecedenceAfterInitialPush: revitTakesPrecedence
                );
                properties.Add(property);
            }

            // return list of properties
            return properties;
        }


        public static List<Models.RoomDataModel> GetRoomsData(string filePath, int rowsToSkip = 5)
        {
            // read data from comma separated file
            List<Models.RoomDataModel> roomsData = [];

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

            using (StreamReader sr = new(filePath))
            {
                // Read header rows. Row 5 (isRevitTakesPrecedenceAfterInitialPush) is optional
                // for backwards compatibility with CSV files written before this change.
                var header1 = sr.ReadLine()?.Split(',') ?? []; // name row
                var header2 = sr.ReadLine()?.Split(',') ?? []; // GUID row
                var header3 = sr.ReadLine()?.Split(',') ?? []; // isReadOnly row
                var header4 = sr.ReadLine()?.Split(',') ?? []; // showInUI row
                var header5Line = sr.ReadLine();                // isRevitTakesPrecedenceAfterInitialPush (may be absent)
                var header5 = header5Line?.Split(',');

                // Reset stream so CsvReader starts from the beginning
                sr.BaseStream.Seek(0, SeekOrigin.Begin);
                sr.DiscardBufferedData();

                using var csv = new CsvReader(sr, config);
                csv.Read();
                csv.ReadHeader();

                // Skip the header rows (minus 1 since one row is already consumed above)
                int actualSkip = header5 != null ? rowsToSkip - 1 : 4 - 1;
                for (int i = 0; i < actualSkip; i++)
                {
                    csv.Read();
                }

                // read the rest of the file
                while (csv.Read())
                {
                    var properties = new List<RoomDataProperty>();
                    for (int i = 1; i < csv.HeaderRecord.Length; i++)
                    {
                        bool revitTakesPrecedence = false;
                        if (header5 != null && i < header5.Length)
                            bool.TryParse(header5[i].ToLower(), out revitTakesPrecedence);

                        var property = new RoomDataProperty(
                            name: header1[i],
                            parameterGUID: header2[i],
                            parameterName: "",
                            value: csv.GetField(i),
                            showInUI: bool.Parse(header4[i].ToLower()),
                            isReadOnly: bool.Parse(header3[i].ToLower()),
                            isUniqueId: false,
                            revitTakesPrecedenceAfterInitialPush: revitTakesPrecedence
                        );
                        properties.Add(property);
                    }

                    bool idRevitTakesPrecedence = false;
                    if (header5 != null && header5.Length > 0)
                        bool.TryParse(header5[0].ToLower(), out idRevitTakesPrecedence);

                    var record = new RoomDataModel(
                         id: new RoomDataProperty(
                            name: header1[0],
                            parameterGUID: header2[0],
                            parameterName: "",
                            value: csv.GetField(0),
                            showInUI: bool.Parse(header4[0].ToLower()),
                            isReadOnly: bool.Parse(header3[0].ToLower()),
                            isUniqueId: true,
                            revitTakesPrecedenceAfterInitialPush: idRevitTakesPrecedence
                         ),
                        otherProperties: properties);

                    roomsData.Add(record);
                }
            }

            return roomsData;
        }
    }
}