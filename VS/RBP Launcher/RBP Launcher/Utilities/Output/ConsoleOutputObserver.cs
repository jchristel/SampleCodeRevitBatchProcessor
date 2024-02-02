using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RBP_Launcher.Utilities.Output
{
    // Console observer implementation
    public class ConsoleOutputObserver : RBP_Launcher.Interfaces.IOutputObserver
    {
        public void Update(string message)
        {
            Console.WriteLine(message);
        }
    }
}
