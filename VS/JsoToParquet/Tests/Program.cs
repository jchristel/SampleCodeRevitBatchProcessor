using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using SampleCodeRevitBatchProcessor.Tests;

namespace Tests
{
    internal class Program
    {
        static void Main(string[] args)
        {
            testJson();
        }

        static async void testJson()
        {
            JsonToParquetTests testJson = new JsonToParquetTests();
            await testJson.WriteJsonToParquetAsync_ValidData_WritesParquetFile();
        }
    }
}
