from typing import Optional, Dict, Any
from datetime import datetime

class InventoryItem:
    def __init__(self, id: int, name: str, quantity: int, inv_number: str, category: str, added_at: str, location_id: int, status: str, image_path: Optional[str], custom_fields: Optional[str], description: Optional[str]):
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

class Location:
    def __init__(self, id: int, name: str, parent_id: Optional[int]):
        self.id = id
        self.name = name
        self.parent_id = parent_id

class HistoryRecord:
    def __init__(self, id: int, inventory_id: int, action: str, timestamp: str, details: str):
        self.id = id
        self.inventory_id = inventory_id
        self.action = action
        self.timestamp = timestamp
        self.details = details

class CustomField:
    def __init__(self, id: int, name: str, field_type: str):
        self.id = id
        self.name = name
        self.field_type = field_type
