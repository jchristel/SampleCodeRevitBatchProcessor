// BSD License - Copyright 2025, Jan Christel

using duHastNet.PushIt.Models;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using duHastNet.PushIt.Interfaces;

namespace duHastNet.PushIt.Utilities
{
    /// <summary>
    /// PoC data source that connects to the drofus REST API using an API-key token.
    ///
    /// REVIT CONTEXT NOTE: All HTTP calls use synchronous WebClient / HttpWebRequest
    /// rather than HttpClient.GetAsync, because RevitTask.RunAsync already provides
    /// a background thread and .GetAwaiter().GetResult() on top of that would risk
    /// a deadlock.  The synchronous path is safe and simple here.
    ///
    /// PoC scope: GetRoomsData returns an EMPTY list — the only outcome surfaced to
    /// the user is the room count stored on DrofusDataSourceSettings.LastRoomCount.
    /// Full room mapping is a future step.
    /// </summary>
    public class DrofusDataSource : IDataSource
    {
        // drofus REST API base — token is sent as "Reference {token}" per their docs.
        // The room list endpoint is GET /api/{database}/rooms
        private const string BaseUrl = "https://api.drofus.com";

        /// <inheritdoc/>
        /// <remarks>
        /// Makes a synchronous GET /api/{database}/rooms call.
        /// On success stores the count in settings.DataSource.Drofus.LastRoomCount.
        /// Always returns an empty list (PoC — mapping not implemented).
        /// Throws <see cref="InvalidOperationException"/> if credentials are missing.
        /// </remarks>
        public List<RoomDataModel> GetRoomsData(DataSourceSettings settings)
        {
            var drofus = settings?.Drofus
                ?? throw new InvalidOperationException(
                    "drofus data source selected but no credentials are configured.");

            if (string.IsNullOrWhiteSpace(drofus.ApiToken))
                throw new InvalidOperationException("drofus API token is empty.");

            if (string.IsNullOrWhiteSpace(drofus.DatabaseName))
                throw new InvalidOperationException("drofus database name is empty.");

            string url = $"{BaseUrl}/api/{drofus.DatabaseName}/rooms";

            try
            {
                // Synchronous HTTP call — safe inside RevitTask.RunAsync background thread.
                HttpWebRequest request = (HttpWebRequest)WebRequest.Create(url);
                request.Method = "GET";
                request.Accept = "application/json";
                request.Headers.Add("Authorization", $"Reference {drofus.ApiToken}");
                request.Timeout = 15_000; // 15 s

                using HttpWebResponse response = (HttpWebResponse)request.GetResponse();

                if (response.StatusCode != HttpStatusCode.OK &&
                    response.StatusCode != HttpStatusCode.PartialContent)
                {
                    throw new InvalidOperationException(
                        $"drofus returned HTTP {(int)response.StatusCode} {response.StatusDescription}.");
                }

                // Read body and count rooms
                using var reader = new System.IO.StreamReader(response.GetResponseStream());
                string json = reader.ReadToEnd();
                var array = JArray.Parse(json);
                int count = array.Count;

                // Store count for the ViewModel to display
                drofus.LastRoomCount = count;
                drofus.IsConnected = true;

                // PoC: return empty — full mapping is the next step
                return new List<RoomDataModel>();
            }
            catch (WebException webEx) when (webEx.Response is HttpWebResponse errResp)
            {
                drofus.IsConnected = false;
                int code = (int)errResp.StatusCode;
                string detail = code == 401 ? "Invalid token."
                              : code == 403 ? "Token has no access to this database."
                              : code == 404 ? "Database not found."
                              : errResp.StatusDescription;
                throw new InvalidOperationException($"drofus connection failed: {detail}", webEx);
            }
            catch (WebException webEx)
            {
                drofus.IsConnected = false;
                throw new InvalidOperationException(
                    $"drofus connection failed: {webEx.Message}", webEx);
            }
        }

        /// <inheritdoc/>
        /// <remarks>PoC: drofus does not provide CSV-style header rows. Returns empty list.</remarks>
        public List<RoomDataProperty> GetHeaderProperties(DataSourceSettings settings)
            => new List<RoomDataProperty>();

        /// <inheritdoc/>
        public bool Validate(DataSourceSettings settings, out string errorMessage)
        {
            var drofus = settings?.Drofus;
            if (drofus == null || string.IsNullOrWhiteSpace(drofus.ApiToken))
            {
                errorMessage = "API token is required.";
                return false;
            }
            if (string.IsNullOrWhiteSpace(drofus.DatabaseName))
            {
                errorMessage = "Database name is required.";
                return false;
            }
            errorMessage = string.Empty;
            return true;
        }
    }
}
