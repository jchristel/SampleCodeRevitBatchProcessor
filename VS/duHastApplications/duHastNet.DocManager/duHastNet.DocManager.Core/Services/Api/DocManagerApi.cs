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

using duHastNet.DocManager.Core.Interfaces;
using duHastNet.DocManager.Core.Models.Config;
using duHastNet.DocManager.Core.Models.Results;
using duHastNet.DocManager.Core.Services;
using duHastNet.DocManager.Core.Services.Repositories;

namespace duHastNet.DocManager.Core.Services.Api;

/// <summary>
/// Main API class for external integration (PyRevit, Revit Plugin, Standalone)
/// </summary>
public class DocManagerApi : IDisposable
{
    private IDatabaseService? _databaseService;
    private IUnitOfWork? _unitOfWork;
    private bool _disposed = false;

    #region Async Methods (for modern .NET usage)

    /// <summary>
    /// Sets up a new document database
    /// </summary>
    /// <param name="config">Database setup configuration</param>
    /// <returns>Setup result with success/failure information</returns>
    public async Task<SetupResult> SetupDatabaseAsync(DatabaseSetupConfig config)
    {
        try
        {
            // Validate input
            if (string.IsNullOrWhiteSpace(config.DatabasePath))
            {
                return SetupResult.CreateFailure("Database path is required");
            }

            // Check if file exists and handle overwrite
            if (File.Exists(config.DatabasePath) && !config.OverwriteExisting)
            {
                return SetupResult.CreateFailure($"Database file already exists: {config.DatabasePath}");
            }

            // Delete existing file if overwrite is enabled
            if (File.Exists(config.DatabasePath) && config.OverwriteExisting)
            {
                File.Delete(config.DatabasePath);
            }

            // Initialize database service
            _databaseService = new DatabaseService();
            await _databaseService.InitializeAsync(config.DatabasePath);

            // Verify database was created successfully
            if (!_databaseService.IsInitialized)
            {
                return SetupResult.CreateFailure("Failed to initialize database");
            }

            // Initialize unit of work
            _unitOfWork = new UnitOfWork(_databaseService.Connection);

            // Validate custom property names
            var invalidPropertyNames = ValidateCustomPropertyNames(config.CustomPropertyNames);

            var result = SetupResult.CreateSuccess(config.DatabasePath);

            if (invalidPropertyNames.Any())
            {
                foreach (var invalidName in invalidPropertyNames)
                {
                    result.AddWarning($"Invalid custom property name: {invalidName}");
                }
            }

            if (config.CustomPropertyNames.Any())
            {
                result.Message = $"Database setup completed successfully with {config.CustomPropertyNames.Count} custom property types defined";
            }

            return result;
        }
        catch (Exception ex)
        {
            return SetupResult.CreateFailure($"Database setup failed: {ex.Message}");
        }
    }

    /// <summary>
    /// Sets up database with simple parameters (for easier calling from external systems)
    /// </summary>
    /// <param name="databasePath">Path to database file</param>
    /// <param name="customPropertyNames">List of custom property names</param>
    /// <param name="overwriteExisting">Whether to overwrite existing database</param>
    /// <returns>Setup result</returns>
    public async Task<SetupResult> SetupDatabaseAsync(string databasePath,
        List<string>? customPropertyNames = null,
        bool overwriteExisting = false)
    {
        var config = new DatabaseSetupConfig
        {
            DatabasePath = databasePath,
            CustomPropertyNames = customPropertyNames ?? new List<string>(),
            OverwriteExisting = overwriteExisting
        };

        return await SetupDatabaseAsync(config);
    }

    /// <summary>
    /// Tests database connectivity and returns status information
    /// </summary>
    /// <returns>Setup result with database information</returns>
    public async Task<SetupResult> TestDatabaseAsync()
    {
        try
        {
            if (!IsDatabaseReady())
            {
                return SetupResult.CreateFailure("Database not initialized - call SetupDatabaseAsync first");
            }

            // Test basic operations
            var revisionCount = await _unitOfWork!.Revisions.CountAsync();
            var documentCount = await _unitOfWork.Documents.CountAsync();
            var propertyCount = await _unitOfWork.CustomProperties.CountAsync();

            // Test integrity
            var integrityOk = await _databaseService!.CheckDatabaseIntegrityAsync();

            var result = SetupResult.CreateSuccess(_databaseService.DatabasePath!);
            result.Message = $"Database test successful. " +
                           $"Revisions: {revisionCount}, " +
                           $"Documents: {documentCount}, " +
                           $"Properties: {propertyCount}. " +
                           $"Integrity: {(integrityOk ? "OK" : "FAILED")}";

            if (!integrityOk)
            {
                result.AddWarning("Database integrity check failed");
            }

            return result;
        }
        catch (Exception ex)
        {
            return SetupResult.CreateFailure($"Database test failed: {ex.Message}");
        }
    }

    /// <summary>
    /// Closes database connection and cleans up resources
    /// </summary>
    public async Task CloseAsync()
    {
        if (_databaseService != null)
        {
            await _databaseService.CloseAsync();
            _databaseService = null;
        }

        _unitOfWork?.Dispose();
        _unitOfWork = null;
    }


    /// <summary>
    /// Connects to an existing database without creating or overwriting
    /// </summary>
    /// <param name="databasePath">Path to existing database file</param>
    /// <returns>Setup result with connection information</returns>
    public async Task<SetupResult> ConnectDatabaseAsync(string databasePath)
    {
        try
        {
            // Validate input
            if (string.IsNullOrWhiteSpace(databasePath))
            {
                return SetupResult.CreateFailure("Database path is required");
            }

            // Check if file exists
            if (!File.Exists(databasePath))
            {
                return SetupResult.CreateFailure($"Database file does not exist: {databasePath}");
            }

            // Close any existing connection
            if (_databaseService != null)
            {
                await _databaseService.CloseAsync();
                _databaseService = null;
            }

            _unitOfWork?.Dispose();
            _unitOfWork = null;

            // Initialize database service with existing file
            _databaseService = new DatabaseService();
            await _databaseService.InitializeAsync(databasePath);

            // Verify database was opened successfully
            if (!_databaseService.IsInitialized)
            {
                return SetupResult.CreateFailure("Failed to connect to database");
            }

            // Initialize unit of work
            _unitOfWork = new UnitOfWork(_databaseService.Connection);

            // Verify database has expected tables (basic validation)
            var revisionCount = await _unitOfWork.Revisions.CountAsync();
            var documentCount = await _unitOfWork.Documents.CountAsync();
            var propertyCount = await _unitOfWork.CustomProperties.CountAsync();

            // Test integrity
            var integrityOk = await _databaseService.CheckDatabaseIntegrityAsync();

            var result = SetupResult.CreateSuccess(databasePath);
            result.Message = $"Connected successfully to database. " +
                           $"Revisions: {revisionCount}, " +
                           $"Documents: {documentCount}, " +
                           $"Properties: {propertyCount}";

            if (!integrityOk)
            {
                result.AddWarning("Database integrity check failed");
            }

            return result;
        }
        catch (Exception ex)
        {
            return SetupResult.CreateFailure($"Failed to connect to database: {ex.Message}");
        }
    }

    #endregion

    #region Synchronous Methods (for IronPython/PyRevit compatibility)

    /// <summary>
    /// Sets up a new document database (synchronous version for IronPython)
    /// </summary>
    /// <param name="config">Database setup configuration</param>
    /// <returns>Setup result with success/failure information</returns>
    public SetupResult SetupDatabase(DatabaseSetupConfig config)
    {
        try
        {
            return SetupDatabaseAsync(config).GetAwaiter().GetResult();
        }
        catch (Exception ex)
        {
            return SetupResult.CreateFailure($"Database setup failed: {ex.Message}");
        }
    }

    /// <summary>
    /// Sets up database with simple parameters (synchronous version for IronPython)
    /// </summary>
    /// <param name="databasePath">Path to database file</param>
    /// <param name="customPropertyNames">List of custom property names</param>
    /// <param name="overwriteExisting">Whether to overwrite existing database</param>
    /// <returns>Setup result</returns>
    public SetupResult SetupDatabase(string databasePath,
        List<string>? customPropertyNames = null,
        bool overwriteExisting = false)
    {
        try
        {
            return SetupDatabaseAsync(databasePath, customPropertyNames, overwriteExisting)
                .GetAwaiter().GetResult();
        }
        catch (Exception ex)
        {
            return SetupResult.CreateFailure($"Database setup failed: {ex.Message}");
        }
    }

    /// <summary>
    /// Tests database connectivity and returns status information (synchronous version for IronPython)
    /// </summary>
    /// <returns>Setup result with database information</returns>
    public SetupResult TestDatabase()
    {
        try
        {
            return TestDatabaseAsync().GetAwaiter().GetResult();
        }
        catch (Exception ex)
        {
            return SetupResult.CreateFailure($"Database test failed: {ex.Message}");
        }
    }

    /// <summary>
    /// Closes database connection and cleans up resources (synchronous version for IronPython)
    /// </summary>
    public void Close()
    {
        try
        {
            CloseAsync().GetAwaiter().GetResult();
        }
        catch (Exception ex)
        {
            // Log error but don't throw during cleanup
            System.Diagnostics.Debug.WriteLine($"Error during close: {ex.Message}");
        }
    }

    #endregion

    #region Shared Methods

    /// <summary>
    /// Checks if the current database is ready for operations
    /// </summary>
    /// <returns>True if database is initialized and ready</returns>
    public bool IsDatabaseReady()
    {
        return _databaseService?.IsInitialized == true && _unitOfWork != null;
    }

    /// <summary>
    /// Gets the current database path
    /// </summary>
    /// <returns>Database file path or null if not initialized</returns>
    public string? GetDatabasePath()
    {
        return _databaseService?.DatabasePath;
    }

    /// <summary>
    /// Validates custom property names
    /// </summary>
    /// <param name="propertyNames">Property names to validate</param>
    /// <returns>List of invalid property names</returns>
    private static List<string> ValidateCustomPropertyNames(List<string> propertyNames)
    {
        var invalid = new List<string>();

        foreach (var name in propertyNames)
        {
            if (string.IsNullOrWhiteSpace(name))
            {
                invalid.Add("[empty/whitespace]");
                continue;
            }

            // Check for valid property name (basic validation)
            if (name.Length > 100)
            {
                invalid.Add($"{name} (too long - max 100 characters)");
            }

            // Check for problematic characters that might cause issues
            if (name.Contains("\"") || name.Contains("'") || name.Contains(";"))
            {
                invalid.Add($"{name} (contains problematic characters)");
            }
        }

        return invalid;
    }

    #endregion

    #region IDisposable Implementation

    public void Dispose()
    {
        if (!_disposed)
        {
            Close(); // Use synchronous version for disposal
            _disposed = true;
        }
    }

    #endregion
}