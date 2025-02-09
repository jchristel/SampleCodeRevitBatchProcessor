using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.UI;

namespace PushIt.Utilities
{
    public class RevitExternalEventHandlerManager
    {
        Models.RevitDataModel _revitDataModel;
        public Models.RevitDataModel RevitDataModel {
            get { return _revitDataModel; } set { _revitDataModel = value; } 
        }
        Revit.CustomExternalEvent _refreshUIDataEventHandler;
        ExternalEvent _refreshUIDataEvent;

        
        public RevitExternalEventHandlerManager()
        {
            

            // Create an instance of the CustomExternalEvent class
            _refreshUIDataEventHandler = new Utilities.Revit.CustomExternalEvent();

            // External Event for the dialog to use (to post requests)
            _refreshUIDataEvent = ExternalEvent.Create(_refreshUIDataEventHandler);
        }

        public void RaiseRefreshUIDataEvent()
        {
            // Raise the external event
            _refreshUIDataEvent.Raise();
        }

        public void DisposeEvents()
        {
            _refreshUIDataEvent.Dispose();
            _refreshUIDataEvent = null;
            _refreshUIDataEventHandler = null;
        }
    }
}
