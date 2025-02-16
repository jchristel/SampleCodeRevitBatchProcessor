using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.DB;

namespace PushIt.RevitActions
{
    public interface IRevitAction
    {
        
        Models.RevitDataModel RevitModel { get; }
       
        void Execute(Document doc);

    }
}
