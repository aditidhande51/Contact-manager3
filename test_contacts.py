"""
Unit tests for contacts_manager.py
Run with: python -m unittest test_contacts.py
"""

import unittest
import os
from contacts_manager import (
    validate_phone,
    validate_email,
    validate_name,
    add_contact,
    search_contacts,
    search_by_phone,
    update_contact,
    delete_contact,
    save_to_file,
    load_from_file,
    export_to_csv,
)


class TestValidation(unittest.TestCase):

    def test_validate_phone_valid(self):
        is_valid, digits = validate_phone("+1 (234) 567-8900")
        self.assertTrue(is_valid)
        self.assertEqual(digits, "12345678900")

    def test_validate_phone_too_short(self):
        is_valid, digits = validate_phone("12345")
        self.assertFalse(is_valid)
        self.assertIsNone(digits)

    def test_validate_phone_too_long(self):
        is_valid, digits = validate_phone("1" * 20)
        self.assertFalse(is_valid)

    def test_validate_email_valid(self):
        self.assertTrue(validate_email("john@example.com"))

    def test_validate_email_invalid(self):
        self.assertFalse(validate_email("not-an-email"))
        self.assertFalse(validate_email("missing@domain"))

    def test_validate_name(self):
        self.assertTrue(validate_name("John Doe"))
        self.assertFalse(validate_name("   "))
        self.assertFalse(validate_name("123"))


class TestCRUD(unittest.TestCase):

    def setUp(self):
        self.contacts = {}

    def test_add_contact_programmatic(self):
        self.contacts = add_contact(
            self.contacts,
            name="Jane Smith",
            phone="234-567-8901",
            email="jane@example.com",
            address="42 Elm St",
            group="Work",
        )
        self.assertIn("Jane Smith", self.contacts)
        self.assertEqual(self.contacts["Jane Smith"]["phone"], "2345678901")
        self.assertEqual(self.contacts["Jane Smith"]["group"], "Work")

    def test_add_contact_invalid_phone_raises(self):
        with self.assertRaises(ValueError):
            add_contact(self.contacts, name="Bad Phone", phone="123")

    def test_add_contact_invalid_email_raises(self):
        with self.assertRaises(ValueError):
            add_contact(self.contacts, name="Bad Email", phone="2345678901",
                         email="not-an-email")

    def test_search_contacts_partial_match(self):
        self.contacts = add_contact(self.contacts, name="John Doe",
                                     phone="2345678901", email="", address="", group="Friends")
        self.contacts = add_contact(self.contacts, name="Johnny Appleseed",
                                     phone="3456789012", email="", address="", group="Friends")
        results = search_contacts(self.contacts, "john")
        self.assertEqual(len(results), 2)

    def test_search_by_phone(self):
        self.contacts = add_contact(self.contacts, name="John Doe",
                                     phone="2345678901", email="", address="", group="Friends")
        results = search_by_phone(self.contacts, "5678901")
        self.assertIn("John Doe", results)

    def test_update_contact(self):
        self.contacts = add_contact(self.contacts, name="John Doe",
                                     phone="2345678901", email="", address="", group="Friends")
        info = self.contacts["John Doe"]
        info["phone"] = "9999999999"
        info["updated_at"] = "2026-06-30T00:00:00"
        self.contacts["John Doe"] = info
        self.assertEqual(self.contacts["John Doe"]["phone"], "9999999999")

    def test_delete_contact_no_confirm(self):
        self.contacts = add_contact(self.contacts, name="John Doe",
                                     phone="2345678901", email="", address="", group="Friends")
        self.contacts = delete_contact(self.contacts, name="John Doe", confirm=False)
        self.assertNotIn("John Doe", self.contacts)

    def test_delete_nonexistent_contact(self):
        result = delete_contact(self.contacts, name="Nobody", confirm=False)
        self.assertEqual(result, {})


class TestFileOperations(unittest.TestCase):

    def setUp(self):
        self.test_file = "test_contacts_data.json"
        self.test_csv = "test_contacts_export.csv"
        self.contacts = {}
        self.contacts = add_contact(
            self.contacts, name="Jane Smith", phone="2345678901",
            email="jane@example.com", address="42 Elm St", group="Work"
        )

    def tearDown(self):
        for f in (self.test_file, self.test_csv):
            if os.path.exists(f):
                os.remove(f)

    def test_save_and_load(self):
        save_to_file(self.contacts, self.test_file)
        loaded = load_from_file(self.test_file)
        self.assertIn("Jane Smith", loaded)
        self.assertEqual(loaded["Jane Smith"]["phone"], "2345678901")

    def test_load_missing_file_returns_empty(self):
        loaded = load_from_file("does_not_exist.json")
        self.assertEqual(loaded, {})

    def test_export_to_csv(self):
        result = export_to_csv(self.contacts, self.test_csv)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.test_csv))


if __name__ == "__main__":
    unittest.main()
