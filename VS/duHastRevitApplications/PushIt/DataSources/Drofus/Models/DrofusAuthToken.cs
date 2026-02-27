// BSD License - Copyright 2025, Jan Christel

namespace duHastNet.PushIt.DataSources.Drofus.Models;

/// <summary>
/// Holds authentication state for a drofus session.
/// Supports both API-key (PoC) and OAuth2 Bearer token (future) modes.
/// </summary>
public class DrofusAuthToken
{
    // -------------------------------------------------------------------------
    // API-key mode (Reference scheme) - suitable for PoC / read-only access
    // -------------------------------------------------------------------------

    /// <summary>Raw API-key value, used with "Authorization: Reference {ApiKey}"</summary>
    public string? ApiKey { get; set; }

    // -------------------------------------------------------------------------
    // OAuth2 Bearer mode - requires manual OAuth client registration with drofus
    // -------------------------------------------------------------------------

    /// <summary>OAuth2 access token value</summary>
    public string? AccessToken { get; set; }

    /// <summary>OAuth2 refresh token (may be null if not issued)</summary>
    public string? RefreshToken { get; set; }

    /// <summary>UTC time at which the access token expires</summary>
    public DateTime? ExpiresAtUtc { get; set; }

    // -------------------------------------------------------------------------
    // Common helpers
    // -------------------------------------------------------------------------

    /// <summary>
    /// Which authentication mode is currently active.
    /// </summary>
    public DrofusAuthMode AuthMode { get; set; } = DrofusAuthMode.None;

    /// <summary>
    /// Returns true when the token appears usable (not expired, correct mode set).
    /// Does NOT guarantee the server will accept it — use Validate() for that.
    /// </summary>
    public bool IsUsable =>
        AuthMode switch
        {
            DrofusAuthMode.ApiKey => !string.IsNullOrWhiteSpace(ApiKey),
            DrofusAuthMode.Bearer => !string.IsNullOrWhiteSpace(AccessToken)
                                     && (ExpiresAtUtc == null || ExpiresAtUtc > DateTime.UtcNow),
            _ => false
        };

    /// <summary>
    /// Builds the value that should be placed in the Authorization HTTP header.
    /// Returns null if the token is not usable.
    /// </summary>
    public string? ToAuthorizationHeaderValue() =>
        AuthMode switch
        {
            DrofusAuthMode.ApiKey when IsUsable    => $"Reference {ApiKey}",
            DrofusAuthMode.Bearer when IsUsable    => $"Bearer {AccessToken}",
            _                                       => null
        };
}

public enum DrofusAuthMode
{
    None,
    /// <summary>
    /// API-key sent as "Authorization: Reference {key}".
    /// Read-only, single-project, suitable for PoC and dashboards.
    /// </summary>
    ApiKey,
    /// <summary>
    /// Full OAuth2 Bearer token.
    /// Requires prior client registration with drofus support.
    /// </summary>
    Bearer
}
