<script lang="ts">
  import { getContext, createEventDispatcher } from 'svelte';
  import { fade } from 'svelte/transition';

  const dispatch = createEventDispatcher();

  import { getChatList } from '$lib/apis/chats';
  import {
    config,
    user,
    models as _models,
    temporaryChatEnabled,
    selectedFolder,
    chats,
    currentChatPage
  } from '$lib/stores';

  import Suggestions from './Suggestions.svelte';
  import Tooltip from '$lib/components/common/Tooltip.svelte';
  import EyeSlash from '$lib/components/icons/EyeSlash.svelte';
  import MessageInput from './MessageInput.svelte';
  import FolderPlaceholder from './Placeholder/FolderPlaceholder.svelte';
  import FolderTitle from './Placeholder/FolderTitle.svelte';

  const i18n = getContext('i18n');

  export let createMessagePair: Function;
  export let stopResponse: Function;

  export let autoScroll = false;

  export let activeModelId: string = '';

  export let history;

  export let prompt = '';
  export let files = [];
  export let messageInput = null;

  export let imageGenerationEnabled = false;
  export let webSearchEnabled = false;

  export let onUpload: Function = (e) => {};
  export let onSelect = (e) => {};
  export let onChange = (e) => {};

  $: model = $_models.find((m) => m.id === activeModelId);
</script>

<div class="m-auto w-full max-w-6xl px-2 @2xl:px-20 translate-y-6 py-24 text-center">
  {#if $temporaryChatEnabled}
    <Tooltip
      content={$i18n.t("This chat won't appear in history and your messages will not be saved.")}
      className="w-full flex justify-center mb-0.5"
      placement="top"
    >
      <div class="flex items-center gap-2 text-gray-500 text-base my-2 w-fit">
        <EyeSlash strokeWidth="2.5" className="size-4" />{$i18n.t('Temporary Chat')}
      </div>
    </Tooltip>
  {/if}

  <div
    class="w-full text-3xl text-gray-800 dark:text-gray-100 text-center flex items-center gap-4 font-primary"
  >
    <div class="w-full flex flex-col justify-center items-center">
      {#if $selectedFolder}
        <FolderTitle
          folder={$selectedFolder}
          onUpdate={async (folder) => {
            await chats.set(await getChatList(localStorage.token, $currentChatPage));
            currentChatPage.set(1);
          }}
          onDelete={async () => {
            await chats.set(await getChatList(localStorage.token, $currentChatPage));
            currentChatPage.set(1);

            selectedFolder.set(null);
          }}
        />
      {:else}
        <div
          class="text-3xl @sm:text-3xl line-clamp-1 flex items-center justify-center"
          in:fade={{ duration: 100 }}
        >
          {$i18n.t('Hi, {{name}}', { name: $user?.name })}
        </div>
      {/if}

      <div class="text-base font-normal @md:max-w-3xl w-full py-3">
        <MessageInput
          bind:this={messageInput}
          {history}
          selectedModels={[activeModelId]}
          bind:files
          bind:prompt
          bind:autoScroll
          bind:imageGenerationEnabled
          bind:webSearchEnabled
          {stopResponse}
          {createMessagePair}
          placeholder={$i18n.t('How can I help you today?')}
          {onChange}
          {onUpload}
          on:submit={(e) => {
            dispatch('submit', e.detail);
          }}
        />
      </div>
    </div>
  </div>

  {#if $selectedFolder}
    <div
      class="mx-auto px-4 md:max-w-3xl md:px-6 font-primary min-h-62"
      in:fade={{ duration: 200, delay: 200 }}
    >
      <FolderPlaceholder folder={$selectedFolder} />
    </div>
  {:else}
    <div class="mx-auto max-w-2xl font-primary mt-2" in:fade={{ duration: 200, delay: 200 }}>
      <div class="mx-5">
        <Suggestions
          suggestionPrompts={model?.info?.meta?.suggestion_prompts ??
            $config?.default_prompt_suggestions ??
            []}
          inputValue={prompt}
          {onSelect}
        />
      </div>
    </div>
  {/if}
</div>
