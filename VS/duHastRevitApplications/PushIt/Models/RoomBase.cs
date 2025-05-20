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

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace duHastNet.PushIt.Models
{
    public class RoomBase
    {

        /// <summary>
        /// Room ID, must be unique
        /// </summary>
        public RoomDataProperty Id { get; set; }

        /// <summary>
        /// Any other properties
        /// </summary>
        private List<RoomDataProperty> _properties = new List<RoomDataProperty>();

        /// <summary>
        /// room properties list
        /// </summary>
        public List<RoomDataProperty> Properties { 
            get => _properties; 
            set => _properties = value;
        }

        /// <summary>
        /// Get the value of a property by its name. If the property does not exist, return "N/A"
        /// if the property contains a new line character it will be replaced with an _
        /// </summary>
        /// <param name="propertyName"></param>
        /// <returns></returns>
        public string GetPropertyValueByName(string propertyName)
        {
            //check the ID field first:
            if (Id.Name == propertyName)
            {
                return Id.Value;
            }

            // get the property from the list of properties
            Models.RoomDataProperty property = Properties.Find(x => x.Name == propertyName);
            if (property != null)
            {
                // check if there is a new row character, if so replace with an underscore
                string modifiedString = property.Value.Replace("\r\n", "_").Replace("\n", "_");
                //return the modified string
                return modifiedString;
            }
            else
            {
                // if the property is not found, return an empty string
                return $"Property {propertyName} does not exist on room: {Id.Value}";
            }
        }

        /// <summary>
        /// Get the value of a property by its parameter guid. If the property does not exist, return "N/A"
        /// if the property contains a new line character it will be replaced with an _
        /// </summary>
        /// <param name="propertyGUID"></param>
        /// <returns></returns>
        public string GetPropertyValueByGUID(string propertyGUID)
        {
            //check the id field first
            if (Id.ParameterGUID == propertyGUID)
                return Id.Value;

            // get the property from the list of properties
            Models.RoomDataProperty property = Properties.Find(x => x.ParameterGUID == propertyGUID);
            if (property != null)
            {
                // check if there is a new row character, if so replace with an underscore
                string modifiedString = property.Value.Replace("\r\n", "_").Replace("\n", "_");
                //return the modified string
                return modifiedString;
            }
            else
            {
                // if the property is not found, return an empty string
                return $"Property {propertyGUID} does not exist on room: {Id.Value}";
            }
        }

        public RoomBase() {
            //initialise the ID value
            Id = new RoomDataProperty("Id", string.Empty, string.Empty, string.Empty, false, false);

        }
    }
}
