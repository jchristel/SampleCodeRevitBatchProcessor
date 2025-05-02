using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Security.Cryptography;

namespace duHastNet.Utils.Hash
{
    public static class ComputeHashUtils
    {
        /// <summary>
        /// Convertes a set of string values into a SHA256 hash
        /// lenght is approx 22 characters
        /// </summary>
        public static string ComputeShortSHA256Hash(params string[] values)
        {
            using (SHA256 sha256 = SHA256.Create())
            {
                string combined = string.Concat(values);
                byte[] hashBytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(combined));
                string base64Hash = Convert.ToBase64String(hashBytes);

                // make it url safe
                return base64Hash.TrimEnd('=').Replace('+', '-').Replace('/', '_');
            }
        }
    }
}
