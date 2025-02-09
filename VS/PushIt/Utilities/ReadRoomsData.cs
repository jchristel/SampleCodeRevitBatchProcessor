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
            // read data from comma separated file
            List<Models.RoomsDataModel> roomsData = new List<Models.RoomsDataModel>();

            var config = new CsvConfiguration(CultureInfo.InvariantCulture)
            {
                HasHeaderRecord = true
            };

            using (StreamReader sr = new StreamReader(filePath))
            using (var csv = new CsvReader(sr, config))
            {
                csv.Context.RegisterClassMap<RoomsDataModelMap>();

                // Read the header row
                csv.Read();
                csv.ReadHeader();

                // Skip the specified number of rows
                for (int i = 0; i < rowsToSkip; i++)
                {
                    csv.Read();
                }

                var records = csv.GetRecords<Models.RoomsDataModel>().ToList();
                foreach (var record in records)
                {
                    roomsData.Add(record);
                }
            }

            // return list of RoomsDataModel
            return roomsData;
        }
    }

    public sealed class RoomsDataModelMap : ClassMap<Models.RoomsDataModel>
    {
        public RoomsDataModelMap()
        {
            Map(m => m.Id).Name("Id");
            Map(m => m.AreaBriefed).Name("AreaBriefed");
            Map(m => m.AreaDesigned).Name("AreaDesigned");
            Map(m => m.NameShort).Name("NameShort");
            Map(m => m.Department).Name("Department");
            Map(m => m.SubDepartment).Name("SubDepartment");
        }
    }

}