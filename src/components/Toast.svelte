<script lang="ts">
  import { toastMessage, toastVisible } from '../store';
</script>

<div id="toast" class="toast" class:show={$toastVisible}>
  <span class="toast-icon">✓</span> 
  <span id="toast-text">{$toastMessage}</span>
</div>
