using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.Models
{
    public class CategoryDataModel
    {
        string _name;

        public string Name => _name;

        public CategoryDataModel(string name)
        {
            _name = name;
        }
    }
}
