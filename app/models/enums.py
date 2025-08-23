import enum

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class DocumentType(str, enum.Enum):
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    AUDIO = "audio"
    VIDEO = "video"

class DocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"

class AuditAction(str, enum.Enum):
    LOGIN = "login"
    LOGOUT = "logout"
    DOCUMENT_UPLOAD = "document_upload"
    DOCUMENT_DELETE = "document_delete"
    QUERY_EXECUTED = "query_executed"
    SETTINGS_CHANGED = "settings_changed"
    SUBSCRIPTION_CHANGED = "subscription_changed"

class QueryType(str, enum.Enum):
    FACTUAL = "factual"
    INTERPRETIVE = "interpretive"
    COMPARATIVE = "comparative"
    PROCEDURAL = "procedural"

class SubscriptionPlan(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PREMIUM = "premium"

class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    INACTIVE = "inactive"
