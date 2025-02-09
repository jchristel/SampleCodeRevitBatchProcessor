using System.Reflection;
using PushIt.Utilities;
using PushIt.Models;
namespace PushItTests

{
    public class UtilitiesTests
    {
        string _dataPath = null;

        [SetUp]
        public void Setup()
        {
            _dataPath = @"C:\Users\janchristel\Documents\GitHub\SampleCodeRevitBatchProcessor\VS\PushIt\Testdata\20250205_CSB.csv";
        
        }

        [Test]
        public void LoadRoomsData()
        {
            List<RoomsDataModel> rooms = ReadRoomsData.GetRoomsData(_dataPath,2);
            Assert.That(rooms, Is.Not.Null, "should succesfully read file.");
            Assert.That(rooms.Count, Is.EqualTo(1621), "should read 1621 rooms");

            Console.WriteLine("First room: name short: {0}", rooms[0].NameShort);
            Console.WriteLine("First room: area designed: {0}", rooms[0].AreaDesigned);
            Console.WriteLine("First room: department: {0}", rooms[0].Department);
            Console.WriteLine("First room: subdepartment: {0}", rooms[0].SubDepartment);
            Console.WriteLine("First room: id: {0}", rooms[0].Id);
            Console.WriteLine("First room: area briefed: {0}", rooms[0].AreaBriefed);
        }
        
    }
}