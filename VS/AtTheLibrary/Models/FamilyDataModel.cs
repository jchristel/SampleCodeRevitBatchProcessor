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
        /// Family ID, must be unique
        /// </summary>
        public FamilyDataProperty Id { get; set; }

        /// <summary>
        /// Any other data model properties
        /// </summary>
        List<FamilyDataProperty> _properties = new List<FamilyDataProperty>();

        public List<FamilyDataProperty> Properties { get => _properties; }

        public FamilyDataModel(FamilyDataProperty id, List<FamilyDataProperty> otherProperties)
        {
            // set the id and other properties
            Id = id;
            _properties = otherProperties;
        }
    }
}
