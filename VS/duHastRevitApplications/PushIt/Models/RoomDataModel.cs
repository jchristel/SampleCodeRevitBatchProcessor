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
    public class RoomDataModel : RoomBase
    {
        /// <summary>
        /// List of matching rooms
        /// </summary>
        private List<RoomRevit> _matchingRevitRooms;

        /// <summary>
        /// List of matching rooms which are result of a split operation
        /// </summary>
        private List<RoomRevit> _matchingSplitRevitRooms;

        public List<RoomRevit> MatchingRevitRooms { get => _matchingRevitRooms; set => _matchingRevitRooms = value; }
        public List<RoomRevit> MatchingSplitRevitRooms { get => _matchingSplitRevitRooms; set => _matchingSplitRevitRooms = value; }

        /// <summary>
        /// Clears the list of matching rooms
        /// </summary>
        public void ClearMatchingRevitRooms()
        {
            _matchingRevitRooms.Clear();
        }

        /// <summary>
        /// Clears the list of matching rooms which are result of a split operation
        /// </summary>
        public void ClearMatchingSplitRevitRooms()
        {
            _matchingSplitRevitRooms.Clear();
        }

        /// <summary>
        /// Clears the list of matching rooms and matching split rooms
        /// </summary>
        public void ClearAllMatchingRevitRooms()
        {
            ClearMatchingRevitRooms();
            ClearMatchingSplitRevitRooms();
        }

        /// <summary>
        /// Adds a matching room to the list of matching rooms
        /// </summary>
        public void AddMatchingRevitRoom(RoomRevit revitRoom)
        {
            _matchingRevitRooms.Add(revitRoom);
        }

        /// <summary>
        /// Adds a matching room to the list of matching split rooms
        /// </summary>
        public void AddMatchingSplitRevitRoom(RoomRevit revitRoom)
        {
            _matchingSplitRevitRooms.Add(revitRoom);
        }

        /// <summary>
        /// returns a list of unique values for a given property from each matching room
        /// </summary>
        public List<string> GetUniquePropertyValueFromEachMatchingRevitRoom(string propertyName)
        {
            List<string> values = new List<string>();
            foreach (Models.RoomRevit revitRoom in MatchingRevitRooms)
            {
                Models.RoomDataProperty property = revitRoom.Properties.Find(x => x.Name == propertyName);
                if (property != null)
                {
                    if (!values.Contains(property.Value))
                        values.Add(property.Value);
                }
            }
            return values;
        }

        /// <summary>
        /// Returns a list of unique values for a given property from each matching split room
        /// </summary>
        public List<string> GetUniquePropertyValueFromEachMatchingSplitRevitRoom(string propertyName)
        {
            List<string> values = new List<string>();
            foreach (Models.RoomRevit revitRoom in MatchingSplitRevitRooms)
            {
                Models.RoomDataProperty property = revitRoom.Properties.Find(x => x.Name == propertyName);
                if (property != null)
                {
                    if (!values.Contains(property.Value))
                        values.Add(property.Value);
                }
            }
            return values;
        }

        /// <summary>
        /// Returns a list of unique values for a given property from all matching rooms and matching split rooms
        /// </summary>
        public List<string> GetUniquePropertyValueFromAllMatchingRevitRoom(string propertyName)
        {
            List<string> valuesMatchingRooms = GetUniquePropertyValueFromEachMatchingRevitRoom(propertyName);
            List<string> valuesMatchingSplitRooms = GetUniquePropertyValueFromEachMatchingSplitRevitRoom(propertyName);
            List<string> values = new List<string>();

            // add the values from the matching rooms
            foreach (string value in valuesMatchingRooms)
            {
                if (!values.Contains(value))
                    values.Add(value);
            }

            // add the values from the matching split rooms
            foreach (string value in valuesMatchingSplitRooms)
            {
                if (!values.Contains(value))
                    values.Add(value);
            }

            return values;
        }

        /// <summary>
        /// Update a read property
        /// </summary>
        /// <param name="propertyName"></param>
        /// <param name="value"></param>
        public void UpdateReadProperties()
        {
            // if there is only one matching room and no matching split rooms, update the read only properties from the matching room
            if (MatchingRevitRooms.Count == 1 && MatchingSplitRevitRooms.Count == 0)
            {
                Models.RoomRevit revitRoom = MatchingRevitRooms[0];
                foreach (Models.RoomDataProperty property in Properties)
                {
                    if (property.IsReadOnly)
                    {
                        property.Value = revitRoom.Properties.Find(x => x.Name == property.Name).Value;
                    }
                }
            }
            // if ther are no matching rooms there cant (should not be ?? )be any matching split rooms
            else if (MatchingRevitRooms.Count == 0 && MatchingSplitRevitRooms.Count == 0)
            {
                // if there is no matching room, clear the read only properties
                foreach (Models.RoomDataProperty property in Properties)
                {
                    if (property.IsReadOnly)
                    {
                        property.Value = "";
                    }
                }
            }
            else
            // if there are multiple matching rooms, put 'varies' into read only properties iv values are different between matching rooms
            {
                foreach (Models.RoomDataProperty property in Properties)
                {
                    if (property.IsReadOnly)
                    {
                        // get the value of this property from each matching room...if its the same for each display that value
                        // otherwise display 'varies'

                        // get the unique values for this property from each matching room
                        List<string> propertyValues = GetUniquePropertyValueFromAllMatchingRevitRoom(property.Name);

                        //check if more than one value
                        if (propertyValues.Count == 1)
                        {
                            property.Value = propertyValues[0];
                        }
                        else
                        {
                            property.Value = "varies";
                        }
                    }
                }
            }
        }

        /// <summary>
        /// Check if room conflicts by id value
        /// </summary>
        /// <param name="other"></param>
        /// <returns></returns>
        public bool ConflictsById(RoomDataModel other)
        {
            if (other == null) return false;
            else if (other.Id.Value != Id.Value) { return false; }
            else
            {
                return true;
            }
        }

        /// <summary>
        /// Check if room conflicts by properties
        /// </summary>
        /// <param name="other"></param>
        /// <returns>True if all properties match, otherwise False</returns>
        public bool ConflictsByProperties(RoomDataModel other)
        {
            if (other == null) return false;
            else if (other.Properties.Count != Properties.Count) { return false; }
            else
            {
                foreach (var property in Properties)
                {
                    if (property.Value != other.Properties.Find(x => x.Name == property.Name).Value)
                    {
                        return false;
                    }
                }
                return true;
            }
        }

        /// <summary>
        /// Returns a string of all the properties that are not read only in ascending order
        /// </summary>
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


        public RoomDataModel()
        {
            // initialize the list of matching rooms
            _matchingRevitRooms = new List<RoomRevit>();
            // initialize the list of matching split rooms
            _matchingSplitRevitRooms = new List<RoomRevit>();
            //initialise the ID value
            Id = new RoomDataProperty("Id", string.Empty, string.Empty, string.Empty, false, false);
        }

        public RoomDataModel(RoomDataProperty id, List<RoomDataProperty> otherProperties)
        {
            // set the id and other properties
            Id = id;
            Properties = otherProperties;

            // initialize the list of matching rooms
            _matchingRevitRooms = new List<RoomRevit>();

            // initialize the list of matching split rooms
            _matchingSplitRevitRooms = new List<RoomRevit>();
        }
    }
}
