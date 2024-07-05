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
    USER_FILE_UPDATE_FAIL = "Failed to update user '{user}' with new file information."

    # Authentication and Login
    LOGIN_SUCCESSFUL = "Login successful."
    LOGOUT_SUCCESSFUL = "Logout successful."
    INCORRECT_PWD = "Password is incorrect. Try again"

    # Routes
    AUTH_ROUTE_SUCCESS = "This is the AUTH Route"
    DOCU_ROUTE_SUCCESS = "This is the DOCU Route"
    QNA_ROUTE_SUCCESS = "This is the QnA Route"

    # File Operations
    FILE_UPLOADED = "File '{file}' successfully uploaded."
    FILE_ALREADY_EXISTS = "File '{file}' already exists in the server."
    FILE_DELETED = "File '{file}' successfilly deleted."
    FILE_NOT_FOUND_LOCAL = "The file '{file}' does not exist on the server."
    FILES_NOT_FOUND = "There are no files uploaded on the server yet."
    FILE_NOT_FOUND_DB = "The file '{file}' does not exist on the database."

    # Tokenization
    FILE_TOKENIZE_SUCCESS = (
        "File '{file}' has been tokenized and embedded in ChromaDB successfully."
    )
    FILE_ALREADY_TOKENIZED = "File '{file}' has already been tokenized."
    FILE_NOT_YET_TOKENIZED = "File '{file}' has not yet been tokenized."
    TOKENIZE_FILE_FAIL = "Tokenization failed for file '{file}': {error}"
    DELETE_TOKENS_SUCCESS = "Successfully deleted {file}'s tokens from the database."
    DELETE_TOKENS_FAIL = "Failed to delete document with tokens_id {tokens_id}."
    USER_TOKENS_UPDATE_FAIL = (
        "Failed to update user '{user}' with tokenized file '{file}'."
    )
    TOKENS_DB_INSERT_FAIL = (
        "Failed to insert DocTokens of '{file}' into docs_db: {error}"
    )
    TOKENS_NOT_FOUND_DB = "DocTokens with ID '{tokens_id}' not found in docs_db."

    # RAG
    FILE_NOT_YET_EMBEDDED = "File '{file}' has not yet been embedded to ChromaDB."
    RAG_QUERY_SUCCESS = "RAG Query successful"

    # TSCC
    TSCC_NOT_FOUND = "TSCC with tscc_id '{tscc_id}' does not exists in tscc_db."
    TSCC_ALREADY_PROCESSED = "File '{file}' has already been processed."
    TSCC_PROCESS_SUCCESS = "File '{file}' has been successfully processed for TSCC."
    TSCC_DB_DELETE_SUCCESS = "Sucessfully deleted {file}'s tscc from the database."
    TSCC_DB_DELETE_FAIL = (
        "Failed to delete TSCC document of file '{file}' from tscc_db."
    )
    TSCC_DB_INSERT_FAIL = (
        "Failed to insert TSCC document of file '{file}' into tscc_db."
    )
