

namespace duHast.Utils
{
    public static class UnitConversion
    {
        /// <summary>
        /// Converts feet and inches to mm.
        /// </summary>
        /// <param name="value">The value in feet to be converted.</param>
        /// <returns>The converted value in mm.</returns>
        public static double ConvertImperialFeetToMetricMm(double value)
        {
            return value * 304.8;
        }

        /// <summary>
        /// Converts square feet and inches to square meters.
        /// </summary>
        /// <param name="value">The value in square feet to be converted.</param>
        /// <returns>The converted value in square meters.</returns>
        public static double ConvertImperialSquareFeetToMetricSquareMetre(double value)
        {
            return value * 0.092903;
        }

        /// <summary>
        /// Converts cubic feet and inches to cubic meters.
        /// </summary>
        /// <param name="value">The value in cubic feet to be converted.</param>
        /// <returns>The converted value in cubic meters.</returns>
        public static double ConvertImperialCubicFeetToMetricCubicMetre(double value)
        {
            return value * 0.02831685;
        }

        /// <summary>
        /// Converts a length value in millimeters to imperial feet.
        /// </summary>
        /// <param name="length">A float value representing the length in millimeters.</param>
        /// <returns>A float value representing the length in imperial feet.</returns>
        public static double ConvertMmToImperialFeet(double length)
        {
            return length / 304.8;
        }
    }
}
