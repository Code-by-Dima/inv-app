Detailed documentation for the inventory system

Technical overview

Application architecture

The application is built using the following components:

Frontend: Flet (Python framework for creating cross-platform applications)
Database: SQLite (stored in the inventory.db file)
Programming language: Python 3.8+
File structure

main.py - Application entry point, application initialization
db.py - Interaction with the database
models.py - Data models
ui.py - Graphical user interface
requirements.txt - Project dependencies
images/ - Directory for storing object images
Detailed description of functionality

1. Working with inventory

InventoryItem data model

class InventoryItem:
    def __init__(self, id: int, name: str, quantity: int, inv_number: str, 
                 category: str, added_at: str, location_id: int, status: str, 
                 image_path: Optional[str], custom_fields: Optional[str], 
                 description: Optional[str]):
        self.id = id
        self.name = name
        self.quantity = quantity
        self.inv_number = inv_number
        self.category = category
        self.added_at = added_at
        self.location_id = location_id
        self.status = status
        self.image_path = image_path
        self.custom_fields = custom_fields
        self.description = description
Basic database operations

Getting a list of objects

def get_inventory(sort_by=“name”, ascending=True, filters=None):
    # Returns a list of inventory objects
    # sort_by - field for sorting
    # ascending - sorting direction
    # filters - dictionary of filters in the format {field: value}
Adding a new object

def add_inventory(item):
    # Adds a new inventory object
    # item - dictionary with object data
Updating an existing object

def edit_inventory(item_id, item):
    # Updates object data by ID
    # item_id - ID of the object to be updated
    # item - dictionary with updated data
Deleting an object

def delete_inventory(item_id):
    # Deletes an object by ID
    # Also automatically deletes related images
2. Managing storage locations

Location data model

class Location:
    def __init__(self, id: int, name: str, parent_id: Optional[int]):
        self.id = id
        self.name = name
        self.parent_id = parent_id  # To create a hierarchy
Basic operations

get_locations() - get a list of storage locations
add_location(name, parent_id) - add a new location
edit_location(loc_id, name, parent_id) - edit a location
delete_location(loc_id) - delete a location
3. Categories and statuses

Getting lists

get_categories() - get a list of categories
get_statuses() - get a list of statuses
4. Data export

Available export formats

CSV - for further processing in spreadsheets
PDF - for printing or archiving
def export_inventory(fmt=“csv”, filename="inventory_export"):
    # Exports data to the specified format
    # fmt - export format (‘csv’ or ‘pdf’)
    # filename - file name for export (without extension)
5. Change log

HistoryRecord data model

class HistoryRecord:
    def __init__(self, id: int, inventory_id: int, action: str, 
                 timestamp: str, details: str):
        self.id = id
        self.inventory_id = inventory_id
        self.action = action
        self.timestamp = timestamp
        self.details = details
Basic operations

log_history(inventory_id, action, details) - add a record to the log
get_history() - get all log records
Integration with other systems

REST API (possible development)

The application can be extended to provide a REST API for remote control via HTTP requests.

Data import/export

Export to CSV and PDF formats is supported. Standard CSV file processing tools can be used to import data.

Functionality extension

Adding new fields

To add new fields to inventory objects, use the custom fields mechanism:

def add_custom_field(name, field_type):
    # Adds a new custom field
    # name - field name
    # field_type - field type (e.g., ‘text’, ‘number’, ‘date’)
Custom reports

To create custom reports, you can use SQL queries directly to the database or extend the export functionality.

Debugging and logging

The application keeps a log of its work in the console. For advanced logging, it is recommended to add the logging module.

Known limitations

The size of the SQLite database is limited by the size of the disk
No support for simultaneous work by multiple users
No authorization and separation of access rights
Future improvements

Addition of a web interface
Implementation of client-server architecture
Addition of an authorization system
Support for working with external APIs
Implementation of automatic backup

Translated with DeepL.com (free version)
