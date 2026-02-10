<script lang="ts">
  import { marked } from 'marked';
  import { getContext } from 'svelte';
  import { goto } from '$app/navigation';

  import { WEBUI_API_BASE_URL } from '$lib/constants';
  import { config, models as _models, settings, user } from '$lib/stores';
  import { getModels } from '$lib/apis';
  import { toggleModelById } from '$lib/apis/models';
  import { updateUserSettings } from '$lib/apis/users';
  import { capitalizeFirstLetter } from '$lib/utils';

  import EllipsisHorizontal from '../../icons/EllipsisHorizontal.svelte';
  import ModelMenu from './ModelMenu.svelte';
  import Tooltip from '../../common/Tooltip.svelte';
  import GarbageBin from '../../icons/GarbageBin.svelte';
  import Switch from '../../common/Switch.svelte';
  import EyeSlash from '../../icons/EyeSlash.svelte';
  import Eye from '../../icons/Eye.svelte';
  import Badge from '$lib/components/common/Badge.svelte';

  const i18n = getContext('i18n');

  export let model;
  export let shiftKey = false;

  export let onHide: (model: any) => void = () => {};
  export let onDelete: (model: any) => void = () => {};
  export let onDeleteConfirm: (model: any) => void = () => {};
  export let onShare: (model: any) => void = () => {};
  export let onClone: (model: any) => void = () => {};
  export let onExport: (model: any) => void = () => {};
  export let onPin: (modelId: string) => void = () => {};
  export let onCopyLink: (model: any) => void = () => {};
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<!-- svelte-ignore a11y_click_events_have_key_events -->
<div
  class="flex transition rounded-2xl w-full p-2.5 cursor-pointer dark:hover:bg-gray-850/50 hover:bg-gray-50"
  id="model-item-{model.id}"
  on:click={async () => {
    $settings.activeModel = model.id;
    await updateUserSettings(localStorage.token, { ui: $settings });
    goto(`/c?models=${encodeURIComponent(model.id)}`);
  }}
>
  <div class="flex group/item gap-3.5 w-full">
    <div class="self-center pl-0.5">
      <div class="flex bg-white rounded-2xl">
        <div
          class="{model.is_active ? '' : 'opacity-50 dark:opacity-50'} bg-transparent rounded-2xl"
        >
          <img
            src={`${WEBUI_API_BASE_URL}/models/model/profile/image?id=${model.id}&lang=${$i18n.language}`}
            alt="modelfile profile"
            class=" rounded-2xl size-12 object-cover"
          />
        </div>
      </div>
    </div>

    <div class=" shrink-0 flex w-full min-w-0 flex-1 pr-1 self-center">
      <div class="flex h-full w-full flex-1 flex-col justify-start self-center group">
        <div class="flex-1 w-full">
          <div class="flex items-center justify-between w-full">
            <Tooltip content={model.name} className=" w-fit" placement="top-start">
              <div class=" font-medium line-clamp-1 capitalize">
                {model.name}
              </div>
            </Tooltip>

            <div class="flex items-center gap-1">
              {#if !model.write_access}
                <div>
                  <Badge type="muted" content={$i18n.t('Read Only')} />
                </div>
              {/if}

              {#if model.write_access || $user?.role === 'admin'}
                <div class="flex {model.is_active ? '' : 'text-gray-500'}">
                  <div class="flex items-center gap-0.5">
                    {#if shiftKey}
                      <Tooltip content={model?.meta?.hidden ? $i18n.t('Show') : $i18n.t('Hide')}>
                        <button
                          class="self-center w-fit text-sm p-1.5 dark:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
                          type="button"
                          on:click={(e) => {
                            e.stopPropagation();
                            onHide(model);
                          }}
                        >
                          {#if model?.meta?.hidden}
                            <EyeSlash />
                          {:else}
                            <Eye />
                          {/if}
                        </button>
                      </Tooltip>

                      <Tooltip content={$i18n.t('Delete')}>
                        <button
                          class="self-center w-fit text-sm p-1.5 dark:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
                          type="button"
                          on:click={(e) => {
                            e.stopPropagation();
                            onDelete(model);
                          }}
                        >
                          <GarbageBin />
                        </button>
                      </Tooltip>
                    {:else}
                      <ModelMenu
                        {model}
                        editHandler={() => {
                          goto(`/workspace/models/edit?id=${encodeURIComponent(model.id)}`);
                        }}
                        shareHandler={() => {
                          onShare(model);
                        }}
                        cloneHandler={() => {
                          onClone(model);
                        }}
                        exportHandler={() => {
                          onExport(model);
                        }}
                        hideHandler={() => {
                          onHide(model);
                        }}
                        pinModelHandler={() => {
                          onPin(model.id);
                        }}
                        copyLinkHandler={() => {
                          onCopyLink(model);
                        }}
                        deleteHandler={() => {
                          onDeleteConfirm(model);
                        }}
                        onClose={() => {}}
                      >
                        <div
                          class="self-center w-fit p-1 text-sm dark:text-white hover:bg-black/5 dark:hover:bg-white/5 rounded-xl"
                        >
                          <EllipsisHorizontal className="size-5" />
                        </div>
                      </ModelMenu>
                    {/if}
                  </div>
                </div>
              {/if}

              {#if model.write_access}
                <button
                  on:click={(e) => {
                    e.stopPropagation();
                  }}
                >
                  <Tooltip content={model.is_active ? $i18n.t('Enabled') : $i18n.t('Disabled')}>
                    <Switch
                      bind:state={model.is_active}
                      on:change={async () => {
                        toggleModelById(localStorage.token, model.id);
                        _models.set(
                          await getModels(
                            localStorage.token,
                            $config?.features?.enable_direct_connections &&
                              ($settings?.directConnections ?? null)
                          )
                        );
                      }}
                    />
                  </Tooltip>
                </button>
              {/if}
            </div>
          </div>

          <div class=" flex gap-1 pr-2 -mt-1 items-center">
            <Tooltip
              content={model?.user?.email ?? $i18n.t('Deleted User')}
              className="flex shrink-0"
              placement="top-start"
            >
              <div class="shrink-0 text-gray-500 text-xs">
                {$i18n.t('By {{name}}', {
                  name: capitalizeFirstLetter(
                    model?.user?.name ?? model?.user?.email ?? $i18n.t('Deleted User')
                  )
                })}
              </div>
            </Tooltip>

            {#if (model?.meta?.description ?? '').trim()}
              <div>·</div>

              <Tooltip
                content={marked.parse(model?.meta?.description)}
                className=" w-fit text-left"
                placement="top-start"
              >
                <div class="flex gap-1 text-xs overflow-hidden">
                  <div class="line-clamp-1">
                    {model?.meta?.description}
                  </div>
                </div>
              </Tooltip>
            {/if}
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
