using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RevitUtils
{
    public static class DesignSetAndOptionDefaultNames
    {
        // default key names for design set and design option 
        public static string DESIGN_SET_NAME = "designSetName";
        public static string DESIGN_OPTION_NAME = "designOptionName";
        public static string DESIGN_OPTION_IS_PRIMARY = "designOptionIsPrimary";

        // default names for design set and design option of the mmain model ( no design set or design option is active)
        public static string MAIN_MODEL_DEFAULT_DESIGN_SET_NAME = "-";
        public static string MAIN_MODEL_DEFAULT_DESIGN_OPTION_NAME = "Main Model";
    }
}
