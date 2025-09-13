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
    /// Unit of Work implementation for managing transactions
    /// </summary>
    public class UnitOfWork : IUnitOfWork
    {
        private readonly SQLiteAsyncConnection _connection;

        public IRevisionRepository Revisions { get; }
        public IDocumentRepository Documents { get; }
        public ICustomPropertyRepository CustomProperties { get; }

        public UnitOfWork(SQLiteAsyncConnection connection)
        {
            _connection = connection;

            Revisions = new RevisionRepository(connection);
            Documents = new DocumentRepository(connection);
            CustomProperties = new CustomPropertyRepository(connection);
        }

        public async Task<int> SaveChangesAsync()
        {
            // With sqlite-net-pcl, changes are immediately persisted
            // This method is here for interface compatibility
            return await Task.FromResult(0);
        }

        public async Task BeginTransactionAsync()
        {
            // Transactions are handled by RunInTransactionAsync
            await Task.CompletedTask;
        }

        public async Task CommitTransactionAsync()
        {
            // Transactions are handled automatically by RunInTransactionAsync
            await Task.CompletedTask;
        }

        public async Task RollbackTransactionAsync()
        {
            // Rollback is handled automatically if exception occurs
            await Task.CompletedTask;
        }

        public void Dispose()
        {
            // Connection is managed by DatabaseService
        }
    }
}
