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

using Autodesk.Revit.DB;
using System;

namespace duHast.RevitUtils.Transactions
{
    public static class TransactionUtils
    {
        /// <summary>
        /// Excutes an action in a transaction.
        /// </summary>
        /// <param name="doc">The document to execute the transaction in.</param>
        /// <param name="transactionName">The name of the transaction.</param>
        /// <param name="actionInTranny">The action to execute in the transaction. ( can not accept any args )</param>
        /// <returns>True if the action was executed successfully, otherwise false. If an excption occurrs during the transaction, it will be rolled back.</returns>
        public static bool InTransaction(Document doc, string transactionName, Func<bool> actionInTranny)
        {
            try
            {
                Transaction tranny = new Transaction(doc, transactionName);

                try
                {
                    tranny.Start();
                    bool flagAction = actionInTranny();
                    tranny.Commit();
                    return flagAction;
                }
                catch (Exception)
                {
                    if (tranny != null && tranny.HasStarted())
                    {
                        tranny.RollBack();
                    }
                    return false;
                }
            }
            catch (Exception)
            {
                return false;
            }
        }
    }
}
