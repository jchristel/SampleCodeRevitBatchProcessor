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
        List<Models.MetaDataMap> MetaDataMap { get; }

        /// <summary>
        /// adds a new meta data mapper to collection
        /// </summary>
        /// <param name="mapper"></param>
        public void AddMapper (Models.MetaDataMap mapper);

        /// <summary>
        /// Remove mapper from collection
        /// </summary>
        /// <param name="mapper"></param>
        public void RemoveMapper (Models.MetaDataMap mapper);

        /// <summary>
        /// Clears all mappers from collection
        /// </summary>
        public void ClearMappers();
    }
}
