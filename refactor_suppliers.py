import re

with open('src/components/SuppliersTab.svelte', 'r') as f:
    content = f.read()

# 1. Variables
content = content.replace("let showBillsModal = false;", "let showLedgerModal = false;")
content = content.replace("let currentSupplierBills = [];", "let currentLedgerItems = [];\n  let currentLedgerSupplier = null;")
content = content.replace("let viewBillsSupplierName = '';", "")

# 2. Handlers
content = content.replace("""const handleSupplierBillsData = (event, res) => {
    if (res.success) {
      currentSupplierBills = res.rows;
      showBillsModal = true;
    } else {
      alert('Error: ' + res.error);
    }
  };""", """const handleSupplierLedgerData = (event, res) => {
    if (res.success) {
      currentLedgerItems = res.rows;
      showLedgerModal = true;
    } else {
      alert('Error: ' + res.error);
    }
  };""")

# 3. Add Ledger refresh to save actions
refresh_code = """      window.ipcRenderer.send('get-suppliers'); // Refresh
      if (showLedgerModal && currentLedgerSupplier) {
        window.ipcRenderer.send('get-supplier-ledger', currentLedgerSupplier.id);
      }"""
content = content.replace("window.ipcRenderer.send('get-suppliers'); // Refresh", refresh_code)

# 4. IPC bindings
content = content.replace("unsubBillsData: (() => void);", "unsubLedgerData: (() => void);")
content = content.replace("unsubBillsData = window.ipcRenderer.on('supplier-bills-data', handleSupplierBillsData);", "unsubLedgerData = window.ipcRenderer.on('supplier-ledger-data', handleSupplierLedgerData);")
content = content.replace("if (unsubBillsData) unsubBillsData();", "if (unsubLedgerData) unsubLedgerData();")

# 5. Functions
content = content.replace("""function viewBills(supplier) {
    billSupplierId = supplier.id;
    viewBillsSupplierName = supplier.name;
    window.ipcRenderer.send('get-supplier-bills', supplier.id);
  }""", """function openLedger(supplier) {
    currentLedgerSupplier = supplier;
    window.ipcRenderer.send('get-supplier-ledger', supplier.id);
  }""")

# 6. Table Buttons
table_buttons = """<div style="display:flex; gap:8px;">
                    <button class="btn-secondary" style="padding:4px 10px; font-size:12px;" on:click={() => openAddBillModal(sup)}>Add Bill</button>
                    <button class="btn-secondary" style="padding:4px 10px; font-size:12px;" on:click={() => viewBills(sup)}>View Bills</button>
                    <button class="btn-secondary" style="padding:4px 10px; font-size:12px;" on:click={() => openPaymentModal(sup)}>Add Open Payment</button>
                    <button class="btn-secondary" style="padding:4px 10px; font-size:12px;" on:click={() => openAddModal(sup)}>Edit</button>
                  </div>"""

new_table_buttons = """<div style="display:flex; gap:8px;">
                    <button class="btn-primary" style="padding:6px 14px; font-size:12px;" on:click={() => openLedger(sup)}>View Ledger</button>
                    <button class="btn-secondary" style="padding:6px 14px; font-size:12px;" on:click={() => openAddModal(sup)}>Edit</button>
                  </div>"""
content = content.replace(table_buttons, new_table_buttons)

with open('src/components/SuppliersTab.svelte', 'w') as f:
    f.write(content)
