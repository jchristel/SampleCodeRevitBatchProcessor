namespace duHastNet.AtTheLibrary.Models
{
    public class FamilyDataProperty
    {
        private string _name;
        private string _value;
        private bool _showInUI;

        public string Name { get => _name; }
        public string Value { get => _value; set => _value = value; }
        public bool ShowInUI { get => _showInUI; }

        public FamilyDataProperty(string name, bool showInUI, string value)
        {
            _name = name;
            _value = value;
            _showInUI = showInUI;
        }
    }
}
