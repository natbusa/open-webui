<script>
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	import Evaluations from '$lib/components/admin/Evaluations.svelte';

	onMount(() => {
		goto('/admin/evaluations/reviews');
	});
</script>

<Evaluations />
