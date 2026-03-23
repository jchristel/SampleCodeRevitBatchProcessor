// BSD License - Copyright 2025, Jan Christel

using System.Collections.Generic;

namespace duHastNet.PushIt.Models.Drofus
{
    /// <summary>
    /// Represents one attribute configuration returned by
    /// <c>GET /api/{db}/{pr}/attributeconfigurations</c>, filtered to those
    /// whose <c>config_type</c> is <c>"room"</c>.
    /// <para>
    /// Attribute configurations are named subsets of the full field catalogue.
    /// The user selects one at the project level; the mapping dialog then filters
    /// the available drofus fields to the elements of that configuration.
    /// Base room catalogue fields are always available on top of the configuration
    /// elements.
    /// </para>
    /// <para>
    /// This class is runtime-only and is never serialised to the settings file.
    /// Only the integer <see cref="Id"/> is persisted, via
    /// <c>DrofusDataSourceSettings.SelectedAttributeConfigurationId</c>, so the
    /// selection can be restored on the next session without a user action.
    /// </para>
    /// </summary>
    public class DrofusAttributeConfiguration
    {
        /// <summary>
        /// Reserved id used by the <see cref="None"/> sentinel.
        /// No real drofus configuration will ever have this id.
        /// </summary>
        public const int NoneId = -1;

        /// <summary>
        /// Singleton sentinel that represents "no configuration selected".
        /// Inserted as the first item in the configuration ComboBox so WPF can
        /// always display "None" rather than a blank when nothing is chosen.
        /// The mapper and settings layers treat <see cref="NoneId"/> identically
        /// to <c>null</c> — it is never persisted to the settings file.
        /// </summary>
        public static readonly DrofusAttributeConfiguration None =
            new DrofusAttributeConfiguration
            {
                Id = NoneId,
                Name = "None",
                IsDefault = false,
                Elements = new List<DrofusAttributeConfigurationElement>(),
            };

        /// <summary>
        /// The integer id of this configuration.
        /// This value is stable across renames — it is the identifier persisted
        /// to settings as <c>SelectedAttributeConfigurationId</c>.
        /// </summary>
        public int Id { get; set; }

        /// <summary>
        /// The human-readable name of this configuration, as defined in drofus,
        /// e.g. <c>"Rooms - Detailed"</c>, <c>"Rooms - Basic"</c>.
        /// Shown in the configuration selector dropdown in the settings panel.
        /// </summary>
        public string Name { get; set; } = string.Empty;

        /// <summary>
        /// <c>true</c> when this is the default configuration for the project,
        /// as designated in drofus. Used to pre-select a sensible default when
        /// no <c>SelectedAttributeConfigurationId</c> is stored in settings.
        /// </summary>
        public bool IsDefault { get; set; }

        /// <summary>
        /// The fields included in this configuration.
        /// Each element maps to a <see cref="DrofusRoomField"/> in the full
        /// catalogue via <see cref="DrofusAttributeConfigurationElement.DrofusAttributeId"/>.
        /// </summary>
        public List<DrofusAttributeConfigurationElement> Elements { get; set; }
            = new List<DrofusAttributeConfigurationElement>();
    }
}
