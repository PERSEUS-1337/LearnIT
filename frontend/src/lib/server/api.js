// api.js

// URLS
// export const BASE_URL = import.meta.env.DEV
// 	? import.meta.env.VITE_DEV_BACKEND_URL
// 	: import.meta.env.VITE_PROD_BACKEND_URL;

export const BASE_URL = "127.0.0.1:8000"

export const API_LOGIN = BASE_URL + '/auth/login';
export const API_GET_DATA = BASE_URL + '/user/me';
export const API_UPDATE_USER_DATA = BASE_URL + '/update-user-data';

// TOKENS
export const TOKEN_EXPIRED = 'Token has expired';
export const AUTHORIZED_ROUTE = 'This is an authorized route. Log-in to continue.';
export const NO_TOKEN = 'No Token provided';

// COOKIES
export const COOKIES_TOKEN_NAME = 'accessToken';
export const COOKIES_USER_ID = 'userId';
export const COOKIES_EMAIL = 'email';

// LOGIN
export const LOGIN_SUCCESS = 'Login Success!';
export const LOGIN_FAILED = 'Login Failed!';
export const INVALID_CREDENTIALS = 'Invalid credentials';
export const USER_NOT_FOUND = 'User not found';

// UPDATE
export const UPDATE_SUCESS = 'Update Success!';

export const PROTECTED_ROUTES = ['/app', '/test'];
