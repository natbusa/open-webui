<script lang="ts">
	import { getContext, onMount } from 'svelte';
	const i18n = getContext('i18n');

	import Switch from '$lib/components/common/Switch.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';

	import { DEFAULT_PERMISSIONS } from '$lib/constants/permissions';

	export let permissions = {};
	export let defaultPermissions = {};
	export let groupMode = false;

	// Reactive statement to ensure all fields are present in `permissions`
	$: {
		permissions = fillMissingProperties(permissions, DEFAULT_PERMISSIONS);
	}

	function fillMissingProperties(obj: any, defaults: any) {
		return {
			...defaults,
			...obj,
			workspace: { ...defaults.workspace, ...obj.workspace },
			sharing: { ...defaults.sharing, ...obj.sharing },
			chat: { ...defaults.chat, ...obj.chat },
			features: { ...defaults.features, ...obj.features },
			settings: { ...defaults.settings, ...obj.settings }
		};
	}

	function getNestedValue(obj: any, path: string): boolean | undefined {
		return path.split('.').reduce((o, k) => o?.[k], obj);
	}

	function isOverridden(path: string): boolean {
		return getNestedValue(permissions, path) !== getNestedValue(defaultPermissions, path);
	}

	// In group mode, hide permissions already disabled in defaults (AND logic makes them always false)
	function show(path: string): boolean {
		return !groupMode || getNestedValue(defaultPermissions, path) !== false;
	}

	onMount(() => {
		permissions = fillMissingProperties(permissions, DEFAULT_PERMISSIONS);
	});
</script>

{#snippet permissionIndicator(path: string)}
	{#if isOverridden(path)}
		<div class="text-xs text-orange-500">{$i18n.t('Overridden')}</div>
	{/if}
{/snippet}

<div class="space-y-2">
	<div>
		<div class=" mb-2 text-sm font-medium">{$i18n.t('Workspace Permissions')}</div>

		{#if show('workspace.models_import')}
			<div class="flex flex-col w-full">
				<div class="flex w-full justify-between my-1">
					<div class=" self-center text-xs font-medium">
						{$i18n.t('Import Models')}
					</div>
					<div class="flex items-center gap-2">
						{@render permissionIndicator('workspace.models_import')}
						<Switch bind:state={permissions.workspace.models_import} />
					</div>
				</div>
			</div>
		{/if}

		{#if show('workspace.models_export')}
			<div class="flex flex-col w-full">
				<div class="flex w-full justify-between my-1">
					<div class=" self-center text-xs font-medium">
						{$i18n.t('Export Models')}
					</div>
					<div class="flex items-center gap-2">
						{@render permissionIndicator('workspace.models_export')}
						<Switch bind:state={permissions.workspace.models_export} />
					</div>
				</div>
			</div>
		{/if}
	</div>

	<hr class=" border-gray-100/30 dark:border-gray-850/30" />

	<div>
		<div class=" mb-2 text-sm font-medium">{$i18n.t('Chat Permissions')}</div>

		{#if show('chat.file_upload')}
			<div class="flex flex-col w-full">
				<div class="flex w-full justify-between my-1">
					<div class=" self-center text-xs font-medium">
						{$i18n.t('Allow File Upload')}
					</div>
					<div class="flex items-center gap-2">
						{@render permissionIndicator('chat.file_upload')}
						<Switch bind:state={permissions.chat.file_upload} />
					</div>
				</div>
			</div>
		{/if}

		{#if show('chat.controls')}
			<div class="flex flex-col w-full">
				<div class="flex w-full justify-between my-1">
					<div class=" self-center text-xs font-medium">
						{$i18n.t('Allow Chat Controls')}
					</div>
					<div class="flex items-center gap-2">
						{@render permissionIndicator('chat.controls')}
						<Switch bind:state={permissions.chat.controls} />
					</div>
				</div>
			</div>
		{/if}

		{#if permissions.chat.controls || (groupMode && show('chat.controls'))}
			{#if show('chat.params')}
				<div class="flex flex-col w-full">
					<div class="flex w-full justify-between my-1">
						<div class=" self-center text-xs font-medium">
							{$i18n.t('Allow Chat Params')}
						</div>
						<div class="flex items-center gap-2">
							{@render permissionIndicator('chat.params')}
							<Switch bind:state={permissions.chat.params} />
						</div>
					</div>
				</div>
			{/if}
		{/if}

		{#if show('chat.edit')}
			<div class="flex flex-col w-full">
				<div class="flex w-full justify-between my-1">
					<div class=" self-center text-xs font-medium">
						{$i18n.t('Allow Chat Edit')}
					</div>
					<div class="flex items-center gap-2">
						{@render permissionIndicator('chat.edit')}
						<Switch bind:state={permissions.chat.edit} />
					</div>
				</div>
			</div>
		{/if}

		{#if show('chat.delete')}
			<div class="flex flex-col w-full">
				<div class="flex w-full justify-between my-1">
					<div class=" self-center text-xs font-medium">
						{$i18n.t('Allow Chat Delete')}
					</div>
					<div class="flex items-center gap-2">
						{@render permissionIndicator('chat.delete')}
						<Switch bind:state={permissions.chat.delete} />
					</div>
				</div>
			</div>
		{/if}

		{#if show('chat.delete_message')}
			<div class="flex flex-col w-full">
				<div class="flex w-full justify-between my-1">
					<div class=" self-center text-xs font-medium">
						{$i18n.t('Allow Delete Messages')}
					</div>
					<div class="flex items-center gap-2">
						{@render permissionIndicator('chat.delete_message')}
						<Switch bind:state={permissions.chat.delete_message} />
					</div>
				</div>
			</div>
		{/if}

		{#if show('chat.regenerate_response')}
			<div class="flex flex-col w-full">
				<div class="flex w-full justify-between my-1">
					<div class=" self-center text-xs font-medium">
						{$i18n.t('Allow Regenerate Response')}
					</div>
					<div class="flex items-center gap-2">
						{@render permissionIndicator('chat.regenerate_response')}
						<Switch bind:state={permissions.chat.regenerate_response} />
					</div>
				</div>
			</div>
		{/if}

		{#if show('chat.rate_response')}
			<div class="flex flex-col w-full">
				<div class="flex w-full justify-between my-1">
					<div class=" self-center text-xs font-medium">
						{$i18n.t('Allow Rate Response')}
					</div>
					<div class="flex items-center gap-2">
						{@render permissionIndicator('chat.rate_response')}
						<Switch bind:state={permissions.chat.rate_response} />
					</div>
				</div>
			</div>
		{/if}

		{#if show('chat.share')}
			<div class="flex flex-col w-full">
				<div class="flex w-full justify-between my-1">
					<div class=" self-center text-xs font-medium">
						{$i18n.t('Allow Chat Share')}
					</div>
					<div class="flex items-center gap-2">
						{@render permissionIndicator('chat.share')}
						<Switch bind:state={permissions.chat.share} />
					</div>
				</div>
			</div>
		{/if}

		{#if show('chat.export')}
			<div class="flex flex-col w-full">
				<div class="flex w-full justify-between my-1">
					<div class=" self-center text-xs font-medium">
						{$i18n.t('Allow Chat Export')}
					</div>
					<div class="flex items-center gap-2">
						{@render permissionIndicator('chat.export')}
						<Switch bind:state={permissions.chat.export} />
					</div>
				</div>
			</div>
		{/if}

		{#if show('chat.stt')}
			<div class="flex flex-col w-full">
				<div class="flex w-full justify-between my-1">
					<div class=" self-center text-xs font-medium">
						{$i18n.t('Allow Speech to Text')}
					</div>
					<div class="flex items-center gap-2">
						{@render permissionIndicator('chat.stt')}
						<Switch bind:state={permissions.chat.stt} />
					</div>
				</div>
			</div>
		{/if}

		{#if show('chat.tts')}
			<div class="flex flex-col w-full">
				<div class="flex w-full justify-between my-1">
					<div class=" self-center text-xs font-medium">
						{$i18n.t('Allow Text to Speech')}
					</div>
					<div class="flex items-center gap-2">
						{@render permissionIndicator('chat.tts')}
						<Switch bind:state={permissions.chat.tts} />
					</div>
				</div>
			</div>
		{/if}

		{#if show('chat.call')}
			<div class="flex flex-col w-full">
				<div class="flex w-full justify-between my-1">
					<div class=" self-center text-xs font-medium">
						{$i18n.t('Allow Call')}
					</div>
					<div class="flex items-center gap-2">
						{@render permissionIndicator('chat.call')}
						<Switch bind:state={permissions.chat.call} />
					</div>
				</div>
			</div>
		{/if}

		{#if show('chat.temporary')}
			<div class="flex flex-col w-full">
				<div class="flex w-full justify-between my-1">
					<div class=" self-center text-xs font-medium">
						{$i18n.t('Allow Temporary Chat')}
					</div>
					<div class="flex items-center gap-2">
						{@render permissionIndicator('chat.temporary')}
						<Switch bind:state={permissions.chat.temporary} />
					</div>
				</div>
			</div>
		{/if}

	</div>

	<hr class=" border-gray-100/30 dark:border-gray-850/30" />

	<div>
		<div class=" mb-2 text-sm font-medium">{$i18n.t('Features Permissions')}</div>

		{#if show('features.api_keys')}
			<div class="flex flex-col w-full">
				<div class="flex w-full justify-between my-1">
					<div class=" self-center text-xs font-medium">
						{$i18n.t('API Keys')}
					</div>
					<div class="flex items-center gap-2">
						{@render permissionIndicator('features.api_keys')}
						<Switch bind:state={permissions.features.api_keys} />
					</div>
				</div>
			</div>
		{/if}

		{#if show('features.folders')}
			<div class="flex flex-col w-full">
				<div class="flex w-full justify-between my-1">
					<div class=" self-center text-xs font-medium">
						{$i18n.t('Folders')}
					</div>
					<div class="flex items-center gap-2">
						{@render permissionIndicator('features.folders')}
						<Switch bind:state={permissions.features.folders} />
					</div>
				</div>
			</div>
		{/if}

		{#if show('features.web_search')}
			<div class="flex flex-col w-full">
				<div class="flex w-full justify-between my-1">
					<div class=" self-center text-xs font-medium">
						{$i18n.t('Web Search')}
					</div>
					<div class="flex items-center gap-2">
						{@render permissionIndicator('features.web_search')}
						<Switch bind:state={permissions.features.web_search} />
					</div>
				</div>
			</div>
		{/if}

		{#if show('features.image_generation')}
			<div class="flex flex-col w-full">
				<div class="flex w-full justify-between my-1">
					<div class=" self-center text-xs font-medium">
						{$i18n.t('Image Generation')}
					</div>
					<div class="flex items-center gap-2">
						{@render permissionIndicator('features.image_generation')}
						<Switch bind:state={permissions.features.image_generation} />
					</div>
				</div>
			</div>
		{/if}

		{#if show('features.memories')}
			<div class="flex flex-col w-full">
				<div class="flex w-full justify-between my-1">
					<div class=" self-center text-xs font-medium">
						{$i18n.t('Memories')}
					</div>
					<div class="flex items-center gap-2">
						{@render permissionIndicator('features.memories')}
						<Switch bind:state={permissions.features.memories} />
					</div>
				</div>
			</div>
		{/if}
	</div>

	<hr class=" border-gray-100/30 dark:border-gray-850/30" />

	<div>
		<div class=" mb-2 text-sm font-medium">{$i18n.t('Settings Permissions')}</div>

		{#if show('settings.interface')}
			<div class="flex flex-col w-full">
				<div class="flex w-full justify-between my-1">
					<div class=" self-center text-xs font-medium">
						{$i18n.t('Interface Settings Access')}
					</div>
					<div class="flex items-center gap-2">
						{@render permissionIndicator('settings.interface')}
						<Switch bind:state={permissions.settings.interface} />
					</div>
				</div>
			</div>
		{/if}
	</div>
</div>
