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

using System.Collections.Generic;

namespace duHastNet.DocManager.Core.Models.CurrentFolder
{
    /// <summary>
    /// Configuration settings for CurrentFolderManager
    /// This class contains all persistable configuration data
    /// </summary>
    public class CurrentFolderManagerSettings
    {
        /// <summary>
        /// The path to the folder containing the incoming documents
        /// Documents in that folder will be moved to the current folder(s) if:
        /// - there is no matching document in the current location(s)
        /// - the previous version of the document was superseded successfully (moved out of the current folder)
        /// </summary>
        public string? IncomingFolderPath { get; set; }

        /// <summary>
        /// The path to the folder containing the current documents.
        /// Can be null if multiple folders are in use. Refer to folder distribution rules.
        /// </summary>
        public string? CurrentFolderPath { get; set; }

        /// <summary>
        /// The path to the folder containing all superseded documents. 
        /// If null, documents will not be moved if a newer version is added to the current folder(s).
        /// If the superseded folder already contains a document (file) with the same name, 
        /// i.e. document manager has been run a number of times using the same documents, 
        /// the document will be replaced with the new version.
        /// </summary>
        public string? SupersededFolderPath { get; set; }

        /// <summary>
        /// A unique character in the file name indicating the start of a revision 
        /// i.e. if the revision is indicated using square brackets: '[a]' the prefix is '['
        /// </summary>
        public string? RevisionPrefix { get; set; }

        /// <summary>
        /// A unique character in the file name indicating the end of a revision
        /// i.e. if the revision is indicated using square brackets: '[a]' the suffix is ']'
        /// </summary>
        public string? RevisionSuffix { get; set; }

        /// <summary>
        /// These rules are used to distribute the documents to folders, 
        /// if current document sets are maintained across multiples.
        /// </summary>
        public List<Interfaces.IFilingRule> FilingRules { get; set; }

        /// <summary>
        /// A list of file types which are supported by the document manager
        /// </summary>
        public List<Models.SupportedFileType> SupportedFileTypes { get; set; }

        /// <summary>
        /// Initializes a new instance of CurrentFolderManagerSettings with default values
        /// </summary>
        public CurrentFolderManagerSettings()
        {
            FilingRules = new List<Interfaces.IFilingRule>();
            SupportedFileTypes = new List<Models.SupportedFileType>();
        }

        /// <summary>
        /// Adds a filing rule to the configuration
        /// </summary>
        public void AddFilingRule(Interfaces.IFilingRule filingRule)
        {
            if (filingRule == null)
            {
                throw new ArgumentNullException(nameof(filingRule));
            }
            FilingRules.Add(filingRule);
        }

        /// <summary>
        /// Removes a filing rule from the configuration
        /// </summary>
        public void RemoveFilingRule(Interfaces.IFilingRule filingRule)
        {
            if (filingRule == null)
            {
                throw new ArgumentNullException(nameof(filingRule));
            }
            FilingRules.Remove(filingRule);
        }

        /// <summary>
        /// Clears all filing rules
        /// </summary>
        public void ClearFilingRules()
        {
            FilingRules.Clear();
        }

        /// <summary>
        /// Adds a supported file type to the configuration
        /// </summary>
        public void AddSupportedFileType(Models.SupportedFileType supportedFileType)
        {
            if (supportedFileType == null)
            {
                throw new ArgumentNullException(nameof(supportedFileType));
            }
            SupportedFileTypes.Add(supportedFileType);
        }

        /// <summary>
        /// Removes a supported file type from the configuration
        /// </summary>
        public void RemoveSupportedFileType(Models.SupportedFileType supportedFileType)
        {
            if (supportedFileType == null)
            {
                throw new ArgumentNullException(nameof(supportedFileType));
            }
            SupportedFileTypes.Remove(supportedFileType);
        }

        /// <summary>
        /// Clears all supported file types
        /// </summary>
        public void ClearSupportedFileTypes()
        {
            SupportedFileTypes.Clear();
        }
    }
}