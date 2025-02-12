using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.DB;

namespace RevitUtils
{
    public static class SharedParaUtils
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
            List<SharedParameterElement> parametersInModel = GetSharedParameters(doc);
            foreach (SharedParameterElement parameter in parametersInModel)
            {
                if (parameter.GuidValue.ToString() == parameterGUID)
                {
                    // get the binding
                    DefinitionBindingMapIterator it = doc.ParameterBindings.ForwardIterator();
                    while (it.MoveNext())
                    {
                        // get the definition
                        Definition definition = it.Key as Definition;
                        if (definition == null || definition.Name != parameter.Name) { continue; }

                        // get the binding
                        ElementBinding binding = it.Current as ElementBinding;
                        if (binding == null) { continue; }

                        // get the categories the parameter is bound to
                        CategorySet categories = binding.Categories;
                        if (categories.Size == 0) { continue; }

                        //iterate over the categories
                        CategorySetIterator categorySetIterator = categories.ForwardIterator();
                        while (categorySetIterator.MoveNext())
                        {
                            //get the category and its name
                            Category category = categorySetIterator.Current as Category;
                            if (category == null) { continue; }

                            // add name to list to be returned
                            parameterBindings.Add(category.Name);
                        }
                    }
                }
            }

            return parameterBindings;
        }


        public static string GetSharedParameterValueFromElementByGUID(Element element, string parameterGUID)
        {
            string parameterValue = null;
            IList<Parameter> parameters = element.GetOrderedParameters();
            foreach (Parameter parameter in parameters)
            {
                try
                {
                    if (parameter.GUID.ToString() == parameterGUID)
                    {
                        parameterValue = parameter.AsString();
                    }
                }
                catch (Exception)
                {
                    //ignore and continue
                }
            }
            return parameterValue;
        }


        public static string GetSharedParameterValueFromElementByElementId(Element element, ElementId parameterId)
        {
            string parameterValue = null;

            IList<Parameter> parameters = element.GetOrderedParameters();
            foreach (Parameter parameter in parameters)
            {
                try
                {
                    if (parameter.Id == parameterId)
                    {
                        if (parameter.StorageType == StorageType.String)
                        {
                            parameterValue = parameter.AsString();
                        }
                        else if (parameter.StorageType == StorageType.Double)
                        {
                            parameterValue = parameter.AsDouble().ToString();
                        }
                        else if (parameter.StorageType == StorageType.Integer)
                        {
                            parameterValue = parameter.AsInteger().ToString();
                        }
                        else
                        {
                            parameterValue = parameter.AsElementId().ToString();
                        }
                    }
                }
                catch (Exception)
                {
                    //ignore and continue
                }
            }
            return parameterValue;
        }

        public static Dictionary<string, ElementId> GetSharedParameterIdsByGUID(Document doc)
        {
            Dictionary<string, ElementId> sharedParameterIds = new Dictionary<string, ElementId>();
            List<SharedParameterElement> sharedParameters = GetSharedParameters(doc);
            foreach (SharedParameterElement sharedParameter in sharedParameters)
            {
                sharedParameterIds.Add(sharedParameter.GuidValue.ToString(), sharedParameter.Id);
            }
            return sharedParameterIds;
        }
    }
}
