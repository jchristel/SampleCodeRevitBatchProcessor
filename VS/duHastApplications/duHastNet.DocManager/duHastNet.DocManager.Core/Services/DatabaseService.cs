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
using duHastNet.DocManager.Core.Interfaces;
using duHastNet.DocManager.Core.Models;

namespace duHastNet.DocManager.Core.Services;

/// <summary>
/// SQLite database service implementation using sqlite-net-pcl
/// </summary>
public class DatabaseService : IDatabaseService
{
    private SQLiteAsyncConnection? _connection;

    public SQLiteAsyncConnection Connection
    {
        get => _connection ?? throw new InvalidOperationException("Database not initialized. Call InitializeAsync first.");
    }

    public bool IsInitialized => _connection != null;
    public string? DatabasePath { get; private set; }

    public DatabaseService()
    {
    }

    public async Task InitializeAsync(string databasePath)
    {
        // Ensure directory exists
        var directory = Path.GetDirectoryName(databasePath);
        if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
        {
            Directory.CreateDirectory(directory);
        }

        // Create connection with proper configuration
        var connectionString = new SQLiteConnectionString(databasePath,
            storeDateTimeAsTicks: false,    // Store as ISO8601 strings
            openFlags: SQLiteOpenFlags.ReadWrite | SQLiteOpenFlags.Create,
            key: null);

        _connection = new SQLiteAsyncConnection(connectionString);
        DatabasePath = databasePath;

        // Enable foreign keys and other pragmas
        await _connection.ExecuteAsync("PRAGMA foreign_keys = ON");
        await _connection.ExecuteAsync("PRAGMA journal_mode = WAL");
        await _connection.ExecuteAsync("PRAGMA synchronous = NORMAL");
        await _connection.ExecuteAsync("PRAGMA cache_size = 10000");
        await _connection.ExecuteAsync("PRAGMA temp_store = MEMORY");

        // Create tables and indexes
        await CreateTablesAsync();
        await CreateIndexesAsync();
    }

    public async Task CreateTablesAsync()
    {
        await Connection.CreateTableAsync<Revision>();
        await Connection.CreateTableAsync<Document>();
        await Connection.CreateTableAsync<CustomProperty>();
    }

    public async Task CreateIndexesAsync()
    {
        // Additional composite indexes for performance
        await Connection.ExecuteAsync(@"
            CREATE INDEX IF NOT EXISTS IX_Documents_Number_Revision 
            ON Documents (Number, Revision)");

        await Connection.ExecuteAsync(@"
            CREATE INDEX IF NOT EXISTS IX_Documents_RevisionId_Number 
            ON Documents (RevisionId, Number)");

        await Connection.ExecuteAsync(@"
            CREATE INDEX IF NOT EXISTS IX_Revisions_Date 
            ON Revisions (RevisionDate)");

        await Connection.ExecuteAsync(@"
            CREATE INDEX IF NOT EXISTS IX_CustomProperties_DocumentId_PropertyName 
            ON CustomProperties (DocumentId, PropertyName)");

        await Connection.ExecuteAsync(@"
            CREATE INDEX IF NOT EXISTS IX_CustomProperties_PropertyName_PropertyValue 
            ON CustomProperties (PropertyName, PropertyValue)");
    }

    public async Task CloseAsync()
    {
        if (_connection != null)
        {
            await _connection.CloseAsync();
            _connection = null;
            DatabasePath = null;
        }
    }

    public async Task OptimizeDatabaseAsync()
    {
        await Connection.ExecuteAsync("VACUUM");
        await Connection.ExecuteAsync("ANALYZE");
    }

    public async Task<bool> CheckDatabaseIntegrityAsync()
    {
        var result = await Connection.QueryAsync<IntegrityCheckResult>("PRAGMA integrity_check");
        return result.Count == 1 && result[0].Result == "ok";
    }

    /// <summary>
    /// Helper class for PRAGMA integrity_check result
    /// </summary>
    private class IntegrityCheckResult
    {
        public string Result { get; set; } = string.Empty;
    }

    public async Task<int> ExecuteAsync(string sql, params object[] args)
    {
        return await Connection.ExecuteAsync(sql, args);
    }

    public async Task<List<T>> QueryAsync<T>(string sql, params object[] args) where T : new()
    {
        return await Connection.QueryAsync<T>(sql, args);
    }

    public void Dispose()
    {
        CloseAsync().Wait();
    }
}