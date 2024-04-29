// /** @type {import('./$types').Actions} */
// /** @type {import('./$types').PageLoad} */
// /** @type {import('@sveltejs/kit').Handle} */

// import axios from 'axios';

// export const actions = {
// 	default: async ({ request }) => {
// 		const formData = await request.formData();
// 		console.log(formData);
// 		try {
// 			const response = await axios.post('http://localhost:8000/docu/upload/', formData);
// 			console.log(response);
// 		} catch (error) {
// 			console.error(error);
// 		}
// 	}
// };
