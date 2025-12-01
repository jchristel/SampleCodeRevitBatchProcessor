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

using duHastNet.DocManager.Core.Interfaces;
using duHastNet.DocManager.Core.Models.Results;
using Newtonsoft.Json;

namespace duHastNet.DocManager.Core.Services;

/// <summary>
/// Service for saving and loading application settings as JSON files
/// </summary>
public class SettingsService : ISettingsService
{
    private const string SettingsFolderName = "duHast";
    private const string BackupExtension = ".bak";
    private const string TempExtension = ".tmp";

    private readonly JsonSerializerSettings _jsonSettings;

    /// <summary>
    /// Gets the full path to the settings directory
    /// Default: %LocalAppData%/duHast
    /// Can be overridden via constructor parameter for shared settings scenarios
    /// </summary>
    public string SettingsDirectory { get; }

    /// <summary>
    /// Initializes a new instance of SettingsService using default settings location
    /// Default location: %LocalAppData%/duHast
    /// </summary>
    public SettingsService()
    {
        // Initialize settings directory path - use default location
        var localAppData = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
        SettingsDirectory = Path.Combine(localAppData, SettingsFolderName);

        // Configure JSON serialization settings
        _jsonSettings = new JsonSerializerSettings
        {
            Formatting = Formatting.Indented,
            NullValueHandling = NullValueHandling.Ignore,
            ReferenceLoopHandling = ReferenceLoopHandling.Ignore,
            TypeNameHandling = TypeNameHandling.Auto,
            PreserveReferencesHandling = PreserveReferencesHandling.Objects
        };

        // Ensure settings directory exists
        EnsureSettingsDirectoryExists();
    }

    /// <summary>
    /// Initializes a new instance of SettingsService with custom settings path
    /// </summary>
    /// <param name="customSettingsPath">Custom path for settings directory. 
    /// Uses the specified path directly without appending "duHast" subfolder.
    /// </param>
    public SettingsService(string customSettingsPath)
    {
        if (string.IsNullOrWhiteSpace(customSettingsPath))
        {
            throw new ArgumentException("Custom settings path cannot be null or empty. Use parameterless constructor for default location.", nameof(customSettingsPath));
        }

        // Use custom path directly
        SettingsDirectory = customSettingsPath;

        // Configure JSON serialization settings
        _jsonSettings = new JsonSerializerSettings
        {
            Formatting = Formatting.Indented,
            NullValueHandling = NullValueHandling.Ignore,
            ReferenceLoopHandling = ReferenceLoopHandling.Ignore,
            TypeNameHandling = TypeNameHandling.Auto,
            PreserveReferencesHandling = PreserveReferencesHandling.Objects
        };

        // Ensure settings directory exists
        EnsureSettingsDirectoryExists();
    }

    /// <summary>
    /// Saves an object to a JSON file
    /// </summary>
    /// <typeparam name="T">Type of object to save</typeparam>
    /// <param name="obj">Object to serialize and save</param>
    /// <param name="filename">Filename (without path) to save to</param>
    /// <returns>Result indicating success or failure</returns>
    public async Task<ResultBase> SaveAsync<T>(T obj, string filename) where T : class
    {
        var result = new SaveResult();

        try
        {
            if (obj == null)
            {
                result.IsSaveSuccessful = false;
                result.AddError("Cannot save null object");
                result.Message = "Save failed: null object";
                return result;
            }

            if (string.IsNullOrWhiteSpace(filename))
            {
                result.IsSaveSuccessful = false;
                result.AddError("Filename cannot be null or empty");
                result.Message = "Save failed: invalid filename";
                return result;
            }

            var filePath = GetSettingsPath(filename);
            var tempPath = filePath + TempExtension;
            var backupPath = filePath + BackupExtension;

            // Create backup of existing file if it exists
            if (File.Exists(filePath))
            {
                try
                {
                    File.Copy(filePath, backupPath, true);
                }
                catch (Exception ex)
                {
                    result.AddWarning($"Failed to create backup: {ex.Message}");
                }
            }

            // Serialize to JSON
            string json;
            try
            {
                json = JsonConvert.SerializeObject(obj, _jsonSettings);
            }
            catch (Exception ex)
            {
                result.IsSaveSuccessful = false;
                result.AddError($"Serialization failed: {ex.Message}");
                result.Message = "Save failed: serialization error";
                return result;
            }

            // Write to temporary file first
            try
            {
                await File.WriteAllTextAsync(tempPath, json);
            }
            catch (Exception ex)
            {
                result.IsSaveSuccessful = false;
                result.AddError($"Failed to write temporary file: {ex.Message}");
                result.Message = "Save failed: write error";
                return result;
            }

            // Replace original file with temporary file
            try
            {
                File.Move(tempPath, filePath, true);
            }
            catch (Exception ex)
            {
                result.IsSaveSuccessful = false;
                result.AddError($"Failed to replace original file: {ex.Message}");
                result.Message = "Save failed: file replacement error";

                // Try to clean up temporary file
                try
                {
                    if (File.Exists(tempPath))
                    {
                        File.Delete(tempPath);
                    }
                }
                catch
                {
                    // Ignore cleanup errors
                }

                return result;
            }

            // Success - clean up temporary file if it still exists
            try
            {
                if (File.Exists(tempPath))
                {
                    File.Delete(tempPath);
                }
            }
            catch
            {
                // Ignore cleanup errors
            }

            result.IsSaveSuccessful = true;
            result.FilePath = filePath;
            result.Message = $"Settings saved successfully to {filename}";
            return result;
        }
        catch (Exception ex)
        {
            result.IsSaveSuccessful = false;
            result.AddError($"Unexpected error during save: {ex.Message}");
            result.Message = "Save failed: unexpected error";
            return result;
        }
    }

    /// <summary>
    /// Loads an object from a JSON file
    /// </summary>
    /// <typeparam name="T">Type of object to load</typeparam>
    /// <param name="filename">Filename (without path) to load from</param>
    /// <returns>Loaded object, or null if file doesn't exist or cannot be loaded</returns>
    public async Task<T?> LoadAsync<T>(string filename) where T : class
    {
        try
        {
            if (string.IsNullOrWhiteSpace(filename))
            {
                return null;
            }

            var filePath = GetSettingsPath(filename);

            // Try to load from main file
            if (File.Exists(filePath))
            {
                try
                {
                    var json = await File.ReadAllTextAsync(filePath);
                    var obj = JsonConvert.DeserializeObject<T>(json, _jsonSettings);
                    return obj;
                }
                catch (Exception ex)
                {
                    // Log error (in production, use proper logging)
                    System.Diagnostics.Debug.WriteLine($"Failed to load from main file: {ex.Message}");

                    // Try backup file
                    var backupPath = filePath + BackupExtension;
                    if (File.Exists(backupPath))
                    {
                        try
                        {
                            var json = await File.ReadAllTextAsync(backupPath);
                            var obj = JsonConvert.DeserializeObject<T>(json, _jsonSettings);
                            return obj;
                        }
                        catch (Exception backupEx)
                        {
                            // Log error
                            System.Diagnostics.Debug.WriteLine($"Failed to load from backup file: {backupEx.Message}");
                        }
                    }
                }
            }

            // File doesn't exist or both main and backup failed - return null
            return null;
        }
        catch (Exception ex)
        {
            // Log error
            System.Diagnostics.Debug.WriteLine($"Unexpected error during load: {ex.Message}");
            return null;
        }
    }

    /// <summary>
    /// Gets the full path for a settings file
    /// </summary>
    /// <param name="filename">Filename (without path)</param>
    /// <returns>Full path to the settings file</returns>
    public string GetSettingsPath(string filename)
    {
        return Path.Combine(SettingsDirectory, filename);
    }

    /// <summary>
    /// Checks if a settings file exists
    /// </summary>
    /// <param name="filename">Filename (without path) to check</param>
    /// <returns>True if the file exists, false otherwise</returns>
    public bool SettingsFileExists(string filename)
    {
        var filePath = GetSettingsPath(filename);
        return File.Exists(filePath);
    }

    /// <summary>
    /// Ensures the settings directory exists, creating it if necessary
    /// </summary>
    private void EnsureSettingsDirectoryExists()
    {
        try
        {
            if (!Directory.Exists(SettingsDirectory))
            {
                Directory.CreateDirectory(SettingsDirectory);
            }
        }
        catch (Exception ex)
        {
            // Log error (in production, use proper logging)
            System.Diagnostics.Debug.WriteLine($"Failed to create settings directory: {ex.Message}");
            throw;
        }
    }
}
