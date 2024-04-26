<svelte:head>
	<title>Selection Page</title>
</svelte:head>

<script>
    import FaRegFilePdf from 'svelte-icons/fa/FaRegFilePdf.svelte'
    import FaRegKeyboard from 'svelte-icons/fa/FaRegKeyboard.svelte'
    import IoIosArrowForward from 'svelte-icons/io/IoIosArrowForward.svelte'
    let documentList = [
        {"title":"Lorem Ipsum", "date":"Lorem Ipsum"}, {"title":"Lorem Ipsum 2", "date":"Lorem Ipsum 2"}, 
    ]
</script>

<div class="flex flex-col w-full justify-between gap-4 items-center">
    <div class="flex flex-col w-full gap-4">
        <div class="w-full text-4xl text-left font-extralight text-primary-content ">
            <p>File Selection</p>
        </div>
    
        <div class="w-full space-y-2">
            {#each documentList as document}
                <div class="flex items-center justify-between bg-gray-100 p-4 rounded-md shadow-md">
                    <div class="flex items-center">
                        <div class="size-10 text-secondary">
                            <FaRegFilePdf  />
                        </div>
                        <span class="ml-2">{document.title}</span>
                    </div>
                    <div class="flex items-center">
                        <span class="text-xs italic text-gray-500">{document.date}</span>
                        <div class="size-8 text-accent ml-2">
                            <IoIosArrowForward  />
                        </div>
                    </div>
                </div>
            {/each}
        </div>
    </div>

    <div class="join">
        <button class="btn btn-lg join-item hover:btn-primary">PDF Upload</button>
        <button class="btn btn-lg join-item hover:btn-primary">Text Input</button>
    </div>
</div>