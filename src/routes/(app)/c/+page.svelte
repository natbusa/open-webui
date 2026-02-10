<script lang="ts">
  import { onMount } from 'svelte';
  import { toast } from 'svelte-sonner';
  import { goto } from '$app/navigation';

  import Chat from '$lib/components/chat/Chat.svelte';
  import { page } from '$app/stores';
  import { settings } from '$lib/stores';

  onMount(() => {
    if (!$settings?.activeModel) {
      goto('/workspace/models');
      return;
    }

    if ($page.url.searchParams.get('error')) {
      toast.error($page.url.searchParams.get('error') || 'An unknown error occurred.');
    }
  });
</script>

{#if $settings?.activeModel}
  <Chat />
{/if}
