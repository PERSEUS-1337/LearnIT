<svelte:head>
	<title>Home Page</title>
</svelte:head>

<script>
	let user = "Resty"
</script>

<div class="w-full flex flex-col text-center items-center justify-between">
	<div class="space-y-4">
		<div class="stats stats-horizontal shadow">
			<div class="stat">
				<div class="stat-title">Read Count</div>
				<div class="stat-value">12</div>
			</div>
			
			<div class="stat">
				<div class="stat-title">Time Spent</div>
				<div class="stat-value">19h</div>
			</div>
			
			<div class="stat">
				<div class="stat-title">Unread</div>
				<div class="stat-value">5</div>
			</div>
		</div>

		<div class="divider"></div> 
			
		<div class=" w-full text-4xl font-extralight text-primary-content text-left items-start">
			<p>Welcome</p>
			<p class="-mt-4 -ml-2 text-secondary text-8xl font-thin animate-pulse">
				{user}
			</p>
		</div>
	</div>
	
	<div>
		<p class="text-sm text-accent font-thin">Ready?</p>
		<button class="btn btn-wide btn-secondary text-2xl font-bold">Let's Read!</button>
	</div>
</div>