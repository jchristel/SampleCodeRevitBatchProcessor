// BSD License - Copyright 2025, Jan Christel

namespace duHastNet.PushIt.Models
{
    /// <summary>
    /// Per-provider settings for the drofus data source.
    /// Stored as a nested object inside DataSourceSettings.
    /// </summary>
    public class DrofusDataSourceSettings
    {
        /// <summary>
        /// The drofus API base URL. Varies by region or client deployment.
        /// e.g. "https://api.hidd.health.nsw.gov.au" or "https://apiau.drofus.com"
        /// </summary>
        public string BaseUrl { get; set; } = string.Empty;

        /// <summary>
        /// drofus database identifier — first path segment after /api/.
        /// e.g. "hi-alburycr"
        /// </summary>
        public string DatabaseName { get; set; } = string.Empty;

        /// <summary>
        /// Project number within the database — second path segment after /api/{database}/.
        /// e.g. "01"
        /// </summary>
        public string ProjectNumber { get; set; } = string.Empty;

        /// <summary>
        /// API-key from the drofus Power Query credentials dialog.
        /// Sent as: Authorization: Reference {ApiToken}
        /// </summary>
        public string ApiToken { get; set; } = string.Empty;

        /// <summary>True once Connect has succeeded.</summary>
        public bool IsConnected { get; set; }

        /// <summary>Room count returned by the last successful connection test.</summary>
        public int LastRoomCount { get; set; }
    }
}