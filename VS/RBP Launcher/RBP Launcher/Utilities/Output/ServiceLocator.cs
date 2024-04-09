using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RBP_Launcher.Utilities.Output
{
    public static class ServiceLocator
    {
        private static Interfaces.IOutputObserver? _outputObserver;

        public static Interfaces.IOutputObserver? OutputObserver
        {
            get { return _outputObserver; }
            set { _outputObserver = value; }
        }
    }
}
