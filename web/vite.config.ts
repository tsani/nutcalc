import { defineConfig } from 'vite';
import preact from '@preact/preset-vite';

const rewriteSlashToIndexHtml = (): any => {
	return {
		name: 'rewrite-slash-to-index-html',
		apply: 'serve',
		enforce: 'post',
		configureServer(server) {
			// rewrite / as index.html
			server.middlewares.use('/', (req, _, next) => {
				if (req.url === '/') {
					req.url = '/index.html'
				}
				next()
			})
		},
	}
}

// https://vitejs.dev/config/
export default defineConfig({
	plugins: [
		preact(),
		rewriteSlashToIndexHtml(),
	],
	appType: 'mpa',
});
