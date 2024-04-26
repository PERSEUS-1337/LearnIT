/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {}
	},
	plugins: [require('daisyui')],
	daisyui: {
		themes: [
			{
				mytheme: {
					primary: '#002c53',
					secondary: '#83b817',
					accent: '#c1d4ec',
					neutral: '#2b3440',
					'base-100': '#ffffff',
					info: '#3abff8',
					success: '#36d399',
					warning: '#fbbd23',
					error: '#f87272'
				},
				learnit_theme: {
					primary: '#CBE4DE',
					secondary: '#2E4F4F',
					accent: '#0E8388',
					neutral: '#2C3333',
					'base-100': '#efefef',
					info: '#7ED4FC',
					success: '#6EE7B7',
					warning: '#FDBA72',
					error: '#F87272'
				}
			}
		]
	}
};
