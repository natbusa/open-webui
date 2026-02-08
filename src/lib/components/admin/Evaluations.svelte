<script>
	import { getContext, tick, onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	import Reviews from './Evaluations/Reviews.svelte';
	import Feedbacks from './Evaluations/Feedbacks.svelte';

	const i18n = getContext('i18n');

	let selectedTab;

	const validTabs = ['reviews', 'feedback'];

	const resolveTab = () => {
		const pathParts = $page.url.pathname.split('/');
		const tabFromPath = pathParts[pathParts.length - 1];

		if (validTabs.includes(tabFromPath)) {
			selectedTab = tabFromPath;
		} else {
			selectedTab = 'reviews';
			goto('/admin/evaluations/reviews', { replaceState: true });
		}
	};

	$: if ($page.url.pathname) {
		resolveTab();
	}

	$: if (selectedTab) {
		scrollToTab(selectedTab);
	}

	const scrollToTab = (tabId) => {
		const tabElement = document.getElementById(tabId);
		if (tabElement) {
			tabElement.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'start' });
		}
	};

	let loaded = false;

	onMount(async () => {
		loaded = true;

		const containerElement = document.getElementById('users-tabs-container');

		if (containerElement) {
			containerElement.addEventListener('wheel', function (event) {
				if (event.deltaY !== 0) {
					containerElement.scrollLeft += event.deltaY;
				}
			});
		}

		await tick();
		scrollToTab(selectedTab);
	});
</script>

{#if loaded}
	<div class="flex flex-col lg:flex-row w-full h-full pb-2 lg:space-x-4">
		<div
			id="users-tabs-container"
			class="tabs mx-[16px] lg:mx-0 lg:px-[16px] flex flex-row overflow-x-auto gap-2.5 max-w-full lg:gap-1 lg:flex-col lg:flex-none lg:w-50 dark:text-gray-200 text-sm font-medium text-left scrollbar-none"
		>
			<button
				id="reviews"
				class="px-0.5 py-1 min-w-fit rounded-lg lg:flex-none flex text-right transition {selectedTab ===
				'reviews'
					? ''
					: ' text-gray-300 dark:text-gray-600 hover:text-gray-700 dark:hover:text-white'}"
				on:click={() => {
					goto('/admin/evaluations/reviews');
				}}
			>
				<div class=" self-center mr-2">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 16 16"
						fill="currentColor"
						class="size-4"
					>
						<path
							fill-rule="evenodd"
							d="M8 1.75a.75.75 0 0 1 .692.462l1.41 3.393 3.664.293a.75.75 0 0 1 .428 1.317l-2.791 2.39.853 3.574a.75.75 0 0 1-1.12.814L8 11.86l-3.136 1.833a.75.75 0 0 1-1.12-.814l.853-3.574-2.79-2.39a.75.75 0 0 1 .427-1.317l3.664-.293 1.41-3.393A.75.75 0 0 1 8 1.75Z"
							clip-rule="evenodd"
						/>
					</svg>
				</div>
				<div class=" self-center">{$i18n.t('Reviews')}</div>
			</button>

			<button
				id="feedback"
				class="px-0.5 py-1 min-w-fit rounded-lg lg:flex-none flex text-right transition {selectedTab ===
				'feedback'
					? ''
					: ' text-gray-300 dark:text-gray-600 hover:text-gray-700 dark:hover:text-white'}"
				on:click={() => {
					goto('/admin/evaluations/feedback');
				}}
			>
				<div class=" self-center mr-2">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 16 16"
						fill="currentColor"
						class="size-4"
					>
						<path
							fill-rule="evenodd"
							d="M5.25 2A2.25 2.25 0 0 0 3 4.25v9a.75.75 0 0 0 1.183.613l1.692-1.195 1.692 1.195a.75.75 0 0 0 .866 0l1.692-1.195 1.693 1.195A.75.75 0 0 0 13 13.25v-9A2.25 2.25 0 0 0 10.75 2h-5.5Zm3.03 3.28a.75.75 0 0 0-1.06-1.06L4.97 6.47a.75.75 0 0 0 0 1.06l2.25 2.25a.75.75 0 0 0 1.06-1.06l-.97-.97h1.315c.76 0 1.375.616 1.375 1.375a.75.75 0 0 0 1.5 0A2.875 2.875 0 0 0 8.625 6.25H7.311l.97-.97Z"
							clip-rule="evenodd"
						/>
					</svg>
				</div>
				<div class=" self-center">{$i18n.t('Feedback')}</div>
			</button>
		</div>

		<div class="flex-1 mt-1 lg:mt-0 px-[16px] lg:pr-[16px] lg:pl-0 overflow-y-scroll">
			{#if selectedTab === 'reviews'}
				<Reviews />
			{:else if selectedTab === 'feedback'}
				<Feedbacks />
			{/if}
		</div>
	</div>
{/if}
