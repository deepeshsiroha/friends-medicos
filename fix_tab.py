import re

with open('src/components/SuppliersTab.svelte', 'r') as f:
    content = f.read()

content = content.replace("window.ipcRenderer.send('get-supplier-ledger', currentLedgerSupplier.id);", "window.ipcRenderer.send('get-supplier-bills', currentLedgerSupplier.id);")

with open('src/components/SuppliersTab.svelte', 'w') as f:
    f.write(content)

print("Fixed get-supplier-ledger calls")
