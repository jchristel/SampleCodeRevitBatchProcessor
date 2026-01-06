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

using duHastNet.DocManager.Core.Interfaces;
using duHastNet.DocManager.Core.Models;
using duHastNet.DocManager.Core.Models.Results;

namespace duHastNet.DocManager.Core.Services.Api;

/// <summary>
/// Main API class for external integration (PyRevit, Revit Plugin, Standalone)
/// This partial class handles data loading operations
/// </summary>
public partial class DocManagerApi
{
    #region Data Loading Operations (Async)

    /// <summary>
    /// Loads all documents and revisions from the database into the provided Manager
    /// </summary>
    /// <param name="manager">Manager instance to populate with data</param>
    /// <returns>Setup result with success/failure information</returns>
    public async Task<SetupResult> LoadDataIntoManagerAsync(IManager manager)
    {
        try
        {
            if (!IsDatabaseReady())
            {
                return SetupResult.CreateFailure("Database not initialized - call SetupDatabaseAsync or ConnectDatabaseAsync first");
            }

            if (manager == null)
            {
                return SetupResult.CreateFailure("Manager cannot be null");
            }

            // Clear existing data in manager
            manager.ClearData();

            // Load custom field definitions first (needed to resolve property names)
            var customFieldDefinitions = await _unitOfWork!.CustomFieldDefinitions.GetAllAsync();
            foreach (var definition in customFieldDefinitions)
            {
                manager.AddCustomFieldDefinition(definition);
            }

            // Load all revisions from database
            var revisions = await _unitOfWork.Revisions.GetAllAsync();
            foreach (var revision in revisions)
            {
                manager.AddRevision(revision);
            }

            // Load all active documents from database (including custom properties)
            var documents = await _unitOfWork.Documents.GetActiveDocumentsAsync();

            // Load custom properties for each document
            foreach (var document in documents)
            {
                var customProperties = await _unitOfWork.CustomProperties.GetPropertiesByDocumentAsync(document.Id);

                // Resolve property names from CustomFieldDefinitions
                foreach (var customProperty in customProperties)
                {
                    var definition = customFieldDefinitions.FirstOrDefault(cfd => cfd.Id == customProperty.CustomFieldDefinitionId);
                    if (definition != null)
                    {
                        customProperty.PropertyName = definition.PropertyName;
                    }
                }

                document.CustomProperties.Clear();
                document.CustomProperties.AddRange(customProperties);

                manager.AddDocument(document);
            }

            // Mark data as loaded
            manager.MarkDataAsLoaded();

            var result = SetupResult.CreateSuccess(_databaseService!.DatabasePath!);
            result.Message = $"Data loaded successfully: {manager.DocumentCount} documents, " +
                           $"{manager.RevisionCount} revisions loaded from database";

            return result;
        }
        catch (Exception ex)
        {
            return SetupResult.CreateFailure($"Failed to load data: {ex.Message}");
        }
    }

    /// <summary>
    /// Reloads all data from the database into the provided Manager
    /// This is useful when external changes have been made to the database
    /// </summary>
    /// <param name="manager">Manager instance to refresh with data</param>
    /// <returns>Setup result with success/failure information</returns>
    public async Task<SetupResult> ReloadDataIntoManagerAsync(IManager manager)
    {
        // Same implementation as LoadDataIntoManagerAsync - it clears and reloads
        return await LoadDataIntoManagerAsync(manager);
    }

    #endregion

    #region Data Loading Operations (Synchronous - for IronPython compatibility)

    /// <summary>
    /// Loads all documents and revisions from the database into the provided Manager (synchronous version)
    /// </summary>
    /// <param name="manager">Manager instance to populate with data</param>
    /// <returns>Setup result with success/failure information</returns>
    public SetupResult LoadDataIntoManager(IManager manager)
    {
        try
        {
            return LoadDataIntoManagerAsync(manager).GetAwaiter().GetResult();
        }
        catch (Exception ex)
        {
            return SetupResult.CreateFailure($"Failed to load data: {ex.Message}");
        }
    }

    /// <summary>
    /// Reloads all data from the database into the provided Manager (synchronous version)
    /// </summary>
    /// <param name="manager">Manager instance to refresh with data</param>
    /// <returns>Setup result with success/failure information</returns>
    public SetupResult ReloadDataIntoManager(Manager manager)
    {
        try
        {
            return ReloadDataIntoManagerAsync(manager).GetAwaiter().GetResult();
        }
        catch (Exception ex)
        {
            return SetupResult.CreateFailure($"Failed to reload data: {ex.Message}");
        }
    }

    #endregion
}
