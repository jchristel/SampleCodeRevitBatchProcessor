//
//License:
//
//
// Revit Batch Processor Sample Code
//
// BSD License
// Copyright 2025, Jan Christel
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

using duHastNet.PushIt.Interfaces;
using duHastNet.PushIt.Models;
using System;

namespace duHastNet.PushIt.Utilities
{
    /// <summary>
    /// Maps a <see cref="DataSourceType"/> value to the corresponding
    /// <see cref="IDataSource"/> implementation.
    /// <para>
    /// Adding a new provider requires only:
    /// <list type="number">
    ///   <item>Adding a value to <see cref="DataSourceType"/>.</item>
    ///   <item>Creating a provider-specific config class (e.g. <c>DrofusDataSourceConfig</c>).</item>
    ///   <item>Adding a property for it on <see cref="DataSourceSettings"/>.</item>
    ///   <item>Implementing <see cref="IDataSource"/> in a new class.</item>
    ///   <item>Adding a case to <see cref="Create"/> below.</item>
    /// </list>
    /// No other changes to the data-loading pipeline are needed.
    /// </para>
    /// </summary>
    public static class DataSourceFactory
    {
        /// <summary>
        /// Creates and returns the <see cref="IDataSource"/> implementation
        /// that corresponds to <paramref name="sourceType"/>.
        /// </summary>
        /// <param name="sourceType">The data source type to instantiate.</param>
        /// <returns>A ready-to-use <see cref="IDataSource"/> instance.</returns>
        /// <exception cref="NotSupportedException">
        /// Thrown when <paramref name="sourceType"/> is
        /// <see cref="DataSourceType.None"/> or an unrecognised value.
        /// Callers should validate settings before attempting to load data.
        /// </exception>
        public static IDataSource Create(DataSourceType sourceType) => sourceType switch
        {
            DataSourceType.Csv => new CsvDataSource(),

            // Future providers – register here:
            // DataSourceType.Drofus => new DrofusDataSource(),

            DataSourceType.None => throw new NotSupportedException(
                "Cannot create a data source when no source type has been selected. " +
                "Ensure DataSourceSettings.SourceType is set before loading data."),

            _ => throw new NotSupportedException(
                $"Data source type '{sourceType}' is not supported. " +
                "Add a new IDataSource implementation and register it in DataSourceFactory.")
        };
    }
}
