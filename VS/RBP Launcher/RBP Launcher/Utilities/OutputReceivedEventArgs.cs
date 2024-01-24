using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RBP_Launcher.Utilities
{
    public class OutputReceivedEventArgs
    {
        public string Output { get; }

        public OutputReceivedEventArgs(string output)
        {
            Output = output;
        }
    }
}
