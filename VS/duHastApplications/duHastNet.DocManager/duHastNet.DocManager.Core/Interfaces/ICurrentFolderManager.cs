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
using duHastNet.DocManager.Core.Models.CurrentFolder;

namespace duHastNet.DocManager.Core.Interfaces;

/// <summary>
/// Interface for CurrentFolderManager - manages document processing from incoming folders
/// </summary>
public interface ICurrentFolderManager
{
    #region Properties

    /// <summary>
    /// Gets the current folder manager settings
    /// </summary>
    CurrentFolderManagerSettings Settings { get; }

    /// <summary>
    /// Gets the list of matched documents with their processing status
    /// </summary>
    List<IncomingDocumentProcessingStatus> MatchedDocuments { get; }

    /// <summary>
    /// Gets the list of errors that occurred during processing
    /// </summary>
    List<Exception> Errors { get; }

    #endregion

    #region Filing Rules Management

    /// <summary>
    /// Adds a filing rule to the settings
    /// </summary>
    /// <param name="filingRule">Filing rule to add</param>
    void AddFilingRule(IFilingRule filingRule);

    /// <summary>
    /// Removes a filing rule from the settings
    /// </summary>
    /// <param name="filingRule">Filing rule to remove</param>
    void RemoveFilingRule(IFilingRule filingRule);

    /// <summary>
    /// Clears all filing rules from the settings
    /// </summary>
    void ClearFilingRules();

    #endregion

    #region Supported File Types Management

    /// <summary>
    /// Adds a supported file type to the settings
    /// </summary>
    /// <param name="supportedFileType">Supported file type to add</param>
    void AddSupportedFileType(SupportedFileType supportedFileType);

    /// <summary>
    /// Removes a supported file type from the settings
    /// </summary>
    /// <param name="supportedFileType">Supported file type to remove</param>
    void RemoveSupportedFileType(SupportedFileType supportedFileType);

    /// <summary>
    /// Clears all supported file types from the settings
    /// </summary>
    void ClearSupportedFileTypes();

    #endregion

    #region Document Processing

    /// <summary>
    /// Gets the list of matched documents with their processing status
    /// </summary>
    /// <returns>List of document processing statuses</returns>
    List<IncomingDocumentProcessingStatus> GetMatchedDocuments();

    /// <summary>
    /// Gets metadata for incoming files and matches them against current documents
    /// </summary>
    /// <param name="currentDocuments">List of current documents in the database</param>
    /// <returns>True if successful, false otherwise</returns>
    bool GetIncomingFilesMetadata(List<Document> currentDocuments);

    /// <summary>
    /// Supersedes documents by moving files and updating database
    /// </summary>
    /// <param name="currentDocuments">List of current documents</param>
    /// <returns>True if successful, false otherwise</returns>
    bool SupersedeDocuments(List<Document> currentDocuments);

    #endregion
}
