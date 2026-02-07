export const DEFAULT_PERMISSIONS = {
	workspace: {
		models: true,
		knowledge: true,
		models_import: false,
		models_export: false
	},
	sharing: {
		models: false,
		public_models: false,
		knowledge: false,
		public_knowledge: false,
		notes: false,
		public_notes: false
	},
	chat: {
		controls: true,
		valves: true,
		system_prompt: true,
		params: true,
		file_upload: true,
		delete: true,
		delete_message: true,
		regenerate_response: true,
		rate_response: true,
		edit: true,
		share: true,
		export: true,
		stt: true,
		tts: true,
		call: true,
		multiple_models: true,
		temporary: true,
		temporary_enforced: false
	},
	features: {
		api_keys: false,
		notes: true,
		folders: true,
		web_search: true,
		image_generation: true,
		memories: true
	},
	settings: {
		interface: true
	}
} as const;
