using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace duHast.AtTheLibrary.Models
{
    public class FamilyDataModel
    {
        /// <summary>
        /// Family ID ,ade up from family name and category
        /// </summary>
        public FamilyDataProperty Id { get; private set; }

        public FamilyDataProperty FamilyName { get; private set; }
        public FamilyDataProperty FamilyCategory { get; private set; }
        public FamilyDataProperty FamilyTypeName { get; private set; }

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

        public void AddMatchingFamily(FamilyRevit family)
        {
            _matchingRevitFamilies.Add(family);
        }

        public FamilyDataModel(FamilyDataProperty id, FamilyDataProperty familyName, FamilyDataProperty familyCategory, FamilyDataProperty familyTypeName,  List<FamilyDataProperty> otherProperties)
        {
            // set the id and other properties
            Id = id;
            FamilyName = familyName;
            FamilyCategory = familyCategory;
            FamilyTypeName = familyTypeName;

            if (otherProperties != null)
            {
                _properties = otherProperties;
            }

            // initialize the list of matching familiesq
            _matchingRevitFamilies = new List<FamilyRevit>();
        }
    }
}
