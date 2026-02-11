<script lang="ts">
  import { toast } from 'svelte-sonner';
  import { config, models, settings } from '$lib/stores';
  import { getContext, onMount, tick } from 'svelte';
  import type { Writable } from 'svelte/store';
  import type { i18n as i18nType } from 'i18next';
  import {
    getPipelineValves,
    getPipelineValvesSpec,
    updatePipelineValves,
    getPipelines,
    getModels,
    getPipelinesList
  } from '$lib/apis';

  import Spinner from '$lib/components/common/Spinner.svelte';
  import Switch from '$lib/components/common/Switch.svelte';

  const i18n: Writable<i18nType> = getContext('i18n');

  export let saveHandler: Function;

  let PIPELINES_LIST = null;
  let selectedPipelinesUrlIdx = '';

  let pipelines = null;

  let valves = null;
  let valves_spec = null;
  let selectedPipelineIdx = null;

  const updateHandler = async () => {
    const pipeline = pipelines[selectedPipelineIdx];

    if (pipeline && (pipeline?.valves ?? false)) {
      for (const property in valves_spec.properties) {
        if (valves_spec.properties[property]?.type === 'array') {
          valves[property] = (valves[property] ?? '').split(',').map((v) => v.trim());
        }
      }

      const res = await updatePipelineValves(
        localStorage.token,
        pipeline.id,
        valves,
        selectedPipelinesUrlIdx
      ).catch((error) => {
        toast.error(`${error}`);
      });

      if (res) {
        toast.success($i18n.t('Valves updated successfully'));
        setPipelines();
        models.set(
          await getModels(
            localStorage.token,
            $config?.features?.enable_direct_connections && ($settings?.directConnections ?? null)
          )
        );
        saveHandler();
      }
    } else {
      toast.error($i18n.t('No valves to update'));
    }
  };

  const getValves = async (idx) => {
    valves = null;
    valves_spec = null;

    valves_spec = await getPipelineValvesSpec(
      localStorage.token,
      pipelines[idx].id,
      selectedPipelinesUrlIdx
    );
    valves = await getPipelineValves(
      localStorage.token,
      pipelines[idx].id,
      selectedPipelinesUrlIdx
    );

    for (const property in valves_spec.properties) {
      if (valves_spec.properties[property]?.type === 'array') {
        valves[property] = valves[property].join(',');
      }
    }
  };

  const setPipelines = async () => {
    pipelines = null;
    valves = null;
    valves_spec = null;

    if (PIPELINES_LIST.length > 0) {
      console.debug(selectedPipelinesUrlIdx);
      pipelines = await getPipelines(localStorage.token, selectedPipelinesUrlIdx);

      if (pipelines.length > 0) {
        selectedPipelineIdx = 0;
        await getValves(selectedPipelineIdx);
      }
    } else {
      pipelines = [];
    }
  };

  onMount(async () => {
    PIPELINES_LIST = await getPipelinesList(localStorage.token);
    console.log(PIPELINES_LIST);

    if (PIPELINES_LIST.length > 0) {
      selectedPipelinesUrlIdx = PIPELINES_LIST[0]['idx'].toString();
    }

    await setPipelines();
  });
</script>

<form
  class="flex flex-col h-full justify-between space-y-3 text-sm"
  on:submit|preventDefault={async () => {
    updateHandler();
  }}
>
  <div class="overflow-y-scroll scrollbar-hidden h-full">
    {#if PIPELINES_LIST !== null}
      {#if PIPELINES_LIST.length > 0}
        <!-- Pipeline Servers -->
        <div class="mb-1 text-sm font-medium">{$i18n.t('Pipeline Servers')}</div>
        <div class="flex flex-col gap-1">
          {#each PIPELINES_LIST as server}
            <button
              class="flex items-center gap-2 w-full text-left px-3 py-2 rounded-lg transition text-sm {selectedPipelinesUrlIdx === server.idx.toString()
                ? 'bg-gray-100 dark:bg-gray-850 font-medium'
                : 'hover:bg-gray-50 dark:hover:bg-gray-900 text-gray-600 dark:text-gray-400'}"
              type="button"
              on:click={async () => {
                selectedPipelinesUrlIdx = server.idx.toString();
                await tick();
                await setPipelines();
              }}
            >
              <span class="truncate">{server.url}</span>
            </button>
          {/each}
        </div>

        <hr class="border-gray-100 dark:border-gray-850 my-3" />

        <!-- Pipelines list -->
        {#if pipelines !== null}
          {#if pipelines.length > 0}
            <div class="mb-1 text-sm font-medium">
              {$i18n.t('Pipelines')}
              <span class="font-normal text-xs text-gray-500 dark:text-gray-400">
                &mdash; {PIPELINES_LIST.find((s) => s.idx.toString() === selectedPipelinesUrlIdx)?.url ?? ''}
              </span>
            </div>
            <div class="flex flex-col gap-1">
              {#each pipelines as pipeline, idx}
                <button
                  class="flex items-center gap-2 w-full text-left px-3 py-2 rounded-lg transition text-sm {selectedPipelineIdx === idx
                    ? 'bg-gray-100 dark:bg-gray-850 font-medium'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-900 text-gray-600 dark:text-gray-400'}"
                  type="button"
                  on:click={async () => {
                    selectedPipelineIdx = idx;
                    await tick();
                    await getValves(idx);
                  }}
                >
                  <span
                    class="shrink-0 text-[10px] font-mono px-1.5 py-0.5 rounded bg-gray-200 dark:bg-gray-800 text-gray-600 dark:text-gray-400"
                  >
                    {pipeline.type ?? 'pipe'}
                  </span>
                  <span class="truncate">{pipeline.name}</span>
                </button>
              {/each}
            </div>

            <!-- Valves -->
            {#if selectedPipelineIdx !== null && pipelines[selectedPipelineIdx]}
              <hr class="border-gray-100 dark:border-gray-850 my-3" />

              <div class="mb-2 text-sm font-medium">
                {$i18n.t('Valves')}
                <span class="font-normal text-xs text-gray-500 dark:text-gray-400">
                  &mdash; {pipelines[selectedPipelineIdx].id}
                </span>
              </div>

              {#if pipelines[selectedPipelineIdx].valves}
                {#if valves}
                  <div class="space-y-2">
                    {#each Object.keys(valves_spec.properties) as property}
                      <div class="py-0.5 w-full">
                        <div class="flex w-full justify-between">
                          <div class="self-center text-xs font-medium">
                            {valves_spec.properties[property].title}
                          </div>

                          <button
                            class="p-1 px-3 text-xs flex rounded-sm transition"
                            type="button"
                            on:click={() => {
                              valves[property] = (valves[property] ?? null) === null ? '' : null;
                            }}
                          >
                            {#if (valves[property] ?? null) === null}
                              <span class="ml-2 self-center">{$i18n.t('None')}</span>
                            {:else}
                              <span class="ml-2 self-center">{$i18n.t('Custom')}</span>
                            {/if}
                          </button>
                        </div>

                        {#if (valves[property] ?? null) !== null}
                          <div class="flex mt-0.5 mb-1.5">
                            <div class="flex-1">
                              {#if valves_spec.properties[property]?.enum ?? null}
                                <select
                                  class="w-full rounded-lg py-2 px-4 text-sm bg-gray-50 dark:text-gray-300 dark:bg-gray-850 outline-hidden"
                                  bind:value={valves[property]}
                                >
                                  {#each valves_spec.properties[property].enum as option}
                                    <option value={option} selected={option === valves[property]}>
                                      {option}
                                    </option>
                                  {/each}
                                </select>
                              {:else if (valves_spec.properties[property]?.type ?? null) === 'boolean'}
                                <div class="flex justify-between items-center">
                                  <div class="text-xs text-gray-500">
                                    {valves[property] ? $i18n.t('Enabled') : $i18n.t('Disabled')}
                                  </div>
                                  <div class="pr-2">
                                    <Switch bind:state={valves[property]} />
                                  </div>
                                </div>
                              {:else}
                                <input
                                  class="w-full rounded-lg py-2 px-4 text-sm bg-gray-50 dark:text-gray-300 dark:bg-gray-850 outline-hidden"
                                  type="text"
                                  placeholder={valves_spec.properties[property].title}
                                  bind:value={valves[property]}
                                  autocomplete="off"
                                  required
                                />
                              {/if}
                            </div>
                          </div>
                        {/if}
                      </div>
                    {/each}
                  </div>
                {:else}
                  <Spinner className="size-5" />
                {/if}
              {:else}
                <div class="text-xs text-gray-500">{$i18n.t('No valves')}</div>
              {/if}
            {/if}
          {:else}
            <div class="text-gray-500">{$i18n.t('Pipelines Not Detected')}</div>
          {/if}
        {:else}
          <div class="flex justify-center">
            <div class="my-auto">
              <Spinner className="size-4" />
            </div>
          </div>
        {/if}
      {:else}
        <div class="text-gray-500">{$i18n.t('Pipelines Not Detected')}</div>
      {/if}
    {:else}
      <div class="flex justify-center h-full">
        <div class="my-auto">
          <Spinner className="size-6" />
        </div>
      </div>
    {/if}
  </div>

  {#if pipelines !== null && pipelines.length > 0 && selectedPipelineIdx !== null && pipelines[selectedPipelineIdx]?.valves}
    <div class="flex justify-end pt-3 text-sm font-medium">
      <button
        class="px-3.5 py-1.5 text-sm font-medium bg-black hover:bg-gray-900 text-white dark:bg-white dark:text-black dark:hover:bg-gray-100 transition rounded-full"
        type="submit"
      >
        {$i18n.t('Save')}
      </button>
    </div>
  {/if}
</form>
