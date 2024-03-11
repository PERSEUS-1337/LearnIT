# api_messages.py

class APIMessages:
    # Success Messages
    SUCCESS = "Operation successful."
    CREATED = "Resource successfully created."
    UPDATED = "Resource successfully updated."
    DELETED = "Resource successfully deleted."
    FETCHED = "Resource successfully retrieved."

    # Error Messages
    INTERNAL_SERVER_ERROR = "Internal server error."
    BAD_REQUEST = "Malformed request or invalid parameters."
    UNAUTHORIZED = "Authentication failed or missing credentials."
    FORBIDDEN = "Access to the requested resource is forbidden."
    NOT_FOUND = "The requested resource was not found."
    METHOD_NOT_ALLOWED = "The HTTP method used is not allowed for the requested resource."
    CONFLICT = "Conflict with the current state of the server."
    PRECONDITION_FAILED = "A precondition for the request failed."

    # Validation Errors
    VALIDATION_ERROR = "Generic validation error."
    REQUIRED_FIELD = "A required field is missing."
    INVALID_FORMAT = "Invalid data format."
    INVALID_VALUE = "The provided value is invalid."
    TOO_SHORT = "The value is too short."
    TOO_LONG = "The value is too long."

    # Authentication and Authorization
    AUTHENTICATION_REQUIRED = "Authentication is required to access the resource."
    INSUFFICIENT_PERMISSIONS = "The user lacks the necessary permissions."
    TOKEN_EXPIRED = "The authentication token has expired."

    # Resource Specific
    RESOURCE_NOT_FOUND = "The requested resource was not found."
    RESOURCE_ALREADY_EXISTS = "The resource already exists."
    RESOURCE_LIMIT_EXCEEDED = "The maximum limit for the resource has been exceeded."

    # File Upload and Processing
    UPLOAD_SUCCESSFUL = "File upload successful."
    INVALID_FILE_TYPE = "Unsupported file type."
    FILE_SIZE_EXCEEDED = "The file size exceeds the allowed limit."

    # Rate Limiting
    RATE_LIMIT_EXCEEDED = "The rate limit for the user or IP has been exceeded."

    # Maintenance and Downtime
    MAINTENANCE_MODE = "The server is currently undergoing maintenance."

    # User Account Management
    USER_CREATED = "User account successfully created."
    USER_UPDATED = "User account successfully updated."
    USER_DELETED = "User account successfully deleted."
    PASSWORD_CHANGED = "Password successfully changed."

    # User Account Errors
    USER_NOT_FOUND = "User not found."
    USERS_NOT_FOUND = "Users not found."
    USER_ALREADY_EXISTS = "User with this username already exists"

    # Authentication and Login
    LOGIN_SUCCESSFUL = "Login successful."
    LOGOUT_SUCCESSFUL = "Logout successful."

    # Password Reset
    PASSWORD_RESET_REQUESTED = "Password reset requested. Check your email for instructions."
    PASSWORD_RESET_SUCCESSFUL = "Password successfully reset."

    # Account Activation
    ACCOUNT_ACTIVATION_REQUIRED = "Account activation is required. Check your email for instructions."
    ACCOUNT_ACTIVATION_SUCCESSFUL = "Account successfully activated."

    # Session Management
    SESSION_EXPIRED = "Session expired. Please log in again."

    # Two-Factor Authentication (2FA)
    TWO_FACTOR_ENABLED = "Two-factor authentication successfully enabled."
    TWO_FACTOR_DISABLED = "Two-factor authentication successfully disabled."
    TWO_FACTOR_REQUIRED = "Two-factor authentication required for this action."

    # Permissions
    INSUFFICIENT_PRIVILEGES = "You do not have sufficient privileges for this action."

    # Security Alerts
    SECURITY_ALERT = "Security alert: Unusual activity detected on your account."

    # Routes
    AUTH_ROUTE_SUCCESS = "This is the AUTH Route"

    # Custom Application-Specific Messages
    # Add your custom messages here
