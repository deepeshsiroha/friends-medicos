<script lang="ts">
  import { onMount } from 'svelte';
  import { activeTab, globalEditRecordId, sidebarOpen, lowStockItems, nearExpiryItems } from '../store';

  let darkTheme = false;

  onMount(() => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    darkTheme = (savedTheme === 'dark');
    if (darkTheme) {
      document.body.classList.add('dark-theme');
    } else {
      document.body.classList.remove('dark-theme');
    }
  });

  function toggleTheme(event: Event) {
    const target = event.target as HTMLInputElement;
    darkTheme = target.checked;
    if (darkTheme) {
      document.body.classList.add('dark-theme');
      localStorage.setItem('theme', 'dark');
    } else {
      document.body.classList.remove('dark-theme');
      localStorage.setItem('theme', 'light');
    }
  }

  function openTab(tabName: string) {
    activeTab.set(tabName);
    sidebarOpen.set(false);
    
    if (tabName === 'history') ipcRenderer.send('get-records');
    if (tabName === 'billing') {
      ipcRenderer.send('get-bills');
      ipcRenderer.send('get-inventory');
    }
    if (tabName === 'inventory') ipcRenderer.send('get-inventory');
    if (tabName === 'analytics') ipcRenderer.send('get-analytics-data');
    if (tabName === 'customers') ipcRenderer.send('get-customers');
    if (tabName === 'suppliers') ipcRenderer.send('get-suppliers');
    if (tabName === 'expenses') ipcRenderer.send('get-expenses');
  }

  function closeDrawer() {
    sidebarOpen.set(false);
  }
</script>

<!-- Sidebar Overlay -->
{#if $sidebarOpen}
  <div class="sidebar-overlay show" on:click={closeDrawer}></div>
{/if}

<!-- Left Sidebar Panel (Drawer) -->
<div class="sidebar" class:open={$sidebarOpen} id="sidebar-drawer">
    <div class="sidebar-header">
        <div class="sidebar-logo">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" stroke-width="2.5"
                stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2" />
            </svg>
            <span>Friends</span> Medicos
        </div>
    </div>
    <div class="sidebar-menu">
        <button class="sidebar-btn" class:active={$activeTab === 'billing'} on:click={() => openTab('billing')}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round">
                <rect x="4" y="2" width="16" height="20" rx="2" />
                <line x1="8" y1="6" x2="16" y2="6" />
                <line x1="8" y1="10" x2="16" y2="10" />
                <line x1="8" y1="14" x2="16" y2="14" />
                <line x1="8" y1="18" x2="16" y2="18" />
            </svg>
            Sales POS / Billing
        </button>
        <button class="sidebar-btn" class:active={$activeTab === 'inventory'} on:click={() => openTab('inventory')}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round">
                <path
                    d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 2-2 0l7-4A2 2 0 0 0 21 16z" />
                <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
                <line x1="12" y1="22.08" x2="12" y2="12" />
            </svg>
            Stock Inventory
        </button>
        <button class="sidebar-btn" id="analytics-sidebar-btn" class:active={$activeTab === 'analytics'} on:click={() => openTab('analytics')}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round">
                <line x1="18" y1="20" x2="18" y2="10" />
                <line x1="12" y1="20" x2="12" y2="4" />
                <line x1="6" y1="20" x2="6" y2="14" />
            </svg>
            Analytics Dashboard
        </button>
        <button class="sidebar-btn" class:active={$activeTab === 'suppliers'} on:click={() => openTab('suppliers')}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                <polyline points="22,6 12,13 2,6"></polyline>
            </svg>
            Suppliers Ledger
        </button>
        <button class="sidebar-btn" class:active={$activeTab === 'customers'} on:click={() => openTab('customers')}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="9" cy="7" r="4"></circle>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
            </svg>
            Customers CRM
        </button>
        <button class="sidebar-btn" class:active={$activeTab === 'expenses'} on:click={() => openTab('expenses')}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round">
                <line x1="12" y1="1" x2="12" y2="23"></line>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
            </svg>
            Daily Expenses
        </button>
        <button class="sidebar-btn" class:active={$activeTab === 'settings'} on:click={() => openTab('settings')}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3" />
                <path
                    d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
            </svg>
            App Settings
        </button>
        <button class="sidebar-btn" class:active={$activeTab === 'alerts'} on:click={() => openTab('alerts')}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>
            Alerts & Warnings
            {#if $lowStockItems.length > 0 || $nearExpiryItems.length > 0}
              <span style="display:inline-block; width:8px; height:8px; background:var(--warn); border-radius:50%; margin-left:auto;"></span>
            {/if}
        </button>
    </div>
    <div class="sidebar-footer">
        <div class="shortcuts-hint" style="padding-right: 0; font-size: 11px;">
            Shortcuts: <kbd>Ctrl+S</kbd> Save Form
        </div>
        <div class="theme-toggle-container">
            <span class="theme-toggle-label">Dark Theme</span>
            <label class="theme-toggle-switch">
                <input type="checkbox" id="theme-toggle-chk" checked={darkTheme} on:change={toggleTheme}>
                <span class="theme-slider"></span>
            </label>
        </div>
    </div>
</div>
