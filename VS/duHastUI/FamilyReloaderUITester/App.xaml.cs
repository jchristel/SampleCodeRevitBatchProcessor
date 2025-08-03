using System.Configuration;
using System.Data;
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
                new duHastNet.UI.FamilyReloaderUI.Models.RevitFamily("family two" ,"joinery", true,2),
                new duHastNet.UI.FamilyReloaderUI.Models.RevitFamily("family three", "Generic Model", false,3)
            };

            duHastNet.UI.FamilyReloaderUI.Main main = new duHastNet.UI.FamilyReloaderUI.Main(
                revitFamilies: families
            );
            var settings = main.Execute();
        }
        
    }

}
