// BSD License - Copyright 2025, Jan Christel

using duHastNet.PushIt.DataSources.Drofus.Models;

namespace duHastNet.PushIt.DataSources.Drofus.Models;

/// <summary>
/// Per-provider settings stored inside DataSourceSettings when SourceType == Drofus.
/// 
/// For the PoC only ApiKey + Region + DatabaseId are needed.
/// The OAuth2 fields are stubbed ready for the real implementation.
/// </summary>
public class DrofusAuthSettings
{
    // -------------------------------------------------------------------------
    // Region / host selection
    // -------------------------------------------------------------------------

    /// <summary>
    /// Which drofus regional API host to use.
    /// Determines the base URL: https://api-{region}.drofus.com
    /// </summary>
    public DrofusRegion Region { get; set; } = DrofusRegion.EU;

    /// <summary>
    /// Resolved base URL derived from Region.
    /// Overridable for on-premises / non-standard deployments.
    /// </summary>
    public string BaseUrl => CustomBaseUrl ?? Region switch
    {
        DrofusRegion.NO => "https://api-no.drofus.com",
        DrofusRegion.EU => "https://api-eu.drofus.com",
        DrofusRegion.US => "https://api-us.drofus.com",
        DrofusRegion.CA => "https://api-ca.drofus.com",
        DrofusRegion.AU => "https://api-au.drofus.com",
        _               => "https://api-eu.drofus.com"
    };

    /// <summary>Optional override for non-standard host URLs.</summary>
    public string? CustomBaseUrl { get; set; }

    // -------------------------------------------------------------------------
    // Project / database identification
    // -------------------------------------------------------------------------

    /// <summary>
    /// The drofus database identifier (e.g. "akl-test", "my-project-db").
    /// Part of every API path: /api/{DatabaseId}/{ProjectNumber}/rooms
    /// </summary>
    public string DatabaseId { get; set; } = string.Empty;

    /// <summary>
    /// The project number within the database (e.g. "01").
    /// Part of every API path: /api/{DatabaseId}/{ProjectNumber}/rooms
    /// </summary>
    public string ProjectNumber { get; set; } = string.Empty;

    // -------------------------------------------------------------------------
    // Authentication mode
    // -------------------------------------------------------------------------

    public DrofusAuthMode AuthMode { get; set; } = DrofusAuthMode.ApiKey;

    // ---- API-key fields (PoC) -----------------------------------------------

    /// <summary>
    /// The API-key generated in the drofus Power Query credentials dialog.
    /// Sent as: Authorization: Reference {ApiKey}
    /// </summary>
    public string? ApiKey { get; set; }

    // ---- OAuth2 fields (future) ---------------------------------------------

    /// <summary>OAuth2 client_id provided by drofus after manual registration.</summary>
    public string? OAuthClientId { get; set; }

    /// <summary>
    /// Redirect URI registered with drofus (must match exactly).
    /// For desktop apps typically: http://127.0.0.1:{LocalPort}/callback
    /// </summary>
    public string? OAuthRedirectUri { get; set; }

    /// <summary>Local TCP port the PoC HTTP listener will bind to for the callback.</summary>
    public int OAuthLocalCallbackPort { get; set; } = 5678;

    /// <summary>OAuth2 authorization endpoint (obtained from drofus after registration).</summary>
    public string? OAuthAuthorizationEndpoint { get; set; }

    /// <summary>OAuth2 token endpoint (obtained from drofus after registration).</summary>
    public string? OAuthTokenEndpoint { get; set; }

    /// <summary>Space-separated OAuth2 scopes to request.</summary>
    public string OAuthScopes { get; set; } = "openid profile";
}

public enum DrofusRegion
{
    NO, EU, US, CA, AU
}
