using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PushIt.Utilities
{
    public interface IRoomProperty
    {
        string Value { get; }
        string Name { get; }
        string ParameterGUID { get; }
        string ParameterName { get; }
    }
}
