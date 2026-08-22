import re

with open('src/components/SuppliersTab.svelte', 'r') as f:
    content = f.read()

# Add delete button to UI
old_td = """                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: right; color: var(--success);">
                    {#if item.type === 'Payment'}
                      ₹{parseFloat(item.amount).toFixed(2)}
                    {:else}
                      -
                    {/if}
                  </td>
                </tr>"""

new_td = """                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: right; color: var(--success);">
                    {#if item.type === 'Payment'}
                      ₹{parseFloat(item.amount).toFixed(2)}
                    {:else}
                      -
                    {/if}
                  </td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: center;">
                    <button class="btn-danger" style="padding: 4px 8px; font-size: 11px;" on:click={() => deleteTransaction(item.id)}>🗑️</button>
                  </td>
                </tr>"""

if old_td in content:
    content = content.replace(old_td, new_td)
else:
    print("Failed to find old td")

# Add header
old_th = """<th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border);">Credit (Paid)</th>"""
new_th = """<th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border);">Credit (Paid)</th>
                <th style="padding: 10px; text-align: center; border-bottom: 1px solid var(--border);">Action</th>"""

content = content.replace(old_th, new_th)

# Add logic
old_logic = """  const handleSupplierLedgerData = (event, res) => {"""

new_logic = """  const handleTransactionDeleted = (event, res) => {
    if (res.success) {
      showToast('Transaction deleted successfully!');
      window.ipcRenderer.send('get-suppliers'); // Refresh main balance
      if (showLedgerModal && currentLedgerSupplier) {
        window.ipcRenderer.send('get-supplier-ledger', currentLedgerSupplier.id);
      }
    } else {
      alert('Error: ' + res.error);
    }
  };

  function deleteTransaction(id) {
    if (confirm("Are you sure you want to delete this transaction? This will reverse its effect on your balance.")) {
      window.ipcRenderer.send('delete-supplier-transaction', id);
    }
  }

  const handleSupplierLedgerData = (event, res) => {"""

content = content.replace(old_logic, new_logic)

# Add to unsubscribes
content = content.replace("let unsubLedgerData: (() => void);", "let unsubLedgerData: (() => void);\n  let unsubTrxDeleted: (() => void);")
content = content.replace("unsubLedgerData = window.ipcRenderer.on('supplier-ledger-data', handleSupplierLedgerData);", "unsubLedgerData = window.ipcRenderer.on('supplier-ledger-data', handleSupplierLedgerData);\n    unsubTrxDeleted = window.ipcRenderer.on('supplier-transaction-deleted', handleTransactionDeleted);")
content = content.replace("if (unsubLedgerData) unsubLedgerData();", "if (unsubLedgerData) unsubLedgerData();\n    if (unsubTrxDeleted) unsubTrxDeleted();")

with open('src/components/SuppliersTab.svelte', 'w') as f:
    f.write(content)

print("Done")
