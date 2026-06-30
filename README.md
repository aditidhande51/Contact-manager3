# Contact Management System

A command-line contact manager built for Week 3 (Functions & Dictionaries). Contacts are stored
in a dictionary keyed by name, with nested dictionaries holding phone, email, address, group,
and timestamps. Data persists to JSON between runs.

## Features

- Add, search, update, and delete contacts with input validation
- Partial-match search by name or phone number
- Persistent storage via JSON (`contacts_data.json`)
- Manual backup to `contacts_data_backup.json`
- Export to CSV (`contacts_export.csv`)
- Contact statistics (totals, group breakdown, recently updated)
- Menu-driven CLI

## Requirements

- Python 3.8+
- No external dependencies (standard library only)

## Usage

```bash
python contacts_manager.py
```

Follow the on-screen menu to add, search, update, delete, or export contacts.

## Running Tests

```bash
python -m unittest test_contacts.py -v
```

## File Structure

```
week3-contact-manager/
├── contacts_manager.py   # Main application
├── contacts_data.json    # Saved contacts (created at runtime)
├── test_contacts.py      # Unit tests
├── README.md
├── requirements.txt
└── .gitignore
```

## Data Model

Each contact is stored as:

```json
{
  "John Doe": {
    "phone": "12345678900",
    "email": "john@example.com",
    "address": "123 Main Street",
    "group": "Friends",
    "created_at": "2026-06-30T10:00:00",
    "updated_at": "2026-06-30T10:00:00"
  }
}
```

## Notes

- Phone numbers are normalized to digits only and must be 10-15 digits long.
- Email is optional but validated if provided.
- Groups default to "Other" if left blank or invalid.
