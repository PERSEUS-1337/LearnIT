import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		host: '0.0.0.0',
		port: 5000,
		proxy: {
			'/docu': {
				target: 'http://127.0.0.1:8000',
				changeOrigin: true,
				rewrite: (path) => path.replace(/^\/docu/, '')
			}
		}
	},
	test: {
		include: ['src/**/*.{test,spec}.{js,ts}']
	}
});