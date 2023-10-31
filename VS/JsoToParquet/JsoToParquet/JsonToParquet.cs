using System;
using System.Collections.Generic;
using System.IO;
using System.Threading.Tasks;
using System.Linq;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using Parquet;
using Parquet.Schema;
using Parquet.Data;



namespace SampleCodeRevitBatchProcessor
{
    public class JsonToParquet
    {
        public async Task WriteJsonToParquetFileAsync(string json, string outputPath)
        {
            try
            {
                // create file schema
                var schema = new ParquetSchema(
                    new DataField<int>("id"),
                    new DataField<string>("city"));

                //create data columns with schema metadata and the data you need
                var idColumn = new DataColumn(
                   schema.DataFields[0],
                   new int[] { 1, 2 });

                var cityColumn = new DataColumn(
                   schema.DataFields[1],
                   new string[] { "London", "Derby" });

                using (Stream fileStream = System.IO.File.OpenWrite("c:\\test.parquet"))
                {
                    using (ParquetWriter parquetWriter = await ParquetWriter.CreateAsync(schema, fileStream))
                    {
                        parquetWriter.CompressionMethod = CompressionMethod.Gzip;
                        parquetWriter.CompressionLevel = System.IO.Compression.CompressionLevel.Optimal;
                        // create a new row group in the file
                        using (ParquetRowGroupWriter groupWriter = parquetWriter.CreateRowGroup())
                        {
                            await groupWriter.WriteColumnAsync(idColumn);
                            await groupWriter.WriteColumnAsync(cityColumn);
                        }
                    }
                }

                Console.WriteLine("Data written to Parquet file successfully.");
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error writing data to Parquet file: " + ex.Message);
            }
        }

        public async Task WriteJsonToParquetFileAsync_Two(string json, string outputPath)
        {
            try
            {
                // Parse the JSON string into a dictionary
                var jsonData = Newtonsoft.Json.JsonConvert.DeserializeObject<Dictionary<string, object>>(json);
                // Parse the JSON string into a dynamic object
                var jsonDataDynamic = JObject.Parse(json);

                // Create a list of data fields for the schema
                var dataFields = new List<DataField>();

                var dataFieldsValues = new List<object>();
                // Create a list of data columns with schema metadata and the data you need
                var dataColumns = new List<DataColumn>();

                foreach (var keyValuePair in jsonData)
                {
                    // Determine the data type based on the JSON value
                    Type dataType = keyValuePair.Value.GetType();

                    // Create a data field for the schema
                    var dataField = new DataField(keyValuePair.Key, dataType);
                    dataFields.Add(dataField);

                    dataFieldsValues.Add(keyValuePair.Value);
                    // Create a data column for the data
                    //var dataColumn = new DataColumn(dataField, new[] { keyValuePair.Value });
                    //dataColumns.Add(dataColumn);
                }

                // Create the Parquet schema
                var schema = new ParquetSchema(dataFields);

                int counter = 0;
                foreach (var property in jsonDataDynamic.Properties())
                {
                    DataColumn dataColumn = GetDataColumn(schema.DataFields[counter], property.Value.Type, property.Value);
                    // Determine the data type based on the JSON value
                    dataColumns.Add(dataColumn);
                }


                using (Stream fileStream = File.OpenWrite(outputPath))
                {
                    using (var parquetWriter = await ParquetWriter.CreateAsync(schema, fileStream))
                    {
                        parquetWriter.CompressionMethod = CompressionMethod.Gzip;
                        parquetWriter.CompressionLevel = System.IO.Compression.CompressionLevel.Optimal;

                        // Create a new row group in the file
                        using (var groupWriter = parquetWriter.CreateRowGroup())
                        {
                            foreach (var dataColumn in dataColumns)
                            {
                                await groupWriter.WriteColumnAsync(dataColumn);
                            }
                        }
                    }
                }

                Console.WriteLine("Data written to Parquet file successfully.");
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error writing data to Parquet file: " + ex.Message);
            }
        }


        // Helper method to map JSON value types to Parquet data types
        private Type GetParquetDataType(JTokenType jsonType)
        {
            switch (jsonType)
            {
                case JTokenType.Integer:
                    return typeof(int);
                case JTokenType.Float:
                    return typeof(float);
                case JTokenType.String:
                    return typeof(string);
                case JTokenType.Boolean:
                    return typeof(bool);
                // Add more type mappings as needed
                default:
                    return typeof(object); // Default to object type
            }
        }


        private DataColumn GetDataColumn(DataField dataField, JTokenType jsonType, object values)
        {
            DataColumn dataColumn = null;
            switch (jsonType)
            {
                case JTokenType.Integer:
                    int[] dummy = new int[] { Convert.ToInt32(values) };
                    dataColumn = new DataColumn(dataField, dummy);
                    return dataColumn;
                case JTokenType.Float:
                    double[] dummyDouble = new double[] { Convert.ToDouble(values) };
                    dataColumn = new DataColumn(dataField, dummyDouble);
                    return dataColumn;
                case JTokenType.String:
                    string[] dummyString = new string[] { Convert.ToString(values) };
                    dataColumn = new DataColumn(dataField, dummyString);
                    return dataColumn;
                case JTokenType.Boolean:
                    bool[] dummyBool = new bool[] { Convert.ToBoolean(values) };
                    dataColumn = new DataColumn(dataField, dummyBool);
                    return dataColumn;
                // Add more type mappings as needed
                default:
                    return dataColumn; // Default to object type
            }
        }


        public async Task WriteJsonToParquetFileAsync_three(string json, string outputPath)
        {
            try
            {
                // Parse the JSON string into a dynamic object
                var jsonData = JObject.Parse(json);

                // Create data columns with schema metadata and the data you need
                var dataColumns = new List<DataColumn>();

                // Define data fields for the schema
                var schemaFields = new List<DataField>();

                foreach (var property in jsonData.Properties())
                {
                    var fieldName = property.Name;
                    var dataType = GetParquetDataType(property.Value.Type);

                    // Create a data field for the schema
                    var dataField = new DataField(fieldName, dataType);
                    schemaFields.Add(dataField);

                    // Create a data column for the data
                    //var data = new JArray(property.Value); // Convert JSON value to an array
                    //var dataArray = data.ToObject(dataType.MakeArrayType());
                    //var dataColumn = new DataColumn(dataField, dataArray);
                    //dataColumns.Add(dataColumn);
                    var dataColumn = new DataColumn(dataField, new[] { property.Value });
                    dataColumns.Add(dataColumn);
                }

                // Create the Parquet schema with defined data fields
                var schema = new ParquetSchema(schemaFields.ToArray());

                using (Stream fileStream = File.OpenWrite(outputPath))
                {
                    using (var parquetWriter = await ParquetWriter.CreateAsync(schema, fileStream))
                    {
                        parquetWriter.CompressionMethod = CompressionMethod.Gzip;
                        parquetWriter.CompressionLevel = System.IO.Compression.CompressionLevel.Optimal;

                        // Create a new row group in the file
                        using (var groupWriter = parquetWriter.CreateRowGroup())
                        {
                            foreach (var dataColumn in dataColumns)
                            {
                                await groupWriter.WriteColumnAsync(dataColumn);
                            }
                        }
                    }
                }

                Console.WriteLine("Data written to Parquet file successfully.");
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error writing data to Parquet file: " + ex.Message);
            }
        }

    }
}
