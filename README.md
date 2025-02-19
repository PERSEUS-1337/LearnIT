# LearnIT
An AI-Powered Learning Companion in Education Setting using Text Segmentation and Contextual Condensing (TSCC)

## Installation
Note: This is only for local deployment. Original deployment was handled on DigitalOcean for the Backend, and Vercel for the Frontend. But the application is still accessible locally, given the right configuration and API keys provided.

Make sure to have python and nvm installed:
- Python: https://www.python.org/downloads/
- NVM: https://www.freecodecamp.org/news/node-version-manager-nvm-install-guide/

You may then proceed to setting up the dev environment to run the full stack application:
### For Backend
```
pip install -r requirements.txt
```
This will install all dependencies for the python backend with the latest versions

### For Frontend
```
npm install
```

Refer to `/backend/requirements.txt` and `frontend/package.json` for the full list of dev dependencies required for this project.

## Usage
Make sure to secure your unique API keys (`.env`) for the application to work

### For backend
Located in `/backend/.env`

```
# DB Constants
MONGO_URI = URI of your MongoDB Atlas Instance
DB_NAME = dev (Collection Name for the whole DB (either DEV or PROD)
USER_DB = users (Where the user details are stored)
FILES_DB = files (Where the uploaded files are stored)
DOCS_DB = docs (Where the tokenized documents are stored)
TSCC_DB = tscc (Where the processed tscc tokens are stored)

# Auth Constants
SECRET_KEY = Any string combination that will serve as your "salt"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

# AI Constants
OPENAI_API_KEY = Attainable via your personal OpenAI account, to gain access to OpenAIs GPT models

# Generic Constants
UPLOAD_PATH = db/uploaded_files (Where user files are uploaded locally)

# Droplet SSH Password
DIGITAL_OCEAN_SSH_PWD = Used for backend deployment purposes, accessing the digital ocean SSH terminal
```
### Frontend
Located in `/frontend/.env`
```
API_URL = The link to the backend API, for local, it is http://127.0.0.1:8000, and it may differ for vps backend deployments
```
---
Once you have all the API keys setup, you can run the application by opening two terminals, and executing the two different commands in the two separate folders of frontend and backend

```bash
# /frontend
npm run dev

# /backend
uvicorn main:app --reload
```

### Special Script for DigitalOcean Droplet: ./persist_fastapi_background.sh

This script contains commands to enable the fastapi backend server, running on the DigitalOcean Droplet, to persist in the background, even after disconnecting from the SSH terminal connection.

## User Manual

### Getting Started

1. **Logging In**
    - To start using the application, you need to log in with your credentials.
    - Go to the **Login Page** and enter your username and password.
    - **Remember Me**: You can choose to remain logged in for future sessions.
    - After logging in, you’ll receive an access token for secure access across the app.
2. **Logging Out**
    - To log out, select **Logout** from the user menu.
    - This will immediately end your session and secure your account.
3. **Registering**
    - Unfortunately, the register page has been completely scrapped, but using POSTMAN, you can invoke registration directly to the api by inputting the following information:
        - POST `http://(ip_addr of your backend)/auth/register`
        - username (string)
        - fullname (string)
        - email (string, proper format)
        - password (string, any format)
---

### User Dashboard

Once logged in, you’ll have access to the main user dashboard, which serves as the central hub for navigating all available features.

---

### File Management

The application offers various file-related features. You can view your uploaded files, upload new files, and manage files as needed.

1. **Viewing Files**
    - Go to **Let's Learn** to see a list of files you have uploaded.
    - Each file entry displays its name, upload date, and status (e.g., tokenized or processed).
    - Click on a file to see more details, such as whether the file has been processed or tokenized.
2. **Uploading Files**
    - Click **Upload New File** to add a file.
    - Supported file formats include PDF and text files.
    - After uploading, the file will appear in your file list and will be ready for further processing.
3. **Deleting Files**
    - To delete a file, navigate to **Let's Learn** and select the delete option for the chosen file.
    - **Note**: Deleting a file will also remove any associated tokens and processing data for that file.

---

### **Document Processing**

Once you’ve uploaded a file (as of now, just a PDF is supported), you can use features such as token generation, TSCC processing, and RAG querying.

1. **Generating Tokens**
    - After uploading a file, you can generate tokens by selecting the **Tokenize File** option.
    - Tokens are small units of information extracted from the file content, making further processing efficient.
2. **TSCC Processing**
    - For deeper analysis, you can use **TSCC Processing**.
    - This feature analyzes and processes the file, extracting key content and insights.
    - You can monitor the processing status in **File Details**; once completed, you’ll be able to view the TSCC data.
3. **Querying with RAG Model**
    - With the **RAG Query** tool, you can ask questions or make specific queries about the file’s content.
    - Input your query, and the RAG model will provide a response based on the processed data.
    - Queries work best on tokenized files, so ensure that token generation has been completed beforehand.

## Demo / Screenshots
|Login | Dashboard | Files | Read | Chat |
| -- | -- | -- | -- | -- |
|![Login Page](images/Login%201.png) | ![Dashboard Page](images/Dashboard%201.png) | ![Files Page](images/Files%201.png) | ![Read Page](images/Read%201.png) | ![Chat Page](images/Chat%201.png) |




## Acknowledgement
I would like to thank Jecho Carlos, for providing me with the insights of how to put the whole stack together, and how to optimize the system, as well as Kenneth Renz Tegrado, for guiding me in the the development of the frontend stack, to which without him, I would be lost in development full stack development hell.
