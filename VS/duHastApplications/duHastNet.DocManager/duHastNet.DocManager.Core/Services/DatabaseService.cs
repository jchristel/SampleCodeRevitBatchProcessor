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
using duHastNet.DocManager.Core.Models.Database;

namespace duHastNet.DocManager.Core.Services;

public class DatabaseService : IDatabaseService
{
    private SQLiteAsyncConnection? _connection;
    private SQLiteConnection? _syncConnection;

    public SQLiteAsyncConnection Connection
    {
        get => _connection ?? throw new InvalidOperationException("Async database connection not initialized. Call InitializeAsync first.");
    }

    public SQLiteConnection SyncConnection
    {
        get => _syncConnection ?? throw new InvalidOperationException("Sync database connection not initialized. Call Initialize first.");
    }

    public bool IsInitialized => _connection != null || _syncConnection != null;
    public string? DatabasePath { get; private set; }

    private bool _disposed = false;

    #region Async Methods

    public async Task InitializeAsync(string databasePath)
    {
        // Input validation - this should catch null before SQLite sees it
        ArgumentNullException.ThrowIfNull(databasePath);

        if (string.IsNullOrEmpty(databasePath))
        {
            throw new ArgumentException("Database path cannot be null or empty.", nameof(databasePath));
        }

        if (string.IsNullOrWhiteSpace(databasePath))
        {
            throw new ArgumentException("Database path cannot be whitespace only.", nameof(databasePath));
        }

        // Close existing async connection if reinitializing
        if (_connection != null)
        {
            await _connection.CloseAsync();
            _connection = null;
        }

        // Ensure directory exists
        var directory = Path.GetDirectoryName(databasePath);
        if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
        {
            Directory.CreateDirectory(directory);
        }

        // Create async connection only
        _connection = new SQLiteAsyncConnection(databasePath);
        DatabasePath = databasePath;

        // Create tables
        await CreateTablesAsync();
    }

    public async Task CreateTablesAsync()
    {
        await Connection.CreateTablesAsync<Revision, Document, CustomFieldDefinition, CustomProperty>();
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

    public async Task<bool> CheckDatabaseIntegrityAsync()
    {
        try
        {
            // Use ExecuteScalarAsync instead of QueryAsync<dynamic>
            // This just tests that we can execute a simple query on the database
            var result = await Connection.ExecuteScalarAsync<string>(
                "SELECT name FROM sqlite_master LIMIT 1");

            // If we get here without exception, the database connection is working
            // The result can be null if no tables exist, but that's still a valid database state
            return true;
        }
        catch
        {
            return false;
        }
    }

    #endregion

    #region Sync Methods

    public void Initialize(string databasePath)
    {
        // Input validation - this should catch null before SQLite sees it
        ArgumentNullException.ThrowIfNull(databasePath);

        if (string.IsNullOrEmpty(databasePath))
        {
            throw new ArgumentException("Database path cannot be null or empty.", nameof(databasePath));
        }

        if (string.IsNullOrWhiteSpace(databasePath))
        {
            throw new ArgumentException("Database path cannot be whitespace only.", nameof(databasePath));
        }

        // Close existing sync connection if reinitializing
        if (_syncConnection != null)
        {
            _syncConnection.Close();
            _syncConnection = null;
        }

        // Ensure directory exists
        var directory = Path.GetDirectoryName(databasePath);
        if (!string.IsNullOrEmpty(directory) && !Directory.Exists(directory))
        {
            Directory.CreateDirectory(directory);
        }

        // Create sync connection only
        _syncConnection = new SQLiteConnection(databasePath);
        DatabasePath = databasePath;

        // Create tables
        CreateTables();
    }

    public void CreateTables()
    {
        SyncConnection.CreateTable<Revision>();
        SyncConnection.CreateTable<Document>();
        SyncConnection.CreateTable<CustomFieldDefinition>();
        SyncConnection.CreateTable<CustomProperty>();
    }

    public void Close()
    {
        if (_syncConnection != null)
        {
            _syncConnection.Close();
            _syncConnection = null;
            DatabasePath = null;
        }
    }

    public bool CheckDatabaseIntegrity()
    {
        try
        {
            // Execute a simple query to test the database connection
            var result = SyncConnection.ExecuteScalar<string>(
                "SELECT name FROM sqlite_master LIMIT 1");

            // If we get here without exception, the database connection is working
            // The result can be null if no tables exist, but that's still a valid database state
            return true;
        }
        catch
        {
            return false;
        }
    }

    #endregion

    #region IDisposable

    protected virtual void Dispose(bool disposing)
    {
        if (!_disposed)
        {
            if (disposing)
            {
                // Dispose managed resources
                // Close whichever connection is initialized
                if (_syncConnection != null)
                {
                    Close();
                }
                else if (_connection != null)
                {
                    CloseAsync().Wait();
                }
            }
            _disposed = true;
        }
    }

    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }

    #endregion
}
