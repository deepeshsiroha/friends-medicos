import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [svelte()],
  base: './', // Crucial for Electron loading assets using relative paths
  build: {
    outDir: 'dist-frontend',
    emptyOutDir: true,
    assetsDir: 'assets',
  }
});
