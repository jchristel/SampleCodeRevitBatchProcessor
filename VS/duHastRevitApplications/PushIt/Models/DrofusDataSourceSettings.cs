// BSD License - Copyright 2025, Jan Christel

namespace duHastNet.PushIt.Models
{
    /// <summary>
    /// Per-provider settings for the drofus data source.
    /// Stored as a nested object inside DataSourceSettings.
    /// Only the fields needed for the PoC: token + database name.
    /// </summary>
    public class DrofusDataSourceSettings
    {
        /// <summary>API-key / bearer token pasted in by the user.</summary>
        public string ApiToken { get; set; } = string.Empty;

        /// <summary>drofus database identifier (e.g. "myproject").</summary>
        public string DatabaseName { get; set; } = string.Empty;

        /// <summary>True once both fields have been filled in and Connect succeeded.</summary>
        public bool IsConnected { get; set; }

        /// <summary>Room count returned by the last successful connection test.</summary>
        public int LastRoomCount { get; set; }
    }
}
