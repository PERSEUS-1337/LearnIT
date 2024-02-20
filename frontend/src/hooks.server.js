/** @type {import('@sveltejs/kit').Handle} */

export async function handle({ event, resolve }) {
	const route = event.url;

	// Start performance measurement
	let start = performance.now();

	// End performance measurement here
	const response = await resolve(event);
	let end = performance.now();
	let responseTime = end - start;
	if (responseTime > 3000) {
		console.info(`🐢 ${route} took ${responseTime.toFixed(2)} ms`);
	} else {
		console.info(`🚀 ${route} took ${responseTime.toFixed(2)} ms`);
	}

	return response;
}
