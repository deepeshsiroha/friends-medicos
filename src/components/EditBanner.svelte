<script lang="ts">
  import { globalEditRecordId, activeTab } from '../store';

  function exitEditMode() {
    globalEditRecordId.set(null);
    window.dispatchEvent(new CustomEvent('clear-consultation-form'));
    activeTab.set('history');
    ipcRenderer.send('get-records');
  }
</script>

{#if $globalEditRecordId !== null}
  <div class="edit-banner" id="edit-mode-banner" style="display: flex;">
      <span>⚠️ EDIT MODE ACTIVE: You are overwriting an existing prescription log entry.</span>
      <button class="btn-cancel-edit" on:click={exitEditMode}>Cancel & Exit Edit Mode</button>
  </div>
{/if}
