//
//License:
//
//
// Revit Batch Processor Sample Code
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
//
//

using CommunityToolkit.Mvvm.ComponentModel;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Services.Api;
using System.Collections.ObjectModel;

namespace duHastNet.DocManager.Revit.Models.Database
{
    /// <summary>
    /// Carries the data retrieved from the Document Manager database.
    /// <para>
    /// Populated before the WPF window opens and passed into the window constructor
    /// alongside <c>RevitDataModel</c>. Intentionally separate from <c>RevitDataModel</c>
    /// to maintain a clear delineation between Revit-sourced and database-sourced data.
    /// </para>
    /// <para>
    /// <see cref="Documents"/> and <see cref="Revisions"/> are <see cref="ObservableCollection{T}"/>
    /// so that panel ViewModels bound to them automatically reflect changes when
    /// <see cref="Reload"/> clears and repopulates the collections.
    /// </para>
    /// </summary>
    public partial class DatabaseDataModel : ObservableObject
    {
        #region Observable Properties

        /// <summary>
        /// Gets a value indicating whether the database is currently connected
        /// and its data successfully loaded.
        /// </summary>
        [ObservableProperty]
        private bool _isConnected;

        #endregion Observable Properties

        #region Collections

        /// <summary>
        /// Gets the existing active documents loaded from the database.
        /// Empty when <see cref="IsConnected"/> is <c>false</c>.
        /// </summary>
        public ObservableCollection<Document> Documents { get; }

        /// <summary>
        /// Gets the existing revisions loaded from the database.
        /// Empty when <see cref="IsConnected"/> is <c>false</c>.
        /// </summary>
        public ObservableCollection<Revision> Revisions { get; }

        #endregion Collections

        #region Constructor

        /// <summary>
        /// Initializes a new instance of <see cref="DatabaseDataModel"/> with pre-loaded data.
        /// </summary>
        /// <param name="isConnected">
        /// <c>true</c> if the database was successfully connected and data loaded;
        /// <c>false</c> if startup failed (pass empty lists in that case).
        /// </param>
        /// <param name="documents">Existing active documents from the database. Must not be null.</param>
        /// <param name="revisions">Existing revisions from the database. Must not be null.</param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="documents"/> or <paramref name="revisions"/> is null.
        /// </exception>
        public DatabaseDataModel(bool isConnected, IList<Document> documents, IList<Revision> revisions)
        {
            _ = documents ?? throw new ArgumentNullException(nameof(documents));
            _ = revisions ?? throw new ArgumentNullException(nameof(revisions));

            _isConnected = isConnected;
            Documents = new ObservableCollection<Document>(documents);
            Revisions = new ObservableCollection<Revision>(revisions);
        }

        #endregion Constructor

        #region Factory

        /// <summary>
        /// Creates a <see cref="DatabaseDataModel"/> representing a failed or unavailable
        /// database connection, with empty collections.
        /// </summary>
        /// <returns>A disconnected <see cref="DatabaseDataModel"/> with empty collections.</returns>
        public static DatabaseDataModel CreateDisconnected()
        {
            return new DatabaseDataModel(false, new List<Document>(), new List<Revision>());
        }

        #endregion Factory

        #region Reload

        /// <summary>
        /// Clears the existing collections, reconnects to the database, and repopulates
        /// <see cref="Documents"/> and <see cref="Revisions"/> with a fresh snapshot.
        /// <para>
        /// <see cref="IsConnected"/> is updated to reflect the outcome. Any failure is
        /// enqueued to the <paramref name="messageStore"/> so it surfaces in the UI banner.
        /// The window remains open and operations are disabled when <see cref="IsConnected"/>
        /// is <c>false</c>.
        /// </para>
        /// </summary>
        /// <param name="docManagerApi">The API instance used to connect and read data. Must not be null.</param>
        /// <param name="databasePath">Path to the database file. Must not be null or whitespace.</param>
        /// <param name="messageStore">Message store for surfacing errors to the UI banner. Must not be null.</param>
        /// <exception cref="ArgumentNullException">
        /// Thrown when <paramref name="docManagerApi"/> or <paramref name="messageStore"/> is null.
        /// </exception>
        /// <exception cref="ArgumentException">
        /// Thrown when <paramref name="databasePath"/> is null or whitespace.
        /// </exception>
        public void Reload(
            DocManagerApi docManagerApi,
            string databasePath,
            duHastNet.Utils.WPF.Stores.MessageStore messageStore)
        {
            _ = docManagerApi ?? throw new ArgumentNullException(nameof(docManagerApi));
            _ = messageStore ?? throw new ArgumentNullException(nameof(messageStore));

            if (string.IsNullOrWhiteSpace(databasePath))
                throw new ArgumentException("Database path must not be null or whitespace.", nameof(databasePath));

            Documents.Clear();
            Revisions.Clear();

            try
            {
                var connectionResult = docManagerApi.ConnectDatabase(databasePath);

                if (!connectionResult.Success)
                {
                    messageStore.EnqueueMessage(
                        $"Could not connect to database: {connectionResult.Message}",
                        duHastNet.Utils.WPF.Stores.MessageTypes.Error);

                    IsConnected = false;
                    return;
                }

                foreach (var document in docManagerApi.GetActiveDocuments())
                    Documents.Add(document);

                foreach (var revision in docManagerApi.GetAllRevisions())
                    Revisions.Add(revision);

                IsConnected = true;
            }
            catch (Exception ex)
            {
                messageStore.EnqueueMessage(
                    $"Failed to read database: {ex.Message}",
                    duHastNet.Utils.WPF.Stores.MessageTypes.Error);

                IsConnected = false;
            }
        }

        #endregion Reload
    }
}
