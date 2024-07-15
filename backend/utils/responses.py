from fastapi import status

from middleware.apiMsg import APIMessages

login_responses = {
    status.HTTP_202_ACCEPTED: {
        "description": "Successful login",
        "content": {
            "application/json": {
                "example": {"access_token": "your_token", "token_type": "bearer"}
            }
        },
    },
    status.HTTP_404_NOT_FOUND: {
        "description": APIMessages.USER_NOT_FOUND,
        "content": {
            "application/json": {"example": {"detail": APIMessages.USER_NOT_FOUND}}
        },
    },
    status.HTTP_401_UNAUTHORIZED: {
        "description": APIMessages.INCORRECT_PASSWORD,
        "content": {
            "application/json": {"example": {"detail": APIMessages.INCORRECT_PASSWORD}}
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal server error",
        "content": {
            "application/json": {
                "example": {"detail": "An unexpected error occurred: (e)"}
            }
        },
    },
}

register_responses = {
    status.HTTP_201_CREATED: {
        "description": "User registered successfully",
        "content": {
            "application/json": {
                "example": {
                    "message": APIMessages.USER_CREATED,
                    "data": {
                        "username": "johndoe",
                        "email": "johndoe@example.com",
                        "full_name": "John Doe",
                    },
                }
            }
        },
    },
    status.HTTP_409_CONFLICT: {
        "description": APIMessages.USER_ALREADY_EXISTS,
        "content": {
            "application/json": {
                "example": {"message": APIMessages.USER_ALREADY_EXISTS}
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "An unexpected error occurred during user registration. Please try again later.",
        "content": {
            "application/json": {
                "example": {
                    "detail": "An unexpected error occurred during user registration. Please try again later."
                }
            }
        },
    },
}

get_curr_user_responses = {
    status.HTTP_200_OK: {
        "description": "Current logged in user details",
        "content": {
            "application/json": {
                "example": {
                    "username": "johndoe",
                    "email": "johndoe@example.com",
                    "full_name": "John Doe",
                }
            }
        },
    },
    status.HTTP_401_UNAUTHORIZED: {
        "description": APIMessages.VALIDATION_ERROR,
        "content": {
            "application/json": {"example": {"detail": APIMessages.VALIDATION_ERROR}}
        },
    },
    status.HTTP_404_NOT_FOUND: {
        "description": APIMessages.USER_NOT_FOUND,
        "content": {
            "application/json": {"example": {"detail": APIMessages.USER_NOT_FOUND}}
        },
    },
}

get_file_responses = {
    status.HTTP_200_OK: {
        "description": "Successful file retrieval",
        "content": {
            "application/json": {
                "example": {
                    "name": "example.txt",
                    "uploaded_at": "2024-07-14T12:34:56",
                    "tokenized": True,
                    "embedded": False,
                    "processed": False,
                    "status": None,
                }
            }
        },
    },
    status.HTTP_404_NOT_FOUND: {
        "description": APIMessages.USER_NOT_FOUND,
        "content": {
            "application/json": {"example": {"detail": APIMessages.USER_NOT_FOUND}}
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal server error",
        "content": {
            "application/json": {
                "example": {"detail": "An unexpected error occurred: (e)"}
            }
        },
    },
}

list_user_files_responses = {
    status.HTTP_200_OK: {
        "description": APIMessages.FILES_RETRIEVED,
        "content": {
            "application/json": {
                "example": [
                    {
                        "name": "example.txt",
                        "uploaded_at": "2024-07-14T12:34:56",
                        "tokenized": True,
                        "embedded": False,
                        "processed": False,
                        "status": None,
                    }
                ]
            }
        },
    },
    status.HTTP_404_NOT_FOUND: {
        "description": APIMessages.USER_NOT_FOUND,
        "content": {
            "application/json": {"example": {"detail": APIMessages.USER_NOT_FOUND}}
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal server error",
        "content": {
            "application/json": {
                "example": {"detail": "An unexpected error occurred: (e)"}
            }
        },
    },
}

get_tokens_responses = {
    status.HTTP_200_OK: {
        "description": "Tokens retrieved successfully",
        "content": {
            "application/json": {
                "example": {
                    "message": APIMessages.TOKEN_GET_SUCCESS.format(
                        tokens_id="filename"
                    ),
                    "data": {
                        "processed": "2023-01-01T00:00:00",
                        "doc_loader_used": "loader_name",
                        "token_count": 100,
                        "chunk_count": 10,
                        "chunks": [{"key": "value"}],
                    },
                }
            }
        },
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "User not found or file not found in the database",
        "content": {
            "application/json": {
                "example": {
                    "detail": APIMessages.USER_NOT_FOUND.format(username="username")
                }
            }
        },
    },
    status.HTTP_409_CONFLICT: {
        "description": APIMessages.NOT_TOKENIZED,
        "content": {
            "application/json": {
                "example": {"detail": APIMessages.NOT_TOKENIZED.format(file="filename")}
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "An unexpected error occurred",
        "content": {
            "application/json": {"example": {"detail": "An unexpected error occurred"}}
        },
    },
}

get_tscc_responses = {
    status.HTTP_200_OK: {
        "description": "TSCC data retrieved successfully",
        "content": {
            "application/json": {
                "example": {
                    "message": APIMessages.TOKEN_GET_SUCCESS.format(
                        tokens_id="filename"
                    ),
                    "data": {
                        "processed": "2023-01-01T00:00:00",
                        "process_time": 0.5,
                        "model_used": "model_name",
                        "token_count": 100,
                        "chunk_count": 10,
                        "chunks": ["chunk1", "chunk2"],
                    },
                }
            }
        },
    },
    status.HTTP_404_NOT_FOUND: {
        "description": "User not found or file not found in the database",
        "content": {
            "application/json": {
                "example": {
                    "detail": APIMessages.USER_NOT_FOUND.format(username="username")
                }
            }
        },
    },
    status.HTTP_409_CONFLICT: {
        "description": APIMessages.NOT_TOKENIZED,
        "content": {
            "application/json": {
                "example": {"detail": APIMessages.NOT_TOKENIZED.format(file="filename")}
            }
        },
    },
    status.HTTP_409_CONFLICT: {
        "description": APIMessages.NOT_TSCC_PROCESSED,
        "content": {
            "application/json": {
                "example": {
                    "detail": APIMessages.NOT_TSCC_PROCESSED.format(file="filename")
                }
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "An unexpected error occurred",
        "content": {
            "application/json": {"example": {"detail": "An unexpected error occurred"}}
        },
    },
}

upload_file_responses = {
    status.HTTP_201_CREATED: {
        "description": "File uploaded successfully",
        "content": {
            "application/json": {
                "example": {
                    "message": APIMessages.FILE_UPLOADED.format(file="filename")
                }
            }
        },
    },
    status.HTTP_404_NOT_FOUND: {
        "description": APIMessages.USER_NOT_FOUND,
        "content": {
            "application/json": {
                "example": {
                    "detail": APIMessages.USER_NOT_FOUND.format(username="username")
                }
            }
        },
    },
    status.HTTP_409_CONFLICT: {
        "description": APIMessages.FILE_ALREADY_EXISTS,
        "content": {
            "application/json": {
                "example": {
                    "detail": APIMessages.FILE_ALREADY_EXISTS.format(file="filename")
                }
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "An unexpected error occurred during file upload",
        "content": {
            "application/json": {
                "example": {
                    "detail": "An unexpected error occurred during file upload. Please try again later."
                }
            }
        },
    },
}

generate_tokens_responses = {
    status.HTTP_200_OK: {
        "description": "Tokens generated successfully",
        "content": {
            "application/json": {
                "example": {
                    "message": APIMessages.TOKENIZE_SUCCESS.format(file="filename"),
                    "data": {"tokens": "example_tokens_data"},
                }
            }
        },
    },
    status.HTTP_404_NOT_FOUND: {
        "description": APIMessages.FILE_NOT_FOUND_LOCAL,
        "content": {
            "application/json": {
                "example": {
                    "detail": APIMessages.FILE_NOT_FOUND_LOCAL.format(file="filename")
                }
            }
        },
    },
    status.HTTP_409_CONFLICT: {
        "description": APIMessages.TOKENS_EXISTS,
        "content": {
            "application/json": {
                "example": {"detail": APIMessages.TOKENS_EXISTS.format(file="filename")}
            }
        },
    },
    status.HTTP_400_BAD_REQUEST: {
        "description": APIMessages.TOKENIZATION_FAIL,
        "content": {
            "application/json": {
                "example": {
                    "detail": APIMessages.TOKENIZATION_FAIL.format(
                        file="filename", error="error_message"
                    )
                }
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "An unexpected error occurred during token generation",
        "content": {
            "application/json": {
                "example": {
                    "detail": "An unexpected error occurred during token generation. Please try again later."
                }
            }
        },
    },
}

process_tscc_responses = {
    status.HTTP_202_ACCEPTED: {
        "description": "TSCC processing initiated in the background",
        "content": {
            "application/json": {
                "example": {
                    "message": APIMessages.TSCC_PROCESSING_BACKGROUND.format(
                        file="filename"
                    ),
                }
            }
        },
    },
    status.HTTP_404_NOT_FOUND: {
        "description": APIMessages.FILE_NOT_FOUND_DB,
        "content": {
            "application/json": {
                "example": {
                    "detail": APIMessages.FILE_NOT_FOUND_DB.format(file="filename"),
                }
            }
        },
    },
    status.HTTP_409_CONFLICT: {
        "description": "Conflict: File already processed or not tokenized",
        "content": {
            "application/json": {
                "example": {
                    "detail": APIMessages.NOT_TOKENIZED.format(file="filename"),
                }
            }
        },
    },
    status.HTTP_400_BAD_REQUEST: {
        "description": APIMessages.TSCC_PROCESS_FAIL,
        "content": {
            "application/json": {
                "example": {
                    "detail": APIMessages.TSCC_PROCESS_FAIL.format(
                        file="filename", error="error_message"
                    ),
                }
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal server error during TSCC processing",
        "content": {
            "application/json": {
                "example": {
                    "detail": "An unexpected error occurred during TSCC processing. Please try again later.",
                }
            }
        },
    },
}

query_rag_responses = {
    status.HTTP_200_OK: {
        "description": "Query successful with RAG model",
        "content": {
            "application/json": {
                "example": {
                    "message": APIMessages.RAG_QUERY_SUCCESS,
                    "data": {"query": "query_text", "response": "response_text"},
                }
            }
        },
    },
    status.HTTP_404_NOT_FOUND: {
        "description": APIMessages.FILE_NOT_FOUND_LOCAL,
        "content": {
            "application/json": {
                "example": {
                    "detail": APIMessages.FILE_NOT_FOUND_LOCAL.format(file="filename"),
                }
            }
        },
    },
    status.HTTP_409_CONFLICT: {
        "description": "Conflict: File not tokenized or not yet embedded",
        "content": {
            "application/json": {
                "example": {
                    "detail": APIMessages.NOT_TOKENIZED.format(file="filename"),
                }
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal server error during query processing",
        "content": {
            "application/json": {
                "example": {
                    "detail": "An unexpected error occurred during query processing. Please try again later.",
                }
            }
        },
    },
}

delete_file_responses = {
    status.HTTP_200_OK: {
        "description": "File successfully deleted",
        "content": {
            "application/json": {
                "example": {
                    "message": APIMessages.FILE_DELETED.format(file="filename"),
                }
            }
        },
    },
    status.HTTP_400_BAD_REQUEST: {
        "description": "Failed to delete file from database",
        "content": {
            "application/json": {
                "example": {
                    "detail": APIMessages.FILE_DELETE_FAIL_DB.format(file="filename"),
                }
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal server error during file deletion",
        "content": {
            "application/json": {
                "example": {
                    "detail": "An unexpected error occurred during file deletion. Please try again later.",
                }
            }
        },
    },
}

delete_tokens_responses = {
    status.HTTP_200_OK: {
        "description": APIMessages.TOKENS_DELETE_SUCCESS,
        "content": {
            "application/json": {
                "example": {
                    "message": APIMessages.TOKENS_DELETE_SUCCESS.format(
                        file="filename"
                    ),
                }
            }
        },
    },
    status.HTTP_400_BAD_REQUEST: {
        "description": APIMessages.TOKENS_DELETE_FAIL,
        "content": {
            "application/json": {
                "example": {
                    "detail": APIMessages.TOKENS_DELETE_FAIL,
                }
            }
        },
    },
    status.HTTP_404_NOT_FOUND: {
        "description": APIMessages.FILE_NOT_FOUND_DB,
        "content": {
            "application/json": {
                "example": {
                    "detail": APIMessages.FILE_NOT_FOUND_DB,
                }
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal server error during token deletion",
        "content": {
            "application/json": {
                "example": {
                    "detail": "An unexpected error occurred during token deletion. Please try again later.",
                }
            }
        },
    },
}

delete_tscc_responses = {
    status.HTTP_200_OK: {
        "description": APIMessages.TOKENS_DELETE_SUCCESS,
        "content": {
            "application/json": {
                "example": {
                    "message": APIMessages.TOKENS_DELETE_SUCCESS.format(
                        file="filename"
                    ),
                }
            }
        },
    },
    status.HTTP_400_BAD_REQUEST: {
        "description": APIMessages.NOT_TSCC_PROCESSED,
        "content": {
            "application/json": {
                "example": {
                    "detail": APIMessages.NOT_TSCC_PROCESSED,
                }
            }
        },
    },
    status.HTTP_404_NOT_FOUND: {
        "description": APIMessages.FILE_NOT_FOUND_DB,
        "content": {
            "application/json": {
                "example": {
                    "detail": APIMessages.FILE_NOT_FOUND_DB,
                }
            }
        },
    },
    status.HTTP_500_INTERNAL_SERVER_ERROR: {
        "description": "Internal server error during tscc deletion",
        "content": {
            "application/json": {
                "example": {
                    "detail": "An unexpected error occurred during tscc deletion. Please try again later.",
                }
            }
        },
    },
}
