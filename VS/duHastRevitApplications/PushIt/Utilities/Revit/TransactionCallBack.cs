using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Autodesk.Revit.DB;

namespace duHastNet.PushIt.Utilities.Revit
{
    public class TransactionCallBack:ICentralLockedCallback
    {

        bool _shouldWaitForLock = false;
        public bool ShouldWaitForLockAvailability()
        {
            return _shouldWaitForLock;
        }

        public TransactionCallBack(bool shouldWaitForLock)
        {
            _shouldWaitForLock = shouldWaitForLock;
        }
    }
}
