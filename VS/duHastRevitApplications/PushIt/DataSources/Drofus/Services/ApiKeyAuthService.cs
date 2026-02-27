// BSD License - Copyright 2025, Jan Christel

using System.Net;
using System.Net.Http.Headers;
using duHastNet.PushIt.DataSources.Drofus.Interfaces;
using duHastNet.PushIt.DataSources.Drofus.Models;

namespace duHastNet.PushIt.DataSources.Drofus.Services;

/// <summary>
/// PoC implementation of IDrofusAuthService using the drofus API-key scheme.
///
/// The API-key is sent as:  Authorization: Reference {key}
/// A lightweight validation call is made to confirm the key, region, database,
/// and project number are correct before returning a usable DrofusAuthToken.
///
/// Limitations (by design for PoC):
///  - Read-only access only
///  - One key = one project
///  - Keys do not expire; RefreshToken is a no-op
/// </summary>
public sealed class ApiKeyAuthService : IDrofusAuthService, IDisposable
{
    private readonly HttpClient _httpClient;
    private readonly bool _ownsHttpClient;

    /// <param name="httpClient">
    /// Optionally inject an existing HttpClient (useful for unit tests with a mock handler).
    /// When null, a new instance is created and owned by this service.
    /// </param>
    public ApiKeyAuthService(HttpClient? httpClient = null)
    {
        if (httpClient is null)
        {
            _httpClient = new HttpClient { Timeout = TimeSpan.FromSeconds(15) };
            _ownsHttpClient = true;
        }
        else
        {
            _httpClient = httpClient;
            _ownsHttpClient = false;
        }
    }

    /// <inheritdoc />
    public async Task<DrofusAuthResult> AcquireTokenAsync(
        DrofusAuthSettings settings,
        CancellationToken cancellationToken = default)
    {
        // --- Guard: must be API-key mode ---------------------------------------
        if (settings.AuthMode != DrofusAuthMode.ApiKey)
            return DrofusAuthResult.Fail(
                $"ApiKeyAuthService only handles '{nameof(DrofusAuthMode.ApiKey)}' mode. " +
                $"Received '{settings.AuthMode}'. Use BearerAuthService for OAuth2.");

        if (string.IsNullOrWhiteSpace(settings.ApiKey))
            return DrofusAuthResult.Fail("ApiKey is required but was not provided.");

        if (string.IsNullOrWhiteSpace(settings.DatabaseId))
            return DrofusAuthResult.Fail("DatabaseId is required (e.g. 'akl-test').");

        if (string.IsNullOrWhiteSpace(settings.ProjectNumber))
            return DrofusAuthResult.Fail("ProjectNumber is required (e.g. '01').");

        // --- Live validation ---------------------------------------------------
        var validationError = await TryValidateKeyAsync(settings, cancellationToken);
        if (validationError is not null)
            return DrofusAuthResult.Fail(validationError);

        // --- Wrap in a usable token -------------------------------------------
        return DrofusAuthResult.Ok(new DrofusAuthToken
        {
            AuthMode = DrofusAuthMode.ApiKey,
            ApiKey   = settings.ApiKey
        });
    }

    /// <inheritdoc />
    /// <remarks>
    /// API-keys do not expire; no server call is made.
    /// The existing token is validated locally and returned unchanged.
    /// </remarks>
    public Task<DrofusAuthResult> RefreshTokenAsync(
        DrofusAuthToken existingToken,
        DrofusAuthSettings settings,
        CancellationToken cancellationToken = default)
    {
        if (existingToken.AuthMode != DrofusAuthMode.ApiKey)
            return Task.FromResult(
                DrofusAuthResult.Fail("RefreshToken called with a non-API-key token."));

        return existingToken.IsUsable
            ? Task.FromResult(DrofusAuthResult.Ok(existingToken))
            : Task.FromResult(DrofusAuthResult.Fail("Existing token is not usable."));
    }

    // -------------------------------------------------------------------------
    // Private helpers
    // -------------------------------------------------------------------------

    /// <summary>
    /// Makes a minimal GET to the rooms endpoint with $top=1 to confirm the key,
    /// database, and project number are valid.
    /// Returns null on success, or an error message string on failure.
    /// </summary>
    private async Task<string?> TryValidateKeyAsync(
        DrofusAuthSettings settings,
        CancellationToken cancellationToken)
    {
        // GET /api/{database}/{project}/rooms?$top=1
        var url = $"{settings.BaseUrl}/api/{Uri.EscapeDataString(settings.DatabaseId)}" +
                  $"/{Uri.EscapeDataString(settings.ProjectNumber)}/rooms?$top=1";

        using var request = new HttpRequestMessage(HttpMethod.Get, url);
        request.Headers.Authorization =
            new AuthenticationHeaderValue("Reference", settings.ApiKey);
        request.Headers.Accept.Add(
            new MediaTypeWithQualityHeaderValue("application/json"));

        HttpResponseMessage response;
        try
        {
            response = await _httpClient.SendAsync(request, cancellationToken);
        }
        catch (HttpRequestException ex)
        {
            return $"Network error contacting '{settings.BaseUrl}': {ex.Message}";
        }
        catch (TaskCanceledException)
        {
            return "Request timed out while validating the drofus API-key.";
        }

        // Any 2xx means the key, database, and project are all accepted
        if (response.IsSuccessStatusCode)
            return null;

        return response.StatusCode switch
        {
            HttpStatusCode.Unauthorized =>
                "The API-key was rejected (401 Unauthorized). " +
                "Confirm the key is correct and was generated for this project.",

            HttpStatusCode.Forbidden =>
                "Access denied (403 Forbidden). " +
                "The key's user may not have read permission on this project.",

            HttpStatusCode.NotFound =>
                $"Project not found (404). Verify DatabaseId='{settings.DatabaseId}' " +
                $"and ProjectNumber='{settings.ProjectNumber}' are correct.",

            _ =>
                $"Unexpected response from drofus: " +
                $"{(int)response.StatusCode} {response.ReasonPhrase}."
        };
    }

    public void Dispose()
    {
        if (_ownsHttpClient)
            _httpClient.Dispose();
    }
}
