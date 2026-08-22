<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { 
    activeTab, toastMessage, toastVisible, showToast, lowStockItems, currentSettings, 
    stockRows, issueRows, billingHistory, 
    editStockModalData, previewModalData, previewModalVisible, globalEditRecordId, basket,
    sidebarOpen, nearExpiryItems, analyticsData, suppliersList, expensesList
  } from './store';

  // Import layout components
  import Sidebar from './components/Sidebar.svelte';
  import TopBar from './components/TopBar.svelte';
  import Toast from './components/Toast.svelte';
  import EditBanner from './components/EditBanner.svelte';

  // Import tab views
  import InventoryTab from './components/InventoryTab.svelte';
  import BillingTab from './components/BillingTab.svelte';
  import SettingsTab from './components/SettingsTab.svelte';
  import AnalyticsTab from './components/AnalyticsTab.svelte';
  import AlertsTab from './components/AlertsTab.svelte';
  import CustomersTab from './components/CustomersTab.svelte';
  import SuppliersTab from './components/SuppliersTab.svelte';
  import ExpensesTab from './components/ExpensesTab.svelte';

  import PreviewModal from './components/PreviewModal.svelte';
  import EditStockModal from './components/EditStockModal.svelte';

  let unsubscribes: (() => void)[] = [];

  onMount(() => {
    // 1. Initial fetches
    ipcRenderer.send('get-settings');
    ipcRenderer.send('get-inventory');
    ipcRenderer.send('get-bills');

    // 2. Register IPC Listeners
    unsubscribes.push(
      ipcRenderer.on('settings-data', (event, rows) => {
        const config: any = {};
        (rows || []).forEach((r: any) => config[r.key] = r.value);
        currentSettings.set(config);
      })
    );



    unsubscribes.push(
      ipcRenderer.on('inventory-data', (event, sRows, iRows) => {
        stockRows.set(sRows || []);
        issueRows.set(iRows || []);
      })
    );



    unsubscribes.push(
      ipcRenderer.on('bills-data', (event, bills) => {
        billingHistory.set(bills || []);
      })
    );

    unsubscribes.push(
      ipcRenderer.on('suppliers-data', (event, response) => {
        if (response.success) suppliersList.set(response.rows);
      })
    );

    unsubscribes.push(
      ipcRenderer.on('expenses-data', (event, response) => {
        if (response.success) expensesList.set(response.rows);
      })
    );

    // 3. Application Start Notifications
    unsubscribes.push(
      ipcRenderer.on('bill-save-status', (event, response) => {
        if (response.success) {
          showToast("Bill Generated successfully!");
          ipcRenderer.send('get-bills');
          ipcRenderer.send('get-inventory'); // because stock might have decremented
          
          // Trigger print event for BillingTab
          window.dispatchEvent(new CustomEvent('auto-print-invoice-saved', { detail: response.id }));
        } else {
          alert("Error saving bill: " + response.error);
        }
      })
    );



    unsubscribes.push(
      ipcRenderer.on('analytics-data-response', (event, res) => {
        if (res.success) {
          analyticsData.set(res.data);
        } else {
          alert("Failed to load analytics: " + res.error);
        }
      })
    );
  });

  onDestroy(() => {
    unsubscribes.forEach(unsub => unsub());
  });
</script>

<Sidebar />

<div class="main-viewport">
  <TopBar />
  <EditBanner />

  {#if $activeTab === 'billing'}
    <BillingTab />
  {:else if $activeTab === 'inventory'}
    <InventoryTab />
  {:else if $activeTab === 'analytics'}
    <AnalyticsTab />
  {:else if $activeTab === 'alerts'}
    <AlertsTab />
  {:else if $activeTab === 'customers'}
    <CustomersTab />
  {:else if $activeTab === 'suppliers'}
    <SuppliersTab />
  {:else if $activeTab === 'expenses'}
    <ExpensesTab />
  {:else if $activeTab === 'settings'}
    <SettingsTab />
  {/if}
</div>

<Toast />

<PreviewModal />
<EditStockModal />
