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

using System;
using System.Collections.Generic;
using System.Linq;

namespace duHastNet.DocManager.Core.Models.MetaData
{
    /// <summary>
    /// Metadata mapper for Aconex cloud document management system
    /// This class maps document properties to Aconex metadata fields
    /// </summary>
    public class MetaDataMapperAconex : Interfaces.ICloudMetaData
    {
        /// <summary>
        /// CSV metadata template file path
        /// </summary>
        private string _metadataTemplateFilePath = string.Empty;

        /// <summary>
        /// Gets or sets the fully qualified path to the metadata template file
        /// which is used to upload documents. The file will be duplicated and modified during upload.
        /// </summary>
        public string MetadataTemplateFilePath
        {
            get => _metadataTemplateFilePath;
            set => _metadataTemplateFilePath = value;
        }

        /// <summary>
        /// A list of all available filds from the aconex metadata template
        /// </summary>
        private List<string> _availableFilds = [];

        public List<string> AvailableFilds
        {
            get => _availableFilds;
        }

        /// <summary>
        /// List of all mapped fields
        /// </summary>
        private List<MetaDataMap> _metaDataMap = [];

        /// <summary>
        /// Gets the collection of metadata field mappings
        /// Maps metadata fields to document properties
        /// </summary>
        public List<MetaDataMap> MetaDataMap
        {
            get => _metaDataMap;
        }

        /// <summary>
        /// Adds a new meta data mapper to collection if not already existing (based on MetaFieldName)
        /// </summary>
        /// <param name="mapper">The metadata mapper to add</param>
        /// <exception cref="ArgumentNullException">Thrown when mapper is null</exception>
        /// <exception cref="Exceptions.MetaMapperDuplicateException">Thrown when a mapper for this field already exists</exception>
        public void AddMapper(MetaDataMap mapper)
        {
            if (mapper == null)
            {
                throw new ArgumentNullException(nameof(mapper));
            }

            // Check if mapper already exists
            var existingMapper = _metaDataMap.FirstOrDefault(m => m.MetaFieldName == mapper.MetaFieldName);

            if (existingMapper == null)
            {
                _metaDataMap.Add(mapper);
            }
            else
            {
                throw new Exceptions.MetaMapperDuplicateException(
                    $"Mapper for field '{mapper.MetaFieldName}' already exists.",
                    existingMapper,
                    mapper);
            }
        }

        /// <summary>
        /// Removes mapper from collection based on MetaFieldName
        /// </summary>
        /// <param name="mapper">The metadata mapper to remove</param>
        /// <exception cref="ArgumentNullException">Thrown when mapper is null</exception>
        public void RemoveMapper(MetaDataMap mapper)
        {
            if (mapper == null)
            {
                throw new ArgumentNullException(nameof(mapper));
            }

            // Check if mapper exists based on MetaFieldName
            var existingMapper = _metaDataMap.FirstOrDefault(m => m.MetaFieldName == mapper.MetaFieldName);

            // If found, remove it
            if (existingMapper != null)
            {
                _metaDataMap.Remove(existingMapper);
            }
        }

        /// <summary>
        /// Clear all mappers from collection
        /// </summary>
        public void ClearMappers()
        {
            _metaDataMap.Clear();
        }

        /// <summary>
        /// Initializes a new instance of MetaDataMapperAconex
        /// </summary>
        public MetaDataMapperAconex()
        {
            _metaDataMap = new List<MetaDataMap>();
            _metadataTemplateFilePath = string.Empty;
        }
    }
}