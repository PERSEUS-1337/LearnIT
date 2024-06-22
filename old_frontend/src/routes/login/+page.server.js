/** @type {import('./$types').Actions} */
/** @type {import('./$types').PageLoad} */
/** @type {import('@sveltejs/kit').Handle} */
/** @type {import('./$types').PageServerLoad} */

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

			console.info(LOGIN_SUCCESS);

			// Redirect on successful login
			redirect('/app'); // Use return instead of throw to properly redirect
		} catch (err) {
			console.log('Error:', err);

			// Handle error, e.g., by returning a fail action or redirecting to an error page
			// For demonstration, we're just logging the error here
		}
	}
};
