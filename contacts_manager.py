"""
Contact Management System
Week 3 Project - Functions & Dictionaries

A command-line contact manager that stores contacts in a dictionary,
persists them to JSON, and supports add/search/update/delete/export
operations with input validation.
"""

import json
import re
import csv
import os
from datetime import datetime, timedelta

DATA_FILE = "contacts_data.json"
BACKUP_FILE = "contacts_data_backup.json"
CSV_FILE = "contacts_export.csv"

VALID_GROUPS = {"Friends", "Work", "Family", "Other"}


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_phone(phone):
    """Validate phone number format. Returns (is_valid, cleaned_digits)."""
    digits = re.sub(r"\D", "", phone)
    if 10 <= len(digits) <= 15:
        return True, digits
    return False, None


def validate_email(email):
    """Validate email format using a simple regex."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_name(name):
    """Names must be non-empty and contain at least one letter."""
    name = name.strip()
    return bool(name) and any(c.isalpha() for c in name)


# ---------------------------------------------------------------------------
# File operations
# ---------------------------------------------------------------------------

def load_from_file(filename=DATA_FILE):
    """Load contacts from a JSON file. Returns an empty dict if missing/corrupt."""
    if not os.path.exists(filename):
        print("No existing contacts file found. Starting fresh.")
        return {}

    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"Loaded {len(data)} contact(s) from {filename}.")
        return data
    except (json.JSONDecodeError, OSError) as e:
        print(f"Could not read {filename} ({e}). Starting with an empty contact list.")
        return {}


def save_to_file(contacts, filename=DATA_FILE):
    """Save contacts dictionary to a JSON file."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(contacts, f, indent=2)
        print(f"Contacts saved to {filename}")
        return True
    except OSError as e:
        print(f"Error saving contacts: {e}")
        return False


def backup_contacts(contacts, filename=BACKUP_FILE):
    """Create a timestamped backup copy of the contacts."""
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(contacts, f, indent=2)
        print(f"Backup written to {filename}")
        return True
    except OSError as e:
        print(f"Error creating backup: {e}")
        return False


def export_to_csv(contacts, filename=CSV_FILE):
    """Export contacts to a CSV file."""
    if not contacts:
        print("No contacts to export.")
        return False

    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Phone", "Email", "Address", "Group",
                              "Created At", "Updated At"])
            for name, info in contacts.items():
                writer.writerow([
                    name,
                    info.get("phone", ""),
                    info.get("email") or "",
                    info.get("address") or "",
                    info.get("group", "Other"),
                    info.get("created_at", ""),
                    info.get("updated_at", ""),
                ])
        print(f"Exported {len(contacts)} contact(s) to {filename}")
        return True
    except OSError as e:
        print(f"Error exporting to CSV: {e}")
        return False


# ---------------------------------------------------------------------------
# CRUD functions
# ---------------------------------------------------------------------------

def add_contact(contacts, name=None, phone=None, email=None, address=None, group=None):
    """
    Add a new contact. If arguments are omitted, prompts the user interactively.
    Returns the updated contacts dictionary.
    """
    print("\n--- ADD NEW CONTACT ---")

    # Name
    if name is None:
        while True:
            name = input("Enter contact name: ").strip()
            if not validate_name(name):
                print("Name cannot be empty and must contain letters!")
                continue
            if name in contacts:
                print(f"Contact '{name}' already exists!")
                choice = input("Do you want to update instead? (y/n): ").strip().lower()
                if choice == "y":
                    update_contact(contacts, name)
                    return contacts
                else:
                    continue
            break
    elif not validate_name(name):
        raise ValueError("Invalid name")

    # Phone
    if phone is None:
        while True:
            phone = input("Enter phone number: ").strip()
            is_valid, cleaned_phone = validate_phone(phone)
            if is_valid:
                break
            print("Invalid phone number! Please enter 10-15 digits.")
    else:
        is_valid, cleaned_phone = validate_phone(phone)
        if not is_valid:
            raise ValueError("Invalid phone number")

    # Email
    if email is None:
        while True:
            email = input("Enter email (optional, press Enter to skip): ").strip()
            if not email or validate_email(email):
                break
            print("Invalid email format!")
    elif email and not validate_email(email):
        raise ValueError("Invalid email")

    # Address / group (only prompt interactively if name was not pre-supplied,
    # i.e. this is an interactive call)
    if address is None:
        address = input("Enter address (optional): ").strip()
    if group is None:
        group = input("Enter group (Friends/Work/Family/Other): ").strip() or "Other"
    if group not in VALID_GROUPS:
        group = "Other"

    now = datetime.now().isoformat()
    contacts[name] = {
        "phone": cleaned_phone,
        "email": email if email else None,
        "address": address if address else None,
        "group": group,
        "created_at": now,
        "updated_at": now,
    }

    print(f"Contact '{name}' added successfully!")
    return contacts


def search_contacts(contacts, search_term):
    """Search contacts by partial, case-insensitive name match."""
    search_term = search_term.lower()
    return {
        name: info for name, info in contacts.items()
        if search_term in name.lower()
    }


def search_by_phone(contacts, phone_term):
    """Search contacts by partial phone number match."""
    digits = re.sub(r"\D", "", phone_term)
    return {
        name: info for name, info in contacts.items()
        if digits in info.get("phone", "")
    }


def update_contact(contacts, name=None):
    """Update an existing contact's fields. Prompts interactively if needed."""
    print("\n--- UPDATE CONTACT ---")

    if name is None:
        name = input("Enter the exact name of the contact to update: ").strip()

    if name not in contacts:
        print(f"Contact '{name}' not found.")
        return contacts

    info = contacts[name]
    print(f"Leave a field blank to keep its current value.")

    new_phone = input(f"Phone [{info['phone']}]: ").strip()
    if new_phone:
        is_valid, cleaned_phone = validate_phone(new_phone)
        if is_valid:
            info["phone"] = cleaned_phone
        else:
            print("Invalid phone number, keeping old value.")

    new_email = input(f"Email [{info.get('email') or ''}]: ").strip()
    if new_email:
        if validate_email(new_email):
            info["email"] = new_email
        else:
            print("Invalid email, keeping old value.")

    new_address = input(f"Address [{info.get('address') or ''}]: ").strip()
    if new_address:
        info["address"] = new_address

    new_group = input(f"Group [{info.get('group')}]: ").strip()
    if new_group:
        info["group"] = new_group if new_group in VALID_GROUPS else "Other"

    info["updated_at"] = datetime.now().isoformat()
    contacts[name] = info
    print(f"Contact '{name}' updated successfully!")
    return contacts


def delete_contact(contacts, name=None, confirm=True):
    """Delete a contact by name, with optional confirmation prompt."""
    print("\n--- DELETE CONTACT ---")

    if name is None:
        name = input("Enter the exact name of the contact to delete: ").strip()

    if name not in contacts:
        print(f"Contact '{name}' not found.")
        return contacts

    if confirm:
        choice = input(f"Are you sure you want to delete '{name}'? (y/n): ").strip().lower()
        if choice != "y":
            print("Deletion cancelled.")
            return contacts

    del contacts[name]
    print(f"Contact '{name}' deleted successfully!")
    return contacts


# ---------------------------------------------------------------------------
# Display functions
# ---------------------------------------------------------------------------

def display_contact(name, info):
    """Print a single contact's details in a formatted block."""
    print(f"{name}")
    print(f"   Phone: {info.get('phone', 'N/A')}")
    if info.get("email"):
        print(f"   Email: {info['email']}")
    if info.get("address"):
        print(f"   Address: {info['address']}")
    print(f"   Group: {info.get('group', 'Other')}")


def display_all(contacts):
    """Display all contacts, sorted alphabetically by name."""
    if not contacts:
        print("\nNo contacts saved yet.")
        return

    print(f"\n--- ALL CONTACTS ({len(contacts)} total) ---")
    print("=" * 60)
    for name in sorted(contacts.keys(), key=str.lower):
        display_contact(name, contacts[name])
        print("-" * 40)


def display_search_results(results):
    """Display search results in a formatted way."""
    if not results:
        print("No contacts found.")
        return

    print(f"\nFound {len(results)} contact(s):")
    print("-" * 50)
    for i, (name, info) in enumerate(sorted(results.items()), 1):
        print(f"{i}. ", end="")
        display_contact(name, info)
        print()


def show_statistics(contacts):
    """Show summary statistics about the contact list."""
    print("\n--- CONTACT STATISTICS ---")
    print(f"Total Contacts: {len(contacts)}")

    if not contacts:
        return

    groups = {}
    recent_count = 0
    cutoff = datetime.now() - timedelta(days=7)

    for info in contacts.values():
        group = info.get("group", "Other")
        groups[group] = groups.get(group, 0) + 1

        updated_at = info.get("updated_at")
        if updated_at:
            try:
                if datetime.fromisoformat(updated_at) >= cutoff:
                    recent_count += 1
            except ValueError:
                pass

    print("\nContacts by Group:")
    for group, count in sorted(groups.items()):
        print(f"  {group}: {count} contact(s)")

    print(f"\nRecently Updated (last 7 days): {recent_count}")


# ---------------------------------------------------------------------------
# Menu / main loop
# ---------------------------------------------------------------------------

def print_menu():
    print("\n" + "=" * 30)
    print("          MAIN MENU")
    print("=" * 30)
    print("1. Add New Contact")
    print("2. Search Contact (by name)")
    print("3. Search Contact (by phone)")
    print("4. Update Contact")
    print("5. Delete Contact")
    print("6. View All Contacts")
    print("7. Export to CSV")
    print("8. View Statistics")
    print("9. Backup Contacts")
    print("10. Exit")
    print("=" * 30)


def get_menu_choice(valid_range):
    """Prompt until the user enters a valid integer within valid_range."""
    while True:
        choice = input(f"Enter your choice (1-{valid_range}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= valid_range:
            return int(choice)
        print("Invalid choice. Please try again.")


def main():
    print("=" * 50)
    print("      CONTACT MANAGEMENT SYSTEM")
    print("=" * 50)

    contacts = load_from_file()

    while True:
        print_menu()
        choice = get_menu_choice(10)

        if choice == 1:
            contacts = add_contact(contacts)
            save_to_file(contacts)

        elif choice == 2:
            term = input("Enter name to search: ").strip()
            display_search_results(search_contacts(contacts, term))

        elif choice == 3:
            term = input("Enter phone (or part of it) to search: ").strip()
            display_search_results(search_by_phone(contacts, term))

        elif choice == 4:
            contacts = update_contact(contacts)
            save_to_file(contacts)

        elif choice == 5:
            contacts = delete_contact(contacts)
            save_to_file(contacts)

        elif choice == 6:
            display_all(contacts)

        elif choice == 7:
            export_to_csv(contacts)

        elif choice == 8:
            show_statistics(contacts)

        elif choice == 9:
            backup_contacts(contacts)

        elif choice == 10:
            save_to_file(contacts)
            print("\n" + "=" * 50)
            print("Thank you for using Contact Management System!")
            print("=" * 50)
            break


if __name__ == "__main__":
    main()
