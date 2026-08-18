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

  let showAddBillModal = false;
  let billSupplierId = 0;
  let billSupplierName = '';
  let supplierBillDate = new Date().toISOString().substring(0, 10);
  let supplierBillAmount = 0;
  let supplierAmountPaid = 0;
  let supplierBillRemarks = '';

  let showBillsModal = false;
  let currentSupplierBills = [];
  let viewBillsSupplierName = '';

  let payBillId = 0;
  let payBillAmount = 0;
  let payBillMax = 0;
  let showPayBillModal = false;

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

  const handleSupplierBillSaved = (event, res) => {
    if (res.success) {
      showToast('Bill saved successfully!');
      showAddBillModal = false;
      window.ipcRenderer.send('get-suppliers'); // Refresh
    } else {
      alert('Error: ' + res.error);
    }
  };

  const handleSupplierBillsData = (event, res) => {
    if (res.success) {
      currentSupplierBills = res.rows;
      showBillsModal = true;
    } else {
      alert('Error: ' + res.error);
    }
  };

  const handleSupplierBillPaid = (event, res) => {
    if (res.success) {
      showToast('Payment recorded successfully!');
      showPayBillModal = false;
      window.ipcRenderer.send('get-supplier-bills', billSupplierId);
      window.ipcRenderer.send('get-suppliers'); // Refresh main balance
    } else {
      alert('Error: ' + res.error);
    }
  };

  let unsubSaved: (() => void);
  let unsubPayment: (() => void);
  let unsubBillSaved: (() => void);
  let unsubBillsData: (() => void);
  let unsubBillPaid: (() => void);

  onMount(() => {
    unsubSaved = window.ipcRenderer.on('supplier-saved', handleSupplierSaved);
    unsubPayment = window.ipcRenderer.on('supplier-payment-added', handleSupplierPaymentAdded);
    unsubBillSaved = window.ipcRenderer.on('supplier-bill-saved', handleSupplierBillSaved);
    unsubBillsData = window.ipcRenderer.on('supplier-bills-data', handleSupplierBillsData);
    unsubBillPaid = window.ipcRenderer.on('supplier-bill-paid', handleSupplierBillPaid);
  });

  onDestroy(() => {
    if (unsubSaved) unsubSaved();
    if (unsubPayment) unsubPayment();
    if (unsubBillSaved) unsubBillSaved();
    if (unsubBillsData) unsubBillsData();
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

  function viewBills(supplier) {
    billSupplierId = supplier.id;
    viewBillsSupplierName = supplier.name;
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
    window.ipcRenderer.send('pay-supplier-bill', payBillId, payBillAmount);
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
                    <button class="btn-secondary" style="padding:4px 10px; font-size:12px;" on:click={() => openAddBillModal(sup)}>Add Bill</button>
                    <button class="btn-secondary" style="padding:4px 10px; font-size:12px;" on:click={() => viewBills(sup)}>View Bills</button>
                    <button class="btn-secondary" style="padding:4px 10px; font-size:12px;" on:click={() => openPaymentModal(sup)}>Add Open Payment</button>
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
      <h3 style="margin-top:0;">Add Open Payment for {paymentSupplierName}</h3>
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

{#if showAddBillModal}
  <div class="modal-overlay show" style="display: flex;">
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

{#if showBillsModal}
  <div class="modal-overlay show" style="display: flex;">
    <div class="modal-card modal-lg" style="background:var(--card-bg);">
      <h3 style="margin-top:0;">Bill History - {viewBillsSupplierName}</h3>
      
      <div style="max-height: 400px; overflow-y: auto; margin-top: 15px;">
        {#if currentSupplierBills.length === 0}
          <div style="padding: 20px; text-align: center; color: var(--text-muted);">No bills found for this supplier.</div>
        {:else}
          <table style="width: 100%; border-collapse: collapse;">
            <thead style="background: var(--bg); position: sticky; top: 0;">
              <tr>
                <th style="padding: 10px; text-align: left; border-bottom: 1px solid var(--border);">Date</th>
                <th style="padding: 10px; text-align: left; border-bottom: 1px solid var(--border);">Remarks</th>
                <th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border);">Bill Amt</th>
                <th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border);">Paid</th>
                <th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border);">Pending</th>
                <th style="padding: 10px; text-align: center; border-bottom: 1px solid var(--border);">Status</th>
                <th style="padding: 10px; text-align: center; border-bottom: 1px solid var(--border);">Action</th>
              </tr>
            </thead>
            <tbody>
              {#each currentSupplierBills as bill}
                <tr>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border);">{bill.bill_date}</td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border);">{bill.remarks || '--'}</td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: right;">₹{parseFloat(bill.bill_amount).toFixed(2)}</td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: right;">₹{parseFloat(bill.amount_paid).toFixed(2)}</td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: right; font-weight: bold; color: var(--danger);">
                    ₹{parseFloat(bill.bill_amount - bill.amount_paid).toFixed(2)}
                  </td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: center;">
                    {#if bill.status === 'Paid'}
                      <span style="background: var(--success); color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px;">Paid</span>
                    {:else if bill.status === 'Partial'}
                      <span style="background: var(--primary); color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px;">Partial</span>
                    {:else}
                      <span style="background: var(--danger); color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px;">Pending</span>
                    {/if}
                  </td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: center;">
                    {#if bill.status !== 'Paid'}
                      <button class="btn-primary" style="padding: 4px 8px; font-size: 11px;" on:click={() => openPayBillModal(bill)}>Pay</button>
                    {/if}
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        {/if}
      </div>
      
      <div style="display:flex; justify-content:flex-end; gap:10px; margin-top:20px;">
        <button class="btn-secondary" on:click={() => showBillsModal = false}>Close</button>
      </div>
    </div>
  </div>
{/if}

{#if showPayBillModal}
  <div class="modal-overlay show" style="display: flex;">
    <div class="modal-card" style="background:var(--card-bg); max-width:400px; z-index: 2000;">
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
