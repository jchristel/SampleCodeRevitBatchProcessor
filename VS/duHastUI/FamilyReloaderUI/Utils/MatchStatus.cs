using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace duHastNet.UI.FamilyReloaderUI.Utils
{
    public enum MatchStatus
    {
        SingleMatch, // just one match in file system found
        NoMatch, // no match in file system found
        MultipleMatches //multiple matches in file system found
    }
}
