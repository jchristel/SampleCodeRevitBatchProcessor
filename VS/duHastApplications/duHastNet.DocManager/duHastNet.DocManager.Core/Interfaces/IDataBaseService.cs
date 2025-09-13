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

using SQLite;

namespace duHastNet.DocManager.Core.Interfaces;

/// <summary>
/// Interface for database connection and management using sqlite-net-pcl
/// </summary>
public interface IDatabaseService : IDisposable
{
    /// <summary>
    /// Gets the current database connection
    /// </summary>
    SQLiteAsyncConnection Connection { get; }

    /// <summary>
    /// Gets whether the database is initialized and connected
    /// </summary>
    bool IsInitialized { get; }

    /// <summary>
    /// Gets the current database file path
    /// </summary>
    string? DatabasePath { get; }

    /// <summary>
    /// Initializes the database with the specified file path.
    /// Creates directory structure if needed and establishes connection.
    /// </summary>
    /// <param name="databasePath">Path to the SQLite database file</param>
    Task InitializeAsync(string databasePath);

    /// <summary>
    /// Creates all required tables (Revisions, Documents, CustomProperties).
    /// Uses sqlite-net-pcl attributes to automatically create tables, indexes, and constraints.
    /// </summary>
    Task CreateTablesAsync();

    /// <summary>
    /// Closes the database connection and cleans up resources
    /// </summary>
    Task CloseAsync();

    /// <summary>
    /// Performs a basic integrity check on the database.
    /// Returns true if the database appears to be functional.
    /// </summary>
    Task<bool> CheckDatabaseIntegrityAsync();
}