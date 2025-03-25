using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace duHast.AtTheLibrary.Models
{
    public class FamilyDataProperty
    {
        private string _name;
        private string _value;

        public FamilyDataProperty(string name,  string value)
        {
            _name = name;
            _value = value;
        }
    }
}
