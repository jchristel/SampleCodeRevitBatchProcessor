using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.IO;

namespace SampleCodeRevitBatchProcessor.Tests
{
    [TestClass]
    public class JsonToParquetTests
    {
        [TestMethod]
        public async Task WriteJsonToParquetAsync_ValidData_WritesParquetFile()
        {
            // Arrange
            var jsonData = "{\"key1\":\"value1\",\"key2\":42,\"key3\":3.14}";
            var outputPath = @"C:\Users\janchristel\Documents\test\output.parquet";
            var jsonToParquet = new JsonToParquet();

            try
            {
                // Act
                await jsonToParquet.WriteJsonToParquetFileAsync_Two(jsonData, outputPath);

                // Assert
                Assert.IsTrue(File.Exists(outputPath), "Parquet file should have been created.");

                // Clean up: Delete the created Parquet file
                File.Delete(outputPath);

                Console.ReadLine();
            }
            catch (Exception ex)
            {
                Assert.Fail($"Test failed with exception: {ex}");
            }
        }
    }
}