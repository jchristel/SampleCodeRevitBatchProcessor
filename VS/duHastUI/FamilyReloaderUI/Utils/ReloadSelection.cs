using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;

namespace duHastNet.UI.FamilyReloaderUI.Utils
{
    public class ReloadSelection
    {

        private List<duHastNet.UI.FamilyReloaderUI.Models.RevitFamily> _familiesToReload;

        public List<duHastNet.UI.FamilyReloaderUI.Models.RevitFamily> FamiliesToReload
        {
            get { return _familiesToReload; }
        }

        public ReloadSelection() 
        {
            _familiesToReload = new List<Models.RevitFamily>();
        }


        public void AddFamily(duHastNet.UI.FamilyReloaderUI.Models.RevitFamily family)
        {
            _familiesToReload.Add(family);
        }
    }
}

