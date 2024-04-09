using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RBP_Launcher.Interfaces
{
    // Define an interface for observers
    public interface IOutputObserver
    {
        void Update(string message);
    }
}
