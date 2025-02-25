using System

namespace test
{
    public class test
    {
        public void startup()
        {
           
            foreach (string wbAssembly in new string[] {
            //"CsvHelper.dll",
            //"LoadingSpinner.dll",
            //"Microsoft.Bcl.AsyncInterfaces.dll",
            //"Microsoft.Bcl.HashCode.dll",
            "Newtonsoft.Json.dll",
            "RevitUtils.23.0.0.1.dll",
            //"System.Buffers.dll",
            //"System.Collections.Immutable.dll",
            //"System.Memory.dll",
            //"System.Numerics.Vectors.dll",
            //"System.Reflection.Metadata.dll",
            //"System.Runtime.CompilerServices.Unsafe.dll",
            //"System.Threading.Channels.dll",
            //"System.Threading.Tasks.Extensions.dll",
            //"System.ValueTuple.dll",
            "Utils.23.0.0.1.dll"

            string BinPath = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
            //string dummy = @"C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\Samples\pyRevit\Extensions\duHast.extension\duHast.tab\PushIt.panel\bin"
            //print(BinPath);
            Assembly.Load(File.ReadAllBytes(Path.Combine(BinPath, wbAssembly)));

            }
            )
         Console.WriteLine("Hello World");
        }
    }
}