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
    /// </summary>
    public class DrofusDataSource : IDataSource
    {
        /// <summary>
        /// Number of rooms requested per API call when paginating.
        /// The drofus API supports <c>$top</c> and <c>$skip</c> query parameters.
        /// A value of 500 is a safe default that keeps individual response payloads
        /// small while requiring only a handful of calls for typical projects.
        /// Raising this toward the API's ceiling of 10 000 reduces round-trips but
        /// increases per-call memory and latency.
        /// </summary>
        private const int PageSize = 500;

        /// <inheritdoc/>
        /// <summary>
        /// Queries the drofus rooms endpoint and translates each room object in
        /// the JSON response into a <see cref="RoomDataModel"/> using the
        /// <see cref="DrofusDataSourceSettings.PropertyMappings"/> list.
        /// <para>
        /// Each mapping entry describes one drofus JSON field and the Revit shared
        /// parameter it maps to. The mapping flagged with
        /// <see cref="DrofusPropertyMap.IsUniqueId"/> provides the value for
        /// <see cref="RoomDataModel.Id"/>; all other mappings become entries in
        /// <see cref="RoomBase.Properties"/>.
        /// </para>
        /// <para>
        /// Rooms whose unique-id field is absent or null in the JSON response are
        /// skipped — they cannot be matched to Revit rooms.
        /// </para>
        /// </summary>
        public List<RoomDataModel> GetRoomsData(DataSourceSettings settings)
        {
            var drofus = settings?.Drofus
                ?? throw new InvalidOperationException(
                    "drofus data source selected but no credentials are configured.");

            ValidateSettings(drofus);

            // The caller (Main / ValidateDrofusMappingsOnStartup) guarantees that
            // exactly one mapping carries IsUniqueId before GetRoomsData is called.
            // We guard here as a belt-and-braces check.
            DrofusPropertyMap? idMapping = drofus.PropertyMappings
                .FirstOrDefault(m => m.IsUniqueId);

            if (idMapping is null)
                throw new InvalidOperationException(
                    "drofus GetRoomsData: no mapping is nominated as the unique " +
                    "identifier (IsUniqueId). Validate mappings before loading rooms.");

            // Non-id mappings become regular RoomDataProperty entries.
            List<DrofusPropertyMap> otherMappings = drofus.PropertyMappings
                .Where(m => !m.IsUniqueId)
                .ToList();

            string baseUrl = BuildUrl(drofus);

            try
            {
                JArray array = FetchAllPages(baseUrl, drofus.ApiToken);

                drofus.LastSkippedRoomCount = 0;

                var rooms = new List<RoomDataModel>(array.Count);
                int skippedCount = 0;

                foreach (JToken token in array)
                {
                    if (token is not JObject roomObj)
                        continue;

                    // ── Unique-id field ───────────────────────────────────────
                    string? idRaw = roomObj[idMapping.DrofusFieldName]?.ToString();

                    if (string.IsNullOrWhiteSpace(idRaw))
                    {
                        // Room has no usable id value — skip it.
                        skippedCount++;
                        continue;
                    }

                    var idProperty = new RoomDataProperty(
                        name: idMapping.RevitParameterName,
                        parameterGUID: idMapping.RevitParameterGuid,
                        parameterName: idMapping.RevitParameterName,
                        value: idRaw,
                        showInUI: true,
                        isReadOnly: false,
                        isUniqueId: true);

                    // ── Other mapped fields ───────────────────────────────────
                    var properties = new List<RoomDataProperty>(otherMappings.Count);

                    foreach (DrofusPropertyMap mapping in otherMappings)
                    {
                        string fieldValue = roomObj[mapping.DrofusFieldName]?.ToString()
                            ?? string.Empty;

                        // RevitToDrofus: Revit is the source — the property must be
                        // read-only in PushIt so it is read from Revit and written to
                        // drofus, never edited manually in the grid.
                        bool isReadOnly = mapping.FlowDirection == MappingFlowDirection.RevitToDrofus;

                        // Carry through the RevitTakesPrecedenceAfterInitialPush flag
                        // from the persisted mapping settings so that RefreshRoomDataWithRevitData
                        // can overwrite these property values with the current Revit value.
                        bool revitTakesPrecedence = drofus.RevitPrecedencePropertyNames != null
                            && drofus.RevitPrecedencePropertyNames.Contains(mapping.RevitParameterName);

                        properties.Add(new RoomDataProperty(
                            name: mapping.RevitParameterName,
                            parameterGUID: mapping.RevitParameterGuid,
                            parameterName: mapping.RevitParameterName,
                            value: fieldValue,
                            showInUI: true,
                            isReadOnly: isReadOnly,
                            isUniqueId: false,
                            revitTakesPrecedenceAfterInitialPush: revitTakesPrecedence));
                    }

                    rooms.Add(new RoomDataModel(idProperty, properties));
                }

                // Surface the skip count as a non-fatal warning via the settings
                // object so the caller can relay it to the message store if desired.
                drofus.LastSkippedRoomCount = skippedCount;

                return rooms;
            }
            catch (WebException webEx) when (webEx.Response is HttpWebResponse errResp)
            {
                throw new InvalidOperationException(
                    $"drofus connection failed: {BuildHttpErrorDetail(drofus, errResp)}", webEx);
            }
            catch (WebException webEx)
            {
                throw new InvalidOperationException(
                    $"drofus connection failed: {webEx.Message}", webEx);
            }
        }

        /// <summary>
        /// Queries the drofus rooms endpoint and returns the JSON property names
        /// present on the first room object in the response.
        /// <para>
        /// Used by <c>ValidateDrofusOnStartup</c> and by the Connect flow
        /// to populate <c>DrofusPropertyMapper.AvailableFields</c> without
        /// duplicating the HTTP logic.
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

            // Request only the first room — we only need the field names, not the data.
            // Appending $top=1 avoids fetching the entire project room list for what
            // is essentially a schema discovery call.
            string url = BuildUrl(drofus) + "?$top=1";

            try
            {
                string json = ExecuteGet(url, drofus.ApiToken);
                var array = JArray.Parse(json);

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
                throw new InvalidOperationException(
                    $"drofus connection failed: {BuildHttpErrorDetail(drofus, errResp)}", webEx);
            }
            catch (WebException webEx)
            {
                throw new InvalidOperationException(
                    $"drofus connection failed: {webEx.Message}", webEx);
            }
        }

        /// <inheritdoc/>
        /// <summary>
        /// Builds a <see cref="RoomDataProperty"/> for each entry in
        /// <see cref="DrofusDataSourceSettings.PropertyMappings"/> so that
        /// <c>VerifyParametersInModel</c> can check that every mapped Revit shared
        /// parameter still exists and is bound in the active document.
        /// <para>
        /// Returns an empty list when no mappings are configured — the caller
        /// treats an empty list as "nothing to verify" rather than an error.
        /// </para>
        /// </summary>
        public List<RoomDataProperty> GetHeaderProperties(DataSourceSettings settings)
        {
            var drofus = settings?.Drofus;
            if (drofus == null || drofus.PropertyMappings.Count == 0)
                return new List<RoomDataProperty>();

            var properties = new List<RoomDataProperty>(drofus.PropertyMappings.Count);

            foreach (DrofusPropertyMap mapping in drofus.PropertyMappings)
            {
                // RevitToDrofus mappings are read-only: Revit is the source of truth.
                bool isReadOnly = mapping.FlowDirection == MappingFlowDirection.RevitToDrofus;

                // Check whether the user has flagged this property to use the stored
                // Revit value on subsequent split-room pushes rather than the SoA value.
                bool revitTakesPrecedence = drofus.RevitPrecedencePropertyNames != null
                    && drofus.RevitPrecedencePropertyNames.Contains(mapping.RevitParameterName);

                properties.Add(new RoomDataProperty(
                    name: mapping.RevitParameterName,
                    parameterGUID: mapping.RevitParameterGuid,
                    parameterName: mapping.RevitParameterName,
                    value: string.Empty,
                    showInUI: true,
                    isReadOnly: isReadOnly,
                    isUniqueId: mapping.IsUniqueId,
                    revitTakesPrecedenceAfterInitialPush: revitTakesPrecedence));
            }

            return properties;
        }

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
        /// Pages through the drofus rooms endpoint using <c>$top</c> / <c>$skip</c>
        /// query parameters and returns all rooms as a single <see cref="JArray"/>.
        /// <para>
        /// Termination: when a page contains fewer items than <see cref="PageSize"/>
        /// the last page has been reached. There is no total-count header to rely on.
        /// </para>
        /// </summary>
        private static JArray FetchAllPages(string baseUrl, string apiToken)
        {
            var all = new JArray();
            int skip = 0;

            while (true)
            {
                string url = $"{baseUrl}?$top={PageSize}&$skip={skip}";
                string json = ExecuteGet(url, apiToken);
                JArray page = JArray.Parse(json);

                foreach (JToken token in page)
                    all.Add(token);

                // A page shorter than PageSize means we have reached the end.
                if (page.Count < PageSize)
                    break;

                skip += PageSize;
            }

            return all;
        }

        /// <summary>
        /// Executes a synchronous GET against <paramref name="url"/> using the
        /// given <paramref name="apiToken"/> and returns the raw response body.
        /// Centralises the WebRequest construction so that <see cref="FetchAllPages"/>
        /// and <see cref="GetAvailableFields"/> share identical HTTP behaviour.
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