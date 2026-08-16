<script lang="ts">
  import { sidebarOpen, currentSettings, globalEditRecordId } from '../store';

  function toggleDrawer() {
    sidebarOpen.update(v => !v);
  }
</script>

<div class="top-app-bar">
    <button class="drawer-toggle-btn" id="drawer-toggle" on:click={toggleDrawer}>
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="3" y1="6" x2="21" y2="6"/>
            <line x1="3" y1="12" x2="21" y2="12"/>
            <line x1="3" y1="18" x2="21" y2="18"/>
        </svg>
    </button>
    <h1 id="app-title-header" style="margin:0; margin-left:16px; font-size: 20px; color: var(--primary); font-family: 'Outfit', sans-serif;">
      {#if $globalEditRecordId}
        FRIENDS MEDICOS (EDIT MODE)
      {:else}
        {$currentSettings.pharmacy_name ?? "FRIENDS MEDICOS PHARMACY"}
      {/if}
    </h1>
</div>
