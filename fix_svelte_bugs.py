import re

with open('src/components/SuppliersTab.svelte', 'r') as f:
    content = f.read()

# Fix delete-supplier-transaction
content = content.replace("window.ipcRenderer.send('delete-supplier-transaction', id);", "window.ipcRenderer.send('delete-supplier-bill', id);")

# Remove openPaymentModal button
content = re.sub(r'<button.*?openPaymentModal.*?</button>', '', content)

with open('src/components/SuppliersTab.svelte', 'w') as f:
    f.write(content)

print("Fixed UI bugs")
