// /** @type {import('./$types').Actions} */
// /** @type {import('./$types').PageLoad} */
// /** @type {import('@sveltejs/kit').Handle} */

// import { redirect, fail } from '@sveltejs/kit';
// import axios from 'axios';
// import {
// 	API_LOGIN,
// 	LOGIN_SUCCESS,
// 	COOKIES_TOKEN_NAME,
// 	COOKIES_USER_ID,
// 	COOKIES_EMAIL
// } from '../../lib/server/api';

// export const actions = {
// 	default: async ({ cookies, request }) => {
// 		const formData = await request.formData();
// 		// const username = formData.get('username');
// 		// const password = formData.get('password');
//         try {
//             console.log(formData);
//             const response = await axios.post('http://localhost:8000/auth/login/', formData);
//             console.log(response);
//         } catch (error) {
//             console.error(error);
//         }

// 		// Delete the cookies first
// 		// cookies.delete(COOKIES_TOKEN_NAME, { path: '/' });
// 		// cookies.delete(COOKIES_USER_ID, { path: '/' });

// 		// Where our authentication takes place
// 		// let accessToken;
// 		// let userId;
// 		// try {

// 		// 	// accessToken = response.data.access_token;
// 		// 	// userId = response.data.user_id;

// 		// 	// cookies.set(COOKIES_TOKEN_NAME, accessToken);
// 		// 	// cookies.set(COOKIES_USER_ID, userId);
// 		// 	// cookies.set(COOKIES_EMAIL, email);

// 		// 	console.info(response);
// 		// } catch (err) {
// 		// 	// console.log(err);
// 		// 	// return fail(err.response.status, { email, error: true, message: err.response.data.message });
// 		// }

// 		throw redirect(302, '/app');
// 	}
// };
