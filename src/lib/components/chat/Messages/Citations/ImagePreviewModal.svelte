<script lang="ts">
	import XMark from '$lib/components/icons/XMark.svelte';

	export let show = false;
	export let src = '';
	export let alt = '';

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			show = false;
		}
	}
</script>

<svelte:window on:keydown={handleKeydown} />

{#if show}
	<!-- svelte-ignore a11y-click-events-have-key-events -->
	<!-- svelte-ignore a11y-no-static-element-interactions -->
	<div
		class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/80 backdrop-blur-sm"
		on:click={() => (show = false)}
	>
		<div class="relative" on:click|stopPropagation>
			<button
				class="absolute -top-10 right-0 text-white hover:text-gray-300 transition"
				on:click={() => (show = false)}
			>
				<XMark className="size-8" />
			</button>

			<!-- svelte-ignore a11y-click-events-have-key-events -->
			<!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
			<img
				{src}
				{alt}
				class="max-w-[80vw] max-h-[80vh] object-contain rounded-lg shadow-2xl"
			/>
		</div>
	</div>
{/if}
