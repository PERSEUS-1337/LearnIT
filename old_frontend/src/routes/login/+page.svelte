<svelte:head>
	<title>Login Page</title>
</svelte:head>

<script>
	import axios from 'axios';

	async function handleSubmit(event) {
        event.preventDefault(); // Prevent the default form submission

        const formData = new FormData(event.target); // Collect form data
        try {
            // Include withCredentials: true in the Axios request configuration
            const response = await axios.post('http://localhost:8000/auth/login/', formData);
            console.log(response.data);

			// Set the access_token in localStorage instead of a cookie
            localStorage.setItem('access_token', response.data.access_token);
        } catch (error) {
            console.error(error);
        }
    }
</script>

<div class="hero min-h-screen">
	<div class="hero-content flex-col">
		<div class="text-center p-4 flex flex-col gap-2">
			<h1 class="text-4xl font-bold text-base-100">LearnIT</h1>
			<h2 class="text-3xl font-bold text-accent">Login Page</h2>
		</div>
		<div
			class="card flex-shrink-0 w-full max-w-sm shadow-2xl bg-base-100 card-compact card-bordered"
		>
			<form on:submit|preventDefault={handleSubmit}>
				<div class="card-body">
					<div class="form-control">
						<label for="email" class="label">
							<span class="label-text">Username</span>
						</label>
						<input
							type="text"
							name="username"
							value=''
							placeholder="example123"
							class="input input-bordered required:border-red-500 invalid:border-red-500 autofill:bg-yellow-200"
						/>
					</div>
					<div class="form-control">
						<label for="password" class="label">
							<span class="label-text">Password</span>
						</label>
						<input
							type="password"
							name="password"
							value=''
							placeholder="Password123"
							class="input input-bordered"
						/>
					</div>
					<div class="form-control mt-6">
						<button class="btn btn-secondary">Login</button>
					</div>
					<!-- {#if form?.error}
						<div class="alert alert-error">
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="stroke-current shrink-0 h-6 w-6"
								fill="none"
								viewBox="0 0 24 24"
								><path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
								/></svg
							>
							<span class="error">{form?.message}</span>
						</div>
					{/if} -->
				</div>
			</form>
		</div>
	</div>
</div>
