using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;


namespace RevitBatchProcessor
{
    public static class WriteToFile
    {
        /// <summary>
        /// method writing data to a text file in synchronous mode
        /// </summary>
        /// <param name="fullFilePath"></param>
        /// <param name="data"></param>
        /// <param name="appendDataToFile"></param>
        /// <returns></returns>
        public static bool WriteSynchronous(
            string fullFilePath,
            string data,
            bool appendDataToFile = true)
        {
            bool exs = true;
            try
            {
                using (StreamWriter sw = new StreamWriter(fullFilePath, appendDataToFile))
                {
                    if (data != null)
                    {
                        sw.WriteLine(data);
                    }
                    sw.Close();
                }
            }
            catch (System.Exception ex)
            {
                exs = false;
            }
            return exs;
        }
    }
}
