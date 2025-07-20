using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace duHastNet.AtTheLibrary.Models
{
    public class Constants
    {

        public const string ColumnHeaderFamilyId = "Id";
        public const string ColumnHeaderFamilyCount = "Count";
        public const string ColumnHeaderFamilyName = "Family Name";
        public const string ColumnHeaderFamilyCategory = "Family Category";
        public const string ColumnHeaderFamilyTypeName = "Family Type Name";


        public static readonly Dictionary<string, string> ColumnFamiliesInfo = new Dictionary<string, string>
        {
            {ColumnHeaderFamilyId.Replace(" ",""), ColumnHeaderFamilyId},
            {ColumnHeaderFamilyCount.Replace(" ",""), ColumnHeaderFamilyCount},
            {ColumnHeaderFamilyName.Replace(" ",""), ColumnHeaderFamilyName},
            {ColumnHeaderFamilyCategory.Replace(" ",""), ColumnHeaderFamilyCategory},
            {ColumnHeaderFamilyTypeName.Replace(" ",""), ColumnHeaderFamilyTypeName},
        };
    }
}
