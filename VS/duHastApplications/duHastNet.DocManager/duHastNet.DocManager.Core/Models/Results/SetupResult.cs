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

namespace duHastNet.DocManager.Core.Models.Results;

/// <summary>
/// Result of database setup operation
/// </summary>
public class SetupResult : ResultBase
{
    /// <summary>
    /// Indicates whether the setup was successful
    /// </summary>
    public bool IsSetupSuccessful { get; set; }

    /// <summary>
    /// Path to the database file that was created or configured
    /// </summary>
    public string? DatabasePath { get; set; }

    /// <summary>
    /// Implementation of abstract Success property - maps to IsSetupSuccessful
    /// </summary>
    public override bool Success
    {
        get => IsSetupSuccessful;
        set => IsSetupSuccessful = value;
    }

    /// <summary>
    /// Initializes a new instance of SetupResult with default message
    /// </summary>
    public SetupResult()
    {
        Message = "Database setup completed successfully";
    }

    /// <summary>
    /// Creates a successful setup result
    /// </summary>
    /// <param name="databasePath">Path to the created database</param>
    /// <returns>SetupResult with IsSetupSuccessful = true</returns>
    public static SetupResult CreateSuccess(string databasePath)
    {
        return new SetupResult
        {
            IsSetupSuccessful = true,
            DatabasePath = databasePath
        };
    }

    /// <summary>
    /// Creates a failed setup result with error messages
    /// </summary>
    /// <param name="errors">Error messages</param>
    /// <returns>SetupResult with IsSetupSuccessful = false</returns>
    public static SetupResult CreateFailure(params string[] errors)
    {
        var result = new SetupResult { IsSetupSuccessful = false };

        foreach (var error in errors)
        {
            result.AddError(error);
        }

        return result;
    }
}