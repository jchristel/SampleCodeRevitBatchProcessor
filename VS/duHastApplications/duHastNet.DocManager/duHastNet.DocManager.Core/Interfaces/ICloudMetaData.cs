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


using duHastNet.DocManager.Core.Models.CurrentFolder;
using duHastNet.DocManager.Core.Models.CloudDocManager.MetaData;

namespace duHastNet.DocManager.Core.Interfaces
{
    /// <summary>
    /// An interface for cloud based document management systems which use meta data to upload documents.
    /// sample provider is Aconex
    /// </summary> 
    public interface ICloudMetaData
    {
        /// <summary>
        /// The fully qualified path to the metadata template file.
        /// which is used to upload documents
        /// The file will be duplicated and modified during upload
        /// </summary>
        string MetadataTemplateFilePath { get; set; }

        /// <summary>
        /// Maps mepa data fields to document properties
        /// </summary>
        List<MetaDataMap> MetaDataMap { get; }

        /// <summary>
        /// Collection of supported file types with their document number modifiers.
        /// Used to apply file-type-specific modifications to document numbers during export.
        /// Each file type may have a different modifier (e.g., PDF = no modifier, DWG = add "-DWG" suffix)
        /// </summary>
        List<SupportedFileType> SupportedFileTypes { get; set; }

        /// <summary>
        /// adds a new meta data mapper to collection
        /// </summary>
        /// <param name="mapper"></param>
        public void AddMapper (MetaDataMap mapper);

        /// <summary>
        /// Remove mapper from collection
        /// </summary>
        /// <param name="mapper"></param>
        public void RemoveMapper (MetaDataMap mapper);

        /// <summary>
        /// Clears all mappers from collection
        /// </summary>
        public void ClearMappers();

        /// <summary>
        /// Cleans up any invalid mappings from the metadata.
        /// Invalid mappings can occur when the available custom fields in the database have changed, or the meta data template has been modified.
        /// </summary>
        public List<string> CleanupMappings(List<string> customFieldNames);

    }
}
