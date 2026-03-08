// BSD License - Copyright 2025, Jan Christel

using Newtonsoft.Json;
using System.Collections.Generic;

namespace duHastNet.PushIt.Models.Drofus
{
    /// <summary>
    /// Per-provider settings for the drofus data source.
    /// Stored as a nested object inside <see cref="DataSourceSettings"/>.
    /// </summary>
    public class DrofusDataSourceSettings
    {
        /// <summary>
        /// The drofus API base URL. Varies by region or client deployment.
        /// e.g. <c>"https://api.hidd.health.nsw.gov.au"</c> or <c>"https://apiau.drofus.com"</c>
        /// </summary>
        public string BaseUrl { get; set; } = string.Empty;

        /// <summary>
        /// drofus database identifier — first path segment after <c>/api/</c>.
        /// e.g. <c>"hi-alburycr"</c>
        /// </summary>
        public string DatabaseName { get; set; } = string.Empty;

        /// <summary>
        /// Project number within the database — second path segment after <c>/api/{database}/</c>.
        /// e.g. <c>"01"</c>
        /// </summary>
        public string ProjectNumber { get; set; } = string.Empty;

        /// <summary>
        /// API-key from the drofus Power Query credentials dialog.
        /// Sent as: <c>Authorization: Reference {ApiToken}</c>
        /// </summary>
        public string ApiToken { get; set; } = string.Empty;

        /// <summary>
        /// Number of rooms skipped during the last <c>GetRoomsData</c> call because
        /// their unique-id field was absent or null in the JSON response.
        /// <para>
        /// Runtime-only — never written to the settings JSON file.
        /// Reset to zero at the start of each <c>GetRoomsData</c> call.
        /// </para>
        /// </summary>
        [JsonIgnore]
        public int LastSkippedRoomCount { get; set; }

        /// <summary>
        /// Room properties available from the drofus API, populated during
        /// startup by <c>ValidateDrofusOnStartup</c> before the window opens.
        /// <para>
        /// Runtime-only — never written to the settings JSON file.
        /// Read by <c>DrofusDataSourceControlViewModel</c> on construction to
        /// pre-populate <see cref="DrofusPropertyMapper.AvailableFields"/>
        /// without requiring a second API call.
        /// </para>
        /// </summary>
        [JsonIgnore]
        public List<string> StartupAvailableFields { get; set; } = new List<string>();

        /// <summary>
        /// Saved drofus → Revit (and reverse) property mappings.
        /// Populated by the user via the mapping UI after a successful Connect.
        /// <para>
        /// Serialised to and from the PushIt settings JSON file alongside the
        /// connection fields. Defaults to an empty list so that a freshly
        /// default-constructed instance requires no migration.
        /// </para>
        /// <para>
        /// Runtime validation state (<see cref="MappingValidationState"/>) is
        /// held in the ViewModel layer and is never included here.
        /// </para>
        /// </summary>
        public List<DrofusPropertyMap> PropertyMappings { get; set; } = new List<DrofusPropertyMap>();

        /// <summary>
        /// Names of properties for which <c>RevitTakesPrecedenceAfterInitialPush</c> is <c>true</c>.
        /// The user sets these via checkboxes in the drofus data source UI panel.
        /// On the first push to a split room, the source-of-accommodation value is written.
        /// On every subsequent push the value stored in Revit takes precedence and the
        /// SoA value is ignored for that property.
        /// <para>
        /// Serialised to the PushIt settings JSON alongside the connection fields.
        /// Defaults to an empty list — all properties follow SoA by default.
        /// </para>
        /// </summary>
        public List<string> RevitPrecedencePropertyNames { get; set; } = new List<string>();
    }
}
