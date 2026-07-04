from enum import Enum
from typing import List, Dict

class Permission(str, Enum):
    # User Management
    CREATE_USER = "create_user"
    READ_USERS = "read_users"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    
    # Document Management
    UPLOAD_DOCUMENT = "upload_document"
    READ_ALL_DOCUMENTS = "read_all_documents"
    DELETE_DOCUMENT = "delete_document"
    UPLOAD_RESTRICTED_DOCUMENT = "upload_restricted_document"
    READ_RESTRICTED_DOCUMENTS = "read_restricted_documents"
    DELETE_ANY_DOCUMENT = "delete_any_document"
    
    # Analytics & System
    VIEW_ANALYTICS = "view_analytics"
    VIEW_AUDIT_LOGS = "view_audit_logs"
    MANAGE_SYSTEM_ALERTS = "manage_system_alerts"
    
    # Features
    USE_AI_CHAT = "use_ai_chat"

# Configurable role mappings
ROLE_PERMISSIONS: Dict[str, List[Permission]] = {
    "Admin": [p for p in Permission], # Admin has all permissions
    "Manager": [
        Permission.READ_USERS,
        Permission.UPLOAD_DOCUMENT,
        Permission.UPLOAD_RESTRICTED_DOCUMENT,
        Permission.READ_ALL_DOCUMENTS,
        Permission.READ_RESTRICTED_DOCUMENTS,
        Permission.VIEW_ANALYTICS,
        Permission.USE_AI_CHAT
    ],
    "Employee": [
        Permission.USE_AI_CHAT,
        Permission.UPLOAD_DOCUMENT,
    ]
}

def has_permission(role: str, permission: Permission) -> bool:
    role_perms = ROLE_PERMISSIONS.get(role, [])
    return permission in role_perms
