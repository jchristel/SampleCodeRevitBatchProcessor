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

using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.Config;
using duHastNet.DocManager.Core.Models.Results;
using duHastNet.DocManager.Core.Services.Repositories;

namespace duHastNet.DocManager.Core.Interfaces;

/// <summary>
/// Interface for DocManagerApi - main API for external integration
/// </summary>
public interface IDocManagerApi : IDisposable
{
    #region Database Setup and Connection

    /// <summary>
    /// Sets up a new document database
    /// </summary>
    /// <param name="config">Database setup configuration</param>
    /// <returns>Setup result with success/failure information</returns>
    Task<SetupResult> SetupDatabaseAsync(DatabaseSetupConfig config);

    /// <summary>
    /// Sets up database with simple parameters (for easier calling from external systems)
    /// </summary>
    /// <param name="databasePath">Path to database file</param>
    /// <param name="customPropertyNames">List of custom property names</param>
    /// <param name="overwriteExisting">Whether to overwrite existing database</param>
    /// <returns>Setup result</returns>
    Task<SetupResult> SetupDatabaseAsync(string databasePath,
        List<string>? customPropertyNames = null,
        bool overwriteExisting = false);

    /// <summary>
    /// Tests database connectivity and returns status information
    /// </summary>
    /// <returns>Setup result with database information</returns>
    Task<SetupResult> TestDatabaseAsync();

    /// <summary>
    /// Closes database connection and cleans up resources
    /// </summary>
    Task CloseAsync();

    /// <summary>
    /// Connects to an existing database without creating or overwriting
    /// </summary>
    /// <param name="databasePath">Path to existing database file</param>
    /// <returns>Setup result with connection information</returns>
    Task<SetupResult> ConnectDatabaseAsync(string databasePath);

    /// <summary>
    /// Checks if database is ready for operations
    /// </summary>
    /// <returns>True if database is initialized and ready</returns>
    bool IsDatabaseReady();

    /// <summary>
    /// Gets the current database path
    /// </summary>
    /// <returns>Database path or null if not initialized</returns>
    string? GetDatabasePath();

    /// <summary>
    /// Gets the unit of work for database operations
    /// </summary>
    /// <returns>Unit of work instance or null if not initialized</returns>
    IUnitOfWork? GetUnitOfWork();

    #endregion

    #region Data Loading

    /// <summary>
    /// Loads data from database into Manager
    /// </summary>
    /// <param name="manager">Manager instance to load data into</param>
    /// <returns>Setup result with load information</returns>
    Task<SetupResult> LoadDataIntoManagerAsync(Manager manager);

    /// <summary>
    /// Reloads data from database into Manager
    /// </summary>
    /// <param name="manager">Manager instance to reload data into</param>
    /// <returns>Setup result with reload information</returns>
    Task<SetupResult> ReloadDataIntoManagerAsync(Manager manager);

    #endregion

    #region Revision Operations

    /// <summary>
    /// Gets all revisions from the database
    /// </summary>
    /// <returns>List of revisions</returns>
    Task<List<Revision>> GetAllRevisionsAsync();

    /// <summary>
    /// Gets revisions by date
    /// </summary>
    /// <param name="date">Date to filter by</param>
    /// <returns>List of revisions for the specified date</returns>
    Task<List<Revision>> GetRevisionsByDateAsync(DateTime date);

    /// <summary>
    /// Creates a new revision
    /// </summary>
    /// <param name="revision">Revision to create</param>
    /// <returns>Number of records affected</returns>
    Task<int> CreateRevisionAsync(Revision revision);

    /// <summary>
    /// Adds a document to a revision
    /// </summary>
    /// <param name="revisionId">Revision ID</param>
    /// <param name="documentId">Document ID</param>
    /// <returns>Number of records affected</returns>
    Task<int> AddDocumentToRevisionAsync(int revisionId, int documentId);

    /// <summary>
    /// Removes a document from a revision
    /// </summary>
    /// <param name="revisionId">Revision ID</param>
    /// <param name="documentId">Document ID</param>
    /// <returns>Number of records affected</returns>
    Task<int> RemoveDocumentFromRevisionAsync(int revisionId, int documentId);

    #endregion

    #region Document Operations

    /// <summary>
    /// Gets a document by ID
    /// </summary>
    /// <param name="documentId">Document ID</param>
    /// <returns>Document or null if not found</returns>
    Task<Document?> GetDocumentByIdAsync(int documentId);

    /// <summary>
    /// Updates a document
    /// </summary>
    /// <param name="document">Document to update</param>
    /// <returns>Number of records affected</returns>
    Task<int> UpdateDocumentAsync(Document document);

    #endregion
}
