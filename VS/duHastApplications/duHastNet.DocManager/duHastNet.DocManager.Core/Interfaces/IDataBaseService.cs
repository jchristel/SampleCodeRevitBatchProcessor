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
/// Interface for database connection and management using sqlite-net-pcl.
/// Provides both synchronous and asynchronous database operations.
/// </summary>
public interface IDatabaseService : IDisposable
{
    /// <summary>
    /// Gets the current asynchronous database connection
    /// </summary>
    SQLiteAsyncConnection Connection { get; }

    /// <summary>
    /// Gets the current synchronous database connection
    /// </summary>
    SQLiteConnection SyncConnection { get; }

    /// <summary>
    /// Gets whether the database is initialized and connected
    /// </summary>
    bool IsInitialized { get; }

    /// <summary>
    /// Gets the current database file path
    /// </summary>
    string? DatabasePath { get; }

    #region Async Methods

    /// <summary>
    /// Initializes the database with the specified file path (async version).
    /// Creates directory structure if needed and establishes connection.
    /// </summary>
    /// <param name="databasePath">Path to the SQLite database file</param>
    Task InitializeAsync(string databasePath);

    /// <summary>
    /// Creates all required tables (Revisions, Documents, CustomProperties) (async version).
    /// Uses sqlite-net-pcl attributes to automatically create tables, indexes, and constraints.
    /// </summary>
    Task CreateTablesAsync();

    /// <summary>
    /// Closes the database connection and cleans up resources (async version)
    /// </summary>
    Task CloseAsync();

    /// <summary>
    /// Performs a basic integrity check on the database (async version).
    /// Returns true if the database appears to be functional.
    /// </summary>
    Task<bool> CheckDatabaseIntegrityAsync();

    /// <summary>
    /// Returns the current data_version pragma value for this connection.
    /// The value increments whenever any connection writes to the database,
    /// making it suitable for detecting external changes via polling.
    /// </summary>
    Task<int> GetDataVersionAsync();

    #endregion

    #region Sync Methods

    /// <summary>
    /// Initializes the database with the specified file path (sync version).
    /// Creates directory structure if needed and establishes connection.
    /// </summary>
    /// <param name="databasePath">Path to the SQLite database file</param>
    void Initialize(string databasePath);

    /// <summary>
    /// Creates all required tables (Revisions, Documents, CustomProperties) (sync version).
    /// Uses sqlite-net-pcl attributes to automatically create tables, indexes, and constraints.
    /// </summary>
    void CreateTables();

    /// <summary>
    /// Closes the database connection and cleans up resources (sync version)
    /// </summary>
    void Close();

    /// <summary>
    /// Performs a basic integrity check on the database (sync version).
    /// Returns true if the database appears to be functional.
    /// </summary>
    bool CheckDatabaseIntegrity();

    /// <summary>
    /// Returns the current data_version pragma value for this connection.
    /// The value increments whenever any connection writes to the database,
    /// making it suitable for detecting external changes via polling.
    /// </summary>
    int GetDataVersion();

    #endregion
}
