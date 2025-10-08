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
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading.Tasks;

namespace duHastNet.DocManager.Core.Models
{
    public class MetaDataMap
    {
        /// <summary>
        /// the meta data field name
        /// </summary>
        private string? _metaFieldName;

        public string? MetaFieldName
        {
            get { return _metaFieldName; }
            set { _metaFieldName = value; }
        }

        /// <summary>
        /// The meta data field value. Null if this value is coming from a document property
        /// </summary>
        private string? _metaFieldValue;

        public string? MetaFieldValue
        {
            get { return _metaFieldValue; }
            set { _metaFieldValue = value; }
        }

        /// <summary>
        /// The matching document property name. Null if a fixed value is used
        /// </summary>
        private string? _documentPropertyName;

        public string? DocumentPropertyName
        {
            get { return _documentPropertyName; }
            set { _documentPropertyName = value; }
        }

        /// <summary>
        /// The name of the cloud service provider this meta data is for
        /// </summary>
        private string? _cloudServiceProviderName;

        public string? CloudServiceProviderName
        {
            get { return _cloudServiceProviderName; }
            set { _cloudServiceProviderName = value; }
        }


        /// <summary>
        /// class containing meta data information
        /// </summary>
        public MetaDataMap() { }
    }
}
