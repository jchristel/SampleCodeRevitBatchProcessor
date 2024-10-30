using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Microsoft.Scripting.Hosting;
using IronPython.Runtime.Exceptions;

namespace PythonTests
{
    public class MatrixTests
    {
        ScriptEngine _engine;
        ScriptScope _scope;

        [SetUp]
        public void Setup()
        {
            // get a python engine
            ScriptEngine engine = PythonRunner.SetupEngine();
            _scope = engine.CreateScope();

            // get the repository path
            string repoPath = PythonRunner.GetRepositoryPath();

            // set path to matrix class
            var pythonFilePath = Path.Combine(repoPath, @"duHast\Geometry\matrix.py");

            //run the file
            engine.ExecuteFile(pythonFilePath, _scope);

            //store the engine instance
            _engine = engine;

        }

        [Test]
        public void Matrix_ToJson()
        {
            // set up a point2 instance
            dynamic matrixInstance = _scope.GetVariable("Matrix")(3, 3);

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
            dynamic matrixInstance = _scope.GetVariable("Matrix")(3, 3);

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
            dynamic matrixInstance = _scope.GetVariable("Matrix")(null, null, null, json);

            Assert.AreEqual(2, matrixInstance.rows);
            Assert.AreEqual(2, matrixInstance.columns);
            Assert.AreEqual(1.0, matrixInstance.data[0][0]);
            Assert.AreEqual(4.0, matrixInstance.data[1][1]);
        }

        [Test]
        public void Matrix_sonInitialization_InvalidJson_ShouldThrowValueError()
        {
            string json = "{\"rows\": 2, \"columns\": 2, \"data\": \"invalid data\"}";

            var ex = Assert.Throws<ValueErrorException>(() => _scope.GetVariable("Matrix")(null, null, null, json));
            Assert.That(ex.Message, Does.Contain("Invalid JSON input"));
        }

        [Test]
        public void Matrix_Constructor_ValidDimensions_ShouldInitializeMatrix()
        {
            dynamic matrixInstance = _scope.GetVariable("Matrix")(2, 3);

            Assert.AreEqual(2, matrixInstance.rows);
            Assert.AreEqual(3, matrixInstance.columns);
        }

        [Test]
        public void Matrix_Constructor_InvalidRowType_ShouldThrowTypeError()
        {
            var ex = Assert.Throws<TypeErrorException>(() => _scope.GetVariable("Matrix")("2",3));
            Assert.That(ex.Message, Does.Contain("rows must be of type int"));
        }

        [Test]
        public void Matrix_Constructor_InvalidColType_ShouldThrowTypeError()
        {
            var ex = Assert.Throws<TypeErrorException>(() => _scope.GetVariable("Matrix")(2, "3"));
            Assert.That(ex.Message, Does.Contain("cols must be of type int"));
        }

        [Test]
        public void Constructor_InvalidMatrixSize_ShouldThrowValueError()
        {
            var ex = Assert.Throws<ValueErrorException>(() => _scope.GetVariable("Matrix")(5,5));
            Assert.That(ex.Message, Does.Contain("Matrix dimensions must be between 1 and 4"));
        }

        [Test]
        public void Matrix_Constructor_ElementsMismatch_ShouldThrowValueError()
        {
            var elements = new[] { new[] { 1.0, 2.0 }, new[] { 3.0 } };

            var ex = Assert.Throws<ValueErrorException>(() => _scope.GetVariable("Matrix")(2, 2, elements));
            Assert.That(ex.Message, Does.Contain("Elements must match the specified dimensions"));
        }


        [Test]
        public void Matrix_MatrixAddition_SameDimensions_ShouldReturnNewMatrix()
        {
            dynamic matrixA = _scope.GetVariable("Matrix")(2, 2, new[] { new[] { 1.0, 2.0 }, new[] { 3.0, 4.0 } });
            dynamic matrixB = _scope.GetVariable("Matrix")(2, 2, new[] { new[] { 5.0, 6.0 }, new[] { 7.0, 8.0 } });
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
            dynamic matrixA = _scope.GetVariable("Matrix")(2, 2, new[] { new[] { 1.0, 2.0 }, new[] { 3.0, 4.0 } });
            dynamic matrixB = _scope.GetVariable("Matrix")(3, 2, new[] { new[] { 5.0, 6.0 }, new[] { 7.0, 8.0 }, new[] { 9.0, 10.0 } });

            var ex = Assert.Throws<System.Exception>(() =>
                AddMatrices(matrixA,matrixB)
            );

            Assert.That(ex.Message, Does.Contain("Can only add another matrix with the same dimensions"));
        }

        [Test]
        public void Matrix_MatrixData_Accessor_ShouldReturnCopyOfData()
        {
            dynamic matrix = _scope.GetVariable("Matrix")(2, 2, new[] { new[] { 1.0, 2.0 }, new[] { 3.0, 4.0 } });
            dynamic data = matrix.data;

            // Modify the retrieved data to check if it's a copy
            data[0][0] = 99.0;

            Assert.AreEqual(1.0, matrix[0][0]);
        }
    }
}
