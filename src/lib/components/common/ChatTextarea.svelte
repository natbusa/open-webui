<script lang="ts">
	import { onMount, tick, getContext, createEventDispatcher } from 'svelte';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let id = '';
	export let placeholder = '';
	export let editable = true;
	export let value = '';

	export let onChange = (e: { md: string }) => {};

	let textareaElement: HTMLTextAreaElement;

	onMount(async () => {
		await tick();
		resize();
	});

	const resize = () => {
		if (textareaElement) {
			textareaElement.style.height = '';
			textareaElement.style.height = `${textareaElement.scrollHeight}px`;
		}
	};

	export const setText = (text: string) => {
		value = text ?? '';
		tick().then(() => {
			resize();
			onChange({ md: value });
		});
	};

	export const focus = () => {
		if (textareaElement) {
			textareaElement.focus();
		}
	};

	export const insertContent = (text: string) => {
		if (!textareaElement) return;
		const start = textareaElement.selectionStart;
		const end = textareaElement.selectionEnd;
		value = value.slice(0, start) + text + value.slice(end);
		tick().then(() => {
			const newPos = start + text.length;
			textareaElement.selectionStart = newPos;
			textareaElement.selectionEnd = newPos;
			resize();
			onChange({ md: value });
			focus();
		});
	};

	export const getWordAtDocPos = () => {
		if (!textareaElement) return '';
		const pos = textareaElement.selectionStart;
		const text = value;
		let wordStart = pos;
		let wordEnd = pos;
		while (wordStart > 0 && !/\s/.test(text[wordStart - 1])) wordStart--;
		while (wordEnd < text.length && !/\s/.test(text[wordEnd])) wordEnd++;
		return text.slice(wordStart, wordEnd);
	};

	export const replaceCommandWithText = (text: string) => {
		if (!textareaElement) return;
		const pos = textareaElement.selectionStart;
		const fullText = value;
		let wordStart = pos;
		let wordEnd = pos;
		while (wordStart > 0 && !/\s/.test(fullText[wordStart - 1])) wordStart--;
		while (wordEnd < fullText.length && !/\s/.test(fullText[wordEnd])) wordEnd++;
		value = fullText.slice(0, wordStart) + text + fullText.slice(wordEnd);
		tick().then(() => {
			const newPos = wordStart + text.length;
			textareaElement.selectionStart = newPos;
			textareaElement.selectionEnd = newPos;
			resize();
			onChange({ md: value });
			focus();
		});
	};

	export const replaceVariables = (variables: Record<string, any>) => {
		value = value.replace(/{{\s*([^|}]+)(?:\|[^}]*)?\s*}}/g, (match, varName) => {
			const trimmedVarName = varName.trim();
			return variables.hasOwnProperty(trimmedVarName) ? String(variables[trimmedVarName]) : match;
		});
		tick().then(() => {
			resize();
			onChange({ md: value });
		});
	};

	export const setContent = (content: any) => {
		if (typeof content === 'string') {
			setText(content);
		}
	};
</script>

<textarea
	bind:this={textareaElement}
	bind:value
	{id}
	{placeholder}
	disabled={!editable}
	class="scrollbar-hidden bg-transparent outline-none w-full resize-none"
	style="field-sizing: content;"
	rows="1"
	on:input={() => {
		resize();
		onChange({ md: value });
	}}
	on:focus={() => {
		resize();
	}}
	on:keydown={(e) => {
		dispatch('keydown', e);
	}}
	on:paste={(e) => {
		dispatch('paste', e);
	}}
></textarea>
