import typography from '@tailwindcss/typography';
import containerQueries from '@tailwindcss/container-queries';

/** @type {import('tailwindcss').Config} */
export default {
	darkMode: 'class',
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			colors: {
				gray: {
					50: 'var(--color-gray-50, #f5efe8)',
					100: 'var(--color-gray-100, #e8ddd0)',
					200: 'var(--color-gray-200, #d4c4b0)',
					300: 'var(--color-gray-300, #c4b8a8)',
					400: 'var(--color-gray-400, #a09080)',
					500: 'var(--color-gray-500, #8a7a6a)',
					600: 'var(--color-gray-600, #6b5d50)',
					700: 'var(--color-gray-700, #4a3d32)',
					800: 'var(--color-gray-800, #362a20)',
					850: 'var(--color-gray-850, #2d1f18)',
					900: 'var(--color-gray-900, #1a1210)',
					950: 'var(--color-gray-950, #0f0a07)'
				},
				amber: {
					400: '#f5a623',
					500: '#d4883a',
					600: '#b8722e',
					700: '#9a5f24'
				}
			},
			typography: {
				DEFAULT: {
					css: {
						pre: false,
						code: false,
						'pre code': false,
						'code::before': false,
						'code::after': false
					}
				}
			},
			padding: {
				'safe-bottom': 'env(safe-area-inset-bottom)'
			},
			transitionProperty: {
				width: 'width'
			}
		}
	},
	plugins: [typography, containerQueries]
};
