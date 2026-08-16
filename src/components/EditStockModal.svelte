<script lang="ts">
  import { editStockModalData, showToast, suppliersList } from '../store';

  let id = 0;
  let name = '';
  let category = 'Tablet';
  let batch = '';
  let pharmacy = '';
  let receivedDate = '';
  let expiry = '';
  let qty = 0;
  let unitPrice = 0;
  let mrp = 0;
  let sellingPrice = 0;
  let gstRate = 12.0;
  let supplierId = 0;
  let remarks = '';

  $: {
    if ($editStockModalData) {
      id = $editStockModalData.id;
      name = $editStockModalData.item_name || '';
      category = $editStockModalData.category || 'Tablet';
      batch = $editStockModalData.batch_no || '';
      pharmacy = $editStockModalData.pharmacy_name || '';
      receivedDate = $editStockModalData.received_date || '';
      expiry = $editStockModalData.expiry_date || '';
      qty = $editStockModalData.received_qty || 0;
      unitPrice = $editStockModalData.unit_price || 0;
      mrp = $editStockModalData.mrp || 0;
      sellingPrice = $editStockModalData.selling_price || 0;
      gstRate = $editStockModalData.gst_rate ?? 12.0;
      supplierId = $editStockModalData.supplier_id || 0;
      remarks = $editStockModalData.remarks || '';
    }
  }

  function closeEditStockModal() {
    editStockModalData.set(null);
  }

  function submitEditStock() {
    if (!name.trim()) {
      alert('Medicine name is required.');
      return;
    }
    if (isNaN(qty) || qty < 1) {
      alert('Received qty must be at least 1.');
      return;
    }
    const priceVal = parseFloat(unitPrice as any);
    if (isNaN(priceVal) || priceVal < 0) {
      alert('Buying price must be a valid non-negative number.');
      return;
    }
    const sellVal = parseFloat(sellingPrice as any);
    if (isNaN(sellVal) || sellVal < 0) {
      alert('Selling price must be a valid non-negative number.');
      return;
    }

    ipcRenderer.send('update-stock', {
      id,
      item_name: name.trim(),
      category: category,
      batch_no: batch.trim(),
      pharmacy_name: pharmacy.trim(),
      received_date: receivedDate,
      received_qty: qty,
      unit_price: priceVal || 0.0,
      mrp: parseFloat(mrp as any) || 0.0,
      selling_price: sellVal || 0.0,
      gst_rate: parseFloat(gstRate as any) || 12.0,
      supplier_id: supplierId || null,
      expiry_date: expiry,
      remarks: remarks.trim()
    });

    closeEditStockModal();
    showToast('Stock item updated successfully!');
  }
</script>

{#if $editStockModalData}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div id="edit-stock-modal" class="modal-overlay show" style="display: flex;">
      <div class="modal-card"
          style="background:var(--card-bg); border:1px solid var(--card-border); backdrop-filter:blur(10px); color:var(--text); max-width:600px; height:auto; max-height:90vh;">
          <div
              style="padding:15px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
              <h3 style="margin:0; font-family:'Outfit',sans-serif;">Edit Stock Item</h3>
              <button on:click={closeEditStockModal}
                  style="border:none; background:none; font-size:18px; cursor:pointer; color:var(--text);">✕</button>
          </div>
          <div style="padding:20px; display:flex; flex-direction:column; gap:14px; overflow-y:auto;">
              <div style="display:flex; gap:12px;">
                  <div class="form-group" style="flex:2.5; margin-bottom:0;">
                      <label for="edit-stock-name">Medicine / Item Name</label>
                      <input type="text" id="edit-stock-name" placeholder="e.g. Paracetamol 500mg" bind:value={name}>
                  </div>
                  <div class="form-group" style="flex:1; margin-bottom:0;">
                      <label for="edit-stock-category">Category</label>
                      <select id="edit-stock-category" bind:value={category} style="padding:8px 12px; border:1px solid var(--border); border-radius:4px; height: 35px;">
                          <option value="Tablet">Tablet</option>
                          <option value="Syrup">Syrup</option>
                          <option value="Powder">Powder</option>
                          <option value="Ointment/Gel">Ointment/Gel</option>
                          <option value="Injection Vial">Injection Vial</option>
                          <option value="Injection Ampule">Injection Ampule</option>
                      </select>
                  </div>
              </div>
              <div style="display:flex; gap:12px;">
                  <div class="form-group" style="flex:1; margin-bottom:0;">
                      <label for="edit-stock-batch">Batch No.</label>
                      <input type="text" id="edit-stock-batch" placeholder="Batch number" bind:value={batch}>
                  </div>
                  <div class="form-group" style="flex:1; margin-bottom:0;">
                      <label for="edit-stock-supplier">Distributor / Supplier</label>
                      <select id="edit-stock-supplier" bind:value={supplierId} style="padding:8px 12px; border:1px solid var(--border); border-radius:4px; height: 35px; width: 100%;">
                          <option value={0}>-- No Supplier --</option>
                          {#each $suppliersList as supplier}
                              <option value={supplier.id}>{supplier.name}</option>
                          {/each}
                      </select>
                  </div>
              </div>
              <div style="display:flex; gap:12px;">
                  <div class="form-group" style="flex:1; margin-bottom:0;">
                      <label for="edit-stock-received-date">Received Date</label>
                      <input type="date" id="edit-stock-received-date" bind:value={receivedDate}>
                  </div>
                  <div class="form-group" style="flex:1; margin-bottom:0;">
                      <label for="edit-stock-expiry">Expiry Date</label>
                      <input type="date" id="edit-stock-expiry" bind:value={expiry}>
                  </div>
              </div>
              <div style="display:flex; gap:12px;">
                  <div class="form-group" style="flex:1; margin-bottom:0;">
                      <label for="edit-stock-qty">Received Qty</label>
                      <input type="number" id="edit-stock-qty" min="1" bind:value={qty}>
                  </div>
                  <div class="form-group" style="flex:1; margin-bottom:0;">
                      <label for="edit-stock-price">Buying Price (₹)</label>
                      <input type="number" id="edit-stock-price" min="0" step="any" bind:value={unitPrice}>
                  </div>
                  <div class="form-group" style="flex:1; margin-bottom:0;">
                      <label for="edit-stock-selling">Selling Price (₹)</label>
                      <input type="number" id="edit-stock-selling" min="0" step="any" bind:value={sellingPrice}>
                  </div>
                  <div class="form-group" style="flex:1; margin-bottom:0;">
                      <label for="edit-stock-mrp">MRP (₹)</label>
                      <input type="number" id="edit-stock-mrp" min="0" step="any" bind:value={mrp}>
                  </div>
              </div>
              <div style="display:flex; gap:12px;">
                  <div class="form-group" style="flex:1; margin-bottom:0;">
                      <label for="edit-stock-gst">GST Rate (%)</label>
                      <select id="edit-stock-gst" bind:value={gstRate} style="padding:8px 12px; border:1px solid var(--border); border-radius:4px; height: 35px; width: 100%;">
                          <option value={0}>0%</option>
                          <option value={5}>5%</option>
                          <option value={12}>12%</option>
                          <option value={18}>18%</option>
                          <option value={28}>28%</option>
                      </select>
                  </div>
                  <div class="form-group" style="flex:2; margin-bottom:0;">
                      <label for="edit-stock-remarks">Remarks</label>
                      <input type="text" id="edit-stock-remarks" placeholder="Optional notes" bind:value={remarks}>
                  </div>
              </div>
              <p style="font-size:11px; color:var(--text-muted); margin:0;">⚠ Remaining qty will be recalculated as:
                  Received Qty − Already Issued Qty.</p>
          </div>
          <div
              style="padding:15px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; gap:10px;">
              <button class="btn-secondary" on:click={closeEditStockModal} style="padding:8px 18px;">Cancel</button>
              <button class="btn-primary" on:click={submitEditStock} style="padding:8px 18px;">Save Changes</button>
          </div>
      </div>
  </div>
{/if}
