<script>
	import { page } from '$app/stores';
</script>

<div class=" text-primary-content h-screen">
	<div class="alert alert-warning">
		<svg
			xmlns="http://www.w3.org/2000/svg"
			class="stroke-current shrink-0 h-6 w-6"
			fill="none"
			viewBox="0 0 24 24"
			><path
				stroke-linecap="round"
				stroke-linejoin="round"
				stroke-width="2"
				d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
			/></svg
		>
		<div>
			<span class="font-bold">{$page.status} {$page.error.message}</span>
			{#if page.status > 499}
				<div class="text-sm">The frontend is running fine. The backend might not be...</div>
			{:else}
				<div class="text-sm">
					The backend is running fine, but you are not supposed to access this.
				</div>
			{/if}
		</div>
		<div>
			{#if page.status > 499}
				<a href="/login" class="btn btn-info btn-xs">Back to Login Page</a>
			{:else}
				<a href="/app" class="btn btn-info btn-xs">Back to App</a>
			{/if}
		</div>
	</div>
</div>

<footer class="footer footer-center text-primary-content">
	<div>
		<p>© 2023 INVENSITY GmbH - All rights reserved</p>
	</div>
</footer>
