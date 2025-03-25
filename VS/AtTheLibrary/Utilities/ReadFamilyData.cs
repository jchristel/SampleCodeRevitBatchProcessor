using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using CsvHelper;
using CsvHelper.Configuration;

namespace duHast.AtTheLibrary.Utilities
{
    public static class ReadFamilyData
    {
        public static List<Models.FamilyDataModel> GetFamiliesData(string filePath, int rowsToSkip = 1)
        {
            // read data from comma separated file
            List<Models.FamilyDataModel> familiesData = new List<Models.FamilyDataModel>();

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

                    string currentFamilyIdentifyer= ""; // family name + category
                    string currentFamilyTypeName = ""; // type name

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

                        // read the data to the right of the first column into property objects
                        var properties = new List<Models.FamilyDataProperty>();

                        for (int i = 3; i < csv.HeaderRecord.Length; i++)
                        {
                            var property = new Models.FamilyDataProperty(
                                name: header1[i],
                                value: csv.GetField(i)
                            );
                            properties.Add(property);
                        }

                        // create a new FamilyDataModel object
                        var record = new Models.FamilyDataModel(
                             id: new Models.FamilyDataProperty(
                                name: header1[1] + "::" + header1[2],
                                value: csv.GetField(1) + "::" + csv.GetField(2)
                             ),
                            otherProperties: properties);

                        familiesData.Add(record);
                    }
                }
            }

            // return list of RoomsDataModel
            return familiesData;
        }
    }
}
