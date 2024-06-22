/** @type {import('@playwright/test').PlaywrightTestConfig} */

const config = {
	use: {
		// Base URL to use in actions like `await page.goto('/')`.
		baseURL: 'http://localhost:5000',

		// Collect trace when retrying the failed test.
		trace: 'on-first-retry'
	},

	testDir: 'tests',
	testMatch: /(.+\.)?(test|spec)\.[jt]s/,

	outputDir: 'test-results',

	// Each test is given 30 seconds.
	timeout: 30000,

	contextOptions: {
		storageState: 'playwright/.auth/user.json'
	},

	webServer: {
		command: 'npm run dev',
		url: 'http://localhost:5000',
		reuseExistingServer: !process.env.CI
	}
};

export default config;
