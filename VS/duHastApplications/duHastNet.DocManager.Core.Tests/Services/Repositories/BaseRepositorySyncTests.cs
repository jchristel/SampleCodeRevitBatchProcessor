using NUnit.Framework;
using SQLite;
using duHastNet.DocManager.Core.Services.Repositories;
using duHastNet.DocManager.Core.Models;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services.Repositories;

[TestFixture]
public class BaseRepositorySyncTests
{
    private SQLiteConnection _connection;
    private string _databasePath;
    private TestRepositorySync _repository;

    // Test entity for BaseRepositorySync testing
    [Table("TestEntities")]
    public class TestEntity
    {
        [PrimaryKey, AutoIncrement]
        public int Id { get; set; }

        [NotNull]
        public string Name { get; set; } = string.Empty;

        [NotNull]
        public string Category { get; set; } = string.Empty;

        public int Value { get; set; }

        public TestEntity() { }

        public TestEntity(string name, string category, int value)
        {
            Name = name;
            Category = category;
            Value = value;
        }
    }

    // Concrete implementation for testing BaseRepositorySync
    public class TestRepositorySync : BaseRepositorySync<TestEntity>
    {
        public TestRepositorySync(SQLiteConnection connection) : base(connection)
        {
        }
    }

    [SetUp]
    public void Setup()
    {
        // Create a temporary database file for testing
        _databasePath = Path.GetTempFileName();

        var connectionString = new SQLiteConnectionString(_databasePath,
            storeDateTimeAsTicks: false,
            openFlags: SQLiteOpenFlags.ReadWrite | SQLiteOpenFlags.Create,
            key: null);

        _connection = new SQLiteConnection(connectionString);

        // Create test table
        _connection.CreateTable<TestEntity>();

        _repository = new TestRepositorySync(_connection);
    }

    [TearDown]
    public void TearDown()
    {
        _connection?.Close();

        if (File.Exists(_databasePath))
        {
            File.Delete(_databasePath);
        }
    }

    [Test]
    public void Insert_ValidEntity_ReturnsNumberOfRowsInserted()
    {
        // Arrange
        var entity = new TestEntity("Test Item", "Category A", 100);

        // Act
        var result = _repository.Insert(entity);

        // Assert
        Assert.That(result, Is.EqualTo(1));
        Assert.That(entity.Id, Is.GreaterThan(0)); // Auto-increment should set the ID
    }

    [Test]
    public void GetById_ExistingEntity_ReturnsEntity()
    {
        // Arrange
        var entity = new TestEntity("Test Item", "Category A", 100);
        _repository.Insert(entity);
        var insertedId = entity.Id;

        // Act
        var result = _repository.GetById(insertedId);

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result.Id, Is.EqualTo(insertedId));
        Assert.That(result.Name, Is.EqualTo("Test Item"));
        Assert.That(result.Category, Is.EqualTo("Category A"));
        Assert.That(result.Value, Is.EqualTo(100));
    }

    [Test]
    public void GetById_NonExistentEntity_ReturnsNull()
    {
        // Act
        var result = _repository.GetById(999);

        // Assert
        Assert.That(result, Is.Null);
    }

    [Test]
    public void GetAll_MultipleEntities_ReturnsAllEntities()
    {
        // Arrange
        var entities = new[]
        {
            new TestEntity("Item 1", "Category A", 100),
            new TestEntity("Item 2", "Category B", 200),
            new TestEntity("Item 3", "Category A", 150)
        };

        foreach (var entity in entities)
        {
            _repository.Insert(entity);
        }

        // Act
        var result = _repository.GetAll();

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(3));
    }

    [Test]
    public void GetAll_EmptyTable_ReturnsEmptyList()
    {
        // Act
        var result = _repository.GetAll();

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public void Find_WithPredicate_ReturnsMatchingEntities()
    {
        // Arrange
        var entities = new[]
        {
            new TestEntity("Item 1", "Category A", 100),
            new TestEntity("Item 2", "Category B", 200),
            new TestEntity("Item 3", "Category A", 150)
        };

        foreach (var entity in entities)
        {
            _repository.Insert(entity);
        }

        // Act
        var result = _repository.Find(e => e.Category == "Category A");

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result.All(e => e.Category == "Category A"), Is.True);
    }

    [Test]
    public void Find_NoMatches_ReturnsEmptyList()
    {
        // Arrange
        var entity = new TestEntity("Item 1", "Category A", 100);
        _repository.Insert(entity);

        // Act
        var result = _repository.Find(e => e.Category == "NonExistent");

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public void FirstOrDefault_WithMatchingPredicate_ReturnsFirstMatch()
    {
        // Arrange
        var entities = new[]
        {
            new TestEntity("Item 1", "Category A", 100),
            new TestEntity("Item 2", "Category A", 200)
        };

        foreach (var entity in entities)
        {
            _repository.Insert(entity);
        }

        // Act
        var result = _repository.FirstOrDefault(e => e.Category == "Category A");

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result.Category, Is.EqualTo("Category A"));
    }

    [Test]
    public void FirstOrDefault_NoMatch_ReturnsNull()
    {
        // Arrange
        var entity = new TestEntity("Item 1", "Category A", 100);
        _repository.Insert(entity);

        // Act
        var result = _repository.FirstOrDefault(e => e.Category == "NonExistent");

        // Assert
        Assert.That(result, Is.Null);
    }

    [Test]
    public void Update_ExistingEntity_UpdatesSuccessfully()
    {
        // Arrange
        var entity = new TestEntity("Original Name", "Category A", 100);
        _repository.Insert(entity);

        // Modify the entity
        entity.Name = "Updated Name";
        entity.Value = 250;

        // Act
        var result = _repository.Update(entity);

        // Assert
        Assert.That(result, Is.EqualTo(1));

        // Verify the update
        var updated = _repository.GetById(entity.Id);
        Assert.That(updated.Name, Is.EqualTo("Updated Name"));
        Assert.That(updated.Value, Is.EqualTo(250));
    }

    [Test]
    public void Delete_ExistingEntity_DeletesSuccessfully()
    {
        // Arrange
        var entity = new TestEntity("Test Item", "Category A", 100);
        _repository.Insert(entity);

        // Act
        var result = _repository.Delete(entity);

        // Assert
        Assert.That(result, Is.EqualTo(1));

        // Verify deletion
        var deleted = _repository.GetById(entity.Id);
        Assert.That(deleted, Is.Null);
    }

    [Test]
    public void Delete_ById_DeletesSuccessfully()
    {
        // Arrange
        var entity = new TestEntity("Test Item", "Category A", 100);
        _repository.Insert(entity);
        var entityId = entity.Id;

        // Act
        var result = _repository.Delete(entityId);

        // Assert
        Assert.That(result, Is.EqualTo(1));

        // Verify deletion
        var deleted = _repository.GetById(entityId);
        Assert.That(deleted, Is.Null);
    }

    [Test]
    public void Count_WithEntities_ReturnsCorrectCount()
    {
        // Arrange
        var entities = new[]
        {
            new TestEntity("Item 1", "Category A", 100),
            new TestEntity("Item 2", "Category B", 200),
            new TestEntity("Item 3", "Category A", 150)
        };

        foreach (var entity in entities)
        {
            _repository.Insert(entity);
        }

        // Act
        var result = _repository.Count();

        // Assert
        Assert.That(result, Is.EqualTo(3));
    }

    [Test]
    public void Count_WithPredicate_ReturnsCorrectCount()
    {
        // Arrange
        var entities = new[]
        {
            new TestEntity("Item 1", "Category A", 100),
            new TestEntity("Item 2", "Category B", 200),
            new TestEntity("Item 3", "Category A", 150)
        };

        foreach (var entity in entities)
        {
            _repository.Insert(entity);
        }

        // Act
        var result = _repository.Count(e => e.Category == "Category A");

        // Assert
        Assert.That(result, Is.EqualTo(2));
    }

    [Test]
    public void Exists_WithMatchingPredicate_ReturnsTrue()
    {
        // Arrange
        var entity = new TestEntity("Test Item", "Category A", 100);
        _repository.Insert(entity);

        // Act
        var result = _repository.Exists(e => e.Name == "Test Item");

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public void Exists_WithNoMatch_ReturnsFalse()
    {
        // Arrange
        var entity = new TestEntity("Test Item", "Category A", 100);
        _repository.Insert(entity);

        // Act
        var result = _repository.Exists(e => e.Name == "NonExistent");

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public void InsertAll_MultipleEntities_InsertsAll()
    {
        // Arrange
        var entities = new[]
        {
            new TestEntity("Item 1", "Category A", 100),
            new TestEntity("Item 2", "Category B", 200),
            new TestEntity("Item 3", "Category A", 150)
        };

        // Act
        var result = _repository.InsertAll(entities);

        // Assert
        Assert.That(result, Is.EqualTo(3));

        var allEntities = _repository.GetAll();
        Assert.That(allEntities, Has.Count.EqualTo(3));
    }

    [Test]
    public void UpdateAll_MultipleEntities_UpdatesAll()
    {
        // Arrange
        var entities = new[]
        {
            new TestEntity("Item 1", "Category A", 100),
            new TestEntity("Item 2", "Category B", 200)
        };

        _repository.InsertAll(entities);

        // Modify entities
        entities[0].Value = 150;
        entities[1].Value = 250;

        // Act
        var result = _repository.UpdateAll(entities);

        // Assert
        Assert.That(result, Is.EqualTo(2));

        var updated1 = _repository.GetById(entities[0].Id);
        var updated2 = _repository.GetById(entities[1].Id);
        Assert.That(updated1.Value, Is.EqualTo(150));
        Assert.That(updated2.Value, Is.EqualTo(250));
    }

    [Test]
    public void DeleteAll_MultipleEntities_DeletesAll()
    {
        // Arrange
        var entities = new[]
        {
            new TestEntity("Item 1", "Category A", 100),
            new TestEntity("Item 2", "Category B", 200),
            new TestEntity("Item 3", "Category A", 150)
        };

        _repository.InsertAll(entities);
        var initialCount = _repository.Count();

        // Act
        var result = _repository.DeleteAll(entities);

        // Assert
        Assert.That(result, Is.EqualTo(3));
        Assert.That(initialCount, Is.EqualTo(3));

        var finalCount = _repository.Count();
        Assert.That(finalCount, Is.EqualTo(0));
    }
}
