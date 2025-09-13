Use the fluent NUnit syntax for all assertions in any new tests:
✅ Length/Count assertions:

Assert.That(someString, Has.Length.EqualTo(10))
Assert.That(collection, Has.Count.EqualTo(5))
Assert.That(collection, Is.Empty)
Assert.That(collection, Is.Not.Empty)

✅ Collection assertions:

Assert.That(collection, Contains.Item(expectedItem))
Assert.That(collection, Has.All.Property("Name").Not.Null)
Assert.That(collection, Has.Some.Property("Status").EqualTo("Active"))

✅ Property assertions:

Assert.That(obj, Has.Property("Name").EqualTo("Expected"))

✅ String assertions:

Assert.That(text, Does.Contain("substring"))
Assert.That(text, Does.StartWith("prefix"))
Assert.That(text, Does.EndWith("suffix"))

Make sure multiple Asserts are combined into a block using:
// Assert
Assert.Multiple(() =>
    {
        Assert.That...
        Assert.That...
    });