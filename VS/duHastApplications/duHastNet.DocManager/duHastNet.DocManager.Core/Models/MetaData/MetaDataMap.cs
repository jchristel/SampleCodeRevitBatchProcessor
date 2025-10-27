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

namespace duHastNet.DocManager.Core.Models.MetaData
{
    /// <summary>
    /// Maps a metadata field to either a fixed value or a document property
    /// Used for cloud document management system integrations
    /// </summary>
    public class MetaDataMap
    {
        /// <summary>
        /// The metadata field name
        /// </summary>
        private string? _metaFieldName;

        /// <summary>
        /// Gets or sets the metadata field name
        /// </summary>
        public string? MetaFieldName
        {
            get { return _metaFieldName; }
            set { _metaFieldName = value; }
        }

        /// <summary>
        /// The metadata field value. Null if this value is coming from a document property
        /// </summary>
        private string? _metaFieldValue;

        /// <summary>
        /// Gets or sets the metadata field value
        /// Use this for fixed/static values. Set to null if the value comes from a document property.
        /// </summary>
        public string? MetaFieldValue
        {
            get { return _metaFieldValue; }
            set { _metaFieldValue = value; }
        }

        /// <summary>
        /// The matching document property name. Null if a fixed value is used (MetaFieldValue)
        /// </summary>
        private string? _documentPropertyName;

        /// <summary>
        /// Gets or sets the document property name that provides the value
        /// Use this for dynamic values from document properties. Set to null if using a fixed value.
        /// </summary>
        public string? DocumentPropertyName
        {
            get { return _documentPropertyName; }
            set { _documentPropertyName = value; }
        }

        /// <summary>
        /// The name of the cloud service provider this meta data is for
        /// </summary>
        private string? _cloudServiceProviderName;

        /// <summary>
        /// Gets or sets the cloud service provider name this metadata mapping is for
        /// </summary>
        public string? CloudServiceProviderName
        {
            get { return _cloudServiceProviderName; }
            set { _cloudServiceProviderName = value; }
        }

        /// <summary>
        /// Initializes a new instance of MetaDataMap
        /// </summary>
        public MetaDataMap()
        {
        }

        /// <summary>
        /// Initializes a new instance of MetaDataMap with specified values
        /// </summary>
        /// <param name="metaFieldName">The metadata field name</param>
        /// <param name="metaFieldValue">The fixed value (use null if value comes from document property)</param>
        /// <param name="documentPropertyName">The document property name (use null if using fixed value)</param>
        /// <param name="cloudServiceProviderName">The cloud service provider name</param>
        public MetaDataMap(string? metaFieldName, string? metaFieldValue, string? documentPropertyName, string? cloudServiceProviderName)
        {
            _metaFieldName = metaFieldName;
            _metaFieldValue = metaFieldValue;
            _documentPropertyName = documentPropertyName;
            _cloudServiceProviderName = cloudServiceProviderName;
        }
    }
}