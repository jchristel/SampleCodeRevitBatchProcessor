//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2025, Jan Christel
// All rights reserved.

// Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

// - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
// - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
// - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
//
// This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
// In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
// or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
//
//
//

using System;

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
