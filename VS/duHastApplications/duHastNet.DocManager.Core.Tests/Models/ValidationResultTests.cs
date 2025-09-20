using NUnit.Framework;
using duHastNet.DocManager.Core.Models.Results;

namespace duHastNet.DocManager.Core.Tests.Models;

[TestFixture]
public class ValidationResultTests
{
    [Test]
    public void DefaultConstructor_InitializesWithDefaultValues()
    {
        // Act
        var result = new ValidationResult();

        // Assert
        Assert.That(result.IsValid, Is.False); // Default should be false for safety
        Assert.That(result.Errors, Is.Not.Null);
        Assert.That(result.Errors.Count, Is.EqualTo(0));
        Assert.That(result.Warnings, Is.Not.Null);
        Assert.That(result.Warnings.Count, Is.EqualTo(0));
    }

    [Test]
    public void Success_CreatesValidResult()
    {
        // Act
        var result = ValidationResult.CreateSuccess();

        // Assert
        Assert.That(result.IsValid, Is.True);
        Assert.That(result.Errors.Count, Is.EqualTo(0));
        Assert.That(result.Warnings.Count, Is.EqualTo(0));
    }

    [Test]
    public void Failure_WithSingleError_CreatesInvalidResult()
    {
        // Arrange
        var errorMessage = "Document number is required";

        // Act
        var result = ValidationResult.CreateFailure(errorMessage);

        // Assert
        Assert.That(result.IsValid, Is.False);
        Assert.That(result.Errors.Count, Is.EqualTo(1));
        Assert.That(result.Errors[0], Is.EqualTo(errorMessage));
        Assert.That(result.Warnings.Count, Is.EqualTo(0));
    }

    [Test]
    public void Failure_WithMultipleErrors_CreatesInvalidResult()
    {
        // Arrange
        var error1 = "Document number is required";
        var error2 = "Document name is required";
        var error3 = "Revision is required";

        // Act
        var result = ValidationResult.CreateFailure(error1, error2, error3);

        // Assert
        Assert.That(result.IsValid, Is.False);
        Assert.That(result.Errors.Count, Is.EqualTo(3));
        Assert.That(result.Errors[0], Is.EqualTo(error1));
        Assert.That(result.Errors[1], Is.EqualTo(error2));
        Assert.That(result.Errors[2], Is.EqualTo(error3));
        Assert.That(result.Warnings.Count, Is.EqualTo(0));
    }

    [Test]
    public void Failure_WithNoErrors_CreatesInvalidResult()
    {
        // Act
        var result = ValidationResult.CreateFailure();

        // Assert
        Assert.That(result.IsValid, Is.False);
        Assert.That(result.Errors.Count, Is.EqualTo(0));
        Assert.That(result.Warnings.Count, Is.EqualTo(0));
    }

    [Test]
    public void AddError_AddsErrorToCollection()
    {
        // Arrange
        var result = new ValidationResult();
        var errorMessage = "Invalid document format";

        // Act
        result.AddError(errorMessage);

        // Assert
        Assert.That(result.Errors.Count, Is.EqualTo(1));
        Assert.That(result.Errors[0], Is.EqualTo(errorMessage));
    }

    [Test]
    public void AddWarning_AddsWarningToCollection()
    {
        // Arrange
        var result = new ValidationResult();
        var warningMessage = "Document name contains special characters";

        // Act
        result.AddWarning(warningMessage);

        // Assert
        Assert.That(result.Warnings.Count, Is.EqualTo(1));
        Assert.That(result.Warnings[0], Is.EqualTo(warningMessage));
    }

    [Test]
    public void AddError_MultipleErrors_AddsAllToCollection()
    {
        // Arrange
        var result = new ValidationResult();
        var error1 = "First error";
        var error2 = "Second error";

        // Act
        result.AddError(error1);
        result.AddError(error2);

        // Assert
        Assert.That(result.Errors.Count, Is.EqualTo(2));
        Assert.That(result.Errors[0], Is.EqualTo(error1));
        Assert.That(result.Errors[1], Is.EqualTo(error2));
    }

    [Test]
    public void AddWarning_MultipleWarnings_AddsAllToCollection()
    {
        // Arrange
        var result = new ValidationResult();
        var warning1 = "First warning";
        var warning2 = "Second warning";

        // Act
        result.AddWarning(warning1);
        result.AddWarning(warning2);

        // Assert
        Assert.That(result.Warnings.Count, Is.EqualTo(2));
        Assert.That(result.Warnings[0], Is.EqualTo(warning1));
        Assert.That(result.Warnings[1], Is.EqualTo(warning2));
    }

    [Test]
    public void MixedErrorsAndWarnings_BothCollectionsPopulated()
    {
        // Arrange
        var result = ValidationResult.CreateSuccess();
        var error = "Critical error";
        var warning = "Minor warning";

        // Act
        result.AddError(error);
        result.AddWarning(warning);

        // Assert
        Assert.That(result.Errors.Count, Is.EqualTo(1));
        Assert.That(result.Warnings.Count, Is.EqualTo(1));
        Assert.That(result.Errors[0], Is.EqualTo(error));
        Assert.That(result.Warnings[0], Is.EqualTo(warning));
        // Note: IsValid remains True from Success() - errors don't automatically change it
    }

    [Test]
    public void IsValid_CanBeSetExplicitly()
    {
        // Arrange
        var result = new ValidationResult();

        // Act
        result.IsValid = true;

        // Assert
        Assert.That(result.IsValid, Is.True);
    }
}