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

namespace duHastNet.PushIt.Models
{
    public class RoomRevit : RoomBase
    {
        Models.RoomDataProperty _id;
        List<Models.RoomDataProperty> _properties;

        string _designSet;
        string _designOption;
        bool _designOptionIsPrimary;
        int _revitElementId;

        public string DesignSet { get => _designSet; set => _designSet = value; }
        public string DesignOption { get => _designOption; set => _designOption = value; }
        public bool DesignOptionIsPrimary { get => _designOptionIsPrimary; set => _designOptionIsPrimary = value; }
        public int RevitElementId { get => _revitElementId; set => _revitElementId = value; }

        public string GetWritePropertiesAsString()
        {
            string properties = "";

            //get the properties that are not read only in ascending order
            var sortedProperties = Properties.FindAll(x => !x.IsReadOnly);
            sortedProperties.Sort((x, y) => x.Name.CompareTo(y.Name));

            //loop through the properties and add them to the string
            foreach (var property in sortedProperties)
            {
                if (!property.IsReadOnly)
                {
                    properties += property.Name + ": " + property.Value + "\n";
                }
            }
            return properties;
        }


        public RoomRevit() { }

        public RoomRevit(Models.RoomDataProperty id, List<Models.RoomDataProperty> properties, string designSet, string designOption, bool designOptionIsPrimary, int revitElementId)
        {
            // set the id and other properties
            Id = id;
            Properties = properties;


            _designSet = designSet;
            _designOption = designOption;
            _designOptionIsPrimary = designOptionIsPrimary;
            _revitElementId = revitElementId;
        }
    }
}
