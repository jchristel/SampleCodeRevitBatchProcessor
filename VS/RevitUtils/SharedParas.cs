using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.DB;

namespace RevitUtils
{
    public static class SharedParas
    {

        public static List<SharedParameterElement> GetSharedParameters(Document doc)
        {
            List<SharedParameterElement> parameters = new List<SharedParameterElement>();
            FilteredElementCollector collector = new FilteredElementCollector(doc);
            collector.OfClass(typeof(SharedParameterElement));
            foreach (SharedParameterElement parameter in collector)
            {
                parameters.Add(parameter);
            }
            return parameters;
        }




        public static List<string> ParameterBindingsByGUID(Document doc, string parameterGUID)
        {
            List<string> parameterBindings = new List<string>();

            // get all parameters in the model
            List< SharedParameterElement > parametersInModel = GetSharedParameters(doc);
            foreach (SharedParameterElement parameter in parametersInModel)
            {
                if (parameter.GuidValue.ToString() == parameterGUID)
                {
                    // get the binding
                    DefinitionBindingMapIterator it = doc.ParameterBindings.ForwardIterator();
                    while (it.MoveNext())
                    {
                        Definition definition = it.Key as Definition;
                        if (definition != null)
                        {
                            if (definition.Name == parameterGUID)
                            {
                                ElementBinding binding = it.Current as ElementBinding;
                                if (binding != null)
                                {
                                    parameterBindings.Add(binding.GetType().ToString());
                                }
                            }
                        }
                    }
                }
            }


            return parameterBindings;
        }
    }
}
