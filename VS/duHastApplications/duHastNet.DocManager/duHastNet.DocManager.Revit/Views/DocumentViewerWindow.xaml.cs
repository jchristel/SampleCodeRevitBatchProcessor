//
// BSD License
// Copyright 2026, Jan Christel
// All rights reserved.

// Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

// - Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
// - Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
// - Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
//
// This software is provided by the copyright holder "as is" and any express or implied warranties, including, but not limited to, the implied warranties of merchantability and fitness for a particular purpose are disclaimed.
// In no event shall the copyright holder be liable for any direct, indirect, incidental, special, exemplary, or consequential damages (including, but not limited to, procurement of substitute goods or services; loss of use, data, or profits;
// or business interruption) however caused and on any theory of liability, whether in contract, strict liability, or tort (including negligence or otherwise) arising in any way out of the use of this software, even if advised of the possibility of such damage.
//
//
//

using System;
using System.Windows;
using CefSharp;
using duHastNet.DocManager.Revit.Bridge;

namespace duHastNet.DocManager.Revit.Views
{
    /// <summary>
    /// Interaction logic for DocumentViewerWindow.xaml
    /// Window that hosts CEFSharp browser to display documents from database
    /// </summary>
    public partial class DocumentViewerWindow : Window
    {
        private readonly WebViewBridge _bridge;

        /// <summary>
        /// Initializes a new instance of DocumentViewerWindow
        /// </summary>
        /// <param name="databasePath">Path to the database file</param>
        public DocumentViewerWindow(string databasePath)
        {
            InitializeComponent();

            // Create the bridge with database path
            _bridge = new WebViewBridge(databasePath);

            // Register the bridge BEFORE browser initialization (new CEFSharp API)
            WebBrowser.JavascriptObjectRepository.Settings.LegacyBindingEnabled = true;
            WebBrowser.JavascriptObjectRepository.Register("bridge", _bridge,
                BindingOptions.DefaultBinder);

            // Subscribe to browser initialization event
            WebBrowser.IsBrowserInitializedChanged += OnBrowserInitialized;
        }

        /// <summary>
        /// Called when the CEFSharp browser finishes initialization
        /// Loads HTML content
        /// </summary>
        private void OnBrowserInitialized(object? sender, DependencyPropertyChangedEventArgs e)
        {
            if (WebBrowser.IsBrowserInitialized)
            {
                // Load the HTML content
                var html = GetHtmlContent();
                WebBrowser.LoadHtml(html, "http://docviewer");
            }
        }

        /// <summary>
        /// Gets the HTML content with embedded JavaScript to display documents
        /// </summary>
        /// <returns>Complete HTML page as string</returns>
        private string GetHtmlContent()
        {
            return @"
<!DOCTYPE html>
<html lang=""en"">
<head>
    <meta charset=""UTF-8"">
    <meta name=""viewport"" content=""width=device-width, initial-scale=1.0"">
    <title>Document Viewer</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            padding: 20px;
            background-color: #f5f5f5;
        }

        h1 {
            color: #333;
            margin-bottom: 20px;
            font-size: 24px;
        }

        #loading {
            color: #666;
            font-size: 16px;
            padding: 20px;
        }

        #error {
            color: #d32f2f;
            background-color: #ffebee;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            display: none;
        }

        table {
            width: 100%;
            background-color: white;
            border-collapse: collapse;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-radius: 4px;
            overflow: hidden;
        }

        thead {
            background-color: #1976d2;
            color: white;
        }

        th {
            padding: 12px;
            text-align: left;
            font-weight: 600;
            font-size: 14px;
        }

        td {
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
            font-size: 14px;
        }

        tr:last-child td {
            border-bottom: none;
        }

        tbody tr:hover {
            background-color: #f5f5f5;
        }

        .stats {
            margin-top: 20px;
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <h1>Documents from Database</h1>
    <div id=""error""></div>
    <div id=""loading"">Loading documents...</div>
    <table id=""documentTable"" style=""display: none;"">
        <thead>
            <tr>
                <th>Document Number</th>
                <th>Name</th>
                <th>Revision</th>
            </tr>
        </thead>
        <tbody id=""documentBody"">
        </tbody>
    </table>
    <div id=""stats"" class=""stats""></div>

    <script>
        // Wait for CefSharp to be ready
        async function loadDocuments() {
            try {
                // Bind the bridge object
                await CefSharp.BindObjectAsync('bridge');

                // Call the GetDocuments method
                const jsonString = await bridge.getDocuments();
                
                // Parse the JSON response
                const response = JSON.parse(jsonString);

                // Check for errors
                if (response.error) {
                    showError(response.message);
                    return;
                }

                // Response is an array of documents
                const documents = response;

                // Hide loading message
                document.getElementById('loading').style.display = 'none';

                // Show table
                document.getElementById('documentTable').style.display = 'table';

                // Populate table
                const tbody = document.getElementById('documentBody');
                tbody.innerHTML = '';

                documents.forEach(doc => {
                    const row = tbody.insertRow();
                    row.insertCell(0).textContent = doc.documentNumber;
                    row.insertCell(1).textContent = doc.name;
                    row.insertCell(2).textContent = doc.revision;
                });

                // Show stats
                document.getElementById('stats').textContent = 
                    `Total documents: ${documents.length}`;

            } catch (error) {
                showError('Failed to load documents: ' + error.message);
            }
        }

        function showError(message) {
            document.getElementById('loading').style.display = 'none';
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = 'Error: ' + message;
            errorDiv.style.display = 'block';
        }

        // Load documents when page is ready
        window.addEventListener('load', loadDocuments);
    </script>
</body>
</html>
";
        }

        /// <summary>
        /// Clean up resources when window closes
        /// </summary>
        protected override void OnClosed(EventArgs e)
        {
            _bridge?.Dispose();
            WebBrowser?.Dispose();
            base.OnClosed(e);
        }
    }
}