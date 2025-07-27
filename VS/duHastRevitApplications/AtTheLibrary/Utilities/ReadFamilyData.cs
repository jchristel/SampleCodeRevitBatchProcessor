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
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;

namespace duHastNet.AtTheLibrary.Utilities
{
    public static class ReadFamilyData
    {
        /// <summary>
        /// Reads family data from a report file created from XML files using duHast pyRevit extension
        /// </summary>
        /// <param name="filePath">the location of the report file as fully qualified file path</param>
        /// <param name="rowsToSkip">number of header rows to skip when reading the file data</param>
        /// <returns></returns>
        public static List<Models.FamilyDataModel> GetFamiliesData(string filePath, int rowsToSkip = 1)
        {
            // read data from comma separated file
            List<Models.FamilyDataModel> familiesData = new List<Models.FamilyDataModel>();

            //check if valid path
            if (!File.Exists(filePath))
            {
                System.Windows.Forms.MessageBox.Show(
                            $"Family report file does not exist at path: {filePath}",
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
                //Read the first line as headers
                var header1 = sr.ReadLine().Split(','); //header row

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

                    //attempt to read the rest of the file
                    try
                    {
                        string currentFamilyIdentifyer = ""; // family name + category + type name as a hash string
                        string previousFamilyIdentifyer = ""; // family name + category + type name as a hash string
                        Models.FamilyDataModel currentFamilyData = null;
                        // read the rest of the file
                        while (csv.Read())
                        {
                            // todo: read data from csv file
                            // each family has multiple types with multiple properties...
                            // each row in the csv file is a family property
                            // families are uniquely identified by the "FAMILY NAME" and "CATEGORY" column in the csv file
                            // columns per row are: 
                            // - "PROJECT FILE NAME",
                            // - "FAMILY NAME",
                            // - "CATEGORY",
                            // - "TYPE NAME",
                            // - "DATE RPOERTED",
                            // - "TIME REPORTED",
                            // - "PARAMETER NAME",
                            // - "PARAMETER TYPE",
                            // - "PARAMETER STORAGE TYPE",
                            // - "PARAMETER UNIT",
                            // - "PARAMETER VALUE",

                            // build unique id for family made up of family name, category and type name
                            currentFamilyIdentifyer = csv.GetField(1) + "::" + csv.GetField(2) + "::" + csv.GetField(3);

                            // read the row and create a new family data property object
                            var property = new Models.FamilyDataProperty(
                                name: csv.GetField(6), 
                                value: csv.GetField(10)
                            );

                            // check if the family has changed, if not no action required
                            if (currentFamilyIdentifyer != previousFamilyIdentifyer)
                            {
                                // family has changed
                                // add the current family to the list
                                if (currentFamilyData != null)
                                {
                                    familiesData.Add(currentFamilyData);
                                }

                                // compute hash value made up of fam name, fam category and type name
                                string hashValue = Utils.Hash.ComputeHashUtils.ComputeShortSHA256Hash(values: new string[] { csv.GetField(1), csv.GetField(2), csv.GetField(3) });

                                // create a new family data model object but check if family is already in the list in case rows are out of order
                                if (familiesData.Any(f => f.Id.Value == hashValue))
                                {
                                    // family is already in the list
                                    // get the family data object
                                    currentFamilyData = familiesData.First(f => f.Id.Value == Utils.Hash.ComputeHashUtils.ComputeShortSHA256Hash(values: new string[] { csv.GetField(1), csv.GetField(2), csv.GetField(3) }));
                                }
                                else
                                {
                                    // family is not in the list
                                    // create a new family data object
                                    currentFamilyData = new Models.FamilyDataModel(
                                    id: new Models.FamilyDataProperty(
                                            name: nameof(Models.FamilyDataModel.Id),
                                            value: hashValue
                                        ),
                                    familyFilePath: new Models.FamilyDataProperty(
                                            name: nameof(Models.FamilyDataModel.FamilyFilePath),
                                            value: csv.GetField(0)
                                        ),
                                    familyName: new Models.FamilyDataProperty(
                                            name: nameof(Models.FamilyDataModel.FamilyName),
                                            value: csv.GetField(1)
                                        ),
                                    familyCategory: new Models.FamilyDataProperty(
                                            name: nameof(Models.FamilyDataModel.FamilyCategory),
                                            value: csv.GetField(2)
                                        ),
                                    familyTypeName: new Models.FamilyDataProperty(
                                            name: nameof(Models.FamilyDataModel.FamilyTypeName),
                                            value: csv.GetField(3)
                                        ),
                                    otherProperties: null);
                                }

                                // set the previous family identifyer to the current family identifyer
                                previousFamilyIdentifyer = currentFamilyIdentifyer;
                            }

                            //add the property to the family data object
                            currentFamilyData.AddProperty(property);
                        }
                    }
                    catch (Exception)
                    {
                        return null;
                    }
                }
            }
            // return list of RoomsDataModel
            return familiesData;
        }
    }
}
