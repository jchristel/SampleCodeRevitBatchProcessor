// BSD License - Copyright 2025, Jan Christel

using duHastNet.PushIt.Interfaces;
using duHastNet.PushIt.Models;
using duHastNet.PushIt.Models.Drofus;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net;

namespace duHastNet.PushIt.Utilities.Drofus
{
    /// <summary>
    /// <see cref="IDataSource"/> implementation for the drofus REST API.
    ///
    /// Connection test: GET {BaseUrl}/api/{DatabaseName}/{ProjectNumber}/rooms
    /// Authentication:  Authorization: Reference {ApiToken}
    ///
    /// REVIT CONTEXT: All HTTP calls are synchronous (HttpWebRequest.GetResponse).
    /// RevitTask.RunAsync already provides a background thread — using async on top
    /// of that risks a deadlock, so the blocking WebRequest path is intentional.
    ///
    /// PoC scope: GetRoomsData returns an empty list after a successful auth check.
    /// The room count is stored on DrofusDataSourceSettings.LastRoomCount for the
    /// ViewModel to display. Full room mapping is the next step after PoC sign-off.
    /// </summary>
    public class DrofusDataSource : IDataSource
    {
        /// <inheritdoc/>
        public List<RoomDataModel> GetRoomsData(DataSourceSettings settings)
        {
            var drofus = settings?.Drofus
                ?? throw new InvalidOperationException(
                    "drofus data source selected but no credentials are configured.");

            ValidateSettings(drofus);

            string url = BuildUrl(drofus);

            try
            {
                string json = ExecuteGet(url, drofus.ApiToken);
                var array = JArray.Parse(json);

                drofus.LastRoomCount = array.Count;
                drofus.IsConnected = true;

                // PoC: return empty — full room mapping is the next step.
                return new List<RoomDataModel>();
            }
            catch (WebException webEx) when (webEx.Response is HttpWebResponse errResp)
            {
                drofus.IsConnected = false;
                throw new InvalidOperationException(
                    $"drofus connection failed: {BuildHttpErrorDetail(drofus, errResp)}", webEx);
            }
            catch (WebException webEx)
            {
                drofus.IsConnected = false;
                throw new InvalidOperationException(
                    $"drofus connection failed: {webEx.Message}", webEx);
            }
        }

        /// <summary>
        /// Queries the drofus rooms endpoint and returns the JSON property names
        /// present on the first room object in the response.
        /// <para>
        /// Used by <c>ValidateDrofusMappingsOnStartup</c> and by the Connect flow
        /// to populate <c>DrofusPropertyMapper.AvailableFields</c> without
        /// duplicating the HTTP logic.
        /// </para>
        /// <para>
        /// Also updates <see cref="DrofusDataSourceSettings.LastRoomCount"/> and
        /// <see cref="DrofusDataSourceSettings.IsConnected"/> as a side-effect of
        /// the successful call, mirroring the behaviour of
        /// <see cref="GetRoomsData"/>.
        /// </para>
        /// </summary>
        /// <param name="settings">
        /// Active data source settings. Must not be <c>null</c> and must contain
        /// a fully populated <see cref="DataSourceSettings.Drofus"/> block.
        /// </param>
        /// <returns>
        /// An ordered list of the JSON field names found on the first room in the
        /// response. Returns an empty list when the response array is empty (no
        /// rooms in the project) — this is not treated as an error.
        /// </returns>
        /// <exception cref="InvalidOperationException">
        /// Thrown when credentials are missing, the HTTP call fails, or the
        /// response cannot be parsed as a JSON array.
        /// </exception>
        public List<string> GetAvailableFields(DataSourceSettings settings)
        {
            var drofus = settings?.Drofus
                ?? throw new InvalidOperationException(
                    "drofus data source selected but no credentials are configured.");

            ValidateSettings(drofus);

            string url = BuildUrl(drofus);

            try
            {
                string json = ExecuteGet(url, drofus.ApiToken);
                var array = JArray.Parse(json);

                drofus.LastRoomCount = array.Count;
                drofus.IsConnected = true;

                if (array.Count == 0)
                    return new List<string>();

                // Extract property names from the first room object only.
                // Field names are dynamic — not hardcoded — so we derive them
                // from the live response rather than a fixed list.
                if (array[0] is not JObject firstRoom)
                    return new List<string>();

                return firstRoom.Properties()
                    .Select(p => p.Name)
                    .ToList();
            }
            catch (WebException webEx) when (webEx.Response is HttpWebResponse errResp)
            {
                drofus.IsConnected = false;
                throw new InvalidOperationException(
                    $"drofus connection failed: {BuildHttpErrorDetail(drofus, errResp)}", webEx);
            }
            catch (WebException webEx)
            {
                drofus.IsConnected = false;
                throw new InvalidOperationException(
                    $"drofus connection failed: {webEx.Message}", webEx);
            }
        }

        /// <inheritdoc/>
        /// <remarks>PoC: drofus has no CSV-style header rows. Returns empty list.</remarks>
        public List<RoomDataProperty> GetHeaderProperties(DataSourceSettings settings)
            => new List<RoomDataProperty>();

        /// <inheritdoc/>
        public bool Validate(DataSourceSettings settings, out string errorMessage)
        {
            var drofus = settings?.Drofus;
            if (drofus == null)
            {
                errorMessage = "drofus settings are not configured.";
                return false;
            }

            if (string.IsNullOrWhiteSpace(drofus.BaseUrl))
            {
                errorMessage = "Base URL is required.";
                return false;
            }

            if (string.IsNullOrWhiteSpace(drofus.DatabaseName))
            {
                errorMessage = "Database name is required.";
                return false;
            }

            if (string.IsNullOrWhiteSpace(drofus.ProjectNumber))
            {
                errorMessage = "Project number is required.";
                return false;
            }

            if (string.IsNullOrWhiteSpace(drofus.ApiToken))
            {
                errorMessage = "API token is required.";
                return false;
            }

            errorMessage = string.Empty;
            return true;
        }

        // ── Private helpers ───────────────────────────────────────────────────

        /// <summary>
        /// Executes a synchronous GET against <paramref name="url"/> using the
        /// given <paramref name="apiToken"/> and returns the raw response body.
        /// Centralises the WebRequest construction so that both
        /// <see cref="GetRoomsData"/> and <see cref="GetAvailableFields"/> share
        /// identical HTTP behaviour.
        /// </summary>
        private static string ExecuteGet(string url, string apiToken)
        {
            HttpWebRequest request = (HttpWebRequest)WebRequest.Create(url);
            request.Method = "GET";
            request.Accept = "application/json";
            request.Headers.Add("Authorization", $"Reference {apiToken}");
            request.Timeout = 15_000; // 15 s

            using HttpWebResponse response = (HttpWebResponse)request.GetResponse();
            using var reader = new StreamReader(response.GetResponseStream()
                ?? throw new InvalidOperationException("drofus API returned an empty response stream."));
            return reader.ReadToEnd();
        }

        private static void ValidateSettings(DrofusDataSourceSettings drofus)
        {
            if (string.IsNullOrWhiteSpace(drofus.BaseUrl))
                throw new InvalidOperationException("drofus base URL is empty.");
            if (string.IsNullOrWhiteSpace(drofus.DatabaseName))
                throw new InvalidOperationException("drofus database name is empty.");
            if (string.IsNullOrWhiteSpace(drofus.ProjectNumber))
                throw new InvalidOperationException("drofus project number is empty.");
            if (string.IsNullOrWhiteSpace(drofus.ApiToken))
                throw new InvalidOperationException("drofus API token is empty.");
        }

        private static string BuildUrl(DrofusDataSourceSettings drofus)
        {
            string baseUrl = drofus.BaseUrl.TrimEnd('/');
            return $"{baseUrl}/api/{drofus.DatabaseName}/{drofus.ProjectNumber}/rooms";
        }

        private static string BuildHttpErrorDetail(
            DrofusDataSourceSettings drofus,
            HttpWebResponse errResp)
        {
            int code = (int)errResp.StatusCode;
            return code == 401 ? "Invalid API token (401 Unauthorised)."
                 : code == 403 ? "Token has no access to this project (403 Forbidden)."
                 : code == 404 ? $"Project not found (404). Check database name " +
                                 $"'{drofus.DatabaseName}' and project number '{drofus.ProjectNumber}'."
                 : $"{code} {errResp.StatusDescription}";
        }
    }
}
