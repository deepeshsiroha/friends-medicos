<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { activeTab, showToast, suppliersList } from '../store';

  let searchQuery = '';
  let unsubscribes: (() => void)[] = [];

  let showAddModal = false;
  let editId = 0;
  let supName = '';
  let supContact = '';
  let supGstin = '';

  let showPaymentModal = false;
  let paymentSupplierId = 0;
  let paymentAmount = 0;
  let paymentSupplierName = '';

  const handleSupplierSaved = (event, res) => {
    if (res.success) {
      showToast('Supplier saved successfully!');
      showAddModal = false;
      window.ipcRenderer.send('get-suppliers'); // Refresh
    } else {
      alert('Error: ' + res.error);
    }
  };

  const handleSupplierPaymentAdded = (event, res) => {
    if (res.success) {
      showToast('Payment recorded successfully!');
      showPaymentModal = false;
      window.ipcRenderer.send('get-suppliers'); // Refresh
    } else {
      alert('Error: ' + res.error);
    }
  };

  let unsubSaved: (() => void);
  let unsubPayment: (() => void);

  onMount(() => {
    unsubSaved = window.ipcRenderer.on('supplier-saved', handleSupplierSaved);
    unsubPayment = window.ipcRenderer.on('supplier-payment-added', handleSupplierPaymentAdded);
  });

  onDestroy(() => {
    if (unsubSaved) unsubSaved();
    if (unsubPayment) unsubPayment();
  });

  $: filteredSuppliers = $suppliersList.filter(s => {
    if (!searchQuery) return true;
    const term = searchQuery.toLowerCase();
    return (s.name || '').toLowerCase().includes(term) || (s.gstin || '').toLowerCase().includes(term);
  });

  function openAddModal(supplier = null) {
    if (supplier) {
      editId = supplier.id;
      supName = supplier.name;
      supContact = supplier.contact;
      supGstin = supplier.gstin;
    } else {
      editId = 0;
      supName = '';
      supContact = '';
      supGstin = '';
    }
    showAddModal = true;
  }

  function saveSupplier() {
    if (!supName.trim()) return alert("Name is required");
    window.ipcRenderer.send('save-supplier', { id: editId, name: supName.trim(), contact: supContact.trim(), gstin: supGstin.trim() });
  }

  function openPaymentModal(supplier) {
    paymentSupplierId = supplier.id;
    paymentSupplierName = supplier.name;
    paymentAmount = 0;
    showPaymentModal = true;
  }

  function savePayment() {
    if (paymentAmount <= 0) return alert("Amount must be positive");
    window.ipcRenderer.send('add-supplier-payment', paymentSupplierId, paymentAmount);
  }
</script>

<div id="suppliers-tab" class="tab-content {$activeTab === 'suppliers' ? 'active' : ''}">
  <div class="table-header-controls" style="margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
    <div>
      <h2 style="margin: 0; font-family: 'Outfit', sans-serif;">Distributor & Supplier Ledger</h2>
      <p style="color: var(--text-muted); font-size: 14px; margin-top: 5px;">Manage distributor balances (Khata) and log payments.</p>
    </div>
    <div style="display: flex; gap: 10px; align-items: center;">
      <input type="text" placeholder="🔍 Search Supplier..." bind:value={searchQuery} style="margin: 0; min-width: 250px;">
      <button class="btn-primary" on:click={() => openAddModal(null)}>+ Add Supplier</button>
    </div>
  </div>

  <div class="card" style="padding: 20px;">
    {#if filteredSuppliers.length === 0}
      <div style="text-align: center; color: var(--text-muted); padding: 40px;">No suppliers found. Click "+ Add Supplier" to begin tracking.</div>
    {:else}
      <div style="max-height: calc(100vh - 250px); overflow-y: auto;">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Supplier Name</th>
              <th>Contact</th>
              <th>GSTIN</th>
              <th>Current Balance</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each filteredSuppliers as sup}
              <tr>
                <td>#{sup.id}</td>
                <td style="font-weight: bold; color: var(--primary);">{sup.name}</td>
                <td>{sup.contact || '--'}</td>
                <td>{sup.gstin || '--'}</td>
                <td style="font-weight: bold; color: {sup.balance > 0 ? 'var(--success)' : (sup.balance < 0 ? 'var(--danger)' : 'var(--text)')};">
                  {sup.balance < 0 ? '-' : ''}₹{Math.abs(sup.balance || 0).toFixed(2)}
                </td>
                <td>
                  <div style="display:flex; gap:8px;">
                    <button class="btn-secondary" style="padding:4px 10px; font-size:12px;" on:click={() => openPaymentModal(sup)}>Add Payment</button>
                    <button class="btn-secondary" style="padding:4px 10px; font-size:12px;" on:click={() => openAddModal(sup)}>Edit</button>
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</div>

{#if showAddModal}
  <div class="modal-overlay show" style="display: flex;">
    <div class="modal-card" style="background:var(--card-bg); max-width:400px;">
      <h3 style="margin-top:0;">{editId ? 'Edit' : 'Add'} Supplier</h3>
      <div class="form-group">
        <label>Name</label>
        <input type="text" bind:value={supName}>
      </div>
      <div class="form-group">
        <label>Contact Details</label>
        <input type="text" bind:value={supContact} placeholder="Phone/Email">
      </div>
      <div class="form-group">
        <label>GSTIN</label>
        <input type="text" bind:value={supGstin}>
      </div>
      <div style="display:flex; justify-content:flex-end; gap:10px; margin-top:20px;">
        <button class="btn-secondary" on:click={() => showAddModal = false}>Cancel</button>
        <button class="btn-primary" on:click={saveSupplier}>Save</button>
      </div>
    </div>
  </div>
{/if}

{#if showPaymentModal}
  <div class="modal-overlay show" style="display: flex;">
    <div class="modal-card" style="background:var(--card-bg); max-width:400px;">
      <h3 style="margin-top:0;">Add Payment for {paymentSupplierName}</h3>
      <div class="form-group">
        <label>Payment Amount (₹)</label>
        <input type="number" bind:value={paymentAmount} min="1">
      </div>
      <p style="font-size:12px; color:var(--text-muted);">This will INCREASE the balance. Balances are negative when you Owe money (Purchases) and positive when paid.</p>
      <div style="display:flex; justify-content:flex-end; gap:10px; margin-top:20px;">
        <button class="btn-secondary" on:click={() => showPaymentModal = false}>Cancel</button>
        <button class="btn-primary" on:click={savePayment}>Record Payment</button>
      </div>
    </div>
  </div>
{/if}
