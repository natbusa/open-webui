<script lang="ts">
	import { DropdownMenu } from 'bits-ui';
	import { getContext, onMount, tick } from 'svelte';
	import { fly } from 'svelte/transition';
	import { flyAndScale } from '$lib/utils/transitions';

	import { config, user, mobile, settings } from '$lib/stores';

	import Dropdown from '$lib/components/common/Dropdown.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Switch from '$lib/components/common/Switch.svelte';
	import GlobeAlt from '$lib/components/icons/GlobeAlt.svelte';
	import Photo from '$lib/components/icons/Photo.svelte';

	const i18n = getContext('i18n');

	export let selectedModels: string[] = [];
	export let fileUploadCapableModels: string[] = [];

	export let showWebSearchButton = false;
	export let webSearchEnabled = false;
	export let showImageGenerationButton = false;
	export let imageGenerationEnabled = false;
	export let onClose: Function;

	let show = false;

	let fileUploadEnabled = true;
	$: fileUploadEnabled =
		fileUploadCapableModels.length === selectedModels.length &&
		($user?.role === 'admin' || $user?.permissions?.chat?.file_upload);
</script>

<Dropdown
	bind:show
	on:change={(e) => {
		if (e.detail === false) {
			onClose();
		}
	}}
>
	<Tooltip content={$i18n.t('Integrations')} placement="top">
		<slot />
	</Tooltip>
	<div slot="content">
		<DropdownMenu.Content
			class="w-full max-w-70 rounded-2xl px-1 py-1  border border-gray-100  dark:border-gray-800 z-50 bg-white dark:bg-gray-850 dark:text-white shadow-lg max-h-72 overflow-y-auto overflow-x-hidden scrollbar-thin"
			sideOffset={4}
			alignOffset={-6}
			side="bottom"
			align="start"
			transition={flyAndScale}
		>
			<div in:fly={{ x: -20, duration: 150 }}>
				{#if showWebSearchButton}
					<Tooltip content={$i18n.t('Search the internet')} placement="top-start">
						<button
							class="flex w-full justify-between gap-2 items-center px-3 py-1.5 text-sm cursor-pointer rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800/50"
							on:click={() => {
								webSearchEnabled = !webSearchEnabled;
							}}
						>
							<div class="flex-1 truncate">
								<div class="flex flex-1 gap-2 items-center">
									<div class="shrink-0">
										<GlobeAlt />
									</div>

									<div class=" truncate">{$i18n.t('Web Search')}</div>
								</div>
							</div>

							<div class=" shrink-0">
								<Switch
									state={webSearchEnabled}
									on:change={async (e) => {
										const state = e.detail;
										await tick();
									}}
								/>
							</div>
						</button>
					</Tooltip>
				{/if}

				{#if showImageGenerationButton}
					<Tooltip content={$i18n.t('Generate an image')} placement="top-start">
						<button
							class="flex w-full justify-between gap-2 items-center px-3 py-1.5 text-sm cursor-pointer rounded-xl hover:bg-gray-50 dark:hover:bg-gray-800/50"
							on:click={() => {
								imageGenerationEnabled = !imageGenerationEnabled;
							}}
						>
							<div class="flex-1 truncate">
								<div class="flex flex-1 gap-2 items-center">
									<div class="shrink-0">
										<Photo className="size-4" strokeWidth="1.5" />
									</div>

									<div class=" truncate">{$i18n.t('Image')}</div>
								</div>
							</div>

							<div class=" shrink-0">
								<Switch
									state={imageGenerationEnabled}
									on:change={async (e) => {
										const state = e.detail;
										await tick();
									}}
								/>
							</div>
						</button>
					</Tooltip>
				{/if}
			</div>
		</DropdownMenu.Content>
	</div>
</Dropdown>
