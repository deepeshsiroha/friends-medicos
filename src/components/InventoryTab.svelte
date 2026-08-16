<script lang="ts">
  import { onMount } from 'svelte';
  import { stockRows, issueRows, editStockModalData, showToast } from '../store';

  let currentSubTab = 'ledger'; // 'ledger' or 'history'

  // Form values
  let invItem = '';
  let invCategory = 'Tablet';
  let invBatch = '';
  let invPharmacy = '';
  let invReceivedDate = '';
  let invQty = '';
  let invPrice = '';
  let invSellingPrice = '';
  let invMrp = '';
  let invExpiry = '';
  let invRemarks = '';

  let stockFilterQuery = '';
  let issueFilterQuery = '';
  let issueStockFilter: 'all' | 'stock' | 'non-stock' = 'all';

  let filterCategory = 'All';
  let filterMaxStock = '';
  let filterExpiryDate = '';

  function resetFilters() {
    filterCategory = 'All';
    filterMaxStock = '';
    filterExpiryDate = '';
  }

  onMount(() => {
    resetReceivedDate();
  });

  function resetReceivedDate() {
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    invReceivedDate = `${yyyy}-${mm}-${dd}`;
  }

  function submitNewStock() {
    if (!invItem || !invQty) {
      alert("Complete Item name and Quantity values!");
      return;
    }
    const qtyInt = parseInt(invQty, 10);
    if (isNaN(qtyInt) || qtyInt <= 0) {
      alert("Please enter a valid quantity!");
      return;
    }
    const priceVal = parseFloat(invPrice);
    if (invPrice && (isNaN(priceVal) || priceVal < 0)) {
      alert("Please enter a valid buying price!");
      return;
    }
    const sellVal = parseFloat(invSellingPrice);
    if (invSellingPrice && (isNaN(sellVal) || sellVal < 0)) {
      alert("Please enter a valid selling price!");
      return;
    }
    const mrpVal = parseFloat(invMrp);

    let receivedDateFormatted = formatDateIST(new Date());
    if (invReceivedDate) {
      const [yyyy, mm, dd] = invReceivedDate.split('-');
      receivedDateFormatted = formatDateIST(new Date(parseInt(yyyy), parseInt(mm) - 1, parseInt(dd)));
    }

    ipcRenderer.send('add-stock', {
      item_name: invItem.trim(),
      category: invCategory,
      batch_no: invBatch.trim(),
      pharmacy_name: invPharmacy.trim(),
      received_date: receivedDateFormatted,
      received_qty: qtyInt,
      unit_price: priceVal || 0.0,
      selling_price: sellVal || 0.0,
      mrp: mrpVal || 0.0,
      expiry_date: invExpiry,
      remarks: invRemarks.trim()
    });

    invItem = '';
    invCategory = 'Tablet';
    invBatch = '';
    invPharmacy = '';
    invQty = '';
    invPrice = '';
    invSellingPrice = '';
    invMrp = '';
    invExpiry = '';
    invRemarks = '';
    resetReceivedDate();
    showToast("New Batch Registered Successfully.");
  }

  function verifyRowDeletion(row: any) {
    const confirmation = confirm(`Are you sure you want to delete the stock entry for "${row.item_name}"? \n\nThis action cannot be undone.`);
    if (confirmation) {
      ipcRenderer.send('delete-stock', row.id);
      showToast("Stock entry deleted successfully.");
    }
  }

  function openEditStockModal(row: any) {
    editStockModalData.set(row);
  }

  function formatDateIST(date: Date) {
    return date.toLocaleDateString('en-IN', {
      timeZone: 'Asia/Kolkata',
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  }

  function formatDateTimeIST(dateVal: string | Date, isIssueDate = false) {
    if (!dateVal) return '--';
    const date = new Date(dateVal);
    
    const dStr = date.toLocaleDateString('en-IN', {
      timeZone: 'Asia/Kolkata',
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });

    const tStr = date.toLocaleTimeString('en-IN', {
      timeZone: 'Asia/Kolkata',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });

    return isIssueDate ? `${dStr} - ${tStr}` : dStr;
  }

  // Reactive filters
  $: filteredStockRows = $stockRows.filter(row => {
    // 1. Text filter search query
    if (stockFilterQuery) {
      const q = stockFilterQuery.toLowerCase();
      const matchesText = (row.item_name || '').toLowerCase().includes(q) ||
                          (row.batch_no || '').toLowerCase().includes(q) ||
                          (row.pharmacy_name || '').toLowerCase().includes(q) ||
                          (row.remarks || '').toLowerCase().includes(q);
      if (!matchesText) return false;
    }

    // 2. Category filter
    if (filterCategory !== 'All') {
      const rowCategory = row.category || 'Tablet';
      if (rowCategory !== filterCategory) return false;
    }

    // 3. Max stock threshold filter
    if (filterMaxStock !== '' && filterMaxStock !== null) {
      const maxVal = parseInt(filterMaxStock as string, 10);
      if (!isNaN(maxVal)) {
        if (maxVal < 0) return false;
        if (row.remaining_qty > maxVal) return false;
      }
    }

    // 4. Expiry date filter (on or before selected date)
    if (filterExpiryDate) {
      if (!row.expiry_date) return false;
      if (row.expiry_date > filterExpiryDate) return false;
    }

    return true;
  });

  $: filteredIssueRows = $issueRows.filter(row => {
    // 1. Search Query Filter
    if (issueFilterQuery) {
      const q = issueFilterQuery.toLowerCase();
      const matchesSearch = (row.item_name || '').toLowerCase().includes(q) ||
                            (row.issued_to_name || '').toLowerCase().includes(q) ||
                            (row.issued_to_mobile || '').toLowerCase().includes(q);
      if (!matchesSearch) return false;
    }

    // 2. Stock Source Filter
    if (issueStockFilter === 'stock') {
      if (!row.inventory_id) return false;
    } else if (issueStockFilter === 'non-stock') {
      if (row.inventory_id) return false;
    }

    return true;
  });
</script>

<div id="inventory-tab" class="tab-content active">
    <div class="inventory-top-bar">
        <button class="btn-sub-tab" class:active={currentSubTab === 'ledger'} on:click={() => currentSubTab = 'ledger'}>Stock Inventory Ledger</button>
        <button class="btn-sub-tab" class:active={currentSubTab === 'history'} on:click={() => currentSubTab = 'history'}>Issue History Logs</button>
    </div>

    {#if currentSubTab === 'ledger'}
      <div id="ledger-view" class="inner-view-panel active">
          <div class="card" style="margin-bottom:25px;">
              <h2>Log Inward Stock Received</h2>
              <div class="input-grid" style="grid-template-columns: 2fr 1fr 1fr 1.5fr; margin-bottom: 12px;">
                  <div class="form-group"><label for="inv-item">Item Name</label><input type="text" id="inv-item" bind:value={invItem}></div>
                  <div class="form-group">
                      <label for="inv-category">Category</label>
                      <select id="inv-category" bind:value={invCategory}>
                          <option value="Tablet">Tablet</option>
                          <option value="Syrup">Syrup</option>
                          <option value="Powder">Powder</option>
                          <option value="Ointment/Gel">Ointment/Gel</option>
                          <option value="Injection Vial">Injection Vial</option>
                          <option value="Injection Ampule">Injection Ampule</option>
                      </select>
                  </div>
                  <div class="form-group"><label for="inv-batch">Batch No.</label><input type="text" id="inv-batch" bind:value={invBatch}></div>
                  <div class="form-group"><label for="inv-pharmacy">Distributor / Supplier</label><input type="text" id="inv-pharmacy" bind:value={invPharmacy} placeholder="Supplier Name"></div>
              </div>
              <div class="input-grid"
                  style="grid-template-columns: 1.5fr 1fr 1fr 1.5fr 2fr 1.5fr; align-items: flex-end;">
                  <div class="form-group"><label for="inv-received-date">Received Date</label><input type="date" id="inv-received-date" bind:value={invReceivedDate}></div>
                  <div class="form-group"><label for="inv-qty">Received Qty</label><input type="number" id="inv-qty" min="1" bind:value={invQty}></div>
                  <div class="form-group"><label for="inv-price">Buying Price</label><input type="number" id="inv-price" min="0" step="any" placeholder="Buying" bind:value={invPrice}></div>
                  <div class="form-group"><label for="inv-selling">Selling Price</label><input type="number" id="inv-selling" min="0" step="any" placeholder="Selling" bind:value={invSellingPrice}></div>
                  <div class="form-group"><label for="inv-mrp">MRP</label><input type="number" id="inv-mrp" min="0" step="any" placeholder="MRP" bind:value={invMrp}></div>
                  <div class="form-group"><label for="inv-expiry">Expiry Date</label><input type="date" id="inv-expiry" bind:value={invExpiry}></div>
                  <div class="form-group"><label for="inv-remarks">Remarks</label><input type="text" id="inv-remarks" bind:value={invRemarks} placeholder="Optional notes"></div>
                  <div class="form-group"><button class="btn-add" on:click={submitNewStock} style="width:100%; padding:10px;">Register Stock</button></div>
              </div>
          </div>

          <div class="table-header-controls" style="display:flex; flex-direction:column; gap:12px; margin-bottom: 20px;">
              <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                  <h2>Current Stock Ledger</h2>
                  <input type="text" id="stock-table-search" class="inline-search" bind:value={stockFilterQuery}
                      placeholder="🔍 Filter stock by name/batch/supplier..." style="max-width:350px; margin:0;">
              </div>
              
              <!-- Advanced Filter Toolbar -->
              <div style="display:flex; flex-wrap:wrap; gap:16px; align-items:center; background:var(--card-bg); border:1px solid var(--border); padding:12px 16px; border-radius:8px; font-size:13px; color:var(--text);">
                  <div style="display:flex; align-items:center; gap:8px;">
                      <span style="font-weight:600; color:var(--text-muted);">Category:</span>
                      <select bind:value={filterCategory} style="padding:6px 10px; border:1px solid var(--border); border-radius:4px; background:var(--bg); color:var(--text); font-size:12px; height: 32px; min-width: 100px;">
                           <option value="All">All Categories</option>
                          <option value="Tablet">Tablet</option>
                          <option value="Syrup">Syrup</option>
                          <option value="Powder">Powder</option>
                          <option value="Ointment/Gel">Ointment/Gel</option>
                          <option value="Injection Vial">Injection Vial</option>
                          <option value="Injection Ampule">Injection Ampule</option>
                      </select>
                  </div>
                  
                  <div style="display:flex; align-items:center; gap:8px;">
                      <span style="font-weight:600; color:var(--text-muted);">Stock Less Than:</span>
                      <input type="number" min="0" placeholder="Enter threshold..." bind:value={filterMaxStock} on:input={() => { if (filterMaxStock !== null && filterMaxStock !== '' && filterMaxStock < 0) filterMaxStock = 0; }} style="padding:6px 10px; border:1px solid var(--border); border-radius:4px; background:var(--bg); color:var(--text); font-size:12px; height:32px; width:120px; box-sizing:border-box;" />
                  </div>
                  
                  <div style="display:flex; align-items:center; gap:8px; flex:1; min-width:250px;">
                      <span style="font-weight:600; color:var(--text-muted);">Expiring On/Before:</span>
                      <input type="date" bind:value={filterExpiryDate} style="padding:6px 10px; border:1px solid var(--border); border-radius:4px; background:var(--bg); color:var(--text); font-size:12px; height:32px; flex:1;" />
                      {#if filterExpiryDate || filterMaxStock || filterCategory !== 'All'}
                          <button class="btn-clear" on:click={resetFilters} style="padding:6px 12px; font-size:12px; border-radius:4px; margin:0; height:32px;">Reset Filters</button>
                      {/if}
                  </div>
              </div>
          </div>
          <table>
              <thead>
                  <tr>
                      <th>S.No.</th>
                      <th>Item</th>
                      <th>Category</th>
                      <th>Batch No.</th>
                      <th>Distributor / Supplier</th>
                      <th>Received Date</th>
                      <th>Received Qty</th>
                      <th>Buying Price</th>
                      <th>Selling Price</th>
                      <th>Expiry Date</th>
                      <th>Issued Qty</th>
                      <th>Remaining Qty</th>
                      <th>Remarks</th>
                      <th>Action</th>
                  </tr>
              </thead>
              <tbody id="inventory-table">
                {#each filteredStockRows as row, idx}
                  <tr>
                      <td>{idx + 1}</td>
                      <td><strong>{row.item_name}</strong></td>
                      <td>{row.category || 'Tablet'}</td>
                      <td>{row.batch_no || '--'}</td>
                      <td>{row.pharmacy_name || '--'}</td>
                      <td>{row.received_date || '--'}</td>
                      <td>{row.received_qty}</td>
                      <td>{row.unit_price ? `₹${parseFloat(row.unit_price).toFixed(2)}` : '₹0.00'}</td>
                      <td>{row.selling_price ? `₹${parseFloat(row.selling_price).toFixed(2)}` : '₹0.00'}</td>
                      <td>
                        {#if row.expiry_date}
                          {@const diffDays = Math.ceil((new Date(row.expiry_date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))}
                          {#if diffDays <= 0}
                            <span class="badge-alert">{row.expiry_date}</span>
                          {:else if diffDays <= 90}
                            <span class="badge-warning">{row.expiry_date}</span>
                          {:else}
                            {row.expiry_date}
                          {/if}
                        {:else}
                          --
                        {/if}
                      </td>
                      <td>{row.issued_qty}</td>
                      <td style="font-weight:bold; color:{row.remaining_qty < 10 ? 'var(--warn)' : 'inherit'}">{row.remaining_qty}</td>
                      <td><small>{row.remarks || ''}</small></td>
                      <td>
                          <!-- svelte-ignore a11y-click-events-have-key-events -->
                          <!-- svelte-ignore a11y-no-static-element-interactions -->
                          <span class="action-link" style="font-size:12px; margin-right:6px;" on:click={() => openEditStockModal(row)}>✏ Edit</span>
                          <!-- svelte-ignore a11y-click-events-have-key-events -->
                          <!-- svelte-ignore a11y-no-static-element-interactions -->
                          <span class="delete-row-btn" on:click={() => verifyRowDeletion(row)} style="font-size:14px;">✕</span>
                      </td>
                  </tr>
                {/each}
                {#if filteredStockRows.length === 0}
                  <tr>
                    <td colspan="12" style="text-align: center; color: var(--text-muted); padding: 30px;">
                      No stock batches found matching the filter.
                    </td>
                  </tr>
                {/if}
              </tbody>
          </table>
      </div>
    {:else}
      <div id="history-view" class="inner-view-panel active">
          <div class="table-header-controls" style="display: flex; justify-content: space-between; align-items: center; gap: 15px; flex-wrap: wrap; margin-bottom: 20px;">
              <h2 style="margin: 0;">Medicine Issue History (Audit Trail)</h2>
              <div style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
                  <!-- Filter Buttons -->
                  <div style="display: inline-flex; border: 1px solid var(--border); border-radius: 6px; overflow: hidden; background: var(--card-bg); height: 32px; align-items: center; box-sizing: border-box;">
                      <button class="filter-btn-stock" class:active={issueStockFilter === 'all'} on:click={() => issueStockFilter = 'all'} style="height: 100%;">
                          All Prescriptions
                      </button>
                      <button class="filter-btn-stock" style="border-left: 1px solid var(--border); border-right: 1px solid var(--border); height: 100%;" class:active={issueStockFilter === 'stock'} on:click={() => issueStockFilter = 'stock'}>
                          Prescribed from Stock
                      </button>
                      <button class="filter-btn-stock" class:active={issueStockFilter === 'non-stock'} on:click={() => issueStockFilter = 'non-stock'} style="height: 100%;">
                          Prescribed but not in Stock
                      </button>
                  </div>

                  <input type="text" id="issues-table-search" class="inline-search" bind:value={issueFilterQuery}
                      placeholder="🔍 Search by Medicine, Name or Mobile..." style="margin: 0; min-width: 250px; height: 32px; box-sizing: border-box; line-height: 32px;">
              </div>
          </div>
          <table>
              <thead>
                  <tr>
                      <th>Issue Date & Time</th>
                      <th>Item Name</th>
                      <th>Patient Name</th>
                      <th>Mobile Number</th>
                      <th>Issued Qty</th>
                      <th>Returned Qty</th>
                  </tr>
              </thead>
              <tbody id="issues-table">
                {#each filteredIssueRows as row}
                  <tr>
                      <td>{formatDateTimeIST(row.issue_date, true)}</td>
                      <td><strong>{row.item_name}</strong></td>
                      <td>{row.issued_to_name}</td>
                      <td>{row.issued_to_mobile}</td>
                      <td style="font-weight:bold; color:var(--primary);">{row.issued_qty}</td>
                      <td>
                        {#if row.returned_qty > 0}
                          <span style="font-weight:bold; color:var(--warn);">{row.returned_qty}</span><br>
                          <small style="color:var(--text-muted);">{formatDateTimeIST(row.return_date)}</small>
                        {:else}
                          <span style="color:var(--border);">--</span>
                        {/if}
                      </td>
                  </tr>
                {/each}
                {#if filteredIssueRows.length === 0}
                  <tr>
                    <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 30px;">
                      No stock issue transactions found.
                    </td>
                  </tr>
                {/if}
              </tbody>
          </table>
      </div>
    {/if}
</div>

<style>
  .filter-btn-stock {
    background: transparent;
    border: none;
    color: var(--text-muted);
    padding: 0 12px;
    font-size: 11px;
    font-family: 'Outfit', sans-serif;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
  .filter-btn-stock:hover {
    background: var(--bg);
    color: var(--text);
  }
  .filter-btn-stock.active {
    background: var(--primary);
    color: white;
  }
</style>
