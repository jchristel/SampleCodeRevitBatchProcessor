// BSD License - Copyright 2025, Jan Christel

using duHastNet.PushIt.DataSources.Drofus.Models;
using duHastNet.Utils.Settings;

namespace duHastNet.PushIt.DataSources.Drofus.Services;

/// <summary>
/// Thin wrapper that persists DrofusSettings to a JSON file alongside the
/// existing PushIt settings files.
///
/// Uses the same SettingsUtils<T> pattern already used throughout the project.
///
/// Default file location:
///   %AppData%\duHast\PushIt\DrofusSettings.json
///
/// The settings are stored separately from the main Settings.json so the
/// drofus API-key doesn't inadvertently end up in shared/committed config files.
/// </summary>
public class DrofusSettingsService
{
    private const string FileName = "DrofusSettings.json";

    private readonly SettingsUtils _settingsUtils;

    public DrofusSettingsService(string? settingsDirectory = null)
    {
        // Mirror the path construction used by the rest of PushIt
        var directory = settingsDirectory
            ?? Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
                "duHast",
                "PushIt");

        var filePath = Path.Combine(directory, FileName);
        _settingsUtils = new SettingsUtils(filePath);
    }

    /// <summary>
    /// Loads saved drofus settings. Returns a new empty instance if no file exists yet.
    /// </summary>
    public DrofusSettings Load()
    {
        return _settingsUtils.LoadSettings<DrofusSettings>() ?? new DrofusSettings();
    }

    /// <summary>
    /// Persists drofus settings. Returns true on success.
    /// </summary>
    public bool Save(DrofusSettings settings)
    {
        return _settingsUtils.SaveSettings(settings);
    }

    /// <summary>
    /// Clears saved settings (e.g. when the user deliberately disconnects).
    /// </summary>
    public bool Clear()
    {
        return Save(new DrofusSettings());
    }
}
