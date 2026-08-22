import re

with open('src/components/SuppliersTab.svelte', 'r') as f:
    content = f.read()

# 1. Remove openPaymentModal
content = re.sub(r"  function openPaymentModal\(supplier\) \{.*?\}", "", content, flags=re.DOTALL)
content = content.replace("let showPaymentModal = false;", "")
content = content.replace("let paymentSupplierId = null;", "")
content = content.replace("let paymentSupplierName = '';", "")
content = content.replace("let paymentAmount = '';", "")
content = re.sub(r"  const savePayment = \(\) => \{.*?\}", "", content, flags=re.DOTALL)
content = re.sub(r"\{\#if showPaymentModal\}.*?\{\/if\}", "", content, flags=re.DOTALL)

# 2. Update openLedger and deleteTransaction
old_open_ledger = """  function openLedger(supplier) {
    currentLedgerSupplier = supplier;
    window.ipcRenderer.send('get-supplier-ledger', supplier.id);
  }"""

new_open_ledger = """  function openLedger(supplier) {
    currentLedgerSupplier = supplier;
    window.ipcRenderer.send('get-supplier-bills', supplier.id);
  }"""
content = content.replace(old_open_ledger, new_open_ledger)

old_delete = """  function deleteTransaction(id) {
    if (confirm('Are you sure you want to delete this ledger entry?')) {
      window.ipcRenderer.send('delete-supplier-transaction', id);
    }
  }"""

new_delete = """  function deleteBill(id) {
    if (confirm('Are you sure you want to delete this Bill?')) {
      window.ipcRenderer.send('delete-supplier-bill', id);
    }
  }"""
content = content.replace(old_delete, new_delete)

# 3. Handle data channels
content = content.replace("'supplier-ledger-data'", "'supplier-bills-data'")
content = content.replace("'supplier-transaction-deleted'", "'supplier-bill-deleted'")

# Replace handleSupplierLedgerData entirely
old_handle_data = re.search(r"  const handleSupplierLedgerData = \(event, res\) => \{.*?\};", content, flags=re.DOTALL)
if old_handle_data:
    new_handle_data = """  const handleSupplierBillsData = (event, res) => {
    if (res.success) {
      currentLedgerItems = res.rows;
      showLedgerModal = true;
    } else {
      alert('Error fetching bills: ' + res.error);
    }
  };"""
    content = content.replace(old_handle_data.group(0), new_handle_data)
    content = content.replace("handleSupplierLedgerData", "handleSupplierBillsData")

# Replace handleTransactionDeleted
old_handle_del = re.search(r"  const handleTransactionDeleted = \(event, res\) => \{.*?\};", content, flags=re.DOTALL)
if old_handle_del:
    new_handle_del = """  const handleBillDeleted = (event, res) => {
    if (res.success) {
      showToast('Bill deleted successfully');
      window.ipcRenderer.send('get-suppliers');
      if (showLedgerModal && currentLedgerSupplier) {
        window.ipcRenderer.send('get-supplier-bills', currentLedgerSupplier.id);
      }
    } else {
      alert('Error deleting bill: ' + res.error);
    }
  };"""
    content = content.replace(old_handle_del.group(0), new_handle_del)
    content = content.replace("handleTransactionDeleted", "handleBillDeleted")

# 4. Update the Ledger Table UI
old_table = re.search(r"<table class=\"data-table\">.*?</table>", content, flags=re.DOTALL)
if old_table:
    new_table = """<table class="data-table">
              <tr>
                <th style="padding: 10px; text-align: left; border-bottom: 1px solid var(--border);">Date</th>
                <th style="padding: 10px; text-align: left; border-bottom: 1px solid var(--border);">Remarks (Invoice)</th>
                <th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border);">Total Bill</th>
                <th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border);">Paid Upfront</th>
                <th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border);">Balance Pending</th>
                <th style="padding: 10px; text-align: center; border-bottom: 1px solid var(--border);">Action</th>
              </tr>
              {#each currentLedgerItems as item}
                <tr>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border);">{item.bill_date}</td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border);">{item.remarks || '--'}</td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: right; color: var(--danger); font-weight: bold;">₹{parseFloat(item.bill_amount).toFixed(2)}</td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: right; color: var(--success);">₹{parseFloat(item.amount_paid).toFixed(2)}</td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: right;">
                    {#if (item.bill_amount - item.amount_paid) > 0}
                      <span style="color: var(--danger); font-weight: bold;">₹{(item.bill_amount - item.amount_paid).toFixed(2)}</span>
                    {:else}
                      <span style="color: var(--success); font-weight: bold;">Settled</span>
                    {/if}
                  </td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: center; display: flex; gap: 8px; justify-content: center;">
                    {#if (item.bill_amount - item.amount_paid) > 0}
                      <button class="btn-primary" style="padding: 4px 10px; font-size: 11px;" on:click={() => openPayBillModal(item)}>Pay</button>
                    {/if}
                    <button class="btn-danger" style="padding: 4px 8px; font-size: 11px;" title="Delete Bill" on:click={() => deleteBill(item.id)}>🗑️</button>
                  </td>
                </tr>
              {/each}
            </table>"""
    content = content.replace(old_table.group(0), new_table)

# Remove "Add Payment" button from the main list actions
content = re.sub(r"<button class=\"btn-success\" style=\"padding:6px 14px; font-size:12px;\" on:click=\{\(\) => openPaymentModal\(sup\)\}>Add Payment</button>", "", content)

# Remove "Add Open Payment" from empty state
content = re.sub(r"<button class=\"btn-success\" on:click=\{\(\) => openPaymentModal\(sup\)\}>Add Open Payment</button>", "", content)

with open('src/components/SuppliersTab.svelte', 'w') as f:
    f.write(content)

print("SuppliersTab UI refactored to Invoice model")
