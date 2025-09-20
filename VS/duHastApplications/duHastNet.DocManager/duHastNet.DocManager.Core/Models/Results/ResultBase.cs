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
/// Base class for operation results
/// </summary>
public abstract class ResultBase
{
    /// <summary>
    /// Indicates whether the operation was successful - must be implemented by derived classes
    /// </summary>
    public abstract bool Success { get; set; }

    /// <summary>
    /// Primary message describing the operation result
    /// </summary>
    public string Message { get; set; } = string.Empty;

    /// <summary>
    /// List of error messages that occurred during the operation
    /// </summary>
    public List<string> Errors { get; set; } = new();

    /// <summary>
    /// List of warning messages that occurred during the operation
    /// </summary>
    public List<string> Warnings { get; set; } = new();

    /// <summary>
    /// Adds an error to the error collection
    /// </summary>
    /// <param name="error">Error message to add</param>
    public void AddError(string error)
    {
        Errors.Add(error);
    }

    /// <summary>
    /// Adds a warning to the warning collection
    /// </summary>
    /// <param name="warning">Warning message to add</param>
    public void AddWarning(string warning)
    {
        Warnings.Add(warning);
    }

    /// <summary>
    /// Gets whether the operation has any errors
    /// </summary>
    public bool HasErrors => Errors.Count > 0;

    /// <summary>
    /// Gets whether the operation has any warnings
    /// </summary>
    public bool HasWarnings => Warnings.Count > 0;
}