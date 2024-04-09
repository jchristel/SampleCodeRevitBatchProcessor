using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace RBP_Launcher.Utilities.Configs
{
    public class LauncherHeadlessConfiguration
    {
        [JsonProperty("rbpFilePath")]
        public string? RbpFilePath { get; set; }

        [JsonProperty("cPython")]
        public List<PythonConfiguration>? CPython { get; set; }

        public static LauncherHeadlessConfiguration? FromJson(string json)
        {
            return JsonConvert.DeserializeObject<LauncherHeadlessConfiguration>(json);
        }
    }

    public class PythonConfiguration
    {
        [JsonProperty("version")]
        public string? Version { get; set; }

        [JsonProperty("filePath")]
        public string? FilePath { get; set; }
    }
}
