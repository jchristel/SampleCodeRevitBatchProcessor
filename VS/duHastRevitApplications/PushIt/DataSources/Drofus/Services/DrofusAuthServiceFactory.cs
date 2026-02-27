// BSD License - Copyright 2025, Jan Christel

using duHastNet.PushIt.DataSources.Drofus.Interfaces;
using duHastNet.PushIt.DataSources.Drofus.Models;

namespace duHastNet.PushIt.DataSources.Drofus.Services;

/// <summary>
/// Returns the correct IDrofusAuthService implementation for a given DrofusAuthMode.
/// Mirrors the DataSourceFactory pattern from the implementation guide.
/// </summary>
public static class DrofusAuthServiceFactory
{
    public static IDrofusAuthService Create(DrofusAuthMode mode, HttpClient? httpClient = null) =>
        mode switch
        {
            DrofusAuthMode.ApiKey  => new ApiKeyAuthService(httpClient),
            DrofusAuthMode.Bearer  => new BearerAuthService(),
            _                      => throw new NotSupportedException(
                                         $"Unknown DrofusAuthMode: '{mode}'.")
        };
}
