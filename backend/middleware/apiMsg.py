class APIMessages:
    # User Account Management
    USER_CREATED = "User account successfully created."
    USER_UPDATED = "User account successfully updated."
    USER_DELETED = "User account successfully deleted."

    # User Account Errors
    USER_NOT_FOUND = "User not found."
    USERS_NOT_FOUND = "Users not found."
    USER_ALREADY_EXISTS = "User with this username already exists"
    USER_UPLOAD_NOT_FOUND = "File '{file}' not found in user uploaded files."
    USER_FILE_INSERT_FAIL = (
        "Failed to insert file '{file}' into user '{user}' information."
    )
    USER_FILE_DELETE_FAIL = (
        "Failed to remove file '{file}' from user '{user}' information."
    )
    USER_TOKENS_INSERT_FAIL = (
        "Failed to insert tokens document '{tokens_id}' to user '{user}'."
    )
    USER_TOKENS_DELETE_FAIL = (
        "Failed to remove tokens document '{tokens_id}' from user '{user}'."
    )
    USER_TSCC_INSERT_FAIL = (
        "Failed to insert tscc document '{tscc_id}' to user '{user}'."
    )
    USER_TSCC_DELETE_FAIL = (
        "Failed to remove tscc document '{tscc_id}' from user '{user}'."
    )

    # Authentication and Login
    LOGIN_SUCCESSFUL = "Login successful."
    LOGOUT_SUCCESSFUL = "Logout successful."
    INCORRECT_PASSWORD = "Password is incorrect. Try again"
    VALIDATION_ERROR = "Could not validate credentials. Try logging in again"

    # Routes
    AUTH_ROUTE_SUCCESS = "This is the AUTH Route"
    USER_ROUTE_SUCCESS = "This is the USER Route"
    DOC_ROUTE_SUCCESS = "This is the DOCU Route"
    QNA_ROUTE_SUCCESS = "This is the QnA Route"

    # File Operations
    FILES_RETRIEVED = "Files successfully retrieves from user files"
    FILE_UPLOADED = "File '{file}' successfully uploaded."
    FILE_ALREADY_EXISTS = "File '{file}' already exists in the server."
    FILE_DELETED = "File '{file}' successfilly deleted."
    FILE_DELETED_DB_ONLY = "File '{file}' successfilly deleted on the database but was not found locally on the server."
    FILE_DELETE_FAIL_DB = "File '{file}' was not deleted from the database successflly."
    FILE_NOT_FOUND_LOCAL = "The file '{file}' does not exist on the server."
    FILE_NOT_FOUND_DB = "The file '{file}' does not exist on the database."
    FILES_NOT_FOUND = "There are no files uploaded on the server yet."
    FILE_NOT_ALLOWED = "Only PDF files are allowed."

    UPLOAD_DOC_INSERT_FAIL = "File '{file}' failed to insert in the files database."

    # Tokenization
    TOKEN_GET_SUCCESS = "Token '{tokens_id}' has successfully been retrieved."
    TOKENIZE_SUCCESS = (
        "File '{file}' has been tokenized and embedded in ChromaDB successfully."
    )
    TOKENS_EXISTS = "File '{file}' has already been tokenized."
    NOT_TOKENIZED = "File '{file}' has not yet been tokenized."
    TOKENIZATION_FAIL = "Tokenization failed for file '{file}': {error}"
    TOKENS_DELETE_SUCCESS = "Successfully deleted {file}'s tokens from the database."
    TOKENS_DELETE_FAIL = "Failed to delete document with tokens_id {tokens_id}."
    TOKENS_INSERT_FAIL = "Failed to insert DocTokens of '{file}' into files_db: {error}"
    TOKENS_UPDATE_FAIL = "Failed to update DocTokens of '{file}' in files_db: {error}"
    TOKENS_NOT_FOUND = "DocTokens with ID '{tokens_id}' not found in files_db."

    # RAG
    FILE_NOT_YET_EMBEDDED = "File '{file}' has not yet been embedded to ChromaDB."
    RAG_QUERY_SUCCESS = "RAG Query successful"

    # TSCC
    TSCC_GET_SUCCESS = "TSCC '{tscc_id}' has successfully been retrieved."
    TSCC_NOT_FOUND = "TSCC with tscc_id '{tscc_id}' does not exist in tscc_db."
    NOT_TSCC_PROCESSED = "File '{file}' is not yet processed for TSCC."
    TSCC_PROCESSING_BACKGROUND = "File '{file}' is currently being processed for TSCC."
    TSCC_PROCESS_SUCCESS = "File '{file}' has been successfully processed for TSCC."
    TSCC_PROCESS_FAIL = "TSCC processing failed for '{file}'."
    TSCC_ALREADY_PROCESSED = "File '{file}' has already been processed."
    TSCC_DB_DELETE_SUCCESS = "Sucessfully deleted {file}'s tscc from the database."
    TSCC_DB_DELETE_FAIL = (
        "Failed to delete TSCC document of file '{file}' from tscc_db."
    )
    TSCC_DB_INSERT_FAIL = (
        "Failed to insert TSCC document of file '{file}' into tscc_db."
    )

    APP_DETAILS_SUCCESS = "App details retrieved successfully."
