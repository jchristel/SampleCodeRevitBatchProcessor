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
                new duHastNet.UI.FamilyReloaderUI.Models.RevitFamily("family One", "Casework",false,1),
                new duHastNet.UI.FamilyReloaderUI.Models.RevitFamily("Furniture_2022" ,"Furniture", true,2),
                new duHastNet.UI.FamilyReloaderUI.Models.RevitFamily("UnitTests_m", "Generic Model", false,3),
                new duHastNet.UI.FamilyReloaderUI.Models.RevitFamily("Sample_Family_Five","specailty", false,4),
            };

            duHastNet.UI.FamilyReloaderUI.Main main = new duHastNet.UI.FamilyReloaderUI.Main(
                revitFamilies: families
            );
            var famsToReload = main.Execute();
            Console.WriteLine($"families to reload: {famsToReload.FamiliesToReload.Count}");
        }
        
    }
}
