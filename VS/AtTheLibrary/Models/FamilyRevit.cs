using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace duHastNet.AtTheLibrary.Models
{
    public class FamilyRevit
    {
        Models.FamilyDataProperty _id;
        public Models.FamilyDataProperty Id { get => _id; set => _id = value; }

        public FamilyDataProperty FamilyName { get; private set; }
        public FamilyDataProperty FamilyCategory { get; private set; }
        public FamilyDataProperty FamilyTypeName { get; private set; }


        int _revitElementId;
        public int RevitElementId { get => _revitElementId; set => _revitElementId = value; }

        public FamilyRevit(FamilyDataProperty id, FamilyDataProperty familyName, FamilyDataProperty familyCategory, FamilyDataProperty familyTypeName)
        {
            Id = id;
            FamilyName = familyName;
            FamilyCategory = familyCategory;
            FamilyTypeName = familyTypeName;
        }
    }
}
