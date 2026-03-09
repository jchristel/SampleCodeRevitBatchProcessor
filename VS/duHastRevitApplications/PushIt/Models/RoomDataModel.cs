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

        public List<RoomRevit> MatchingRevitRooms { get => _matchingRevitRooms; set => _matchingRevitRooms = value; }

        /// <summary>
        /// Clears the list of matching rooms
        /// </summary>
        public void ClearMatchingRevitRooms()
        {
            _matchingRevitRooms.Clear();
        }

        /// <summary>
        /// Adds a matching room to the list of matching rooms
        /// </summary>
        public void AddMatchingRevitRoom(RoomRevit revitRoom)
        {
            _matchingRevitRooms.Add(revitRoom);
        }

        /// <summary>
        /// returns a list of unique values for a given property from each matching room
        /// </summary>
        public List<string> GetUniquePropertyValueFromEachMatchingRevitRoom(string propertyName)
        {
            List<string> values = [];
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
        /// Updates property values that are sourced from Revit rather than the data source.
        /// This covers two cases:
        /// <list type="bullet">
        ///   <item><description>
        ///     <see cref="RoomDataProperty.IsReadOnly"/> — always read from Revit (e.g. computed
        ///     values like area that Revit owns entirely).
        ///   </description></item>
        ///   <item><description>
        ///     <see cref="RoomDataProperty.RevitTakesPrecedenceAfterInitialPush"/> — written from
        ///     the data source on the first push, but thereafter the value stored in Revit is
        ///     treated as authoritative and overrides the data-source value on every refresh.
        ///   </description></item>
        /// </list>
        /// If one matching Revit room exists, both property kinds are updated from it.
        /// If no match exists, both property kinds are cleared to empty string.
        /// Split rooms are standalone <see cref="RoomDataModel"/> records and use this same logic.
        /// </summary>
        /// <param name="isSplitRoom">
        /// When <c>true</c> the room is a split room and properties marked
        /// <see cref="RoomDataProperty.RevitTakesPrecedenceAfterInitialPush"/> will be read back
        /// from Revit.  For regular SoA and new rooms this flag should be <c>false</c> so that
        /// only <see cref="RoomDataProperty.IsReadOnly"/> properties are refreshed from Revit.
        /// </param>
        public void UpdateReadProperties(bool isSplitRoom = false)
        {
            if (MatchingRevitRooms.Count == 1)
            {
                Models.RoomRevit revitRoom = MatchingRevitRooms[0];
                foreach (Models.RoomDataProperty property in Properties)
                {
                    bool shouldReadFromRevit = property.IsReadOnly
                        || (property.RevitTakesPrecedenceAfterInitialPush && isSplitRoom);

                    if (shouldReadFromRevit)
                    {
                        Models.RoomDataProperty revitProperty = revitRoom.Properties.Find(x => x.Name == property.Name);
                        if (revitProperty != null)
                            property.Value = revitProperty.Value;
                    }
                }
            }
            else if (MatchingRevitRooms.Count == 0)
            {
                foreach (Models.RoomDataProperty property in Properties)
                {
                    bool shouldClear = property.IsReadOnly
                        || (property.RevitTakesPrecedenceAfterInitialPush && isSplitRoom);

                    if (shouldClear)
                        property.Value = "";
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
            _matchingRevitRooms = [];
            //initialise the ID value
            Id = new RoomDataProperty("Id", string.Empty, string.Empty, string.Empty, false, false, true);
        }

        public RoomDataModel(RoomDataProperty id, List<RoomDataProperty> otherProperties)
        {
            // set the id and other properties
            Id = id;
            Properties = otherProperties;

            // initialize the list of matching rooms
            _matchingRevitRooms = [];
        }
    }
}
