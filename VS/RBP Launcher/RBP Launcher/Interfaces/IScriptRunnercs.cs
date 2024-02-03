using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Collections.Generic;

namespace RBP_Launcher.Interfaces
{
    
    // interface used by classes running scripts in various languages
    public interface IScriptRunner
    {
        bool ExecuteScript(string scriptFilePath, List<string>? scriptArguments);
    }

}
