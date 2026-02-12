<script lang="ts">
  import { toast } from 'svelte-sonner';

  import fileSaver from 'file-saver';
  const { saveAs } = fileSaver;

  import { onMount, getContext, tick } from 'svelte';
  import { goto } from '$app/navigation';
  const i18n = getContext('i18n');

  import { WEBUI_NAME, config, models as _models, settings, user } from '$lib/stores';
  import {
    createNewModel,
    deleteModelById,
    getModelItems as getWorkspaceModels,
    getModelTags,
    updateModelById
  } from '$lib/apis/models';

  import { getModels } from '$lib/apis';
  import { updateUserSettings } from '$lib/apis/users';

  import { copyToClipboard } from '$lib/utils';

  import ModelCard from './Models/ModelCard.svelte';
  import ModelDeleteConfirmDialog from '../common/ConfirmDialog.svelte';
  import Search from '../icons/Search.svelte';
  import Plus from '../icons/Plus.svelte';
  import ChevronRight from '../icons/ChevronRight.svelte';
  import Spinner from '../common/Spinner.svelte';
  import XMark from '../icons/XMark.svelte';
  import ViewSelector from './common/ViewSelector.svelte';
  import TagSelector from './common/TagSelector.svelte';
  import Pagination from '../common/Pagination.svelte';

  let shiftKey = false;

  let importFiles;
  let modelsImportInputElement: HTMLInputElement;
  let tagsContainerElement: HTMLDivElement;

  let loaded = false;

  let showModelDeleteConfirm = false;

  let selectedModel = null;

  let tags = [];
  let selectedTag = '';

  let query = '';
  let viewOption = '';

  let page = 1;
  let models = null;
  let total = null;

  let baseModels = [];
  let baseTotal = 0;
  let starModels = [];
  let starTotal = 0;

  const hasTag = (m, tagName) => (m.meta?.tags ?? []).some((t) => t.name === tagName);

  let searchDebounceTimer;

  $: if (
    page !== undefined &&
    query !== undefined &&
    selectedTag !== undefined &&
    viewOption !== undefined
  ) {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
      getModelList();
    }, 300);
  }

  const getFixedLists = async () => {
    try {
      const [baseRes, starRes] = await Promise.all([
        getWorkspaceModels(localStorage.token, '', '', 'base', null, null, 1),
        getWorkspaceModels(localStorage.token, '', '', 'star', null, null, 1)
      ]);
      baseModels = baseRes?.items ?? [];
      baseTotal = baseRes?.total ?? 0;
      const rawStar = starRes?.items ?? [];
      starModels = rawStar.filter((m) => !hasTag(m, 'base'));
      starTotal = starModels.length;
    } catch (err) {
      console.error(err);
    }
  };

  const getModelList = async () => {
    try {
      const res = await getWorkspaceModels(
        localStorage.token,
        query,
        viewOption,
        selectedTag,
        null,
        null,
        page
      ).catch((error) => {
        toast.error(`${error}`);
        return null;
      });

      if (res) {
        models = res.items.filter((m) => !hasTag(m, 'base') && !hasTag(m, 'star'));
        if (!selectedTag) {
          total = res.total - baseTotal - starTotal;
        } else {
          total = res.total;
        }

        // get tags
        tags = await getModelTags(localStorage.token).catch((error) => {
          toast.error(`${error}`);
          return [];
        });
        tags = tags.filter((tag) => tag !== 'base' && tag !== 'star');
      }
    } catch (err) {
      console.error(err);
    }
  };

  const deleteModelHandler = async (model) => {
    const res = await deleteModelById(localStorage.token, model.id).catch((e) => {
      toast.error(`${e}`);
      return null;
    });

    if (res) {
      toast.success($i18n.t(`Deleted {{name}}`, { name: model.id }));

      page = 1;
      getFixedLists();
      getModelList();
    }

    await _models.set(
      await getModels(
        localStorage.token,
        $config?.features?.enable_direct_connections && ($settings?.directConnections ?? null)
      )
    );
  };

  const cloneModelHandler = async (model) => {
    sessionStorage.model = JSON.stringify({
      ...model,
      id: `${model.id}-clone`,
      name: `${model.name} (Clone)`
    });
    goto('/workspace/models/create');
  };

  const shareModelHandler = async (model) => {
    toast.success($i18n.t('Redirecting you to Open WebUI Community'));

    const url = 'https://openwebui.com';

    const tab = await window.open(`${url}/models/create`, '_blank');

    const messageHandler = (event) => {
      if (event.origin !== url) return;
      if (event.data === 'loaded') {
        tab.postMessage(JSON.stringify(model), '*');
        window.removeEventListener('message', messageHandler);
      }
    };

    window.addEventListener('message', messageHandler, false);
  };

  const hideModelHandler = async (model) => {
    model.meta = {
      ...model.meta,
      hidden: !(model?.meta?.hidden ?? false)
    };

    console.log(model);

    const res = await updateModelById(localStorage.token, model.id, model);

    if (res) {
      toast.success(
        $i18n.t(`Model {{name}} is now {{status}}`, {
          name: model.id,
          status: model.meta.hidden ? 'hidden' : 'visible'
        })
      );

      page = 1;
      getFixedLists();
      getModelList();
    }

    await _models.set(
      await getModels(
        localStorage.token,
        $config?.features?.enable_direct_connections && ($settings?.directConnections ?? null)
      )
    );
  };

  const copyLinkHandler = async (model) => {
    const baseUrl = window.location.origin;
    const res = await copyToClipboard(`${baseUrl}/c?model=${encodeURIComponent(model.id)}`);

    if (res) {
      toast.success($i18n.t('Copied link to clipboard'));
    } else {
      toast.error($i18n.t('Failed to copy link'));
    }
  };

  const downloadModels = async (models) => {
    let blob = new Blob([JSON.stringify(models)], {
      type: 'application/json'
    });
    saveAs(blob, `models-export-${Date.now()}.json`);
  };

  const exportModelHandler = async (model) => {
    let blob = new Blob([JSON.stringify([model])], {
      type: 'application/json'
    });
    saveAs(blob, `${model.id}-${Date.now()}.json`);
  };

  const pinModelHandler = async (modelId) => {
    let pinnedModels = $settings?.pinnedModels ?? [];

    if (pinnedModels.includes(modelId)) {
      pinnedModels = pinnedModels.filter((id) => id !== modelId);
    } else {
      pinnedModels = [...new Set([...pinnedModels, modelId])];
    }

    settings.set({ ...$settings, pinnedModels: pinnedModels });
    await updateUserSettings(localStorage.token, { ui: $settings });
  };

  onMount(async () => {
    viewOption = localStorage.workspaceViewOption ?? '';
    page = 1;

    getFixedLists();

    loaded = true;

    const onKeyDown = (event) => {
      if (event.key === 'Shift') {
        shiftKey = true;
      }
    };

    const onKeyUp = (event) => {
      if (event.key === 'Shift') {
        shiftKey = false;
      }
    };

    const onBlur = () => {
      shiftKey = false;
    };

    window.addEventListener('keydown', onKeyDown);
    window.addEventListener('keyup', onKeyUp);
    window.addEventListener('blur-sm', onBlur);

    return () => {
      window.removeEventListener('keydown', onKeyDown);
      window.removeEventListener('keyup', onKeyUp);
      window.removeEventListener('blur-sm', onBlur);
    };
  });
</script>

<svelte:head>
  <title>
    {$i18n.t('Models')} • {$WEBUI_NAME}
  </title>
</svelte:head>

{#if loaded}
  <ModelDeleteConfirmDialog
    bind:show={showModelDeleteConfirm}
    on:confirm={() => {
      deleteModelHandler(selectedModel);
    }}
  />

  <div class="flex flex-col gap-1 px-1 mt-1.5 mb-3">
    <input
      id="models-import-input"
      bind:this={modelsImportInputElement}
      bind:files={importFiles}
      type="file"
      accept=".json"
      hidden
      on:change={() => {
        console.log(importFiles);

        let reader = new FileReader();
        reader.onload = async (event) => {
          let savedModels = [];
          try {
            savedModels = JSON.parse(event.target.result);
            console.log(savedModels);
          } catch (e) {
            toast.error($i18n.t('Invalid JSON file'));
            return;
          }

          for (const model of savedModels) {
            if (model?.info ?? false) {
              if ($_models.find((m) => m.id === model.id)) {
                await updateModelById(localStorage.token, model.id, model.info).catch((error) => {
                  toast.error(`${error}`);
                  return null;
                });
              } else {
                await createNewModel(localStorage.token, model.info).catch((error) => {
                  toast.error(`${error}`);
                  return null;
                });
              }
            } else {
              if (model?.id && model?.name) {
                await createNewModel(localStorage.token, model).catch((error) => {
                  toast.error(`${error}`);
                  return null;
                });
              }
            }
          }

          await _models.set(
            await getModels(
              localStorage.token,
              $config?.features?.enable_direct_connections && ($settings?.directConnections ?? null)
            )
          );

          page = 1;
          getFixedLists();
          getModelList();
        };

        reader.readAsText(importFiles[0]);
      }}
    />
    <div class="flex justify-between items-center">
      <div class="flex items-center md:self-center text-xl font-medium px-0.5 gap-2 shrink-0">
        <div>
          {$i18n.t('Models')}
        </div>

        <div class="text-lg font-medium text-gray-500 dark:text-gray-500">
          {total}
        </div>
      </div>

      <div class="flex w-full justify-end gap-1.5">
        {#if $user?.role === 'admin' || $user?.permissions?.workspace?.models_import}
          <button
            class="flex text-xs items-center space-x-1 px-3 py-1.5 rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 dark:text-gray-200 transition"
            on:click={() => {
              modelsImportInputElement.click();
            }}
          >
            <div class=" self-center font-medium line-clamp-1">
              {$i18n.t('Import')}
            </div>
          </button>
        {/if}

        {#if total && ($user?.role === 'admin' || $user?.permissions?.workspace?.models_export)}
          <button
            class="flex text-xs items-center space-x-1 px-3 py-1.5 rounded-xl bg-gray-50 hover:bg-gray-100 dark:bg-gray-850 dark:hover:bg-gray-800 dark:text-gray-200 transition"
            on:click={async () => {
              downloadModels(models);
            }}
          >
            <div class=" self-center font-medium line-clamp-1">
              {$i18n.t('Export')}
            </div>
          </button>
        {/if}
        <a
          class=" px-2 py-1.5 rounded-xl bg-black text-white dark:bg-white dark:text-black transition font-medium text-sm flex items-center"
          href="/workspace/models/create"
        >
          <Plus className="size-3" strokeWidth="2.5" />

          <div class=" hidden md:block md:ml-1 text-xs">{$i18n.t('New Model')}</div>
        </a>
      </div>
    </div>
  </div>

  {#if baseModels.length > 0}
    <div
      class="py-2 bg-white dark:bg-gray-900 rounded-3xl border border-gray-100/30 dark:border-gray-850/30 mb-3"
    >
      <div class="px-4 py-2">
        <div class="text-sm font-medium text-gray-500 dark:text-gray-400">
          {$i18n.t('Base Models')}
        </div>
      </div>
      <div class="px-3 my-1 gap-1 lg:gap-2 grid md:grid-cols-2 lg:grid-cols-3">
        {#each baseModels as model (model.id)}
          <ModelCard
            {model}
            {shiftKey}
            onHide={hideModelHandler}
            onDelete={deleteModelHandler}
            onDeleteConfirm={(m) => {
              selectedModel = m;
              showModelDeleteConfirm = true;
            }}
            onShare={shareModelHandler}
            onClone={cloneModelHandler}
            onExport={exportModelHandler}
            onPin={(id) => pinModelHandler(id)}
            onCopyLink={copyLinkHandler}
          />
        {/each}
      </div>
    </div>
  {/if}

  {#if starModels.length > 0}
    <div
      class="py-2 bg-white dark:bg-gray-900 rounded-3xl border border-gray-100/30 dark:border-gray-850/30 mb-3"
    >
      <div class="px-4 py-2">
        <div class="text-sm font-medium text-gray-500 dark:text-gray-400">
          {$i18n.t('Starred Assistants')}
        </div>
      </div>
      <div class="px-3 my-1 gap-1 lg:gap-2 grid md:grid-cols-2 lg:grid-cols-3">
        {#each starModels as model (model.id)}
          <ModelCard
            {model}
            {shiftKey}
            onHide={hideModelHandler}
            onDelete={deleteModelHandler}
            onDeleteConfirm={(m) => {
              selectedModel = m;
              showModelDeleteConfirm = true;
            }}
            onShare={shareModelHandler}
            onClone={cloneModelHandler}
            onExport={exportModelHandler}
            onPin={(id) => pinModelHandler(id)}
            onCopyLink={copyLinkHandler}
          />
        {/each}
      </div>
    </div>
  {/if}

  <div
    class="py-2 bg-white dark:bg-gray-900 rounded-3xl border border-gray-100/30 dark:border-gray-850/30"
  >
    <div class="px-3.5 flex flex-1 items-center w-full space-x-2 py-0.5 pb-2">
      <div class="flex flex-1 items-center">
        <div class=" self-center ml-1 mr-3">
          <Search className="size-3.5" />
        </div>
        <input
          class=" w-full text-sm py-1 rounded-r-xl outline-hidden bg-transparent"
          bind:value={query}
          placeholder={$i18n.t('Search Models')}
          maxlength="500"
        />

        {#if query}
          <div class="self-center pl-1.5 translate-y-[0.5px] rounded-l-xl bg-transparent">
            <button
              class="p-0.5 rounded-full hover:bg-gray-100 dark:hover:bg-gray-900 transition"
              on:click={() => {
                query = '';
              }}
            >
              <XMark className="size-3" strokeWidth="2" />
            </button>
          </div>
        {/if}
      </div>
    </div>

    <div
      class="px-3 flex w-full bg-transparent overflow-x-auto scrollbar-none"
      on:wheel={(e) => {
        if (e.deltaY !== 0) {
          e.preventDefault();
          e.currentTarget.scrollLeft += e.deltaY;
        }
      }}
    >
      <div
        class="flex gap-0.5 w-fit text-center text-sm rounded-full bg-transparent px-0.5 whitespace-nowrap"
        bind:this={tagsContainerElement}
      >
        <ViewSelector
          bind:value={viewOption}
          onChange={async (value) => {
            localStorage.workspaceViewOption = value;
            await tick();
          }}
        />

        {#if (tags ?? []).length > 0}
          <TagSelector
            bind:value={selectedTag}
            items={tags.map((tag) => {
              return { value: tag, label: tag };
            })}
          />
        {/if}
      </div>
    </div>

    {#if models !== null}
      {#if (models ?? []).length !== 0}
        <div class="px-3 my-2 gap-1 lg:gap-2 grid md:grid-cols-2 lg:grid-cols-3" id="model-list">
          {#each models as model (model.id)}
            <ModelCard
              {model}
              {shiftKey}
              onHide={hideModelHandler}
              onDelete={deleteModelHandler}
              onDeleteConfirm={(m) => {
                selectedModel = m;
                showModelDeleteConfirm = true;
              }}
              onShare={shareModelHandler}
              onClone={cloneModelHandler}
              onExport={exportModelHandler}
              onPin={(id) => pinModelHandler(id)}
              onCopyLink={copyLinkHandler}
            />
          {/each}
        </div>

        {#if total > 30}
          <Pagination bind:page count={total} perPage={30} />
        {/if}
      {:else}
        <div class=" w-full h-full flex flex-col justify-center items-center my-16 mb-24">
          <div class="max-w-md text-center">
            <div class=" text-3xl mb-3">😕</div>
            <div class=" text-lg font-medium mb-1">{$i18n.t('No models found')}</div>
            <div class=" text-gray-500 text-center text-xs">
              {$i18n.t('Try adjusting your search or filter to find what you are looking for.')}
            </div>
          </div>
        </div>
      {/if}
    {:else}
      <div class="w-full h-full flex justify-center items-center py-10">
        <Spinner className="size-4" />
      </div>
    {/if}
  </div>

  {#if $config?.features.enable_community_sharing}
    <div class=" my-16">
      <div class=" text-xl font-medium mb-1 line-clamp-1">
        {$i18n.t('Made by Open WebUI Community')}
      </div>

      <a
        class=" flex cursor-pointer items-center justify-between hover:bg-gray-50 dark:hover:bg-gray-850 w-full mb-2 px-3.5 py-1.5 rounded-xl transition"
        href="https://openwebui.com/models"
        target="_blank"
      >
        <div class=" self-center">
          <div class=" font-medium line-clamp-1">{$i18n.t('Discover a model')}</div>
          <div class=" text-sm line-clamp-1">
            {$i18n.t('Discover, download, and explore model presets')}
          </div>
        </div>

        <div>
          <div>
            <ChevronRight />
          </div>
        </div>
      </a>
    </div>
  {/if}
{:else}
  <div class="w-full h-full flex justify-center items-center">
    <Spinner className="size-5" />
  </div>
{/if}
