//
// BSD License
// Copyright 2025, Jan Christel
// All rights reserved.

using NUnit.Framework;
using duHastNet.DocManager.Core.Models.CloudDocManager.MetaData;
using duHastNet.DocManager.Core.Models.CurrentFolder;

namespace duHastNet.DocManager.Core.Tests.Models.CloudDocManager.MetaData
{

[TestFixture]
public class MetaDataMapperAconexTests
{
    private MetaDataMapperAconex _mapper;

    [SetUp]
    public void Setup()
    {
        _mapper = new MetaDataMapperAconex();
    }

    #region Constructor Tests

    [Test]
    public void Constructor_InitializesWithEmptyCollections()
    {
        var mapper = new MetaDataMapperAconex();

        Assert.Multiple(() =>
        {
            Assert.That(mapper, Is.Not.Null);
            Assert.That(mapper.MetaDataMap, Is.Empty);
            Assert.That(mapper.AvailableFields, Is.Empty);
            Assert.That(mapper.SupportedFileTypes, Is.Empty);
            Assert.That(mapper.MetadataTemplateFilePath, Is.EqualTo(string.Empty));
        });
    }

    #endregion

    #region AddMapper Tests

    [Test]
    public void AddMapper_WithValidMapper_AddsToCollection()
    {
        var metaMap = new MetaDataMap("DocumentNumber", null, "Number", null, "Aconex");

        _mapper.AddMapper(metaMap);

        Assert.That(_mapper.MetaDataMap, Has.Count.EqualTo(1));
    }

    [Test]
    public void AddMapper_WithNullMapper_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => _mapper.AddMapper(null));
    }

    [Test]
    public void AddMapper_WithDuplicateMetaFieldName_ThrowsException()
    {
        var metaMap1 = new MetaDataMap("DocumentNumber", null, "Number", null, "Aconex");
        var metaMap2 = new MetaDataMap("DocumentNumber", null, "Num", null, "Aconex");

        _mapper.AddMapper(metaMap1);

        // MetaMapperDuplicateException is internal, so we use Catch to capture any exception
        var ex = Assert.Catch(() => _mapper.AddMapper(metaMap2));
        Assert.That(ex.GetType().Name, Is.EqualTo("MetaMapperDuplicateException"));
    }

    #endregion

    #region RemoveMapper Tests

    [Test]
    public void RemoveMapper_WithExistingMapper_RemovesFromCollection()
    {
        var metaMap = new MetaDataMap("DocumentNumber", null, "Number", null, "Aconex");
        _mapper.AddMapper(metaMap);

        _mapper.RemoveMapper(metaMap);

        Assert.That(_mapper.MetaDataMap, Is.Empty);
    }

    [Test]
    public void RemoveMapper_WithNullMapper_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => _mapper.RemoveMapper(null));
    }

    [Test]
    public void RemoveMapper_WithNonExistentMapper_DoesNotThrow()
    {
        var metaMap = new MetaDataMap("DocumentNumber", null, "Number", null, "Aconex");

        Assert.DoesNotThrow(() => _mapper.RemoveMapper(metaMap));
    }

    #endregion

    #region ClearMappers Tests

    [Test]
    public void ClearMappers_RemovesAllMappers()
    {
        _mapper.AddMapper(new MetaDataMap("Field1", null, "Prop1", null, "Aconex"));
        _mapper.AddMapper(new MetaDataMap("Field2", null, "Prop2", null, "Aconex"));

        _mapper.ClearMappers();

        Assert.That(_mapper.MetaDataMap, Is.Empty);
    }

    #endregion

    #region UpdateAvailableFields Tests

    [Test]
    public void UpdateAvailableFields_WithValidList_UpdatesFields()
    {
        var fields = new List<string> { "DocumentNumber", "DocumentName", "Revision" };

        _mapper.UpdateAvailableFields(fields);

        Assert.Multiple(() =>
        {
            Assert.That(_mapper.AvailableFields, Has.Count.EqualTo(3));
            Assert.That(_mapper.AvailableFields, Contains.Item("DocumentNumber"));
        });
    }

    [Test]
    public void UpdateAvailableFields_WithNullList_ThrowsArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => _mapper.UpdateAvailableFields(null));
    }

    [Test]
    public void UpdateAvailableFields_ReplacesExistingFields()
    {
        _mapper.UpdateAvailableFields(new List<string> { "Field1" });
        _mapper.UpdateAvailableFields(new List<string> { "Field2" });

        Assert.Multiple(() =>
        {
            Assert.That(_mapper.AvailableFields, Has.Count.EqualTo(1));
            Assert.That(_mapper.AvailableFields[0], Is.EqualTo("Field2"));
        });
    }

    #endregion

    #region CleanupInvalidMappings Tests

    [Test]
    public void CleanupInvalidMappings_RemovesInvalidMappings()
    {
        _mapper.UpdateAvailableFields(new List<string> { "ValidField" });
        _mapper.AddMapper(new MetaDataMap("ValidField", null, "Prop1", null, "Aconex"));
        _mapper.AddMapper(new MetaDataMap("InvalidField", null, "Prop2", null, "Aconex"));

        var removed = _mapper.CleanupInvalidMappings();

        Assert.Multiple(() =>
        {
            Assert.That(_mapper.MetaDataMap, Has.Count.EqualTo(1));
            Assert.That(removed, Contains.Item("InvalidField"));
        });
    }

    [Test]
    public void CleanupInvalidMappings_WithAllValidMappings_RemovesNone()
    {
        _mapper.UpdateAvailableFields(new List<string> { "Field1", "Field2" });
        _mapper.AddMapper(new MetaDataMap("Field1", null, "Prop1", null, "Aconex"));
        _mapper.AddMapper(new MetaDataMap("Field2", null, "Prop2", null, "Aconex"));

        var removed = _mapper.CleanupInvalidMappings();

        Assert.Multiple(() =>
        {
            Assert.That(_mapper.MetaDataMap, Has.Count.EqualTo(2));
            Assert.That(removed, Is.Empty);
        });
    }

    #endregion

    #region CleanupInvalidCustomFieldsMappings Tests

    [Test]
    public void CleanupInvalidCustomFieldsMappings_RemovesInvalidDocumentPropertyMappings()
    {
        var customFields = new List<string> { "CustomField1" };
        var defaultProps = new List<string> { "DocumentNumber" };

        _mapper.AddMapper(new MetaDataMap("Meta1", null, "CustomField1", null, "Aconex"));
        _mapper.AddMapper(new MetaDataMap("Meta2", null, "DocumentNumber", null, "Aconex"));
        _mapper.AddMapper(new MetaDataMap("Meta3", null, "InvalidField", null, "Aconex"));

        var removed = _mapper.CleanupInvalidCustomFieldsMappings(customFields, defaultProps);

        Assert.Multiple(() =>
        {
            Assert.That(_mapper.MetaDataMap, Has.Count.EqualTo(2));
            Assert.That(removed, Contains.Item("InvalidField"));
        });
    }

    #endregion

    #region Property Tests

    [Test]
    public void MetadataTemplateFilePath_CanBeSetAndRetrieved()
    {
        var path = @"C:\Template\metadata.csv";

        _mapper.MetadataTemplateFilePath = path;

        Assert.That(_mapper.MetadataTemplateFilePath, Is.EqualTo(path));
    }

    [Test]
    public void SupportedFileTypes_CanBeSetAndRetrieved()
    {
        var fileTypes = new List<SupportedFileType>
        {
            new SupportedFileType { FileExtension = ".pdf" }
        };

        _mapper.SupportedFileTypes = fileTypes;

        Assert.That(_mapper.SupportedFileTypes, Has.Count.EqualTo(1));
    }

    #endregion
}
}
