import re

with open('src/components/SuppliersTab.svelte', 'r') as f:
    content = f.read()

# 1. Add Delete Supplier logic
old_logic = """  const handleSupplierSaved = (event, res) => {"""

new_logic = """  const handleSupplierDeleted = (event, res) => {
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

  const handleSupplierSaved = (event, res) => {"""

if "deleteSupplier(supplier)" not in content:
    content = content.replace(old_logic, new_logic)

# 2. Add unsubTrxDeleted (wait, we already did unsubTrxDeleted, let's add unsubSupplierDeleted)
content = content.replace("let unsubTrxDeleted: (() => void);", "let unsubTrxDeleted: (() => void);\n  let unsubSupplierDeleted: (() => void);")
content = content.replace("unsubTrxDeleted = window.ipcRenderer.on('supplier-transaction-deleted', handleTransactionDeleted);", "unsubTrxDeleted = window.ipcRenderer.on('supplier-transaction-deleted', handleTransactionDeleted);\n    unsubSupplierDeleted = window.ipcRenderer.on('supplier-deleted', handleSupplierDeleted);")
content = content.replace("if (unsubTrxDeleted) unsubTrxDeleted();", "if (unsubTrxDeleted) unsubTrxDeleted();\n    if (unsubSupplierDeleted) unsubSupplierDeleted();")

# 3. Add Delete Button to Supplier Table
old_btns = """                  <div style="display:flex; gap:8px;">
                    <button class="btn-primary" style="padding:6px 14px; font-size:12px;" on:click={() => openLedger(sup)}>View Ledger</button>
                    <button class="btn-secondary" style="padding:6px 14px; font-size:12px;" on:click={() => openAddModal(sup)}>Edit</button>
                  </div>"""

new_btns = """                  <div style="display:flex; gap:8px;">
                    <button class="btn-primary" style="padding:6px 14px; font-size:12px;" on:click={() => openLedger(sup)}>View Ledger</button>
                    <button class="btn-secondary" style="padding:6px 14px; font-size:12px;" on:click={() => openAddModal(sup)}>Edit</button>
                    <button class="btn-danger" style="padding:6px 14px; font-size:12px;" on:click={() => deleteSupplier(sup)}>Delete</button>
                  </div>"""

if old_btns in content:
    content = content.replace(old_btns, new_btns)
else:
    print("WARNING: Could not find old_btns to replace.")

with open('src/components/SuppliersTab.svelte', 'w') as f:
    f.write(content)

print("Done with frontend changes")
