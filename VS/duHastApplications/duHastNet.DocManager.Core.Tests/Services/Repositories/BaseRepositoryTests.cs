using NUnit.Framework;
using SQLite;
using duHastNet.DocManager.Core.Services.Repositories;
using duHastNet.DocManager.Core.Models;
using System.IO;

namespace duHastNet.DocManager.Core.Tests.Services.Repositories;

[TestFixture]
public class BaseRepositoryTests
{
    private SQLiteAsyncConnection _connection;
    private string _databasePath;
    private TestRepository _repository;

    // Test entity for BaseRepository testing
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

    // Concrete implementation for testing BaseRepository
    public class TestRepository : BaseRepository<TestEntity>
    {
        public TestRepository(SQLiteAsyncConnection connection) : base(connection)
        {
        }
    }

    [SetUp]
    public async Task Setup()
    {
        // Create a temporary database file for testing
        _databasePath = Path.GetTempFileName();

        var connectionString = new SQLiteConnectionString(_databasePath,
            storeDateTimeAsTicks: false,
            openFlags: SQLiteOpenFlags.ReadWrite | SQLiteOpenFlags.Create,
            key: null);

        _connection = new SQLiteAsyncConnection(connectionString);

        // Create test table
        await _connection.CreateTableAsync<TestEntity>();

        _repository = new TestRepository(_connection);
    }

    [TearDown]
    public async Task TearDown()
    {
        if (_connection != null)
        {
            await _connection.CloseAsync();
        }

        if (File.Exists(_databasePath))
        {
            File.Delete(_databasePath);
        }
    }

    [Test]
    public async Task InsertAsync_ValidEntity_ReturnsNumberOfRowsInserted()
    {
        // Arrange
        var entity = new TestEntity("Test Item", "Category A", 100);

        // Act
        var result = await _repository.InsertAsync(entity);

        // Assert
        Assert.That(result, Is.EqualTo(1));
        Assert.That(entity.Id, Is.GreaterThan(0)); // Auto-increment should set the ID
    }

    [Test]
    public async Task GetByIdAsync_ExistingEntity_ReturnsEntity()
    {
        // Arrange
        var entity = new TestEntity("Test Item", "Category A", 100);
        await _repository.InsertAsync(entity);
        var insertedId = entity.Id;

        // Act
        var result = await _repository.GetByIdAsync(insertedId);

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result.Id, Is.EqualTo(insertedId));
        Assert.That(result.Name, Is.EqualTo("Test Item"));
        Assert.That(result.Category, Is.EqualTo("Category A"));
        Assert.That(result.Value, Is.EqualTo(100));
    }

    [Test]
    public async Task GetByIdAsync_NonExistentEntity_ReturnsNull()
    {
        // Act
        var result = await _repository.GetByIdAsync(999);

        // Assert
        Assert.That(result, Is.Null);
    }

    [Test]
    public async Task GetAllAsync_MultipleEntities_ReturnsAllEntities()
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
            await _repository.InsertAsync(entity);
        }

        // Act
        var result = await _repository.GetAllAsync();

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(3));
    }

    [Test]
    public async Task GetAllAsync_EmptyTable_ReturnsEmptyList()
    {
        // Act
        var result = await _repository.GetAllAsync();

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public async Task FindAsync_WithPredicate_ReturnsMatchingEntities()
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
            await _repository.InsertAsync(entity);
        }

        // Act
        var result = await _repository.FindAsync(e => e.Category == "Category A");

        // Assert
        Assert.That(result, Has.Count.EqualTo(2));
        Assert.That(result.All(e => e.Category == "Category A"), Is.True);
    }

    [Test]
    public async Task FindAsync_NoMatches_ReturnsEmptyList()
    {
        // Arrange
        var entity = new TestEntity("Item 1", "Category A", 100);
        await _repository.InsertAsync(entity);

        // Act
        var result = await _repository.FindAsync(e => e.Category == "NonExistent");

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result, Has.Count.EqualTo(0));
    }

    [Test]
    public async Task FirstOrDefaultAsync_WithMatchingPredicate_ReturnsFirstMatch()
    {
        // Arrange
        var entities = new[]
        {
            new TestEntity("Item 1", "Category A", 100),
            new TestEntity("Item 2", "Category A", 200)
        };

        foreach (var entity in entities)
        {
            await _repository.InsertAsync(entity);
        }

        // Act
        var result = await _repository.FirstOrDefaultAsync(e => e.Category == "Category A");

        // Assert
        Assert.That(result, Is.Not.Null);
        Assert.That(result.Category, Is.EqualTo("Category A"));
    }

    [Test]
    public async Task FirstOrDefaultAsync_NoMatch_ReturnsNull()
    {
        // Arrange
        var entity = new TestEntity("Item 1", "Category A", 100);
        await _repository.InsertAsync(entity);

        // Act
        var result = await _repository.FirstOrDefaultAsync(e => e.Category == "NonExistent");

        // Assert
        Assert.That(result, Is.Null);
    }

    [Test]
    public async Task UpdateAsync_ExistingEntity_UpdatesSuccessfully()
    {
        // Arrange
        var entity = new TestEntity("Original Name", "Category A", 100);
        await _repository.InsertAsync(entity);

        // Modify the entity
        entity.Name = "Updated Name";
        entity.Value = 250;

        // Act
        var result = await _repository.UpdateAsync(entity);

        // Assert
        Assert.That(result, Is.EqualTo(1));

        // Verify the update
        var updated = await _repository.GetByIdAsync(entity.Id);
        Assert.That(updated.Name, Is.EqualTo("Updated Name"));
        Assert.That(updated.Value, Is.EqualTo(250));
    }

    [Test]
    public async Task DeleteAsync_ExistingEntity_DeletesSuccessfully()
    {
        // Arrange
        var entity = new TestEntity("Test Item", "Category A", 100);
        await _repository.InsertAsync(entity);

        // Act
        var result = await _repository.DeleteAsync(entity);

        // Assert
        Assert.That(result, Is.EqualTo(1));

        // Verify deletion
        var deleted = await _repository.GetByIdAsync(entity.Id);
        Assert.That(deleted, Is.Null);
    }

    [Test]
    public async Task DeleteAsync_ById_DeletesSuccessfully()
    {
        // Arrange
        var entity = new TestEntity("Test Item", "Category A", 100);
        await _repository.InsertAsync(entity);
        var entityId = entity.Id;

        // Act
        var result = await _repository.DeleteAsync(entityId);

        // Assert
        Assert.That(result, Is.EqualTo(1));

        // Verify deletion
        var deleted = await _repository.GetByIdAsync(entityId);
        Assert.That(deleted, Is.Null);
    }

    [Test]
    public async Task CountAsync_WithEntities_ReturnsCorrectCount()
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
            await _repository.InsertAsync(entity);
        }

        // Act
        var result = await _repository.CountAsync();

        // Assert
        Assert.That(result, Is.EqualTo(3));
    }

    [Test]
    public async Task CountAsync_WithPredicate_ReturnsCorrectCount()
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
            await _repository.InsertAsync(entity);
        }

        // Act
        var result = await _repository.CountAsync(e => e.Category == "Category A");

        // Assert
        Assert.That(result, Is.EqualTo(2));
    }

    [Test]
    public async Task ExistsAsync_WithMatchingPredicate_ReturnsTrue()
    {
        // Arrange
        var entity = new TestEntity("Test Item", "Category A", 100);
        await _repository.InsertAsync(entity);

        // Act
        var result = await _repository.ExistsAsync(e => e.Name == "Test Item");

        // Assert
        Assert.That(result, Is.True);
    }

    [Test]
    public async Task ExistsAsync_WithNoMatch_ReturnsFalse()
    {
        // Arrange
        var entity = new TestEntity("Test Item", "Category A", 100);
        await _repository.InsertAsync(entity);

        // Act
        var result = await _repository.ExistsAsync(e => e.Name == "NonExistent");

        // Assert
        Assert.That(result, Is.False);
    }

    [Test]
    public async Task InsertAllAsync_MultipleEntities_InsertsAll()
    {
        // Arrange
        var entities = new[]
        {
            new TestEntity("Item 1", "Category A", 100),
            new TestEntity("Item 2", "Category B", 200),
            new TestEntity("Item 3", "Category A", 150)
        };

        // Act
        var result = await _repository.InsertAllAsync(entities);

        // Assert
        Assert.That(result, Is.EqualTo(3));

        var allEntities = await _repository.GetAllAsync();
        Assert.That(allEntities, Has.Count.EqualTo(3));
    }

    [Test]
    public async Task UpdateAllAsync_MultipleEntities_UpdatesAll()
    {
        // Arrange
        var entities = new[]
        {
            new TestEntity("Item 1", "Category A", 100),
            new TestEntity("Item 2", "Category B", 200)
        };

        await _repository.InsertAllAsync(entities);

        // Modify entities
        entities[0].Value = 150;
        entities[1].Value = 250;

        // Act
        var result = await _repository.UpdateAllAsync(entities);

        // Assert
        Assert.That(result, Is.EqualTo(2));

        var updated1 = await _repository.GetByIdAsync(entities[0].Id);
        var updated2 = await _repository.GetByIdAsync(entities[1].Id);
        Assert.That(updated1.Value, Is.EqualTo(150));
        Assert.That(updated2.Value, Is.EqualTo(250));
    }

    [Test]
    public async Task DeleteAllAsync_MultipleEntities_DeletesAll()
    {
        // Arrange
        var entities = new[]
        {
            new TestEntity("Item 1", "Category A", 100),
            new TestEntity("Item 2", "Category B", 200),
            new TestEntity("Item 3", "Category A", 150)
        };

        await _repository.InsertAllAsync(entities);
        var initialCount = await _repository.CountAsync();

        // Act
        var result = await _repository.DeleteAllAsync(entities);

        // Assert
        Assert.That(result, Is.EqualTo(3));
        Assert.That(initialCount, Is.EqualTo(3));

        var finalCount = await _repository.CountAsync();
        Assert.That(finalCount, Is.EqualTo(0));
    }
}