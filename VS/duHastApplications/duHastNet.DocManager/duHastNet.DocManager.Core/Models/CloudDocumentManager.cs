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


using duHastNet.DocManager.Core.Models.MetaData;

namespace duHastNet.DocManager.Core.Models
{
    public class CloudDocumentManager
    {
        /// <summary>
        /// A class representing an interface to a cloud document manager
        /// most likely to be a text file telling the cloud document manager what to do with files uploaded
        /// In the moment only aconex is supported
        /// may be extended in the future
        /// </summary>
        /// 

        #region Events

        /// <summary>
        /// Event raised when metadata mappings have been modified externally
        /// (e.g., when custom fields are deactivated and their mappings are removed)
        /// </summary>
        public event EventHandler? MappingsChanged;

        #endregion Events

        #region properties
        private Interfaces.ICloudMetaData? _metaDataMapper;
        
        public Interfaces.ICloudMetaData? MetaDataMapper
        {
            get => _metaDataMapper;
            set => _metaDataMapper = value;
        }

        /// <summary>
        /// Indicates whether the cloud document manager integration is enabled
        /// </summary>
        private bool _cloudDocumentManagerEnabled = false;
        public bool CloudDocumentManagerEnabled
        {
            get => _cloudDocumentManagerEnabled;
            set => _cloudDocumentManagerEnabled = value;
        }

        #endregion properties

        #region Constructor

        public CloudDocumentManager()
        {

            // Don't create a default mapper - let the UI/ViewModel create one when user selects a provider
            // This allows the "None" selection to work properly in the UI
            MetaDataMapper = null;
        }

        #endregion Constructor

        #region Methods

        /// <summary>
        /// Raises the MappingsChanged event
        /// Called externally when metadata mappings are modified (e.g., after cleanup)
        /// </summary>
        public void RaiseMappingsChanged()
        {
            MappingsChanged?.Invoke(this, EventArgs.Empty);
        }

        #endregion Methods
    }
}
