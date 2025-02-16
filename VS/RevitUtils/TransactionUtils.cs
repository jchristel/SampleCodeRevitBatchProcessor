using Autodesk.Revit.DB;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RevitUtils
{
    public static class TransactionUtils
    {
        public static bool inTransaction(Document doc, string transactionName, Func<bool> actionInTranny)
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
