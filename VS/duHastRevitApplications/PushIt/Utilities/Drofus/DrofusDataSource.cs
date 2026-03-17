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
        /// <para>
        /// When <see cref="DrofusDataSourceSettings.PropertyMappings"/> is non-empty,
        /// a <c>$select</c> query parameter is appended to the rooms URL so that
        /// extended fields (<c>room_data_*</c>, <c>room_measurement_*</c>, etc.) are
        /// included in the response. The <c>id</c> field is always returned by the
        /// API regardless of <c>$select</c>.
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

            // Build the base rooms URL, appending $select when mappings are present
            // so that extended fields are actually returned in the payload.
            // $select is skipped when PropertyMappings is empty — the existing
            // idMapping guard above will throw before any room processing begins,
            // so an empty mappings list can never reach FetchAllPages. This is a
            // defensive one-liner to avoid producing a malformed URL (Gap 3).
            string baseUrl = BuildUrl(drofus);
            if (drofus.PropertyMappings.Count > 0)
            {
                string selectFields = string.Join(",",
                    drofus.PropertyMappings.Select(m => m.DrofusFieldName));
                baseUrl = $"{baseUrl}?$select={selectFields}";
            }

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
        /// Fetches the complete room field catalogue from the drofus OPTIONS endpoint.
        /// <para>
        /// Calls <c>OPTIONS /api/{db}/{pr}/rooms</c> and parses the JSON array response
        /// into a list of <see cref="DrofusRoomField"/> objects. The full catalogue is
        /// returned in a single response — no paging is required.
        /// </para>
        /// <para>
        /// Any entry whose <c>id</c> property is null, missing, or whitespace is
        /// silently dropped — a null-id field is a malformed API response and should
        /// not surface to the user (Gap 6).
        /// </para>
        /// </summary>
        /// <param name="settings">
        /// Active data source settings. Must not be <c>null</c> and must contain
        /// a fully populated <see cref="DataSourceSettings.Drofus"/> block.
        /// </param>
        /// <returns>
        /// The complete list of room fields available in this drofus project.
        /// Returns an empty list if the OPTIONS response contains no entries.
        /// </returns>
        /// <exception cref="InvalidOperationException">
        /// Thrown when credentials are missing, the HTTP call fails, or the
        /// response cannot be parsed as a JSON array. This failure is fatal to
        /// the Connect / startup sequence (Gap 1).
        /// </exception>
        public List<DrofusRoomField> GetFieldCatalogue(DataSourceSettings settings)
        {
            var drofus = settings?.Drofus
                ?? throw new InvalidOperationException(
                    "drofus data source selected but no credentials are configured.");

            ValidateSettings(drofus);

            string url = BuildUrl(drofus);

            try
            {
                string json = ExecuteOptions(url, drofus.ApiToken);
                var array = JArray.Parse(json);

                var fields = new List<DrofusRoomField>(array.Count);

                foreach (JToken token in array)
                {
                    if (token is not JObject fieldObj)
                        continue;

                    // Gap 6: silently drop any entry with a null/missing/whitespace id.
                    string? id = fieldObj["id"]?.ToString();
                    if (string.IsNullOrWhiteSpace(id))
                        continue;

                    fields.Add(new DrofusRoomField
                    {
                        Id            = id,
                        Name          = fieldObj["name"]?.ToString()          ?? id,
                        PropertyGroup = fieldObj["propertyGroup"]?.ToString() ?? string.Empty,
                        DataType      = fieldObj["dataType"]?.ToString()      ?? string.Empty,
                        Unit          = fieldObj["unit"]?.ToString()          ?? string.Empty,
                    });
                }

                return fields;
            }
            catch (WebException webEx) when (webEx.Response is HttpWebResponse errResp)
            {
                throw new InvalidOperationException(
                    $"drofus field catalogue request failed: {BuildHttpErrorDetail(drofus, errResp)}", webEx);
            }
            catch (WebException webEx)
            {
                throw new InvalidOperationException(
                    $"drofus field catalogue request failed: {webEx.Message}", webEx);
            }
        }

        /// <summary>
        /// Fetches the attribute configurations for this drofus project and returns
        /// those whose <c>config_type</c> is <c>"room"</c>.
        /// <para>
        /// Calls <c>GET /api/{db}/{pr}/attributeconfigurations</c> using
        /// <see cref="FetchAllPages"/> for correctness (the endpoint supports
        /// <c>$top</c>/<c>$skip</c>), though in practice the number of configurations
        /// per project is small. Filtering to <c>config_type == "room"</c> is applied
        /// client-side after parsing — no server-side <c>$filter</c> is used, since
        /// <c>applicable_to</c> is always <c>null</c> in live responses and cannot be
        /// used as a filter. Known <c>config_type</c> values: <c>"room"</c>,
        /// <c>"revit-occurrence"</c>, <c>"standardroom"</c>, <c>"article"</c>,
        /// <c>"space"</c>.
        /// </para>
        /// </summary>
        /// <param name="settings">
        /// Active data source settings. Must not be <c>null</c> and must contain
        /// a fully populated <see cref="DataSourceSettings.Drofus"/> block.
        /// </param>
        /// <returns>
        /// The list of room attribute configurations for this project. May be empty
        /// if no room configurations are set up in drofus (Scenario 1 / Gap 2).
        /// </returns>
        /// <exception cref="InvalidOperationException">
        /// Thrown when credentials are missing, the HTTP call fails, or the
        /// response cannot be parsed. Failure is fatal to the mapping interface
        /// (Gap 2) — treated identically to Scenario 1 (no room configurations).
        /// </exception>
        public List<DrofusAttributeConfiguration> GetAttributeConfigurations(DataSourceSettings settings)
        {
            var drofus = settings?.Drofus
                ?? throw new InvalidOperationException(
                    "drofus data source selected but no credentials are configured.");

            ValidateSettings(drofus);

            string baseUrl = BuildAttributeConfigurationsUrl(drofus);

            try
            {
                JArray array = FetchAllPages(baseUrl, drofus.ApiToken);

                var configurations = new List<DrofusAttributeConfiguration>();

                foreach (JToken token in array)
                {
                    if (token is not JObject configObj)
                        continue;

                    // Client-side filter: only room configurations are relevant to PushIt.
                    string configType = configObj["config_type"]?.ToString() ?? string.Empty;
                    if (!string.Equals(configType, "room", StringComparison.OrdinalIgnoreCase))
                        continue;

                    var elements = new List<DrofusAttributeConfigurationElement>();

                    if (configObj["elements"] is JArray elementsArray)
                    {
                        foreach (JToken elemToken in elementsArray)
                        {
                            if (elemToken is not JObject elemObj)
                                continue;

                            elements.Add(new DrofusAttributeConfigurationElement
                            {
                                DrofusAttributeId    = elemObj["drofus_attribute_id"]?.ToString()    ?? string.Empty,
                                DrofusAttributeLabel = elemObj["drofus_attribute_label"]?.ToString() ?? string.Empty,
                                Direction            = elemObj["direction"]?.ToString()              ?? string.Empty,
                            });
                        }
                    }

                    configurations.Add(new DrofusAttributeConfiguration
                    {
                        Id         = configObj["id"]?.Value<int>() ?? 0,
                        Name       = configObj["name"]?.ToString() ?? string.Empty,
                        IsDefault  = configObj["is_default"]?.Value<bool>() ?? false,
                        Elements   = elements,
                    });
                }

                return configurations;
            }
            catch (WebException webEx) when (webEx.Response is HttpWebResponse errResp)
            {
                throw new InvalidOperationException(
                    $"drofus attribute configurations request failed: {BuildHttpErrorDetail(drofus, errResp)}", webEx);
            }
            catch (WebException webEx)
            {
                throw new InvalidOperationException(
                    $"drofus attribute configurations request failed: {webEx.Message}", webEx);
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
        /// Constructs an <see cref="HttpWebRequest"/> with the common headers shared
        /// by all drofus API verbs: <c>Authorization: Reference {apiToken}</c> and
        /// <c>Accept: application/json</c>.
        /// <para>
        /// The HTTP verb (<c>Method</c>) is intentionally not set here — each
        /// Execute* method sets its own verb after calling this helper. This keeps
        /// each method self-documenting and allows future verbs to diverge in headers
        /// or response handling without refactoring this shared setup.
        /// </para>
        /// </summary>
        private static HttpWebRequest CreateRequest(string url, string apiToken)
        {
            HttpWebRequest request = (HttpWebRequest)WebRequest.Create(url);
            request.Accept = "application/json";
            request.Headers.Add("Authorization", $"Reference {apiToken}");
            request.Timeout = 15_000; // 15 s
            return request;
        }

        /// <summary>
        /// Executes a synchronous GET against <paramref name="url"/> and returns
        /// the raw response body.
        /// </summary>
        private static string ExecuteGet(string url, string apiToken)
        {
            HttpWebRequest request = CreateRequest(url, apiToken);
            request.Method = "GET";

            using HttpWebResponse response = (HttpWebResponse)request.GetResponse();
            using var reader = new StreamReader(response.GetResponseStream()
                ?? throw new InvalidOperationException("drofus API returned an empty response stream."));
            return reader.ReadToEnd();
        }

        /// <summary>
        /// Executes a synchronous OPTIONS against <paramref name="url"/> and returns
        /// the raw response body. Used exclusively by <see cref="GetFieldCatalogue"/>
        /// to retrieve the complete room property catalogue.
        /// </summary>
        private static string ExecuteOptions(string url, string apiToken)
        {
            HttpWebRequest request = CreateRequest(url, apiToken);
            request.Method = "OPTIONS";

            using HttpWebResponse response = (HttpWebResponse)request.GetResponse();
            using var reader = new StreamReader(response.GetResponseStream()
                ?? throw new InvalidOperationException("drofus API returned an empty response stream."));
            return reader.ReadToEnd();
        }

        /// <summary>
        /// Reserved for the future drofus write-back path (RevitToDrofus direction).
        /// <para>
        /// The drofus REST API PATCH endpoints are not yet implemented in PushIt.
        /// This stub reserves the method signature so the pattern is established and
        /// future implementation requires no structural refactoring. The signature
        /// must not be called — it will throw immediately.
        /// </para>
        /// </summary>
        /// <exception cref="NotImplementedException">
        /// Always thrown. This method is a reserved stub only.
        /// </exception>
#pragma warning disable IDE0060 // unused parameters are intentional on a stub
        private static string ExecutePatch(string url, string body, string apiToken)
        {
            // Reserved for future RevitToDrofus write-back. Do not implement until
            // the drofus PATCH endpoint contract is confirmed and the write path
            // in PushIt is fully designed.
            throw new NotImplementedException(
                "ExecutePatch is reserved for the future drofus write-back path and is not yet implemented.");
        }
#pragma warning restore IDE0060

        /// <summary>
        /// Pages through a drofus list endpoint using <c>$top</c> / <c>$skip</c>
        /// query parameters and returns all results as a single <see cref="JArray"/>.
        /// <para>
        /// Termination: when a page contains fewer items than <see cref="PageSize"/>
        /// the last page has been reached. There is no total-count header to rely on.
        /// </para>
        /// <para>
        /// The caller is responsible for appending any other query parameters (e.g.
        /// <c>$select</c>) to <paramref name="baseUrl"/> before calling this method.
        /// This method detects whether <paramref name="baseUrl"/> already contains a
        /// <c>?</c> and uses <c>&amp;</c> rather than <c>?</c> when appending the
        /// paging parameters, so existing query strings are not overwritten.
        /// </para>
        /// </summary>
        private static JArray FetchAllPages(string baseUrl, string apiToken)
        {
            var all = new JArray();
            int skip = 0;

            // Detect whether the caller has already appended a query string so we
            // can use & for paging parameters rather than ? (fixes $select coexistence).
            string pagingSeparator = baseUrl.Contains('?') ? "&" : "?";

            while (true)
            {
                string url = $"{baseUrl}{pagingSeparator}$top={PageSize}&$skip={skip}";
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

        private static string BuildAttributeConfigurationsUrl(DrofusDataSourceSettings drofus)
        {
            string baseUrl = drofus.BaseUrl.TrimEnd('/');
            return $"{baseUrl}/api/{drofus.DatabaseName}/{drofus.ProjectNumber}/attributeconfigurations";
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
