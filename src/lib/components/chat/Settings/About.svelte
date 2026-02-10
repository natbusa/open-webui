<script lang="ts">
  import { getOllamaVersion } from '$lib/apis/ollama';
  import { WEBUI_BUILD_HASH, WEBUI_VERSION } from '$lib/constants';
  import { WEBUI_NAME, config, showChangelog } from '$lib/stores';
  import { onMount, getContext } from 'svelte';

  import Tooltip from '$lib/components/common/Tooltip.svelte';

  const i18n = getContext('i18n');

  let ollamaVersion = '';

  onMount(async () => {
    ollamaVersion = await getOllamaVersion(localStorage.token).catch((error) => {
      return '';
    });
  });
</script>

<div id="tab-about" class="flex flex-col h-full justify-between space-y-3 text-sm mb-6">
  <div class=" space-y-3 overflow-y-scroll max-h-[28rem] md:max-h-full">
    <div>
      <div class=" mb-2.5 text-sm font-medium flex space-x-2 items-center">
        <div>
          {$WEBUI_NAME}
          {$i18n.t('Version')}
        </div>
      </div>
      <div class="flex w-full justify-between items-center">
        <div class="flex flex-col text-xs text-gray-700 dark:text-gray-200">
          <div class="flex gap-1">
            <Tooltip content={WEBUI_BUILD_HASH}>
              v{WEBUI_VERSION}
            </Tooltip>
          </div>

          <button
            class=" underline flex items-center space-x-1 text-xs text-gray-500 dark:text-gray-500"
            on:click={() => {
              showChangelog.set(true);
            }}
          >
            <div>{$i18n.t("See what's new")}</div>
          </button>
        </div>
      </div>
    </div>

    {#if ollamaVersion}
      <hr class=" border-gray-100/30 dark:border-gray-850/30" />

      <div>
        <div class=" mb-2.5 text-sm font-medium">{$i18n.t('Ollama Version')}</div>
        <div class="flex w-full">
          <div class="flex-1 text-xs text-gray-700 dark:text-gray-200">
            {ollamaVersion ?? 'N/A'}
          </div>
        </div>
      </div>
    {/if}

    <hr class=" border-gray-100/30 dark:border-gray-850/30" />

    <div class="text-xs text-gray-400 dark:text-gray-500 space-y-2">
      <div>
        <span class="text-gray-500 dark:text-gray-300 font-medium">Open WebUI Lite</span>
        — a streamlined fork of
        <a
          class="text-gray-500 dark:text-gray-300 font-medium"
          href="https://github.com/open-webui/open-webui"
          target="_blank">Open WebUI</a
        >.
      </div>

      <div>
        Modified by
        <a
          class="text-gray-500 dark:text-gray-300 font-medium"
          href="https://natbusa.github.io"
          target="_blank">Nate Busa</a
        >
        with assistance from
        <a
          class="text-gray-500 dark:text-gray-300 font-medium"
          href="https://www.anthropic.com"
          target="_blank">Claude, Anthropic</a
        >.
      </div>

      <div>
        Original project created by
        <a
          class="text-gray-500 dark:text-gray-300 font-medium"
          href="https://github.com/tjbck"
          target="_blank">Timothy J. Baek</a
        >.
      </div>
    </div>

    <div class="mt-3 text-xs text-gray-400 dark:text-gray-500">
      Emoji graphics provided by
      <a href="https://github.com/jdecked/twemoji" target="_blank">Twemoji</a>, licensed under
      <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank">CC-BY 4.0</a>.
    </div>

    <div class="mt-2">
      <pre
        class="text-xs text-gray-400 dark:text-gray-500">Copyright (c) {new Date().getFullYear()} <a
          href="https://openwebui.com"
          target="_blank"
          class="underline">Open WebUI Inc.</a
        > <a href="https://github.com/open-webui/open-webui/blob/main/LICENSE" target="_blank"
          >All rights reserved.</a
        >
</pre>
    </div>
  </div>
</div>
