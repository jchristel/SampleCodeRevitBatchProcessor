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

using duHastNet.DocManager.Core.Models.MetaData;

namespace duHastNet.DocManager.UI.Shared.ViewModels.CloudProviderControls
{
    /// <summary>
    /// ViewModel wrapper for MetaDataMap to provide display properties for ListView
    /// </summary>
    public class MetaDataMapViewModel
    {
        /// <summary>
        /// The underlying MetaDataMap model
        /// </summary>
        public MetaDataMap Model { get; }

        /// <summary>
        /// Gets the metadata field name
        /// </summary>
        public string MetaFieldName => Model.MetaFieldName ?? string.Empty;

        /// <summary>
        /// Gets the value or property name for display
        /// Shows either the static value or the document property name
        /// </summary>
        public string ValueOrProperty
        {
            get
            {
                if (!string.IsNullOrWhiteSpace(Model.MetaFieldValue))
                {
                    return Model.MetaFieldValue;
                }
                else if (!string.IsNullOrWhiteSpace(Model.DocumentPropertyName))
                {
                    return Model.DocumentPropertyName;
                }
                else if (!string.IsNullOrWhiteSpace(Model.FilePropertyName))
                {
                    return $"[File].{Model.FilePropertyName}";
                }
                else
                {
                    return "(Not Set)";
                }
            }
        }

        /// <summary>
        /// Gets the mapping type for display
        /// </summary>
        public string MappingType
        {
            get
            {
                if (!string.IsNullOrWhiteSpace(Model.MetaFieldValue))
                {
                    return "Static Value";
                }
                else if (!string.IsNullOrWhiteSpace(Model.DocumentPropertyName))
                {
                    return "Document Property";
                }
                else if (!string.IsNullOrWhiteSpace(Model.FilePropertyName))
                {
                    return "From File";
                }
                else
                {
                    return "None";
                }
            }
        }

        /// <summary>
        /// Constructor
        /// </summary>
        /// <param name="model">The underlying MetaDataMap model</param>
        public MetaDataMapViewModel(MetaDataMap model)
        {
            Model = model ?? throw new ArgumentNullException(nameof(model));
        }

        /// <summary>
        /// Creates a string representation for debugging
        /// </summary>
        public override string ToString()
        {
            return $"{MetaFieldName}: {ValueOrProperty} ({MappingType})";
        }
    }
}
