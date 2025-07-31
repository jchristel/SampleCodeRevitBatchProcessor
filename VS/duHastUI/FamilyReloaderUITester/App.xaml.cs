using System;
using System.Collections.Generic;
using System.Configuration;
using System.Data;
using System.Linq;
using System.Threading.Tasks;
using System.Windows;

namespace FamilyReloaderUITester
{
    /// <summary>
    /// Interaction logic for App.xaml
    /// </summary>
    public partial class App : Application
    {

        public App()
        {
            List<duHastNet.UI.FamilyReloaderUI.Models.RevitFamily> families = new List<duHastNet.UI.FamilyReloaderUI.Models.RevitFamily>
            {
                new duHastNet.UI.FamilyReloaderUI.Models.RevitFamily("family One", "Casework",false),
                new duHastNet.UI.FamilyReloaderUI.Models.RevitFamily("family two" ,"joinery", true),
                new duHastNet.UI.FamilyReloaderUI.Models.RevitFamily("family three", "Generic Model", false)
            };

            duHastNet.UI.FamilyReloaderUI.Main main = new duHastNet.UI.FamilyReloaderUI.Main(
                revitFamilies: families
            );
            var settings = main.Execute();
        }
        
    }
}
