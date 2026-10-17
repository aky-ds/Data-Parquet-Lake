import unittest

from src.transform import (
    normalize_header,
    generate_record_id,
    coerce_value,
)
from src.validation import validate_record


class TestTransform(unittest.TestCase):

    def test_header_normalization(self):
        self.assertEqual(
            normalize_header(" Customer Name "),
            "customer_name",
        )

    def test_deterministic_record_id(self):
        first = {"name": "Ayaz", "age": 25}
        second = {"age": 25, "name": "Ayaz"}

        self.assertEqual(
            generate_record_id(first),
            generate_record_id(second),
        )

    def test_integer_conversion(self):
        self.assertEqual(coerce_value("25", "int"), 25)

    def test_invalid_integer(self):
        with self.assertRaises(ValueError):
            coerce_value("twenty", "int")

    def test_boolean_conversion(self):
        self.assertTrue(coerce_value("yes", "bool"))
        self.assertFalse(coerce_value("no", "bool"))

    def test_required_field_validation(self):
        schema = {
            "name": {
                "type": "string",
                "nullable": False,
            }
        }

        errors = validate_record(
            {"name": None},
            schema,
        )

        self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()