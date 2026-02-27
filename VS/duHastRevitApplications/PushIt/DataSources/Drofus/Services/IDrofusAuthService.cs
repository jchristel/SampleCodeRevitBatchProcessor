// BSD License - Copyright 2025, Jan Christel

using duHastNet.PushIt.DataSources.Drofus.Models;

namespace duHastNet.PushIt.DataSources.Drofus.Interfaces;

/// <summary>
/// Abstraction over the drofus authentication mechanism.
/// 
/// The PoC implements ApiKeyAuthService (no browser, no OAuth client registration needed).
/// A future BearerAuthService can be dropped in behind the same interface once
/// an OAuth client ID has been registered with drofus support.
/// </summary>
public interface IDrofusAuthService
{
    /// <summary>
    /// Obtain a usable DrofusAuthToken.
    /// 
    /// For API-key mode: validates the key with a lightweight /api/ping or
    /// equivalent call; wraps it in a token if successful.
    ///
    /// For OAuth2 Bearer mode: starts the Authorization Code + PKCE flow,
    /// opens a browser, listens on a local redirect URI, exchanges the code
    /// for an access/refresh token pair, and returns the result.
    /// </summary>
    Task<DrofusAuthResult> AcquireTokenAsync(DrofusAuthSettings settings, CancellationToken cancellationToken = default);

    /// <summary>
    /// Silently refresh an existing token if possible (OAuth2 refresh_token grant).
    /// For API-key mode this is a no-op — returns the same token unchanged.
    /// </summary>
    Task<DrofusAuthResult> RefreshTokenAsync(DrofusAuthToken existingToken, DrofusAuthSettings settings, CancellationToken cancellationToken = default);
}
