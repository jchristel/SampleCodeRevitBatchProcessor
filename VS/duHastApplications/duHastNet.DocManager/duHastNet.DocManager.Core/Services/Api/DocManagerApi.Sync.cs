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
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.Config;
using duHastNet.DocManager.Core.Models.Results;
using duHastNet.DocManager.Core.Services;
using duHastNet.DocManager.Core.Services.Repositories;

namespace duHastNet.DocManager.Core.Services.Api;

/// <summary>
/// Partial class for DocManagerApi - Synchronous Operations Support
/// This file adds synchronous database operations for IronPython/PyRevit compatibility
/// </summary>
public partial class DocManagerApi
{

    #region Synchronous Methods - Updated Implementations

    /// <summary>
    /// Sets up a new document database (synchronous version for IronPython)
    /// UPDATED: Now uses proper sync methods instead of .GetAwaiter().GetResult()
    /// </summary>
    /// <param name="config">Database setup configuration</param>
    /// <returns>Setup result with success/failure information</returns>
    public SetupResult SetupDatabase(DatabaseSetupConfig config)
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

            // Initialize database service using SYNC method
            _databaseService = new DatabaseService();
            _databaseService.Initialize(config.DatabasePath);

            // Verify database was created successfully
            if (!_databaseService.IsInitialized)
            {
                return SetupResult.CreateFailure("Failed to initialize database");
            }

            // Initialize SYNC unit of work
            _unitOfWorkSync = new UnitOfWorkSync(_databaseService.SyncConnection);

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
    /// Sets up database with simple parameters (synchronous version for IronPython)
    /// UPDATED: Now calls sync SetupDatabase instead of async version
    /// </summary>
    /// <param name="databasePath">Path to database file</param>
    /// <param name="customPropertyNames">List of custom property names</param>
    /// <param name="overwriteExisting">Whether to overwrite existing database</param>
    /// <returns>Setup result</returns>
    public SetupResult SetupDatabase(string databasePath,
        List<string>? customPropertyNames = null,
        bool overwriteExisting = false)
    {
        var config = new DatabaseSetupConfig
        {
            DatabasePath = databasePath,
            CustomPropertyNames = customPropertyNames ?? new List<string>(),
            OverwriteExisting = overwriteExisting
        };

        return SetupDatabase(config);
    }

    /// <summary>
    /// Tests database connectivity and returns status information (synchronous version for IronPython)
    /// UPDATED: Now uses proper sync methods instead of .GetAwaiter().GetResult()
    /// </summary>
    /// <returns>Setup result with database information</returns>
    public SetupResult TestDatabase()
    {
        try
        {
            if (!IsDatabaseReady())
            {
                return SetupResult.CreateFailure("Database not initialized - call SetupDatabase first");
            }

            // Test basic operations using SYNC methods
            var revisionCount = _unitOfWorkSync!.Revisions.Count();
            var documentCount = _unitOfWorkSync.Documents.Count();
            var activeDocuments = _unitOfWorkSync.Documents.GetActiveDocuments();
            
            // TODO: Add other counts as repositories are implemented
            // var propertyCount = _unitOfWorkSync.CustomProperties.Count();

            // Test integrity using SYNC method
            var integrityOk = _databaseService!.CheckDatabaseIntegrity();

            var result = SetupResult.CreateSuccess(_databaseService.DatabasePath!);
            result.Message = $"Database test successful. " +
                           $"Revisions: {revisionCount}, " +
                           $"Documents: {documentCount} (Active: {activeDocuments.Count}). " +
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
    /// Closes database connection and cleans up resources (synchronous version for IronPython)
    /// UPDATED: Now uses proper sync Close method instead of Task.Run
    /// </summary>
    public void Close()
    {
        try
        {
            // Use SYNC close method
            _databaseService?.Close();
            _databaseService = null;

            _unitOfWork?.Dispose();
            _unitOfWork = null;

            _unitOfWorkSync?.Dispose();
            _unitOfWorkSync = null;
        }
        catch (Exception ex)
        {
            // Log error but don't throw during cleanup
            System.Diagnostics.Debug.WriteLine($"Error during close: {ex.Message}");
        }
    }

    /// <summary>
    /// Connects to an existing database (synchronous version for IronPython)
    /// UPDATED: Now uses proper sync methods instead of .GetAwaiter().GetResult()
    /// </summary>
    /// <param name="databasePath">Path to existing database file</param>
    /// <returns>Setup result with connection information</returns>
    public SetupResult ConnectDatabase(string databasePath)
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

            // Close any existing connection using SYNC method
            _databaseService?.Close();
            _databaseService = null;

            _unitOfWork?.Dispose();
            _unitOfWork = null;

            _unitOfWorkSync?.Dispose();
            _unitOfWorkSync = null;

            // Initialize database service with existing file using SYNC method
            _databaseService = new DatabaseService();
            _databaseService.Initialize(databasePath);

            // Verify database was opened successfully
            if (!_databaseService.IsInitialized)
            {
                return SetupResult.CreateFailure("Failed to connect to database");
            }

            // Initialize SYNC unit of work
            _unitOfWorkSync = new UnitOfWorkSync(_databaseService.SyncConnection);

            // Verify database has expected tables (basic validation) using SYNC methods
            var revisionCount = _unitOfWorkSync.Revisions.Count();
            var documentCount = _unitOfWorkSync.Documents.Count();
            var activeDocuments = _unitOfWorkSync.Documents.GetActiveDocuments();
            
            // TODO: Add other counts as repositories are implemented
            // var propertyCount = _unitOfWorkSync.CustomProperties.Count();

            // Test integrity using SYNC method
            var integrityOk = _databaseService.CheckDatabaseIntegrity();

            var result = SetupResult.CreateSuccess(databasePath);
            result.Message = $"Connected successfully to database. " +
                           $"Revisions: {revisionCount}, " +
                           $"Documents: {documentCount} (Active: {activeDocuments.Count})";

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

    #region Synchronous Revision Methods - NEW

    /// <summary>
    /// Gets all revisions from the database (synchronous version for IronPython)
    /// </summary>
    /// <returns>List of all revisions</returns>
    /// <exception cref="InvalidOperationException">Thrown if database is not initialized</exception>
    public List<Revision> GetAllRevisions()
    {
        if (!IsDatabaseReady())
            throw new InvalidOperationException("Database not initialized");

        return _unitOfWorkSync!.Revisions.GetAll();
    }

    /// <summary>
    /// Gets all revisions with a specific date (synchronous version for IronPython)
    /// </summary>
    /// <param name="date">The revision date to search for</param>
    /// <returns>List of revisions with the specified date</returns>
    /// <exception cref="InvalidOperationException">Thrown if database is not initialized</exception>
    public List<Revision> GetRevisionsByDate(DateTime date)
    {
        if (!IsDatabaseReady())
            throw new InvalidOperationException("Database not initialized");

        return _unitOfWorkSync!.Revisions.GetRevisionsByDate(date);
    }

    /// <summary>
    /// Creates a new revision in the database (synchronous version for IronPython)
    /// </summary>
    /// <param name="revision">The revision to create</param>
    /// <returns>Number of records affected (should be 1 on success)</returns>
    /// <exception cref="InvalidOperationException">Thrown if database is not initialized</exception>
    /// <exception cref="ArgumentNullException">Thrown if revision is null</exception>
    public int CreateRevision(Revision revision)
    {
        if (!IsDatabaseReady())
            throw new InvalidOperationException("Database not initialized");

        if (revision == null)
            throw new ArgumentNullException(nameof(revision));

        return _unitOfWorkSync!.Revisions.Insert(revision);
    }

    /// <summary>
    /// Adds a document to a revision's document list (synchronous version for IronPython)
    /// </summary>
    /// <param name="revisionId">Revision ID to update</param>
    /// <param name="documentId">Document ID to add</param>
    /// <returns>Number of records affected</returns>
    /// <exception cref="InvalidOperationException">Thrown if database is not initialized</exception>
    public int AddDocumentToRevision(int revisionId, int documentId)
    {
        if (!IsDatabaseReady())
            throw new InvalidOperationException("Database not initialized");

        return _unitOfWorkSync!.Revisions.AddDocumentToRevision(revisionId, documentId);
    }

    /// <summary>
    /// Removes a document from a revision's document list (synchronous version for IronPython)
    /// </summary>
    /// <param name="revisionId">Revision ID to update</param>
    /// <param name="documentId">Document ID to remove</param>
    /// <returns>Number of records affected</returns>
    /// <exception cref="InvalidOperationException">Thrown if database is not initialized</exception>
    public int RemoveDocumentFromRevision(int revisionId, int documentId)
    {
        if (!IsDatabaseReady())
            throw new InvalidOperationException("Database not initialized");

        return _unitOfWorkSync!.Revisions.RemoveDocumentFromRevision(revisionId, documentId);
    }

    #endregion

    #region Synchronous Document Methods - NEW

    /// <summary>
    /// Gets a document by its ID (synchronous version for IronPython)
    /// </summary>
    /// <param name="documentId">The document ID</param>
    /// <returns>The document if found, null otherwise</returns>
    /// <exception cref="InvalidOperationException">Thrown if database is not initialized</exception>
    public Document? GetDocumentById(int documentId)
    {
        if (!IsDatabaseReady())
            throw new InvalidOperationException("Database not initialized");

        return _unitOfWorkSync!.Documents.GetById(documentId);
    }

    /// <summary>
    /// Updates an existing document in the database (synchronous version for IronPython)
    /// </summary>
    /// <param name="document">The document to update</param>
    /// <returns>Number of records affected (should be 1 on success)</returns>
    /// <exception cref="InvalidOperationException">Thrown if database is not initialized</exception>
    /// <exception cref="ArgumentNullException">Thrown if document is null</exception>
    public int UpdateDocument(Document document)
    {
        if (!IsDatabaseReady())
            throw new InvalidOperationException("Database not initialized");

        if (document == null)
            throw new ArgumentNullException(nameof(document));

        return _unitOfWorkSync!.Documents.Update(document);
    }

    /// <summary>
    /// Gets all active documents from the database (synchronous version for IronPython)
    /// </summary>
    /// <returns>List of all active documents</returns>
    /// <exception cref="InvalidOperationException">Thrown if database is not initialized</exception>
    public List<Document> GetActiveDocuments()
    {
        if (!IsDatabaseReady())
            throw new InvalidOperationException("Database not initialized");

        return _unitOfWorkSync!.Documents.GetActiveDocuments();
    }

    /// <summary>
    /// Gets documents by revision ID (synchronous version for IronPython)
    /// </summary>
    /// <param name="revisionId">The revision ID</param>
    /// <returns>List of documents for the specified revision</returns>
    /// <exception cref="InvalidOperationException">Thrown if database is not initialized</exception>
    public List<Document> GetDocumentsByRevision(int revisionId)
    {
        if (!IsDatabaseReady())
            throw new InvalidOperationException("Database not initialized");

        return _unitOfWorkSync!.Documents.GetDocumentsByRevision(revisionId);
    }

    /// <summary>
    /// Gets documents by document number (synchronous version for IronPython)
    /// </summary>
    /// <param name="documentNumber">The document number</param>
    /// <returns>List of documents with the specified number</returns>
    /// <exception cref="InvalidOperationException">Thrown if database is not initialized</exception>
    public List<Document> GetDocumentsByNumber(string documentNumber)
    {
        if (!IsDatabaseReady())
            throw new InvalidOperationException("Database not initialized");

        return _unitOfWorkSync!.Documents.GetDocumentsByNumber(documentNumber);
    }

    #endregion

    #region Helper Methods

    /// <summary>
    /// Gets the sync unit of work for direct repository access (for advanced scenarios)
    /// </summary>
    /// <returns>Sync unit of work instance</returns>
    /// <exception cref="InvalidOperationException">Thrown if database is not initialized</exception>
    public IUnitOfWorkSync GetUnitOfWorkSync()
    {
        if (_unitOfWorkSync == null)
        {
            throw new InvalidOperationException("Database not initialized with sync connection. Call SetupDatabase or ConnectDatabase first.");
        }
        return _unitOfWorkSync;
    }


    #endregion
}
