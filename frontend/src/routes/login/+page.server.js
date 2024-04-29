/** @type {import('./$types').Actions} */
/** @type {import('./$types').PageLoad} */
/** @type {import('@sveltejs/kit').Handle} */

import { redirect, fail } from '@sveltejs/kit';
import axios from 'axios';
import {
	API_LOGIN,
	LOGIN_SUCCESS,
	COOKIES_TOKEN_NAME,
	COOKIES_USER_ID,
	COOKIES_EMAIL
} from '../../lib/server/api';

export const actions = {
	default: async ({ cookies, request }) => {
		const formData = await request.formData();
		const username = formData.get('username');
		const password = formData.get('password');
		console.log(username, password);

		// Delete the cookies first
		// cookies.delete(COOKIES_TOKEN_NAME);
		// cookies.delete(COOKIES_USER_ID);

		// Where our authentication takes place
		let accessToken;
		let userId;
		try {
			const response = await axios.post('http://localhost:8000/auth/login', {
				username: username,
				password: password
			});
            console.log(response);
			accessToken = response.data.access_token;
			// userId = response.data.user_id;

			// cookies.set(COOKIES_TOKEN_NAME, accessToken);
			// cookies.set(COOKIES_USER_ID, userId);
			// cookies.set(COOKIES_EMAIL, email);

			console.info(LOGIN_SUCCESS);
		} catch (err) {
			console.log(err);
			// return fail(err.response, { username, error: true, message: err.response.data.message });
		}

		// throw redirect(302, '/app');
	}
};
