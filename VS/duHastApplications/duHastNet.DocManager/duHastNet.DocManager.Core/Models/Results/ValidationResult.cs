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


/// <summary>
/// Validation result for document operations
/// </summary>
namespace duHastNet.DocManager.Core.Models.Results;

public class ValidationResult : ResultBase
{
    /// <summary>
    /// Indicates whether the validation passed
    /// </summary>
    public bool IsValid { get; set; }

    /// <summary>
    /// Implementation of abstract Success property - maps to IsValid for validation context
    /// </summary>
    public override bool Success
    {
        get => IsValid;
        set => IsValid = value;
    }

    /// <summary>
    /// Initializes a new instance of ValidationResult with default message
    /// </summary>
    public ValidationResult()
    {
        Message = "Validation completed";
    }

    /// <summary>
    /// Creates a successful validation result
    /// </summary>
    /// <returns>ValidationResult with IsValid = true</returns>
    public static ValidationResult CreateSuccess()
    {
        return new ValidationResult { IsValid = true };
    }

    /// <summary>
    /// Creates a failed validation result with error messages
    /// </summary>
    /// <param name="errors">Error messages</param>
    /// <returns>ValidationResult with IsValid = false</returns>
    public static ValidationResult CreateFailure(params string[] errors)
    {
        var result = new ValidationResult { IsValid = false };

        foreach (var error in errors)
        {
            result.AddError(error);
        }

        return result;
    }
}
