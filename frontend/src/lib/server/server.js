import axios from 'axios';
import { API_GET_DATA } from './api';

export async function fetchData(token) {
	return await axios
		.get(API_GET_DATA, {
			headers: {
				Authorization: `Bearer ${token}` // Include the JWT token in the "Authorization" header
			}
		})
		.then((response) => {
			console.info('Request successful');
			console.info('Status code:', response.status);
			return response.data;
		})
		.catch((error) => {
			console.error('Request failed');
			console.error('Status code:', error.response.status);
			console.error('Error message:', error.response.message);
			throw error;
		});
}
