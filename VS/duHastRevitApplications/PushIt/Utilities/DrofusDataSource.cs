// BSD License - Copyright 2025, Jan Christel

using duHastNet.PushIt.Interfaces;
using duHastNet.PushIt.Models;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.IO;
using System.Net;

namespace duHastNet.PushIt.Utilities
{
    /// <summary>
    /// PoC IDataSource implementation for the drofus REST API.
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

            // Build URL: {BaseUrl}/api/{DatabaseName}/{ProjectNumber}/rooms
            string url = BuildUrl(drofus);

            try
            {
                HttpWebRequest request = (HttpWebRequest)WebRequest.Create(url);
                request.Method = "GET";
                request.Accept = "application/json";
                request.Headers.Add("Authorization", $"Reference {drofus.ApiToken}");
                request.Timeout = 15_000; // 15 s

                using HttpWebResponse response = (HttpWebResponse)request.GetResponse();

                using var reader = new StreamReader(response.GetResponseStream());
                string json = reader.ReadToEnd();
                var array = JArray.Parse(json);

                drofus.LastRoomCount = array.Count;
                drofus.IsConnected = true;

                // PoC: return empty — full mapping is the next step
                return new List<RoomDataModel>();
            }
            catch (WebException webEx) when (webEx.Response is HttpWebResponse errResp)
            {
                drofus.IsConnected = false;
                int code = (int)errResp.StatusCode;
                string detail = code == 401 ? "Invalid API token (401 Unauthorised)."
                              : code == 403 ? "Token has no access to this project (403 Forbidden)."
                              : code == 404 ? $"Project not found (404). Check database name '{drofus.DatabaseName}' and project number '{drofus.ProjectNumber}'."
                              : $"{code} {errResp.StatusDescription}";
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
            // Trim trailing slash from base URL so we don't get double slashes
            string baseUrl = drofus.BaseUrl.TrimEnd('/');
            return $"{baseUrl}/api/{drofus.DatabaseName}/{drofus.ProjectNumber}/rooms";
        }
    }
}