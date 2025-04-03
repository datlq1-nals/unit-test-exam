from enum import Enum
from typing import Dict, Any

# Order Types
class OrderType(Enum):
    TYPE_A = "A"
    TYPE_B = "B"
    TYPE_C = "C"

# Order Statuses
class OrderStatus(Enum):
    NEW = "new"
    EXPORTED = "exported"
    EXPORT_FAILED = "export_failed"
    PROCESSED = "processed"
    PENDING = "pending"
    ERROR = "error"
    API_ERROR = "api_error"
    API_FAILURE = "api_failure"
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    UNKNOWN_TYPE = "unknown_type"
    DB_ERROR = "db_error"

# Order Priorities
class OrderPriority(Enum):
    HIGH = "high"
    LOW = "low"

# Thresholds
class Thresholds:
    HIGH_VALUE_ORDER = 150.0
    HIGH_PRIORITY_ORDER = 200.0
    API_SUCCESS_THRESHOLD = 50.0
    API_AMOUNT_THRESHOLD = 100.0

# CSV Headers
class CSVHeaders:
    HEADERS = ["ID", "Type", "Amount", "Flag", "Status", "Priority"]
    HIGH_VALUE_NOTE = ["", "", "", "", "Note", "High value order"]

# API Response Status
class APIResponseStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
