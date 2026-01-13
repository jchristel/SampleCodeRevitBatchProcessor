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
using SQLite;


namespace duHastNet.DocManager.Core.Services.Repositories
{
    /// <summary>
    /// Synchronous Unit of Work implementation for managing transactions.
    /// Provides sync database access for IronPython/PyRevit compatibility.
    /// </summary>
    public class UnitOfWorkSync : IUnitOfWorkSync
    {
        private readonly SQLiteConnection _connection;

        public IRevisionRepositorySync Revisions { get; }
        public IDocumentRepositorySync Documents { get; }
        
        // TODO: Add other repositories as they are implemented
        // public ICustomPropertyRepositorySync CustomProperties { get; }
        // public ICustomFieldDefinitionRepositorySync CustomFieldDefinitions { get; }

        public UnitOfWorkSync(SQLiteConnection connection)
        {
            _connection = connection ?? throw new ArgumentNullException(nameof(connection));

            Revisions = new RevisionRepositorySync(connection);
            Documents = new DocumentRepositorySync(connection);
            
            // TODO: Initialize other repositories as they are implemented
            // CustomProperties = new CustomPropertyRepositorySync(connection);
            // CustomFieldDefinitions = new CustomFieldDefinitionRepositorySync(connection);
        }

        public int SaveChanges()
        {
            // With sqlite-net-pcl, changes are immediately persisted
            // This method is here for interface compatibility
            return 0;
        }

        public void Dispose()
        {
            // Connection is managed by DatabaseService
        }
    }
}
