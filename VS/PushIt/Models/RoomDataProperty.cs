using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.Models
{
    public class RoomDataProperty
    {
        private string _name;
        private string _parameterGUID;
        private string _parameterName;
        private string _value;

        public string Value { get => _value; }
        public string Name { get => _name; }
        public string ParameterGUID { get => _parameterGUID; }
        public string ParameterName { get => _parameterName; }




        public RoomDataProperty(string name, string parameterGUID, string parameterName, string value)
        {
            _name = name;
            _parameterGUID = parameterGUID;
            _parameterName = parameterName;
            _value = value;
        }

    }
}
