// BSD License - Copyright 2025, Jan Christel

using Newtonsoft.Json;

namespace duHastNet.PushIt.DataSources.Drofus.Models;

/// <summary>
/// Serialisable drofus configuration stored inside the PushIt settings file.
/// Sits alongside the existing DataSourceSettings fields; added to Settings.cs
/// when the Drofus source type is selected.
///
/// JSON example (written to the existing PushIt settings file):
/// {
///   "DataSource": {
///     "SourceType": "Drofus",
///     "Drofus": {
///       "Region": "EU",
///       "DatabaseId": "my-project-db",
///       "ProjectNumber": "01",
///       "ApiKey": "abc123..."
///     }
///   }
/// }
/// </summary>
public class DrofusSettings
{
    /// <summary>Which drofus regional API host to target.</summary>
    public DrofusRegion Region { get; set; } = DrofusRegion.EU;

    /// <summary>
    /// The drofus database identifier shown in the project URL
    /// (e.g. the segment after api-eu.drofus.com/api/).
    /// </summary>
    public string DatabaseId { get; set; } = string.Empty;

    /// <summary>Project number within the database (e.g. "01").</summary>
    public string ProjectNumber { get; set; } = string.Empty;

    /// <summary>
    /// API-key generated in drofus (Power Query → Credentials → Generate Key).
    /// Stored in plain text in the local settings file — acceptable for a
    /// single-user desktop app; the key is read-only and project-scoped.
    /// </summary>
    public string ApiKey { get; set; } = string.Empty;

    /// <summary>
    /// Returns true when all required fields have values.
    /// Does NOT perform live validation against the drofus API.
    /// </summary>
    [JsonIgnore]
    public bool IsConfigured =>
        !string.IsNullOrWhiteSpace(DatabaseId) &&
        !string.IsNullOrWhiteSpace(ProjectNumber) &&
        !string.IsNullOrWhiteSpace(ApiKey);

    /// <summary>Converts to the runtime auth settings object used by IDrofusAuthService.</summary>
    public DrofusAuthSettings ToAuthSettings() => new()
    {
        AuthMode      = DrofusAuthMode.ApiKey,
        Region        = Region,
        DatabaseId    = DatabaseId,
        ProjectNumber = ProjectNumber,
        ApiKey        = ApiKey
    };
}
