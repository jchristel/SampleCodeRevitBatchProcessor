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
                new duHastNet.UI.FamilyReloaderUI.Models.RevitFamily("Furniture_2022" ,"Furniture", true),
                new duHastNet.UI.FamilyReloaderUI.Models.RevitFamily("UnitTests_m", "Generic Model", false),
                new duHastNet.UI.FamilyReloaderUI.Models.RevitFamily("Sample_Family_Five","specailty", false),
            };

            duHastNet.UI.FamilyReloaderUI.Main main = new duHastNet.UI.FamilyReloaderUI.Main(
                revitFamilies: families
            );
            var famsToReload = main.Execute();
            Console.WriteLine($"families to reload: {famsToReload.FamiliesToReload.Count}");
        }
        
    }
}
