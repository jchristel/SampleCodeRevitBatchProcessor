using System;
using System.Security.Cryptography;
using System.Text;

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
            string combined = string.Concat(values);
            byte[] hashBytes = SHA256.HashData(Encoding.UTF8.GetBytes(combined));
            string base64Hash = Convert.ToBase64String(hashBytes);

            // make it url safe
            return base64Hash.TrimEnd('=').Replace('+', '-').Replace('/', '_');
        }
    }
}
