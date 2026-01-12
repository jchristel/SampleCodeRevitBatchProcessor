//
// BSD License
// Copyright 2026, Jan Christel
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

using System;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using duHastNet.DocManager.Core.Services.Api;

namespace duHastNet.DocManager.Revit.Bridge
{
    /// <summary>
    /// Bridge class that exposes .NET methods to JavaScript in CEFSharp WebView
    /// Uses DocManagerApi for proper database access following Core architecture
    /// Database connection is established lazily on first GetDocuments call
    /// </summary>
    public class WebViewBridge
    {
        private readonly string _databasePath;
        private DocManagerApi? _docManagerApi;
        private bool _isInitialized = false;
        private bool _disposed = false;
        private readonly object _lockObject = new object();

        /// <summary>
        /// Initializes a new instance of WebViewBridge with the database path
        /// Database connection happens lazily on first method call
        /// </summary>
        /// <param name="databasePath">Path to the SQLite database</param>
        public WebViewBridge(string databasePath)
        {
            if (string.IsNullOrWhiteSpace(databasePath))
            {
                throw new ArgumentNullException(nameof(databasePath));
            }

            _databasePath = databasePath;
        }

        /// <summary>
        /// Ensures database connection is established (lazy initialization)
        /// </summary>
        private async Task EnsureInitializedAsync()
        {
            if (_isInitialized)
                return;

            lock (_lockObject)
            {
                if (_isInitialized)
                    return;

                _docManagerApi = new DocManagerApi();
                _isInitialized = true;
            }

            // Connect to database (this is async but called from async method)
            var connectResult = await _docManagerApi.ConnectDatabaseAsync(_databasePath);

            if (!connectResult.Success)
            {
                throw new InvalidOperationException($"Failed to connect to database: {connectResult.Message}");
            }
        }

        /// <summary>
        /// Gets all documents from the database and returns them as JSON
        /// This method is called from JavaScript
        /// </summary>
        /// <returns>JSON string containing array of documents with DocumentNumber, Name, and Revision</returns>
        public async Task<string> GetDocuments()
        {
            try
            {
                // Ensure database is connected (lazy initialization)
                await EnsureInitializedAsync();

                // Get unit of work from DocManagerApi
                var unitOfWork = _docManagerApi!.GetUnitOfWork();

                if (unitOfWork == null)
                {
                    throw new InvalidOperationException("Database not connected");
                }

                // Get all active documents using the repository
                var documents = await unitOfWork.Documents.GetActiveDocumentsAsync();

                // Project to simplified DTOs with only needed properties
                var documentDtos = documents.Select(d => new
                {
                    DocumentNumber = d.Number,
                    Name = d.Name,
                    Revision = d.Revision
                }).ToList();

                // Serialize to JSON
                var json = JsonSerializer.Serialize(documentDtos, new JsonSerializerOptions
                {
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
                    WriteIndented = true
                });

                return json;
            }
            catch (Exception ex)
            {
                // Return error as JSON
                var error = new
                {
                    error = true,
                    message = ex.Message,
                    stackTrace = ex.StackTrace
                };

                return JsonSerializer.Serialize(error);
            }
        }

        /// <summary>
        /// Disposes resources used by the bridge
        /// </summary>
        public void Dispose()
        {
            if (!_disposed)
            {
                _docManagerApi?.Dispose();
                _disposed = true;
            }
        }
    }
}