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
using SQLite;

namespace duHastNet.DocManager.Core.Services.Repositories
{
    public class CustomFieldDefinitionRepository: BaseRepository<CustomFieldDefinition>, ICustomFieldDefinitionRepository
    {
        public CustomFieldDefinitionRepository(SQLiteAsyncConnection connection) : base(connection)
        {
        }

        /// <summary>
        /// Checks if a custom field definition with the specified property name exists.
        /// </summary>
        public async Task<bool> CustomFieldDefinitionExistsAsync(string propertyName)
        {
            var count = await _connection.Table<CustomFieldDefinition>()
                .CountAsync(d => d.PropertyName == propertyName);

            return count > 0;
        }

        /// <summary>
        /// Retrieves a list of distinct custom field definition names.
        /// </summary> 
        public async Task<List<string>> GetDistinctCustomFieldDefinitionNamesAsync()
        {
            // Fetch all custom field definitions from the database (activce and inactive)
            var customFieldDefinitions = await _connection.Table<CustomFieldDefinition>()
                .ToListAsync();

            // Extract distinct property names and order them alphabetically
            return customFieldDefinitions.Select(d => d.PropertyName)
                .Distinct()
                .OrderBy(n => n)
                .ToList();
        }

        /// <summary>
        /// Retrieves a list of active custom field definitions.
        /// </summary>
        /// <remarks>The returned list is ordered by the <see cref="CustomFieldDefinition.PropertyName"/>
        /// property.</remarks>
        /// <returns>A task that represents the asynchronous operation. The task result contains a list of  <see
        /// cref="CustomFieldDefinition"/> objects where <see cref="CustomFieldDefinition.IsActive"/> is <see
        /// langword="true"/>.</returns>
        public async Task<List<CustomFieldDefinition>> GetActiveCustomFieldDefinitionsAsync()
        {
            return await _connection.Table<CustomFieldDefinition>()
                .Where(cfd => cfd.IsActive)
                .OrderBy(cfd => cfd.PropertyName)
                .ToListAsync();
        }

        /// <summary>
        /// Retrieves a list of inactive custom field definitions.
        /// </summary>
        /// <remarks>The returned list is ordered by the <see cref="CustomFieldDefinition.PropertyName"/>
        /// <returns> A task that represents the asynchronous operation. The task result contains a list of  <see
        /// cref="CustomFieldDefinition"/> objects where <see cref="CustomFieldDefinition.IsActive"/> is <see
        /// langword="false"/>.</returns>
        public async Task<List<CustomFieldDefinition>> GetInactiveCustomFieldDefinitionsAsync()
        {
            return await _connection.Table<CustomFieldDefinition>()
                .Where(cfd => !cfd.IsActive)
                .OrderBy(cfd => cfd.PropertyName)
                .ToListAsync();
        }

        /// <summary>
        /// Updates the active status of a document
        /// </summary>
        /// <param name="customFieldDefinitionId">Document ID to update</param>
        /// <param name="isActive">New active status</param>
        /// <returns>Number of records affected</returns>
        public async Task<int> UpdateActiveStatusAsync(int customFieldDefinitionId, bool isActive)
        {
            var customFieldDef = await GetByIdAsync(customFieldDefinitionId);
            if (customFieldDef == null) return 0;

            customFieldDef.IsActive = isActive;
            return await UpdateAsync(customFieldDef);
        }

        /// <summary>
        /// Retrieves a custom field definition by its property name.
        /// </summary>
        /// <param name="propertyName"></param>
        /// <returns></returns>
        public async Task<CustomFieldDefinition?> GetCustomFieldDefinitionByNameAsync(string propertyName)
        {
            return await _connection.Table<CustomFieldDefinition>()
                .Where(cfd => cfd.PropertyName == propertyName)
                .FirstOrDefaultAsync();
        }
    }
}
