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

using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.Database;
using duHastNet.DocManager.Core.Models.Results;

namespace duHastNet.DocManager.Core.Services.Api;

/// <summary>
/// Main API class for external integration (PyRevit, Revit Plugin, Standalone)
/// This partial class handles custom field definition operations
/// </summary>
public partial class DocManagerApi
{
    #region Custom Field Operations (Async)

    /// <summary>
    /// Adds a new custom field definition and creates CustomProperty records for all documents
    /// </summary>
    /// <param name="propertyName">Name of the custom field</param>
    /// <param name="isActive">Whether the field is active (default true)</param>
    /// <returns>Setup result with success/failure information</returns>
    public async Task<SetupResult> AddCustomFieldDefinitionAsync(string propertyName, bool isActive = true)
    {
        try
        {
            if (!IsDatabaseReady())
            {
                return SetupResult.CreateFailure("Database not initialized - call SetupDatabaseAsync or ConnectDatabaseAsync first");
            }

            // Validate property name
            var validationErrors = ValidateCustomPropertyNames(new List<string> { propertyName });
            if (validationErrors.Any())
            {
                return SetupResult.CreateFailure($"Invalid property name: {validationErrors[0]}");
            }

            // Check for duplicates
            var exists = await _unitOfWork!.CustomFieldDefinitions.PropertyNameExistsAsync(propertyName);
            if (exists)
            {
                return SetupResult.CreateFailure($"Custom field '{propertyName}' already exists");
            }

            // Create the custom field definition
            var customFieldDefinition = new CustomFieldDefinition(propertyName, isActive);
            await _unitOfWork.CustomFieldDefinitions.InsertAsync(customFieldDefinition);

            // Get all active documents
            var documents = await _unitOfWork.Documents.GetActiveDocumentsAsync();

            // Create CustomProperty records for all documents with empty values
            foreach (var document in documents)
            {
                var customProperty = new CustomProperty(
                    document.Id,
                    customFieldDefinition.Id,
                    string.Empty); // Empty value initially

                await _unitOfWork.CustomProperties.InsertAsync(customProperty);
            }

            var result = SetupResult.CreateSuccess(_databaseService!.DatabasePath!);
            result.Message = $"Custom field '{propertyName}' added successfully. Created {documents.Count} property records.";

            return result;
        }
        catch (Exception ex)
        {
            return SetupResult.CreateFailure($"Failed to add custom field: {ex.Message}");
        }
    }

    /// <summary>
    /// Updates the IsActive status of a custom field definition
    /// </summary>
    /// <param name="customFieldDefinitionId">ID of the custom field definition</param>
    /// <param name="isActive">New active status</param>
    /// <returns>Setup result with success/failure information</returns>
    public async Task<SetupResult> UpdateCustomFieldIsActiveAsync(int customFieldDefinitionId, bool isActive)
    {
        try
        {
            if (!IsDatabaseReady())
            {
                return SetupResult.CreateFailure("Database not initialized");
            }

            // Get the custom field definition
            var definition = await _unitOfWork!.CustomFieldDefinitions.GetByIdAsync(customFieldDefinitionId);
            if (definition == null)
            {
                return SetupResult.CreateFailure($"Custom field definition with ID {customFieldDefinitionId} not found");
            }

            // Update IsActive status
            var rowsAffected = await _unitOfWork.CustomFieldDefinitions.UpdateIsActiveAsync(customFieldDefinitionId, isActive);

            if (rowsAffected == 0)
            {
                return SetupResult.CreateFailure("Failed to update custom field status");
            }

            var result = SetupResult.CreateSuccess(_databaseService!.DatabasePath!);
            result.Message = $"Custom field '{definition.PropertyName}' {(isActive ? "activated" : "deactivated")} successfully";

            return result;
        }
        catch (Exception ex)
        {
            return SetupResult.CreateFailure($"Failed to update custom field: {ex.Message}");
        }
    }

    /// <summary>
    /// Gets all custom field definitions from the database
    /// </summary>
    /// <returns>List of custom field definitions</returns>
    public async Task<List<CustomFieldDefinition>> GetCustomFieldDefinitionsAsync()
    {
        try
        {
            if (!IsDatabaseReady())
            {
                return new List<CustomFieldDefinition>();
            }

            return await _unitOfWork!.CustomFieldDefinitions.GetAllAsync();
        }
        catch (Exception)
        {
            return new List<CustomFieldDefinition>();
        }
    }

    /// <summary>
    /// Gets only active custom field definitions from the database
    /// </summary>
    /// <returns>List of active custom field definitions</returns>
    public async Task<List<CustomFieldDefinition>> GetActiveCustomFieldDefinitionsAsync()
    {
        try
        {
            if (!IsDatabaseReady())
            {
                return new List<CustomFieldDefinition>();
            }

            return await _unitOfWork!.CustomFieldDefinitions.GetActiveAsync();
        }
        catch (Exception)
        {
            return new List<CustomFieldDefinition>();
        }
    }

    #endregion

}
