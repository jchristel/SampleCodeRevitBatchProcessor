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

using duHastNet.DocManager.Core.Models.Database;

namespace duHastNet.DocManager.Core.Interfaces
{
    /// <summary>
    /// Repository interface for CustomFieldDefinition entities
    /// </summary>
    public interface ICustomFieldDefinitionRepository : IRepository<CustomFieldDefinition>
    {
        /// <summary>
        /// Gets a custom field definition by property name
        /// </summary>
        Task<CustomFieldDefinition?> GetByPropertyNameAsync(string propertyName);

        /// <summary>
        /// Gets all active custom field definitions
        /// </summary>
        Task<List<CustomFieldDefinition>> GetActiveAsync();

        /// <summary>
        /// Gets all inactive custom field definitions
        /// </summary>
        Task<List<CustomFieldDefinition>> GetInactiveAsync();

        /// <summary>
        /// Checks if a property name already exists (case-insensitive)
        /// </summary>
        Task<bool> PropertyNameExistsAsync(string propertyName);

        /// <summary>
        /// Updates the IsActive status of a custom field definition
        /// </summary>
        Task<int> UpdateIsActiveAsync(int id, bool isActive);
    }
}