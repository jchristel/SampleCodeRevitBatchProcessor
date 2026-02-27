// BSD License - Copyright 2025, Jan Christel

namespace duHastNet.PushIt.DataSources.Drofus.Models;

/// <summary>
/// Result returned by any IDrofusAuthService method.
/// Mirrors the ResultBase / SetupResult pattern used elsewhere in the project.
/// </summary>
public class DrofusAuthResult
{
    public bool Success { get; private init; }
    public string? ErrorMessage { get; private init; }
    public DrofusAuthToken? Token { get; private init; }

    private DrofusAuthResult() { }

    public static DrofusAuthResult Ok(DrofusAuthToken token) =>
        new() { Success = true, Token = token };

    public static DrofusAuthResult Fail(string message) =>
        new() { Success = false, ErrorMessage = message };
}
