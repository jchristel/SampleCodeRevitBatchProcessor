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
using System.Linq;

namespace duHastNet.AtTheLibrary.Models
{
    public class FamilyDataModel
    {
        /// <summary>
        /// Family ID , up from family name and category
        /// </summary>
        public FamilyDataProperty Id { get; private set; }

        public FamilyDataProperty FamilyFilePath { get; private set; }
        public FamilyDataProperty FamilyName { get; private set; }
        public FamilyDataProperty FamilyCategory { get; private set; }
        public FamilyDataProperty FamilyTypeName { get; private set; }
        public bool HasTypeCatalogueFile { get; set; }

        /// <summary>
        /// Any other data model properties
        /// </summary>
        List<FamilyDataProperty> _properties = new List<FamilyDataProperty>();

        public List<FamilyDataProperty> Properties { get => _properties; }

        /// <summary>
        /// List of matching families in the file
        /// </summary>
        private List<FamilyRevit> _matchingRevitFamilies;
        public List<FamilyRevit> MatchingRevitFamilies { get => _matchingRevitFamilies; private set => _matchingRevitFamilies = value; }

        public void AddProperty(FamilyDataProperty property)
        {
            _properties.Add(property);
        }

        /// <summary>
        /// returns all properties from the family
        /// </summary>
        /// <returns></returns>
        public List<FamilyDataProperty> GetAllProperties()
        {
            return _properties;
        }

        /// <summary>
        /// Normalises a property name for fuzzy matching by removing all underscores
        /// and spaces, enabling comparison across XML-serialised names (underscores)
        /// and Revit parameter names (spaces).
        /// e.g. "Assembly Code", "Assembly_Code" and "Assembly_Code " all normalise
        /// to "AssemblyCode".
        /// </summary>
        private static string NormalisePropertyName(string name)
        {
            return name.Replace("_", "").Replace(" ", "");
        }

        /// <summary>
        /// Returns the property matching the given name.
        /// First attempts an exact (ordinal, case-insensitive) match.
        /// If that fails, falls back to a normalised comparison that treats
        /// underscores and spaces as equivalent, accommodating the mismatch
        /// between XML-serialised names ("Assembly_Code") and Revit parameter
        /// names ("Assembly Code").
        /// </summary>
        /// <param name="name">The property name to look up.</param>
        /// <returns>The matching property, or null if none found.</returns>
        public FamilyDataProperty GetPropertyByName(string name)
        {
            // 1. exact match (case-insensitive)
            var exact = _properties.FirstOrDefault(x =>
                string.Equals(x.Name, name, System.StringComparison.OrdinalIgnoreCase));
            if (exact != null)
                return exact;

            // 2. fallback: normalise both sides and compare
            string normalisedSearch = NormalisePropertyName(name);
            return _properties.FirstOrDefault(x =>
                string.Equals(NormalisePropertyName(x.Name), normalisedSearch, System.StringComparison.OrdinalIgnoreCase));
        }

        public void AddMatchingFamily(FamilyRevit family)
        {
            _matchingRevitFamilies.Add(family);
        }

        public FamilyDataModel(
            FamilyDataProperty id,
            FamilyDataProperty familyFilePath,
            FamilyDataProperty familyName,
            FamilyDataProperty familyCategory,
            FamilyDataProperty familyTypeName,
            bool hasTypeCatalogueFile,
            List<FamilyDataProperty> otherProperties)
        {
            // set the id and other properties
            Id = id;
            FamilyFilePath = familyFilePath;
            FamilyName = familyName;
            FamilyCategory = familyCategory;
            FamilyTypeName = familyTypeName;
            HasTypeCatalogueFile = hasTypeCatalogueFile;

            if (otherProperties != null)
            {
                _properties = otherProperties;
            }

            // initialize the list of matching familiesq
            _matchingRevitFamilies = new List<FamilyRevit>();
        }
    }
}
