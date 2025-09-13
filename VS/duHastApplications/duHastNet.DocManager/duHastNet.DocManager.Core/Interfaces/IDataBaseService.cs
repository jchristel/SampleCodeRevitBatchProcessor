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

using SQLite;

namespace duHastNet.DocManager.Core.Interfaces;

/// <summary>
/// Interface for database connection and management
/// </summary>
public interface IDatabaseService
{
    /// <summary>
    /// Gets the current database connection
    /// </summary>
    SQLiteAsyncConnection Connection { get; }

    /// <summary>
    /// Initializes the database with the specified file path
    /// </summary>
    Task InitializeAsync(string databasePath);

    /// <summary>
    /// Creates all required tables (Revisions, Documents, CustomProperties)
    /// </summary>
    Task CreateTablesAsync();

    /// <summary>
    /// Creates additional indexes for performance
    /// </summary>
    Task CreateIndexesAsync();

    /// <summary>
    /// Closes the database connection
    /// </summary>
    Task CloseAsync();

    /// <summary>
    /// Checks if the database is initialized and connected
    /// </summary>
    bool IsInitialized { get; }

    /// <summary>
    /// Gets the current database file path
    /// </summary>
    string? DatabasePath { get; }

    /// <summary>
    /// Optimizes the database (VACUUM, ANALYZE)
    /// </summary>
    Task OptimizeDatabaseAsync();

    /// <summary>
    /// Checks database integrity
    /// </summary>
    Task<bool> CheckDatabaseIntegrityAsync();

    /// <summary>
    /// Executes a raw SQL command (for advanced operations)
    /// </summary>
    Task<int> ExecuteAsync(string sql, params object[] args);

    /// <summary>
    /// Executes a raw SQL query and returns results
    /// </summary>
    Task<List<T>> QueryAsync<T>(string sql, params object[] args) where T : new();
}