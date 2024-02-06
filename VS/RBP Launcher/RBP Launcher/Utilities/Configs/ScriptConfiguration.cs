using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace RBP_Launcher.Utilities.Configs
{
    public class ScriptConfiguration
    {
        public class Script
        {
            [JsonProperty("start_interval")]
            public int? StartInterval { get; set; }

            [JsonProperty("pre script")]
            public ScriptDetails? PreScript { get; set; }

            [JsonProperty("post script")]
            public ScriptDetails? PostScript { get; set; }

            [JsonProperty("setting files")]
            public List<string>? SettingFiles { get; set; }
        }

        public class ScriptDetails
        {
            [JsonProperty("python version")]
            public string? PythonVersion { get; set; }

            [JsonProperty("script file path")]
            public string? ScriptFilePath { get; set; }

            [JsonProperty("script arguments")]
            public List<string>? ScriptArguments { get; set; }
        }

        [JsonProperty("pre script")]
        public List<ScriptDetails>? PreScript { get; set; }

        [JsonProperty("batch processor scripts")]
        public List<Script>? BatchProcessorScripts { get; set; }

        [JsonProperty("post script")]
        public List<ScriptDetails>? PostScript { get; set; }

        public static ScriptConfiguration? FromJson(string json)
        {
            return JsonConvert.DeserializeObject<ScriptConfiguration>(json);
        }
    }
}
