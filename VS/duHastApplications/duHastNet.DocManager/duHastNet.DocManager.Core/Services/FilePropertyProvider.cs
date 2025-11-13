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

namespace duHastNet.DocManager.Core.Services;

/// <summary>
/// Provides a centralized list of available file properties and their extraction logic
/// This is the single source of truth for file properties used in metadata mappings
/// </summary>
public static class FilePropertyProvider
{
    // Public constants for property names
    public const string PropertyFileName = "FileName";
    public const string PropertyFileNameWithoutExtension = "FileNameWithoutExtension";
    public const string PropertyExtension = "Extension";
    public const string PropertyFullPath = "FullPath";
    public const string PropertyDirectoryName = "DirectoryName";

    /// <summary>
    /// Gets the list of available file property names for UI dropdowns and validation
    /// These are the canonical names users will see in the UI
    /// </summary>
    /// <returns>List of file property names in display order</returns>
    public static List<string> GetAvailableFileProperties()
    {
        return new List<string>
        {
            PropertyFileName,
            PropertyFileNameWithoutExtension,
            PropertyExtension,
            PropertyFullPath,
            PropertyDirectoryName
        };
    }

    /// <summary>
    /// Extracts a file property value from a file path
    /// </summary>
    /// <param name="filePath">The full path to the file</param>
    /// <param name="propertyName">The file property name (case-insensitive)</param>
    /// <returns>The extracted property value, or empty string if property not found or path is null</returns>
    public static string GetFilePropertyValue(string? filePath, string propertyName)
    {
        if (string.IsNullOrWhiteSpace(filePath))
            return string.Empty;

        // Normalize property name to match canonical names, but be flexible with variations
        switch (propertyName.ToLowerInvariant().Replace(" ", ""))
        {
            // FileName - file name with extension
            case "filename":
            case "name":
                return Path.GetFileName(filePath);

            // FileNameWithoutExtension - file name without extension
            case "filenamewithoutextension":
            case "namewithoutextension":
                return Path.GetFileNameWithoutExtension(filePath);

            // Extension - file extension without the dot
            case "extension":
            case "fileextension":
            case "ext":
                var ext = Path.GetExtension(filePath);
                return string.IsNullOrEmpty(ext) ? string.Empty : ext.TrimStart('.');

            // FullPath - complete file path
            case "fullpath":
            case "filepath":
            case "path":
                return filePath;

            // DirectoryName - directory containing the file
            case "directoryname":
            case "directory":
            case "folder":
            case "foldername":
                return Path.GetDirectoryName(filePath) ?? string.Empty;

            default:
                // Property not recognized
                return string.Empty;
        }
    }

    /// <summary>
    /// Validates if a property name is a valid file property
    /// </summary>
    /// <param name="propertyName">The property name to validate</param>
    /// <returns>True if the property name is valid, false otherwise</returns>
    public static bool IsValidFileProperty(string? propertyName)
    {
        if (string.IsNullOrWhiteSpace(propertyName))
            return false;

        var availableProperties = GetAvailableFileProperties();
        return availableProperties.Any(p => 
            string.Equals(p, propertyName, StringComparison.OrdinalIgnoreCase));
    }

    /// <summary>
    /// Gets a description for a file property (for tooltips, help text, etc.)
    /// </summary>
    /// <param name="propertyName">The file property name</param>
    /// <returns>Description of what the property contains</returns>
    public static string GetFilePropertyDescription(string propertyName)
    {
        switch (propertyName.ToLowerInvariant().Replace(" ", ""))
        {
            case "filename":
                return "The file name including extension (e.g., 'Document-Rev-A.pdf')";
            
            case "filenamewithoutextension":
                return "The file name without extension (e.g., 'Document-Rev-A')";
            
            case "extension":
                return "The file extension without the dot (e.g., 'pdf')";
            
            case "fullpath":
                return "The complete file path (e.g., 'C:\\Incoming\\Document-Rev-A.pdf')";
            
            case "directoryname":
                return "The directory containing the file (e.g., 'C:\\Incoming')";
            
            default:
                return "File property";
        }
    }
}
