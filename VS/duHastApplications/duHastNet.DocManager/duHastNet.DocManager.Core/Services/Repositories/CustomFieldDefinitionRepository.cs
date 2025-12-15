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
using duHastNet.DocManager.Core.Models.Database;
using SQLite;

namespace duHastNet.DocManager.Core.Services.Repositories
{
    /// <summary>
    /// Repository implementation for CustomFieldDefinition entities
    /// </summary>
    public class CustomFieldDefinitionRepository : BaseRepository<CustomFieldDefinition>, ICustomFieldDefinitionRepository
    {
        public CustomFieldDefinitionRepository(SQLiteAsyncConnection connection) : base(connection)
        {
        }

        public async Task<CustomFieldDefinition?> GetByPropertyNameAsync(string propertyName)
        {
            return await _connection.Table<CustomFieldDefinition>()
                .Where(cfd => cfd.PropertyName == propertyName)
                .FirstOrDefaultAsync();
        }

        public async Task<List<CustomFieldDefinition>> GetActiveAsync()
        {
            return await _connection.Table<CustomFieldDefinition>()
                .Where(cfd => cfd.IsActive)
                .OrderBy(cfd => cfd.PropertyName)
                .ToListAsync();
        }

        public async Task<List<CustomFieldDefinition>> GetInactiveAsync()
        {
            return await _connection.Table<CustomFieldDefinition>()
                .Where(cfd => !cfd.IsActive)
                .OrderBy(cfd => cfd.PropertyName)
                .ToListAsync();
        }

        public async Task<bool> PropertyNameExistsAsync(string propertyName)
        {
            var count = await _connection.Table<CustomFieldDefinition>()
                .Where(cfd => cfd.PropertyName.ToLower() == propertyName.ToLower())
                .CountAsync();

            return count > 0;
        }

        public async Task<int> UpdateIsActiveAsync(int id, bool isActive)
        {
            return await _connection.ExecuteAsync(
                "UPDATE CustomFieldDefinitions SET IsActive = ? WHERE Id = ?",
                isActive, id);
        }
    }
}