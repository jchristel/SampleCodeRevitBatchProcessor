using PythonTests.Setup;
using NUnit.Framework;
using System;
using System.Collections.Generic;
using System.IO;
using IronPython.Hosting;
using Microsoft.Scripting.Hosting;
using Newtonsoft.Json;


namespace PythonTests.UtilitiesTests
{
    public class FilesJSONTests
    {
        private string tempDirectory;

        [SetUp]
        public void SetUp()
        {
            tempDirectory = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
            Directory.CreateDirectory(tempDirectory);
        }

        [TearDown]
        public void TearDown()
        {
            if (Directory.Exists(tempDirectory))
            {
                Directory.Delete(tempDirectory, true);
            }
        }

        private static dynamic ConvertToPythonDict(Dictionary<string, string> jsonDic)
        {
            // required to buil an actual python dictionary rather than a c# dictionary
            var pyDict = PythonEngineManager.PythonDictionary;
            // this uses a global dictionary...need to clear it before using it to asvoid it containing old data
            pyDict.Clear();

            foreach (var item in jsonDic)
            {
                Console.WriteLine($"..toPyDic..key: {item.Key} value: {item.Value}");
                pyDict[item.Key] = item.Value;
            }
            Console.WriteLine(pyDict);
            return pyDict;
        }

        private static dynamic ConvertToPythonDictNested(Dictionary<string, object> jsonDic)
        {
            var pyDict = PythonEngineManager.PythonDictionary;

            foreach (var item in jsonDic)
            {
                if (item.Value is Dictionary<string, object> nestedDict)
                {
                    pyDict[item.Key] = ConvertToPythonDictNested(nestedDict);
                }
                else if (item.Value is Dictionary<string, string> nestedDictString)
                {
                    pyDict[item.Key] = ConvertToPythonDict(nestedDictString);
                }
                else
                {
                    pyDict[item.Key] = item.Value;
                }
            }
            return pyDict;
        }

        private static string prepComparisonString<T>(T jsonData) where T : IDictionary<string, string>
        {
            // Use Newtonsoft.Json to serialize the dictionary to a JSON string
            // required since ironpython json format contains a space after the colon  "{"key": "value"}"
            // but the c# version is missing that space: "{"key":"value"}"

            var stringWriter = new StringWriter();
            using (var jsonWriter = new JsonTextWriter(stringWriter)
            {
                Formatting = Formatting.None,
                Indentation = 0,
                IndentChar = ' ',
                QuoteName = true,
                QuoteChar = '"'
            })
            {
                jsonWriter.WriteStartObject();
                foreach (var kvp in jsonData)
                {
                    jsonWriter.WritePropertyName(kvp.Key);
                    jsonWriter.WriteRaw(" ");
                    jsonWriter.WriteValue(kvp.Value);
                }
                jsonWriter.WriteEndObject();
            }
            return stringWriter.ToString();
        }

        [Test]
        public void ModuleShouldBeLoaded()
        {
            Assert.That(PythonEngineManager.FilesJSONModule, Is.Not.Null, "file_json should be loaded.");
        }

        [Test]
        public void WriteJsonToFile_ShouldWriteValidJson()
        {
            var jsonData = new Dictionary<string, string> { { "key", "value" } };
            var pyJsonData = ConvertToPythonDict(jsonData);
            string filePath = Path.Combine(tempDirectory, "output.json");

            dynamic result = PythonEngineManager.FilesJSONModule.write_json_to_file(pyJsonData, filePath);

            Assert.That(result.status, Is.True, result.message);
            Assert.That(File.Exists(filePath), Is.True);
            string fileContent = File.ReadAllText(filePath);

            // Use Newtonsoft.Json to serialize the dictionary to a JSON string
            string expectedJson = prepComparisonString(jsonData);
            Assert.That(fileContent, Is.EqualTo(expectedJson), "data should be equal");
        }

        [Test]
        public void WriteJsonToFile_ShouldHandleEmptyData()
        {
            dynamic module = PythonEngineManager.FilesJSONModule;
            var jsonData = new Dictionary<string, string>();
            var pyJsonData = ConvertToPythonDict(jsonData);
            string filePath = Path.Combine(tempDirectory, "output.json");

            dynamic result = module.write_json_to_file(pyJsonData, filePath);

            Assert.That(result.status, Is.True, result.message);
            Assert.That(File.Exists(filePath), Is.True);
            string fileContent = File.ReadAllText(filePath);

            string expectedJson = prepComparisonString(jsonData);
            Assert.That(fileContent, Is.EqualTo(expectedJson), "data should be equal");
        }

        [Test]
        public void WriteJsonToFile_ShouldHandleUtf8Characters()
        {
            dynamic module = PythonEngineManager.FilesJSONModule;
            var jsonData = new Dictionary<string, string> { { "key", "value with ütf8" } };
            var pyJsonData = ConvertToPythonDict(jsonData);
            string filePath = Path.Combine(tempDirectory, "output.json");

            dynamic result = module.write_json_to_file(pyJsonData, filePath);

            Assert.That(result.status, Is.True, result.message);
            Assert.That(File.Exists(filePath), Is.True);
            string fileContent = File.ReadAllText(filePath);

            string expectedJson = prepComparisonString(jsonData);
            Assert.That(fileContent, Is.EqualTo(expectedJson), "data should be equal");
        }

        [Test]
        public void WriteJsonToFile_ShouldReturnErrorOnInvalidPath()
        {
            dynamic module = PythonEngineManager.FilesJSONModule;
            var jsonData = new Dictionary<string, string> { { "key", "value" } };
            string invalidFilePath = Path.Combine(tempDirectory, "invalid\0path.json");

            dynamic result = module.write_json_to_file(jsonData, invalidFilePath);

            Assert.That(result.status, Is.False);
            Assert.That(result.message, Does.Contain("Failed to write data to file"));
        }

        [Test]
        public void WriteJsonToFile_ShouldHandleNonSerializableData()
        {
            dynamic module = PythonEngineManager.FilesJSONModule;
            var jsonData = new Dictionary<string, object> { { "key", new Dictionary<string, string> { { "nestedKey", "nestedValue" } } } };
            var pyJsonData = ConvertToPythonDictNested(jsonData);
            string filePath = Path.Combine(tempDirectory, "output.json");

            dynamic result = module.write_json_to_file(pyJsonData, filePath);

            // will return false since the nested dictionary is not serializable
            Assert.That(result.status, Is.False, result.message);
            Assert.That(File.Exists(filePath), Is.False);
        }

        [Test]
        public void WriteAndReadJsonData_ShouldMatchOriginalData()
        {
            var jsonData = new Dictionary<string, string> { 
                { "key1", "value1" },
                { "key2", "value2" },
                { "key3", "value3" }
            };
            var pyJsonData = ConvertToPythonDict(jsonData);
            string filePath = Path.Combine(tempDirectory, "output.json");

            // Write JSON data to file
            dynamic writeResult = PythonEngineManager.FilesJSONModule.write_json_to_file(pyJsonData, filePath);

            Assert.That(writeResult.status, Is.True, writeResult.message);
            Assert.That(File.Exists(filePath), Is.True);

            // Read JSON data from file
            dynamic readResult = PythonEngineManager.FilesJSONModule.read_json_data_from_file(filePath);
            Assert.That(readResult.status, Is.True, readResult.message);

            var jsonDataRead = readResult.result[0];
            // Convert the read result to a C# dictionary for comparison
            var readData = new Dictionary<string, string>();
            foreach (var key in jsonDataRead.keys())
            {
                readData[key] = jsonDataRead[key];
            }

            // Sort the dictionaries by their keys
            var sortedJsonData = new SortedDictionary<string, string>(jsonData);
            var sortedReadData = new SortedDictionary<string, string>(readData);

            // Use Newtonsoft.Json to serialize the sorted dictionaries to JSON strings
            string expectedJson = prepComparisonString(sortedJsonData);
            string readJson = prepComparisonString(sortedReadData);

            Assert.That(readJson, Is.EqualTo(expectedJson), "data should be equal");
        }

        [Test]
        public void WriteAndReadJsonData_ShouldHandleNonUtf8Characters()
        {
            var jsonData = new Dictionary<string, string> {
                { "key1", "value1" },
                { "key2", "value2" },
                { "key3", "value3 with non-utf8 character: \u00A9" } // © character
            };  
            var pyJsonData = ConvertToPythonDict(jsonData);
            string filePath = Path.Combine(tempDirectory, "output.json");

            // Write JSON data to file
            dynamic writeResult = PythonEngineManager.FilesJSONModule.write_json_to_file(pyJsonData, filePath);

            Assert.That(writeResult.status, Is.True, writeResult.message);
            Assert.That(File.Exists(filePath), Is.True);

            // Read JSON data from file
            dynamic readResult = PythonEngineManager.FilesJSONModule.read_json_data_from_file(filePath);
            Assert.That(readResult.status, Is.True, readResult.message);

            var jsonDataRead = readResult.result[0];
            // Convert the read result to a C# dictionary for comparison
            var readData = new Dictionary<string, string>();
            foreach (var key in jsonDataRead.keys())
            {
                readData[key] = jsonDataRead[key];
            }

            // Sort the dictionaries by their keys
            var sortedJsonData = new SortedDictionary<string, string>(jsonData);
            var sortedReadData = new SortedDictionary<string, string>(readData);

            // Use Newtonsoft.Json to serialize the sorted dictionaries to JSON strings
            string expectedJson = prepComparisonString(sortedJsonData);
            string readJson = prepComparisonString(sortedReadData);

            Assert.That(readJson, Is.EqualTo(expectedJson), "data should be equal");
        }

        [Test]
        public void WriteAndReadJsonData_ShouldHandleEmptyJson()
        {
            var jsonData = new Dictionary<string, string>(); // Empty dictionary
            var pyJsonData = ConvertToPythonDict(jsonData);
            string filePath = Path.Combine(tempDirectory, "output.json");

            // Write JSON data to file
            dynamic writeResult = PythonEngineManager.FilesJSONModule.write_json_to_file(pyJsonData, filePath);

            Assert.That(writeResult.status, Is.True, writeResult.message);
            Assert.That(File.Exists(filePath), Is.True);

            // Read JSON data from file
            dynamic readResult = PythonEngineManager.FilesJSONModule.read_json_data_from_file(filePath);
            Assert.That(readResult.status, Is.True, readResult.message);

            var jsonDataRead = readResult.result[0];
            // Convert the read result to a C# dictionary for comparison
            var readData = new Dictionary<string, string>();
            foreach (var key in jsonDataRead.keys())
            {
                readData[key] = jsonDataRead[key];
            }

            // Sort the dictionaries by their keys
            var sortedJsonData = new SortedDictionary<string, string>(jsonData);
            var sortedReadData = new SortedDictionary<string, string>(readData);

            // Use Newtonsoft.Json to serialize the sorted dictionaries to JSON strings
            string expectedJson = prepComparisonString(sortedJsonData);
            string readJson = prepComparisonString(sortedReadData);

            Assert.That(readJson, Is.EqualTo(expectedJson), "data should be equal");
        }

        [Test]
        public void WriteAndCombineJsonFiles_ShouldMatchCombinedData()
        {
            var jsonData1 = new Dictionary<string, string> {
                { "key1", "value1" },
                { "key2", "value2" }
            };
            var jsonData2 = new Dictionary<string, string> {
                { "key3", "value3" },
                { "key4", "value4" }
            };

            var pyJsonData1 = ConvertToPythonDict(jsonData1);
            

            string filePath1 = Path.Combine(tempDirectory, "file1.json");
            string filePath2 = Path.Combine(tempDirectory, "file2.json");

            // Write JSON data to files
            dynamic writeResult1 = PythonEngineManager.FilesJSONModule.write_json_to_file(pyJsonData1, filePath1);
            Assert.That(writeResult1.status, Is.True, writeResult1.message);
            Assert.That(File.Exists(filePath1), Is.True);
            var write_resultdata1 = writeResult1.result[0];
            Console.WriteLine($"writeResult1: {write_resultdata1}");


            // Read JSON data from file
            dynamic readResult1 = PythonEngineManager.FilesJSONModule.read_json_data_from_file(filePath1);
            Assert.That(readResult1.status, Is.True, readResult1.message);

            var jsonDataRead__ = readResult1.result[0];
            // Convert the read result to a C# dictionary for comparison
            foreach (var key in jsonDataRead__.keys())
            {
                Console.WriteLine($"..1..key: {key} value: {jsonDataRead__[key]}");

            }

            // this needs to happen seqentially since the python dictionary is global and will contain the data from the first write
            // If I change that before writing it to file, the data will be lost and be replaced with the second data
            var pyJsonData2 = ConvertToPythonDict(jsonData2);

            dynamic writeResult2 = PythonEngineManager.FilesJSONModule.write_json_to_file(pyJsonData2, filePath2);
            Assert.That(writeResult2.status, Is.True, writeResult2.message);
            Assert.That(File.Exists(filePath2), Is.True);
            var write_resultdata2 = writeResult1.result[0];
            Console.WriteLine($"writeResult2: {write_resultdata2}");

            dynamic readResult2 = PythonEngineManager.FilesJSONModule.read_json_data_from_file(filePath2);
            Assert.That(readResult2.status, Is.True, readResult2.message);

            var jsonDataRead_2_ = readResult2.result[0];
            foreach (var key in jsonDataRead_2_.keys())
            {
                Console.WriteLine($"..2..key: {key} value: {jsonDataRead_2_[key]}");
            }


            // Combine JSON files
            dynamic combineResult = PythonEngineManager.FilesJSONModule.combine_files_json(folder_path:tempDirectory, file_extension: ".json", output_file_name: "combined.json");
            Assert.That(combineResult.status, Is.True);

            Console.WriteLine(combineResult.message);

            // Read combined JSON data from file
            string combinedFilePath = Path.Combine(tempDirectory, "combined.json");
            dynamic readResult = PythonEngineManager.FilesJSONModule.read_json_data_from_file(combinedFilePath);
            Assert.That(readResult.status, Is.True, readResult.message);

            Console.WriteLine(readResult.message);
            Console.WriteLine($"number of dictioanries in result read {readResult.result.Count}");


            var combinedDataRead = readResult.result[0];
            // Convert the read result to a C# list of sorted dictionaries for comparison
            var readDataList = new List<string>();
            foreach (var jsonDataRead in combinedDataRead)
            {
                var readData = new SortedDictionary<string, string>();
                foreach (var key in jsonDataRead.keys())
                {
                    readData[key] = jsonDataRead[key];
                    Console.WriteLine($"key: {key} value: {jsonDataRead[key]}");
                }
                readDataList.Add(prepComparisonString(readData));
            }

            // Expected combined data as sorted dictionaries
            var expectedDataList = new List<string> {
                prepComparisonString(jsonData1),
                prepComparisonString(jsonData2)
            };

            // Use Newtonsoft.Json to serialize the lists of sorted dictionaries to JSON strings
            //string expectedJson = JsonConvert.SerializeObject(expectedDataList, Formatting.Indented);
            //string readJson = JsonConvert.SerializeObject(readDataList, Formatting.Indented);

            Assert.That(readDataList, Is.EqualTo(expectedDataList), "combined data should be equal");
        }

        [Test]
        public void WriteAndCombineJsonFiles_WithOneEmptyFile_ShouldMatchCombinedData()
        {
            var jsonData1 = new Dictionary<string, string> {
                { "key1", "value1" },
                { "key2", "value2" }
            };
            var jsonData2 = new Dictionary<string, string> ();

            var pyJsonData1 = ConvertToPythonDict(jsonData1);


            string filePath1 = Path.Combine(tempDirectory, "file1.json");
            string filePath2 = Path.Combine(tempDirectory, "file2.json");

            // Write JSON data to files
            dynamic writeResult1 = PythonEngineManager.FilesJSONModule.write_json_to_file(pyJsonData1, filePath1);
            Assert.That(writeResult1.status, Is.True, writeResult1.message);
            Assert.That(File.Exists(filePath1), Is.True);
            var write_resultdata1 = writeResult1.result[0];
            Console.WriteLine($"writeResult1: {write_resultdata1}");


            // Read JSON data from file
            dynamic readResult1 = PythonEngineManager.FilesJSONModule.read_json_data_from_file(filePath1);
            Assert.That(readResult1.status, Is.True, readResult1.message);

            var jsonDataRead__ = readResult1.result[0];
            // Convert the read result to a C# dictionary for comparison
            foreach (var key in jsonDataRead__.keys())
            {
                Console.WriteLine($"..1..key: {key} value: {jsonDataRead__[key]}");

            }

            // this needs to happen seqentially since the python dictionary is global and will contain the data from the first write
            // If I change that before writing it to file, the data will be lost and be replaced with the second data
            var pyJsonData2 = ConvertToPythonDict(jsonData2);

            dynamic writeResult2 = PythonEngineManager.FilesJSONModule.write_json_to_file(pyJsonData2, filePath2);
            Assert.That(writeResult2.status, Is.True, writeResult2.message);
            Assert.That(File.Exists(filePath2), Is.True);
            var write_resultdata2 = writeResult1.result[0];
            Console.WriteLine($"writeResult2: {write_resultdata2}");

            dynamic readResult2 = PythonEngineManager.FilesJSONModule.read_json_data_from_file(filePath2);
            Assert.That(readResult2.status, Is.True, readResult2.message);

            var jsonDataRead_2_ = readResult2.result[0];
            foreach (var key in jsonDataRead_2_.keys())
            {
                Console.WriteLine($"..2..key: {key} value: {jsonDataRead_2_[key]}");
            }


            // Combine JSON files
            dynamic combineResult = PythonEngineManager.FilesJSONModule.combine_files_json(folder_path: tempDirectory, file_extension: ".json", output_file_name: "combined.json");
            Assert.That(combineResult.status, Is.True);

            Console.WriteLine(combineResult.message);

            // Read combined JSON data from file
            string combinedFilePath = Path.Combine(tempDirectory, "combined.json");
            dynamic readResult = PythonEngineManager.FilesJSONModule.read_json_data_from_file(combinedFilePath);
            Assert.That(readResult.status, Is.True, readResult.message);

            Console.WriteLine(readResult.message);
            Console.WriteLine($"number of dictioanries in result read {readResult.result.Count}");


            var combinedDataRead = readResult.result[0];
            // Convert the read result to a C# list of sorted dictionaries for comparison
            var readDataList = new List<string>();
            foreach (var jsonDataRead in combinedDataRead)
            {
                var readData = new SortedDictionary<string, string>();
                foreach (var key in jsonDataRead.keys())
                {
                    readData[key] = jsonDataRead[key];
                    Console.WriteLine($"key: {key} value: {jsonDataRead[key]}");
                }
                readDataList.Add(prepComparisonString(readData));
            }

            // Expected combined data as sorted dictionaries
            var expectedDataList = new List<string> {
                prepComparisonString(jsonData1),
                prepComparisonString(jsonData2)
            };

            // Use Newtonsoft.Json to serialize the lists of sorted dictionaries to JSON strings
            //string expectedJson = JsonConvert.SerializeObject(expectedDataList, Formatting.Indented);
            //string readJson = JsonConvert.SerializeObject(readDataList, Formatting.Indented);

            Assert.That(readDataList, Is.EqualTo(expectedDataList), "combined data should be equal");
        }

        [Test]
        public void WriteAndCombineJsonFiles_WithTwoEmptyFile_ShouldMatchCombinedData()
        {
            var jsonData1 = new Dictionary<string, string> ();
            var jsonData2 = new Dictionary<string, string>();

            var pyJsonData1 = ConvertToPythonDict(jsonData1);


            string filePath1 = Path.Combine(tempDirectory, "file1.json");
            string filePath2 = Path.Combine(tempDirectory, "file2.json");

            // Write JSON data to files
            dynamic writeResult1 = PythonEngineManager.FilesJSONModule.write_json_to_file(pyJsonData1, filePath1);
            Assert.That(writeResult1.status, Is.True, writeResult1.message);
            Assert.That(File.Exists(filePath1), Is.True);
            var write_resultdata1 = writeResult1.result[0];
            Console.WriteLine($"writeResult1: {write_resultdata1}");


            // Read JSON data from file
            dynamic readResult1 = PythonEngineManager.FilesJSONModule.read_json_data_from_file(filePath1);
            Assert.That(readResult1.status, Is.True, readResult1.message);

            var jsonDataRead__ = readResult1.result[0];
            // Convert the read result to a C# dictionary for comparison
            foreach (var key in jsonDataRead__.keys())
            {
                Console.WriteLine($"..1..key: {key} value: {jsonDataRead__[key]}");

            }

            // this needs to happen seqentially since the python dictionary is global and will contain the data from the first write
            // If I change that before writing it to file, the data will be lost and be replaced with the second data
            var pyJsonData2 = ConvertToPythonDict(jsonData2);

            dynamic writeResult2 = PythonEngineManager.FilesJSONModule.write_json_to_file(pyJsonData2, filePath2);
            Assert.That(writeResult2.status, Is.True, writeResult2.message);
            Assert.That(File.Exists(filePath2), Is.True);
            var write_resultdata2 = writeResult1.result[0];
            Console.WriteLine($"writeResult2: {write_resultdata2}");

            dynamic readResult2 = PythonEngineManager.FilesJSONModule.read_json_data_from_file(filePath2);
            Assert.That(readResult2.status, Is.True, readResult2.message);

            var jsonDataRead_2_ = readResult2.result[0];
            foreach (var key in jsonDataRead_2_.keys())
            {
                Console.WriteLine($"..2..key: {key} value: {jsonDataRead_2_[key]}");
            }


            // Combine JSON files
            dynamic combineResult = PythonEngineManager.FilesJSONModule.combine_files_json(folder_path: tempDirectory, file_extension: ".json", output_file_name: "combined.json");
            Assert.That(combineResult.status, Is.True);

            Console.WriteLine(combineResult.message);

            // Read combined JSON data from file
            string combinedFilePath = Path.Combine(tempDirectory, "combined.json");
            dynamic readResult = PythonEngineManager.FilesJSONModule.read_json_data_from_file(combinedFilePath);
            Assert.That(readResult.status, Is.True, readResult.message);

            Console.WriteLine(readResult.message);
            Console.WriteLine($"number of dictioanries in result read {readResult.result.Count}");


            var combinedDataRead = readResult.result[0];
            // Convert the read result to a C# list of sorted dictionaries for comparison
            var readDataList = new List<string>();
            foreach (var jsonDataRead in combinedDataRead)
            {
                var readData = new SortedDictionary<string, string>();
                foreach (var key in jsonDataRead.keys())
                {
                    readData[key] = jsonDataRead[key];
                    Console.WriteLine($"key: {key} value: {jsonDataRead[key]}");
                }
                readDataList.Add(prepComparisonString(readData));
            }

            // Expected combined data as sorted dictionaries
            var expectedDataList = new List<string> {
                prepComparisonString(jsonData1),
                prepComparisonString(jsonData2)
            };

            // Use Newtonsoft.Json to serialize the lists of sorted dictionaries to JSON strings
            //string expectedJson = JsonConvert.SerializeObject(expectedDataList, Formatting.Indented);
            //string readJson = JsonConvert.SerializeObject(readDataList, Formatting.Indented);

            Assert.That(readDataList, Is.EqualTo(expectedDataList), "combined data should be equal");
        }


    }
}
