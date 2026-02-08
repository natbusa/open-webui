<script lang="ts">
	import { onMount, getContext } from 'svelte';
	import { models } from '$lib/stores';
	import { getReviews } from '$lib/apis/evaluations';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import ChevronUp from '$lib/components/icons/ChevronUp.svelte';
	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';
	import { WEBUI_API_BASE_URL } from '$lib/constants';

	const i18n = getContext('i18n');

	let rankedModels = [];
	let loading = true;
	let orderBy = 'score';
	let direction: 'asc' | 'desc' = 'desc';

	const toggleSort = (key: string) => {
		if (orderBy === key) {
			direction = direction === 'asc' ? 'desc' : 'asc';
		} else {
			orderBy = key;
			direction = key === 'name' ? 'asc' : 'desc';
		}
	};

	const loadReviews = async () => {
		loading = true;
		try {
			const result = await getReviews(localStorage.token);
			const statsMap = new Map((result?.entries ?? []).map((e) => [e.model_id, e]));

			rankedModels = $models
				.filter((m) => !m?.info?.meta?.hidden)
				.map((model) => {
					const s = statsMap.get(model.id);
					return {
						...model,
						score: s?.score ?? null,
						total: s?.total ?? 0,
						positive: s?.positive ?? 0,
						negative: s?.negative ?? 0
					};
				})
				.sort((a, b) => {
					if (a.score === null) return 1;
					if (b.score === null) return -1;
					return b.score - a.score;
				});
		} catch (err) {
			console.error('Reviews load failed:', err);
		}
		loading = false;
	};

	onMount(() => {
		loadReviews();
	});

	$: sortedModels = [...rankedModels].sort((a, b) => {
		const getValue = (m, key) => {
			if (key === 'name') return m.name ?? m.id ?? '';
			if (key === 'score') return m.score === null ? -Infinity : m.score;
			if (key === 'positive' || key === 'negative' || key === 'total') {
				return m[key] ?? 0;
			}
			return 0;
		};
		const aVal = getValue(a, orderBy);
		const bVal = getValue(b, orderBy);
		if (orderBy === 'name') {
			return direction === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
		}
		return direction === 'asc' ? aVal - bVal : bVal - aVal;
	});
</script>

<div
	class="pt-0.5 pb-1 gap-1 flex flex-col md:flex-row justify-between sticky top-0 z-10 bg-white dark:bg-gray-900"
>
	<div class="flex items-center text-xl font-medium px-0.5 gap-2 shrink-0">
		{$i18n.t('Reviews')}
		<span class="text-lg text-gray-500">{rankedModels.length}</span>
	</div>
</div>

<div
	class="scrollbar-hidden relative whitespace-nowrap overflow-x-auto max-w-full rounded-sm min-h-[100px]"
>
	{#if loading}
		<div
			class="absolute inset-0 flex items-center justify-center z-10 bg-white/50 dark:bg-gray-900/50"
		>
			<Spinner className="size-5" />
		</div>
	{/if}

	{#if !rankedModels.length && !loading}
		<div class="text-center text-xs text-gray-500 py-1">{$i18n.t('No models found')}</div>
	{:else if rankedModels.length}
		<table
			class="w-full text-sm text-left text-gray-500 dark:text-gray-400 {loading
				? 'opacity-20'
				: ''}"
		>
			<thead class="text-xs text-gray-800 uppercase bg-transparent dark:text-gray-200">
				<tr class="border-b-[1.5px] border-gray-50 dark:border-gray-850/30">
					{#each [{ key: 'score', label: 'RK', class: 'w-3' }, { key: 'name', label: 'Model', class: '' }, { key: 'score', label: 'Score', class: 'text-right w-fit' }, { key: 'positive', label: 'Positive', class: 'text-right w-5' }, { key: 'negative', label: 'Negative', class: 'text-right w-5' }, { key: 'total', label: 'Total', class: 'text-right w-5' }] as col}
						<th
							scope="col"
							class="px-2.5 py-2 cursor-pointer select-none {col.class}"
							on:click={() => toggleSort(col.key)}
						>
							<div
								class="flex gap-1.5 items-center {col.class.includes('right')
									? 'justify-end'
									: ''}"
							>
								{$i18n.t(col.label)}
								{#if orderBy === col.key}
									{#if direction === 'asc'}<ChevronUp className="size-2" />{:else}<ChevronDown
											className="size-2"
										/>{/if}
								{:else}
									<span class="invisible"><ChevronUp className="size-2" /></span>
								{/if}
							</div>
						</th>
					{/each}
				</tr>
			</thead>
			<tbody>
				{#each sortedModels as model, idx (model.id)}
					<tr
						class="bg-white dark:bg-gray-900 text-xs group hover:bg-gray-50 dark:hover:bg-gray-850/50 transition"
					>
						<td class="px-3 py-1.5 font-medium text-gray-900 dark:text-white">
							{model.score !== null ? idx + 1 : '-'}
						</td>
						<td class="px-3 py-1.5">
							<div class="flex items-center gap-2">
								<img
									src="{WEBUI_API_BASE_URL}/models/model/profile/image?id={model.id}"
									alt={model.name}
									class="size-5 rounded-full object-cover"
								/>
								<span class="font-medium text-gray-800 dark:text-gray-200"
									>{model.name}</span
								>
							</div>
						</td>
						<td class="px-3 py-1.5 text-right font-medium text-gray-900 dark:text-white">
							{model.score !== null ? (model.score * 100).toFixed(1) + '%' : '-'}
						</td>
						<td class="px-3 py-1.5 text-right font-medium text-green-500 w-10">
							{#if model.total === 0}-{:else}
								<Tooltip
									content="{((model.positive / model.total) * 100).toFixed(1)}%"
								>
									<span>{model.positive}</span>
								</Tooltip>
							{/if}
						</td>
						<td class="px-3 py-1.5 text-right font-medium text-red-500 w-10">
							{#if model.total === 0}-{:else}
								<Tooltip
									content="{((model.negative / model.total) * 100).toFixed(1)}%"
								>
									<span>{model.negative}</span>
								</Tooltip>
							{/if}
						</td>
						<td class="px-3 py-1.5 text-right font-medium text-gray-600 dark:text-gray-300 w-10">
							{model.total || '-'}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	{/if}
</div>

<div class="text-gray-500 text-xs mt-1.5 w-full flex justify-end">
	<div class="text-right">
		<div class="line-clamp-1">
			ⓘ {$i18n.t(
				'Reviews are ranked by positive feedback rate with Jeffreys smoothing and confidence weighting.'
			)}
		</div>
		{$i18n.t('Models with fewer reviews are pulled toward an average score until more data is collected.')}
	</div>
</div>
