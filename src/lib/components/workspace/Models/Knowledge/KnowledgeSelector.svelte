<script lang="ts">
	import { DropdownMenu } from 'bits-ui';
	import { onMount, getContext, createEventDispatcher } from 'svelte';

	import { searchKnowledgeBases } from '$lib/apis/knowledge';

	import { flyAndScale } from '$lib/utils/transitions';
	import { decodeString } from '$lib/utils';

	import Dropdown from '$lib/components/common/Dropdown.svelte';
	import Search from '$lib/components/icons/Search.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Database from '$lib/components/icons/Database.svelte';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let onClose: Function = () => {};

	let show = false;

	let query = '';

	let items = [];

	$: if (query !== null) {
		getItems();
	}

	const getItems = async () => {
		const res = await searchKnowledgeBases(localStorage.token, query).catch(() => {
			return null;
		});

		if (res) {
			items = res.items.map((item) => {
				return {
					...item,
					type: 'collection'
				};
			});
		}
	};

	onMount(async () => {
		getItems();
	});
</script>

<Dropdown
	bind:show
	on:change={(e) => {
		if (e.detail === false) {
			onClose();
			query = '';
		}
	}}
>
	<slot />

	<div slot="content">
		<DropdownMenu.Content
			class="z-[10000] text-black dark:text-white rounded-2xl shadow-lg border border-gray-200 dark:border-gray-800 flex flex-col bg-white dark:bg-gray-850 w-70 p-1.5"
			sideOffset={8}
			side="bottom"
			align="start"
			transition={flyAndScale}
		>
			<div class=" flex w-full space-x-2 px-2 pb-0.5">
				<div class="flex flex-1">
					<div class=" self-center mr-2">
						<Search className="size-3.5" />
					</div>
					<input
						class=" w-full text-sm pr-4 py-1 rounded-r-xl outline-hidden bg-transparent"
						bind:value={query}
						placeholder={$i18n.t('Search')}
					/>
				</div>
			</div>

			<div class="max-h-56 overflow-y-scroll gap-0.5 flex flex-col">
				{#if items.length === 0}
					<div class="text-center text-xs text-gray-500 dark:text-gray-400 pt-4 pb-6">
						{$i18n.t('No knowledge found')}
					</div>
				{:else}
					{#each items as item}
						<div
							class=" px-2.5 py-1 rounded-xl w-full text-left flex justify-between items-center text-sm hover:bg-gray-50 hover:dark:bg-gray-800 hover:dark:text-gray-100 selected-command-option-button"
						>
							<button
								class="w-full flex-1"
								type="button"
								on:click={() => {
									dispatch('select', item);
									show = false;
								}}
							>
								<div class="  text-black dark:text-gray-100 flex items-center gap-1 shrink-0">
									<Tooltip content={$i18n.t('Knowledge Base')} placement="top">
										<Database className="size-4" />
									</Tooltip>

									<Tooltip
										content={item.description || decodeString(item?.name)}
										placement="top-start"
									>
										<div class="line-clamp-1 flex-1 text-sm text-left">
											{decodeString(item?.name)}
										</div>
									</Tooltip>
								</div>
							</button>
						</div>
					{/each}
				{/if}
			</div>
		</DropdownMenu.Content>
	</div>
</Dropdown>
