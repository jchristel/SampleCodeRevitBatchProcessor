//
//License: BSD License
// Copyright 2025, Jan Christel
//

using System;
using System.Linq;
using System.Text.Json;
using duHastNet.DocManager.Core.Services.Api;

namespace duHastNet.DocManager.Revit.Bridge
{
    /// <summary>
    /// Bridge class that exposes .NET methods to JavaScript in CEFSharp WebView
    /// Uses DocManagerApi synchronous methods for proper database access
    /// No async/await - all operations are truly synchronous
    /// </summary>
    public class WebViewBridge
    {
        private readonly DocManagerApi _docManagerApi;
        private bool _disposed = false;

        /// <summary>
        /// Initializes a new instance of WebViewBridge with the database path
        /// Connects to database synchronously using new true sync methods
        /// </summary>
        /// <param name="databasePath">Path to the SQLite database</param>
        public WebViewBridge(string databasePath)
        {
            if (string.IsNullOrWhiteSpace(databasePath))
            {
                throw new ArgumentNullException(nameof(databasePath));
            }

            _docManagerApi = new DocManagerApi();
            
            // Use TRUE synchronous method - no blocking, no async wrapping
            var connectResult = _docManagerApi.ConnectDatabase(databasePath);
            
            if (!connectResult.Success)
            {
                throw new InvalidOperationException($"Failed to connect to database: {connectResult.Message}");
            }
        }

        /// <summary>
        /// Gets all documents from the database and returns them as JSON
        /// This method is called from JavaScript - fully synchronous, no async
        /// </summary>
        /// <returns>JSON string containing array of documents with DocumentNumber, Name, and Revision</returns>
        public string GetDocuments()
        {
            try
            {
                // Get SYNC unit of work from DocManagerApi
                var unitOfWorkSync = _docManagerApi.GetUnitOfWorkSync();

                // Get all active documents using SYNC method
                var documents = unitOfWorkSync.Documents.GetActiveDocuments();

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
