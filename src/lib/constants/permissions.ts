export const DEFAULT_PERMISSIONS = {
	workspace: {
		models_import: false,
		models_export: false
	},
	sharing: {
		notes: false,
		public_notes: false
	},
	chat: {
		controls: true,
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
		temporary: true
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
