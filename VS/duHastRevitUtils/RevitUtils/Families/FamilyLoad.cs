//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2025, Jan Christel
// All rights reserved.

// Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

// - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
// - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
// - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
//
// This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
// In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
// or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
//
//
//


using System;
using Autodesk.Revit.DB;

namespace duHastNet.RevitUtils.Families
{
    public class FamilyLoad:duHastNet.Utils.Logging.LogActionsBase
    {
        /// <summary>
        /// place holder for the loaded family
        /// </summary>
        Family _loadedFamily = null;
        public Family LoadedFamily { 
            get { return _loadedFamily; }
            private set { _loadedFamily = value; }
        }


        /// <summary>
        /// Load a family into the document.
        /// </summary>
        /// <param name="doc">The current document.</param>
        /// <param name="familyPath">The fully qualified file path from which to load the family from.</param>
        /// <param name="overwriteExisting">Overwrite existing parameter values if true, otherwise dont. Default is overwrite existing values.</param>
        /// <param name="famSource">The source for any shared nested families already present in the project. Default is project is source.</param>
        /// <returns></returns>
        public bool LoadFamily(Document doc, string familyPath, bool overwriteExisting, FamilySource famSource = FamilySource.Project)
        {
            //wrap the action in a try catch block
            try
            {
                //get the family name from the path
                string familyName = System.IO.Path.GetFileNameWithoutExtension(familyPath);

                //set up a load option ( overwrite existing parameters, use nested shared families from the project )
                FamilyLoadOption loadOption = new FamilyLoadOption(
                    overWriteExisting:overwriteExisting,
                    familySource: famSource
                );

                // set up an action to run inside a Revit transaction
                Func<bool> actionInTranny = () =>
                {
                    try
                    {
                        //place holder for the loaded family
                        Family family = null;

                        //load the family and all its types
                        bool loadResult = doc.LoadFamily(
                            filename: familyPath,
                            familyLoadOptions: loadOption,  // overwrite parameter values etc
                            family: out family
                        );

                        //update single family instance
                        AddMessage($"Loaded family: {familyPath} with load result: {loadResult}", Utils.WPF.Stores.MessageTypes.Information);

                        // store the loaded family
                        LoadedFamily = family;

                        return loadResult;
                    }
                    catch (Exception ex)
                    {
                        //log the exception
                        AddMessage(ex.Message, Utils.WPF.Stores.MessageTypes.Error);
                        return false;
                    }
                };

                //execute the action in a transaction
                bool result = Transactions.TransactionUtils.InTransaction(
                    doc: doc,
                    transactionName: $"Load family {familyName}",
                    actionInTranny: actionInTranny
                );

                return result;
            }
            catch (Exception ex)
            {
                AddMessage(ex.Message, Utils.WPF.Stores.MessageTypes.Error);
                return false;
            }
        }


        /// <summary>
        /// Load a family symbol into the document.
        /// </summary>
        /// <param name="doc">The current document.</param>
        /// <param name="familyPath">The fully qualified file path from which to load the family from.</param>
        /// <param name="typeName">The type (symbol) name.</param>
        /// <param name="overwriteExisting">Overwrite existing parameter values if true, otherwise dont. Default is overwrite existing values.</param>
        /// <param name="famSource">The source for any shared nested families already present in the project. Default is project is source.</param>
        /// <returns></returns>
        public bool LoadFamilyType(Document doc, string familyPath, string typeName, bool overwriteExisting, FamilySource famSource = FamilySource.Project)
        {
            //wrap the action in a try catch block
            try
            {
                //get the family name from the path
                string familyName = System.IO.Path.GetFileNameWithoutExtension(familyPath);

                //set up a load option ( overwrite existing parameters, use nested shared families from the project )
                FamilyLoadOption loadOption = new FamilyLoadOption(
                    overWriteExisting: overwriteExisting,
                    familySource: famSource
                );

                // set up an action to run inside a Revit transaction
                Func<bool> actionInTranny = () =>
                {
                    try
                    {
                        //place holder for the loaded family
                        FamilySymbol familySymbol = null;

                        //load the family and all its types
                        bool loadResult = doc.LoadFamilySymbol(
                            filename: familyPath,
                            name: typeName,
                            familyLoadOptions: loadOption,  // overwrite parameter values etc
                            symbol: out familySymbol
                        );

                        //update single family instance
                        AddMessage($"Loaded family: {familyPath} with load result: {loadResult}", Utils.WPF.Stores.MessageTypes.Information);

                        // store the loaded family
                        LoadedFamily = familySymbol.Family;

                        return loadResult;
                    }
                    catch (Exception ex)
                    {
                        //log the exception
                        AddMessage(ex.Message, Utils.WPF.Stores.MessageTypes.Error);
                        return false;
                    }
                };

                //execute the action in a transaction
                bool result = Transactions.TransactionUtils.InTransaction(
                    doc: doc,
                    transactionName: $"Load family symbol {typeName} in {familyName}",
                    actionInTranny: actionInTranny
                );

                return result;
            }
            catch (Exception ex)
            {
                AddMessage(ex.Message, Utils.WPF.Stores.MessageTypes.Error);
                return false;
            }
        }
    }
}
