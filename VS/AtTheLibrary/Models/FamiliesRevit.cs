using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace duHast.AtTheLibrary.Models
{
    public class FamiliesRevit
    {
        Models.FamilyDataProperty _id;
        public Models.FamilyDataProperty Id { get => _id; set => _id = value; }

        int _revitElementId;
        public int RevitElementId { get => _revitElementId; set => _revitElementId = value; }
    }
}
