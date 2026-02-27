// BSD License - Copyright 2025, Jan Christel

using duHastNet.PushIt.DataSources.Drofus.Interfaces;
using duHastNet.PushIt.DataSources.Drofus.Models;

namespace duHastNet.PushIt.DataSources.Drofus.Services;

/// <summary>
/// STUB - not yet implemented.
///
/// Future OAuth2 Authorization Code + PKCE flow for drofus Bearer tokens.
///
/// Pre-requisites before this can be built:
///  1. Contact support@drofus.com to register an OAuth2 client application.
///     Provide the desired redirect_uri (e.g. http://127.0.0.1:5678/callback)
///     and optionally a post_logout_redirect_uri.
///  2. Receive a client_id, authorization endpoint, and token endpoint from drofus.
///  3. Populate OAuthClientId, OAuthAuthorizationEndpoint, and OAuthTokenEndpoint
///     in DrofusAuthSettings.
///
/// Planned implementation steps:
///  1. Generate a PKCE code_verifier and code_challenge (S256).
///  2. Build the authorization URL with code_challenge, state, scope, redirect_uri.
///  3. Open the URL in the system browser (Process.Start).
///  4. Start a local HttpListener on 127.0.0.1:{OAuthLocalCallbackPort}.
///  5. Wait for the browser callback containing "code" and "state" query params.
///  6. Verify the returned state matches the generated state (CSRF guard).
///  7. POST to token endpoint: grant_type=authorization_code, code, code_verifier,
///     redirect_uri, client_id.
///  8. Parse access_token, refresh_token, expires_in from the JSON response.
///  9. Wrap in DrofusAuthToken and return DrofusAuthResult.Ok(token).
///
/// RefreshTokenAsync will use grant_type=refresh_token against the token endpoint.
/// </summary>
public sealed class BearerAuthService : IDrofusAuthService
{
    public Task<DrofusAuthResult> AcquireTokenAsync(
        DrofusAuthSettings settings,
        CancellationToken cancellationToken = default)
    {
        // TODO: implement Authorization Code + PKCE flow (see class summary above)
        return Task.FromResult(DrofusAuthResult.Fail(
            "OAuth2 Bearer authentication is not yet implemented. " +
            "Use ApiKeyAuthService for the PoC, or contact support@drofus.com " +
            "to register an OAuth2 client before implementing this service."));
    }

    public Task<DrofusAuthResult> RefreshTokenAsync(
        DrofusAuthToken existingToken,
        DrofusAuthSettings settings,
        CancellationToken cancellationToken = default)
    {
        // TODO: implement refresh_token grant
        return Task.FromResult(DrofusAuthResult.Fail(
            "OAuth2 token refresh is not yet implemented."));
    }
}
