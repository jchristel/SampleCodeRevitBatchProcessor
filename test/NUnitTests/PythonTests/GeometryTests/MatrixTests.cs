using IronPython.Runtime.Exceptions;
using PythonTests.Setup;

namespace PythonTests.GeometryTests
{
    public class MatrixTests
    {
        [Test]
        public void ClassesShouldBeLoaded()
        {
            Assert.IsNotNull(PythonEngineManager.MatrixClass, "Matrix should be loaded.");
        }

        [Test]
        public void Matrix_ToJson()
        {
            // set up a point2 instance
            dynamic matrixInstance = PythonEngineManager.MatrixClass(3, 3);

            var result = matrixInstance.to_json();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"columns\": 3, \"data\": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]], \"rows\": 3}";

            Assert.AreEqual(jsonString, result);
        }

        [Test]
        public void Matrix_ToJsonUtf()
        {
            // set up a point2 instance
            dynamic matrixInstance = PythonEngineManager.MatrixClass(3, 3);

            var result = matrixInstance.to_json_utf();

            // Output the result to the console
            Console.WriteLine($"Result of to_json: {result}");

            // The expected JSON string
            string jsonString = "{\"columns\": 3, \"data\": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]], \"rows\": 3}";

            Assert.AreEqual(jsonString, result);
        }

        [Test]
        public void Matrix_JsonInitialization_ValidJson_ShouldInitializeMatrix()
        {
            string json = "{\"rows\": 2, \"columns\": 2, \"data\": [[1.0, 2.0], [3.0, 4.0]]}";
            dynamic matrixInstance = PythonEngineManager.MatrixClass(null, null, null, json);

            Assert.AreEqual(2, matrixInstance.rows);
            Assert.AreEqual(2, matrixInstance.columns);
            Assert.AreEqual(1.0, matrixInstance.data[0][0]);
            Assert.AreEqual(4.0, matrixInstance.data[1][1]);
        }

        [Test]
        public void Matrix_sonInitialization_InvalidJson_ShouldThrowValueError()
        {
            string json = "{\"rows\": 2, \"columns\": 2, \"data\": \"invalid data\"}";

            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.MatrixClass(null, null, null, json));
            Assert.That(ex.Message, Does.Contain("Invalid JSON input"));
        }

        [Test]
        public void Matrix_Constructor_ValidDimensions_ShouldInitializeMatrix()
        {
            dynamic matrixInstance = PythonEngineManager.MatrixClass(2, 3);

            Assert.AreEqual(2, matrixInstance.rows);
            Assert.AreEqual(3, matrixInstance.columns);
        }

        [Test]
        public void Matrix_Constructor_InvalidRowType_ShouldThrowTypeError()
        {
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.MatrixClass("2",3));
            Assert.That(ex.Message, Does.Contain("rows must be of type int"));
        }

        [Test]
        public void Matrix_Constructor_InvalidColType_ShouldThrowTypeError()
        {
            var ex = Assert.Throws<TypeErrorException>(() => PythonEngineManager.MatrixClass(2, "3"));
            Assert.That(ex.Message, Does.Contain("cols must be of type int"));
        }

        [Test]
        public void Constructor_InvalidMatrixSize_ShouldThrowValueError()
        {
            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.MatrixClass(5,5));
            Assert.That(ex.Message, Does.Contain("Matrix dimensions must be between 1 and 4"));
        }

        [Test]
        public void Matrix_Constructor_ElementsMismatch_ShouldThrowValueError()
        {
            var elements = new[] { new[] { 1.0, 2.0 }, new[] { 3.0 } };

            var ex = Assert.Throws<ValueErrorException>(() => PythonEngineManager.MatrixClass(2, 2, elements));
            Assert.That(ex.Message, Does.Contain("Elements must match the specified dimensions"));
        }


        [Test]
        public void Matrix_MatrixAddition_SameDimensions_ShouldReturnNewMatrix()
        {
            dynamic matrixA = PythonEngineManager.MatrixClass(2, 2, new[] { new[] { 1.0, 2.0 }, new[] { 3.0, 4.0 } });
            dynamic matrixB = PythonEngineManager.MatrixClass(2, 2, new[] { new[] { 5.0, 6.0 }, new[] { 7.0, 8.0 } });
            dynamic result = matrixA + matrixB;

            Assert.AreEqual(2, result.rows);
            Assert.AreEqual(2, result.columns);
            Assert.AreEqual(6.0, result[0][0]);
            Assert.AreEqual(12.0, result[1][1]);
        }

        // Helper method to perform the addition
        private static dynamic AddMatrices(dynamic matrix, dynamic other)
        {
            return matrix + other;
        }

        [Test]
        public void Matrix_MatrixAddition_DifferentDimensions_ShouldThrowIncompatibleMatrixDimensions()
        {
            dynamic matrixA = PythonEngineManager.MatrixClass(2, 2, new[] { new[] { 1.0, 2.0 }, new[] { 3.0, 4.0 } });
            dynamic matrixB = PythonEngineManager.MatrixClass(3, 2, new[] { new[] { 5.0, 6.0 }, new[] { 7.0, 8.0 }, new[] { 9.0, 10.0 } });

            var ex = Assert.Throws<System.Exception>(() =>
                AddMatrices(matrixA,matrixB)
            );

            Assert.That(ex.Message, Does.Contain("Can only add another matrix with the same dimensions"));
        }

        [Test]
        public void Matrix_MatrixData_Accessor_ShouldReturnCopyOfData()
        {
            dynamic matrix = PythonEngineManager.MatrixClass(2, 2, new[] { new[] { 1.0, 2.0 }, new[] { 3.0, 4.0 } });
            dynamic data = matrix.data;

            // Modify the retrieved data to check if it's a copy
            data[0][0] = 99.0;

            Assert.AreEqual(1.0, matrix[0][0]);
        }

        [Test]
        public void EqualMatricesShouldReturnTrue()
        {
            // Assuming PythonEngineManager.MatrixClass can accept a list of lists instead of a double[,]
            var elementsA = new List<List<double>>
                {
                    new List<double> { 1.0, 2.0 },
                    new List<double> { 3.0, 4.0 }
                };
            var elementsB = new List<List<double>>
                {
                    new List<double> { 1.0, 2.0 },
                    new List<double> { 3.0, 4.0 }
                };

            // Initialize matrices with lists of lists
            var matrixA = PythonEngineManager.MatrixClass(2, 2, elementsA);
            var matrixB = PythonEngineManager.MatrixClass(2, 2, elementsB);

            Assert.IsTrue(matrixA == matrixB, "Expected equal matrices to return true.");
        }

        [Test]
        public void MatricesWithDifferentSizesShouldReturnFalse()
        {
            var matrixA = PythonEngineManager.MatrixClass(2, 2, new[] { new[] { 1.0, 2.0 }, new[] { 3.0, 4.0 } });
            var matrixB = PythonEngineManager.MatrixClass(3, 3, new[] { new[] { 1.0, 2.0, 3.0 }, new[] { 4.0, 5.0, 6.0 }, new[] { 7.0, 8.0, 9.0 } });

            Assert.IsFalse(matrixA == matrixB, "Expected unequal matrices to return false.");
        }

        [Test]
        public void MatricesWithDifferentElementsShouldReturnFalse()
        {
            var matrixA = PythonEngineManager.MatrixClass(2, 2, new[] { new[] { 1.0, 2.0 }, new[] { 3.0, 4.0 } });
            var matrixB = PythonEngineManager.MatrixClass(2, 2, new[] { new[] { 1.0, 2.1 }, new[] { 3.0, 4.0 } }); // 2.1 instead of 2.0

            Assert.IsFalse(matrixA == matrixB, "Expected matrices with different elements to return false.");
        }

        [Test]
        public void EqualMatricesShouldNotBeNotEqual()
        {
            var matrixA = PythonEngineManager.MatrixClass(2, 2, new[] { new[] { 1.0, 2.0 }, new[] { 3.0, 4.0 } });
            var matrixB = PythonEngineManager.MatrixClass(2, 2, new[] { new[] { 1.0, 2.0 }, new[] { 3.0, 4.0 } });

            Assert.IsFalse(matrixA != matrixB, "Expected equal matrices to return false for not equal.");
        }

        [Test]
        public void DifferentMatricesShouldReturnTrueForNotEqual()
        {
            var matrixA = PythonEngineManager.MatrixClass(2, 2, new[] { new[] { 1.0, 2.0 }, new[] { 3.0, 4.0 } });
            var matrixB = PythonEngineManager.MatrixClass(2, 2, new[] { new[] { 1.0, 2.1 }, new[] { 3.0, 4.0 } });

            Assert.IsTrue(matrixA != matrixB, "Expected different matrices to return true for not equal.");
        }

        [Test]
        public void ComparingMatrixWithNullShouldReturnFalse()
        {
            var matrixA = PythonEngineManager.MatrixClass(2, 2, new[] { new[] { 1.0, 2.0 }, new[] { 3.0, 4.0 } });

            Assert.IsFalse(matrixA == null, "Expected a matrix to not equal null.");
        }
    }
}
