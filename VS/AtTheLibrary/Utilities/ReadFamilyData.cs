using System;
using System.Collections.Generic;
using System.Diagnostics.Tracing;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using CsvHelper;
using CsvHelper.Configuration;

namespace duHastNet.AtTheLibrary.Utilities
{
    public static class ReadFamilyData
    {
        public static List<Models.FamilyDataModel> GetFamiliesData(string filePath, int rowsToSkip = 1, List<string> supportedParameterNames = null)
        {
            // read data from comma separated file
            List<Models.FamilyDataModel> familiesData = new List<Models.FamilyDataModel>();

            // check if supportedParameterNames is null and if so make it an empty list for the code to work
            if (supportedParameterNames == null)
            {
                supportedParameterNames = new List<string>();
            }

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
                        string currentFamilyIdentifyer= ""; // family name + category + type name as a hash string
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
                            var property = new Models.FamilyDataProperty(name: csv.GetField(6), showInUI: supportedParameterNames.Contains(csv.GetField(6)), value: csv.GetField(10));

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
                                            showInUI: true,
                                            value: hashValue
                                        ),
                                    familyName: new Models.FamilyDataProperty(
                                            name: nameof(Models.FamilyDataModel.FamilyName),
                                            showInUI: true,
                                            value: csv.GetField(1)
                                        ),
                                    familyCategory: new Models.FamilyDataProperty(
                                            name: nameof(Models.FamilyDataModel.FamilyCategory),
                                            showInUI: true,
                                            value: csv.GetField(2)
                                        ),
                                    familyTypeName: new Models.FamilyDataProperty(
                                            name: nameof(Models.FamilyDataModel.FamilyTypeName),
                                            showInUI: true,
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
                    catch (Exception ex)
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
