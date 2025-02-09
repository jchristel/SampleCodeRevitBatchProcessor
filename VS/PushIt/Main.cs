using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.ApplicationServices;
using Autodesk.Revit.Attributes;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using Autodesk.Revit.UI.Selection;
using Autodesk.Revit.DB.Architecture;
using PushIt.Views;


namespace PushIt
{
    [Transaction(TransactionMode.Manual)]
    [Regeneration(RegenerationOption.Manual)]
    public class Main : IExternalCommand
    {
        Models.RevitDataModel _revitDataModel = new Models.RevitDataModel();
        Stores.NavigationStore _navigationStore = new Stores.NavigationStore();
        Stores.MessageStore _messageStore = new Stores.MessageStore();

        public Result Execute(ExternalCommandData commandData, ref string message, ElementSet elements)
        {
            //Get application and document objects
            UIApplication uiapp = commandData.Application;
            Document doc = uiapp.ActiveUIDocument.Document;



            // get room data from file
            string dataPath = @"C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\PushIt\Testdata\20250205_CSB.csv";

            // add rooms to RevitDataModel
            List<Models.RoomsDataModel> rooms = GetRooms(dataPath);
            foreach (Models.RoomsDataModel room in rooms)
            {
                _revitDataModel.AddRoom(room);
            }

            TaskDialog td = new TaskDialog("TaskDialog Demonstration by Spiderinnet");
            td.Title = "This is 'Title'.";
            td.TitleAutoPrefix = true;
            td.AllowCancellation = true;
            td.MainInstruction = "This is 'MainInstruction'.";
            td.MainContent = "Found rooms:" + (rooms.Count).ToString();
            td.FooterText = "This is 'FooterText'.";
            td.ExpandedContent = "This is 'ExpandedContent'.\nLine1: blar blar...\nLine2: blar blar...\nLine3: blar blar...";

            // Dialog showup stuffs
            TaskDialogResult tdRes = td.Show();

            //RoomsSelection roomsSelection = new RoomsSelection();
            //roomsSelection.Show();

            //set up the navigation store
            _navigationStore.CurrentViewModel = CreateRoomsSelectionViewModel();

            //show the main window
            MainWindow mainWindow = new MainWindow()
            {
                DataContext = new ViewModels.MainViewModel(_navigationStore)
            };
            mainWindow.Show();

            return Result.Succeeded;

        }

        private ViewModels.RoomsSelectionViewModel CreateRoomsSelectionViewModel()
        {
            return new ViewModels.RoomsSelectionViewModel(
                _revitDataModel, _navigationStore, _messageStore);
        }

        public List<Models.RoomsDataModel> GetRooms(string dataPath)
        {
            List<Models.RoomsDataModel> rooms = Utilities.ReadRoomsData.GetRoomsData(dataPath);
            return rooms;
        }
    }
}
