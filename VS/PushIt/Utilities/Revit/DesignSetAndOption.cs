using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.DB;

namespace PushIt.Utilities.Revit
{
    public static class DesignSetAndOptionUtils
    {

        /// <summary>
        /// returns the active design set and option name
        /// </summary>
        public static (string designSetName, string designOptionName) GetActiveDesignSetAndOptionName(Document doc)
        {
            // get the documents current design set and option
            var activeDesignOption = RevitUtils.DesignSetAndOptionsUtils.GetActiveDesignOption(doc);
            var activeDesignSet = RevitUtils.DesignSetAndOptionsUtils.GetDesignSetOfActiveDesignOption(doc);
            
            string designSetName = activeDesignSet == null ? RevitUtils.DesignSetAndOptionDefaultNames.MAIN_MODEL_DEFAULT_DESIGN_SET_NAME : activeDesignSet.Name;
            string designOptionName = activeDesignOption == null ? RevitUtils.DesignSetAndOptionDefaultNames.MAIN_MODEL_DEFAULT_DESIGN_OPTION_NAME : activeDesignOption.Name;

            return (designSetName, designOptionName);
        }
    }
}
