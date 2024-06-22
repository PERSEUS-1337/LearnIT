<svelte:head>
	<title>LearnIT</title>
</svelte:head>

<script>
	import MdMenu from 'svelte-icons/md/MdMenu.svelte';
</script>

<div class="h-screen max-w-screen flex flex-col overflow-hidden no-scrollbar gap-4">
	<div class="navbar rounded-md shadow-md p-4">
		<div class="flex-1">
			<button class="btn btn-sm btn-square btn-ghost btn-primary">
				<MdMenu />
			</button>
			<a class="btn btn-ghost text-xl btn-primary">LearnIT</a>
		</div>
		<div class="flex-none gap-2">
			<div class="dropdown dropdown-end">
			<div tabindex="0" role="button" class="btn btn-ghost btn-circle avatar">
				<div class="w-10 rounded-full">
				<img alt="Tailwind CSS Navbar component" src="https://daisyui.com/images/stock/photo-1534528741775-53994a69daeb.jpg" />
				</div>
			</div>
			<ul tabindex="0" class="mt-3 z-[1] p-2 shadow menu menu-sm dropdown-content bg-base-100 rounded-box w-52">
				<li>
				<a class="justify-between">
					Profile
					<span class="badge">New</span>
				</a>
				</li>
				<li><a>Settings</a></li>
				<li><a>Logout</a></li>
			</ul>
			</div>
		</div>
	</div>
	<div class="h-full w-full pb-12 px-4 flex ">
		<slot />
	</div>
</div>


