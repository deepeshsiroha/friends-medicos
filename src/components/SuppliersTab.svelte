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

  
  let paymentSupplierId = 0;
  let paymentAmount = 0;
  

  let showAddBillModal = false;
  let billSupplierId = 0;
  let billSupplierName = '';
  let supplierBillDate = new Date().toISOString().substring(0, 10);
  let supplierBillAmount = 0;
  let supplierAmountPaid = 0;
  let supplierBillRemarks = '';

  let showLedgerModal = false;
  let currentLedgerItems = [];
  let currentLedgerSupplier = null;
  

  let payBillId = 0;
  let payBillAmount = 0;
  let payBillMax = 0;
  let showPayBillModal = false;

  const handleSupplierDeleted = (event, res) => {
    if (res.success) {
      showToast('Supplier deleted successfully!');
      window.ipcRenderer.send('get-suppliers'); // Refresh list
    } else {
      alert('Error: ' + res.error);
    }
  };

  function deleteSupplier(supplier) {
    if (confirm(`Are you sure you want to delete supplier "${supplier.name}"? This will delete all their transactions and bills permanently.`)) {
      window.ipcRenderer.send('delete-supplier', supplier.id);
    }
  }

  const handleSupplierSaved = (event, res) => {
    if (res.success) {
      showToast('Supplier saved successfully!');
      showAddModal = false;
            window.ipcRenderer.send('get-suppliers'); // Refresh
      if (showLedgerModal && currentLedgerSupplier) {
        window.ipcRenderer.send('get-supplier-bills', currentLedgerSupplier.id);
      }
    } else {
      alert('Error: ' + res.error);
    }
  };

  const handleSupplierPaymentAdded = (event, res) => {
    if (res.success) {
      showToast('Payment recorded successfully!');
      showPaymentModal = false;
            window.ipcRenderer.send('get-suppliers'); // Refresh
      if (showLedgerModal && currentLedgerSupplier) {
        window.ipcRenderer.send('get-supplier-bills', currentLedgerSupplier.id);
      }
    } else {
      alert('Error: ' + res.error);
    }
  };

  const handleSupplierBillSaved = (event, res) => {
    if (res.success) {
      showToast('Bill saved successfully!');
      showAddBillModal = false;
            window.ipcRenderer.send('get-suppliers'); // Refresh
      if (showLedgerModal && currentLedgerSupplier) {
        window.ipcRenderer.send('get-supplier-bills', currentLedgerSupplier.id);
      }
    } else {
      alert('Error: ' + res.error);
    }
  };

  const handleBillDeleted = (event, res) => {
    if (res.success) {
      showToast('Bill deleted successfully');
      window.ipcRenderer.send('get-suppliers');
      if (showLedgerModal && currentLedgerSupplier) {
        window.ipcRenderer.send('get-supplier-bills', currentLedgerSupplier.id);
      }
    } else {
      alert('Error deleting bill: ' + res.error);
    }
  };

  function deleteBill(id) {
    if (confirm("Are you sure you want to delete this transaction? This will reverse its effect on your balance.")) {
      window.ipcRenderer.send('delete-supplier-bill', id);
    }
  }

  const handleSupplierBillsData = (event, res) => {
    if (res.success) {
      currentLedgerItems = res.rows;
      showLedgerModal = true;
    } else {
      alert('Error fetching bills: ' + res.error);
    }
  };

  const handleSupplierBillPaid = (event, res) => {
    if (res.success) {
      showToast('Payment recorded successfully!');
      showPayBillModal = false;
      window.ipcRenderer.send('get-supplier-bills', billSupplierId);
      window.ipcRenderer.send('get-suppliers'); // Refresh
      if (showLedgerModal && currentLedgerSupplier) {
        window.ipcRenderer.send('get-supplier-bills', currentLedgerSupplier.id);
      }
    } else {
      alert('Error: ' + res.error);
    }
  };

  let unsubSaved: (() => void);
  let unsubPayment: (() => void);
  let unsubBillSaved: (() => void);
  let unsubLedgerData: (() => void);
  let unsubTrxDeleted: (() => void);
  let unsubSupplierDeleted: (() => void);
  let unsubBillPaid: (() => void);

  onMount(() => {
    unsubSaved = window.ipcRenderer.on('supplier-saved', handleSupplierSaved);
    unsubPayment = window.ipcRenderer.on('supplier-payment-added', handleSupplierPaymentAdded);
    unsubBillSaved = window.ipcRenderer.on('supplier-bill-saved', handleSupplierBillSaved);
    unsubLedgerData = window.ipcRenderer.on('supplier-bills-data', handleSupplierBillsData);
    unsubTrxDeleted = window.ipcRenderer.on('supplier-bill-deleted', handleBillDeleted);
    unsubSupplierDeleted = window.ipcRenderer.on('supplier-deleted', handleSupplierDeleted);
    unsubBillPaid = window.ipcRenderer.on('supplier-bill-paid', handleSupplierBillPaid);
  });

  onDestroy(() => {
    if (unsubSaved) unsubSaved();
    if (unsubPayment) unsubPayment();
    if (unsubBillSaved) unsubBillSaved();
    if (unsubLedgerData) unsubLedgerData();
    if (unsubTrxDeleted) unsubTrxDeleted();
    if (unsubSupplierDeleted) unsubSupplierDeleted();
    if (unsubBillPaid) unsubBillPaid();
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



  function savePayment() {
    if (paymentAmount <= 0) return alert("Amount must be positive");
    window.ipcRenderer.send('add-supplier-payment', paymentSupplierId, paymentAmount);
  }

  function openAddBillModal(supplier) {
    billSupplierId = supplier.id;
    billSupplierName = supplier.name;
    supplierBillDate = new Date().toISOString().substring(0, 10);
    supplierBillAmount = 0;
    supplierAmountPaid = 0;
    supplierBillRemarks = '';
    showAddBillModal = true;
  }

  function saveSupplierBill() {
    if (supplierBillAmount <= 0) return alert("Bill amount must be positive");
    if (supplierAmountPaid < 0 || supplierAmountPaid > supplierBillAmount) return alert("Invalid amount paid");
    
    window.ipcRenderer.send('save-supplier-bill', {
      supplier_id: billSupplierId,
      bill_date: supplierBillDate,
      bill_amount: supplierBillAmount,
      amount_paid: supplierAmountPaid,
      remarks: supplierBillRemarks
    });
  }

  function openLedger(supplier) {
    currentLedgerSupplier = supplier;
    window.ipcRenderer.send('get-supplier-bills', supplier.id);
  }

  function openPayBillModal(bill) {
    payBillId = bill.id;
    payBillMax = bill.bill_amount - bill.amount_paid;
    payBillAmount = payBillMax;
    showPayBillModal = true;
  }

  function saveBillPayment() {
    if (payBillAmount <= 0 || payBillAmount > payBillMax) return alert("Invalid payment amount");
    window.ipcRenderer.send('pay-supplier-bill', { billId: payBillId, amount: payBillAmount });
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
                    <button class="btn-primary" style="padding:6px 14px; font-size:12px;" on:click={() => openLedger(sup)}>View Ledger</button>
                    <button class="btn-secondary" style="padding:6px 14px; font-size:12px;" on:click={() => openAddModal(sup)}>Edit</button>
                    <button class="btn-danger" style="padding:6px 14px; font-size:12px;" on:click={() => deleteSupplier(sup)}>Delete</button>
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



{#if showAddBillModal}
  <div class="modal-overlay show" style="display: flex; z-index: 4000;">
    <div class="modal-card" style="background:var(--card-bg); max-width:400px;">
      <h3 style="margin-top:0;">Add Bill for {billSupplierName}</h3>
      <div class="form-group">
        <label>Bill Date</label>
        <input type="date" bind:value={supplierBillDate}>
      </div>
      <div class="form-group">
        <label>Bill Amount (₹)</label>
        <input type="number" bind:value={supplierBillAmount} min="1">
      </div>
      <div class="form-group">
        <label>Amount Paid Upfront (₹)</label>
        <input type="number" bind:value={supplierAmountPaid} min="0">
      </div>
      <div class="form-group">
        <label>Remarks / Invoice No.</label>
        <input type="text" bind:value={supplierBillRemarks}>
      </div>
      <div style="display:flex; justify-content:flex-end; gap:10px; margin-top:20px;">
        <button class="btn-secondary" on:click={() => showAddBillModal = false}>Cancel</button>
        <button class="btn-primary" on:click={saveSupplierBill}>Save Bill</button>
      </div>
    </div>
  </div>
{/if}

{#if showLedgerModal && currentLedgerSupplier}
  <div class="modal-overlay show" style="display: flex;">
    <div class="modal-card" style="background:var(--card-bg); width: 850px; max-width:95vw; max-height: 90vh; display: flex; flex-direction: column;">
      
      <!-- Header Section -->
      <div style="padding: 24px 24px 20px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; background: var(--bg-color); border-radius: 12px 12px 0 0;">
        <div>
          <h2 style="margin: 0; font-size: 20px; display: flex; align-items: center; gap: 10px;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--primary);"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
            {currentLedgerSupplier.name}
          </h2>
          <div style="font-size: 13px; color: var(--text-muted); margin-top: 6px;">
            GSTIN: {currentLedgerSupplier.gstin || 'N/A'} • Contact: {currentLedgerSupplier.contact || 'N/A'}
          </div>
        </div>
        
        <div style="text-align: right; background: var(--card-bg); padding: 12px 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid var(--border);">
          <div style="font-size: 12px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Total Outstanding</div>
          {#if currentLedgerSupplier.balance < 0}
            <div style="color: var(--danger); font-size: 22px; font-weight: 700;">₹{Math.abs(currentLedgerSupplier.balance).toFixed(2)}</div>
            <div style="font-size: 11px; color: var(--danger); opacity: 0.8;">You owe supplier</div>
          {:else if currentLedgerSupplier.balance > 0}
            <div style="color: var(--success); font-size: 22px; font-weight: 700;">₹{currentLedgerSupplier.balance.toFixed(2)}</div>
            <div style="font-size: 11px; color: var(--success); opacity: 0.8;">Advance paid</div>
          {:else}
            <div style="color: var(--text-muted); font-size: 22px; font-weight: 700;">₹0.00</div>
            <div style="font-size: 11px; color: var(--text-muted);">Fully Settled</div>
          {/if}
        </div>
      </div>

      <!-- Table Section -->
      <div style="padding: 24px; overflow-y: auto; flex-grow: 1;">
        {#if currentLedgerItems.length === 0}
          <div class="empty-state" style="padding: 40px; text-align: center; color: var(--text-muted);">
            <div style="font-size: 40px; margin-bottom: 16px;">📄</div>
            <h3 style="margin: 0 0 8px;">No Bills Found</h3>
            <p style="margin: 0; font-size: 14px;">Add a bill to start tracking the ledger for {currentLedgerSupplier.name}.</p>
          </div>
        {:else}
          <div style="border: 1px solid var(--border); border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            <table class="data-table" style="width: 100%; border-collapse: collapse; background: var(--card-bg);">
              <thead>
                <tr style="background: var(--bg-color);">
                  <th style="padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--border); color: var(--text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Date</th>
                  <th style="padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--border); color: var(--text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Remarks (Invoice)</th>
                  <th style="padding: 12px 16px; text-align: right; border-bottom: 1px solid var(--border); color: var(--text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Total Bill</th>
                  <th style="padding: 12px 16px; text-align: right; border-bottom: 1px solid var(--border); color: var(--text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Paid Upfront</th>
                  <th style="padding: 12px 16px; text-align: right; border-bottom: 1px solid var(--border); color: var(--text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Balance Pending</th>
                  <th style="padding: 12px 16px; text-align: center; border-bottom: 1px solid var(--border); color: var(--text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Action</th>
                </tr>
              </thead>
              <tbody>
                {#each currentLedgerItems as item}
                  <tr style="transition: background 0.2s;" on:mouseover={(e) => e.currentTarget.style.background='var(--bg-color)'} on:mouseleave={(e) => e.currentTarget.style.background='transparent'}>
                    <td style="padding: 14px 16px; border-bottom: 1px solid var(--border); font-size: 14px;">{item.bill_date}</td>
                    <td style="padding: 14px 16px; border-bottom: 1px solid var(--border); font-size: 14px; font-weight: 500;">{item.remarks || '--'}</td>
                    <td style="padding: 14px 16px; border-bottom: 1px solid var(--border); text-align: right; font-size: 14px;">₹{parseFloat(item.bill_amount).toFixed(2)}</td>
                    <td style="padding: 14px 16px; border-bottom: 1px solid var(--border); text-align: right; font-size: 14px;">
                      {#if item.amount_paid > 0}
                        <span style="color: var(--success); font-weight: 500;">₹{parseFloat(item.amount_paid).toFixed(2)}</span>
                      {:else}
                        <span style="color: var(--text-muted);">₹0.00</span>
                      {/if}
                    </td>
                    <td style="padding: 14px 16px; border-bottom: 1px solid var(--border); text-align: right; font-size: 14px;">
                      {#if (item.bill_amount - item.amount_paid) > 0}
                        <span style="color: var(--danger); font-weight: 700; background: rgba(239, 68, 68, 0.1); padding: 4px 8px; border-radius: 4px;">₹{(item.bill_amount - item.amount_paid).toFixed(2)}</span>
                      {:else}
                        <span style="color: var(--success); font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">✓ Settled</span>
                      {/if}
                    </td>
                    <td style="padding: 14px 16px; border-bottom: 1px solid var(--border); text-align: center;">
                      <div style="display: flex; gap: 6px; justify-content: center; align-items: center;">
                        {#if (item.bill_amount - item.amount_paid) > 0}
                          <button class="btn-primary" style="padding: 6px 12px; font-size: 12px; border-radius: 6px; font-weight: 600; box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);" on:click={() => openPayBillModal(item)}>Pay</button>
                        {/if}
                        <button class="btn-secondary" style="padding: 6px 10px; font-size: 14px; border-radius: 6px; color: var(--danger); border-color: transparent; background: transparent;" title="Delete Bill" on:click={() => deleteBill(item.id)}>🗑️</button>
                      </div>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {/if}
      </div>

      <!-- Footer Section -->
      <div style="padding: 16px 24px; border-top: 1px solid var(--border); display: flex; justify-content: space-between; background: var(--bg-color); border-radius: 0 0 12px 12px;">
        <button class="btn-primary" style="padding: 8px 24px; font-weight: 500;" on:click={() => openAddBillModal(currentLedgerSupplier)}>+ Add Bill</button>
        <button class="btn-secondary" style="padding: 8px 24px; font-weight: 500;" on:click={() => showLedgerModal = false}>Close Ledger</button>
      </div>

    </div>
  </div>
{/if}

{#if showPayBillModal}
  <div class="modal-overlay show" style="display: flex; z-index: 4000;">
    <div class="modal-card" style="background:var(--card-bg); max-width:400px;">
      <h3 style="margin-top:0;">Pay Bill</h3>
      <div class="form-group">
        <label>Amount to Pay (Max ₹{payBillMax.toFixed(2)})</label>
        <input type="number" bind:value={payBillAmount} min="1" max={payBillMax}>
      </div>
      <div style="display:flex; justify-content:flex-end; gap:10px; margin-top:20px;">
        <button class="btn-secondary" on:click={() => showPayBillModal = false}>Cancel</button>
        <button class="btn-primary" on:click={saveBillPayment}>Submit Payment</button>
      </div>
    </div>
  </div>
{/if}
