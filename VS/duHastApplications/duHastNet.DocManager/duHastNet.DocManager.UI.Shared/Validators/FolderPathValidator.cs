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


using System.ComponentModel.DataAnnotations;
using System.IO;
using System.Linq;

namespace duHastNet.DocManager.UI.Shared.Validators
{
    /// <summary>
    /// Custom validator for folder path validation
    /// Used with INotifyDataErrorInfo validation system
    /// </summary>
    public static class FolderPathValidator
    {
        /// <summary>
        /// Validates that a folder path exists and is accessible
        /// </summary>
        /// <param name="path">The folder path to validate</param>
        /// <param name="context">Validation context</param>
        /// <returns>ValidationResult indicating success or failure with error message</returns>
        public static ValidationResult? ValidateFolderExists(string? path, ValidationContext context)
        {
            // Empty/null paths are valid (optional fields)
            if (string.IsNullOrWhiteSpace(path))
            {
                return new ValidationResult("Path can not be empty");
            }

            // Check for invalid path characters
            var invalidChars = Path.GetInvalidPathChars();
            if (path.Any(c => invalidChars.Contains(c)))
            {
                return new ValidationResult("Path contains invalid characters");
            }

            try
            {
                // Check if directory exists
                if (!Directory.Exists(path))
                {
                    return new ValidationResult("Folder does not exist");
                }

                return ValidationResult.Success;
            }
            catch (Exception ex)
            {
                // Catch any other path-related errors (security, etc.)
                return new ValidationResult($"Invalid path: {ex.Message}");
            }
        }
    }
}
