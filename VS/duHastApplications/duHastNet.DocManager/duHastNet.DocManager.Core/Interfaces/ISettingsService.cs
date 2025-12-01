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

using duHastNet.DocManager.Core.Models.Results;

namespace duHastNet.DocManager.Core.Interfaces;

/// <summary>
/// Interface for saving and loading application settings as JSON files
/// </summary>
public interface ISettingsService
{
    /// <summary>
    /// Gets the full path to the settings directory
    /// Default: %LocalAppData%/duHast
    /// Can be overridden via constructor parameter for shared settings scenarios
    /// </summary>
    string SettingsDirectory { get; }

    /// <summary>
    /// Saves an object to a JSON file
    /// </summary>
    /// <typeparam name="T">Type of object to save</typeparam>
    /// <param name="obj">Object to serialize and save</param>
    /// <param name="filename">Filename (without path) to save to</param>
    /// <returns>Result indicating success or failure</returns>
    Task<ResultBase> SaveAsync<T>(T obj, string filename) where T : class;

    /// <summary>
    /// Loads an object from a JSON file
    /// </summary>
    /// <typeparam name="T">Type of object to load</typeparam>
    /// <param name="filename">Filename (without path) to load from</param>
    /// <returns>Loaded object, or null if file doesn't exist or cannot be loaded</returns>
    Task<T?> LoadAsync<T>(string filename) where T : class;

    /// <summary>
    /// Gets the full path for a settings file
    /// </summary>
    /// <param name="filename">Filename (without path)</param>
    /// <returns>Full path to the settings file</returns>
    string GetSettingsPath(string filename);

    /// <summary>
    /// Checks if a settings file exists
    /// </summary>
    /// <param name="filename">Filename (without path) to check</param>
    /// <returns>True if the file exists, false otherwise</returns>
    bool SettingsFileExists(string filename);
}
