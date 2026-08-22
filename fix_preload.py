import re

with open('preload.js', 'r') as f:
    content = f.read()

content = content.replace("'delete-supplier-transaction',", "'delete-supplier-bill',")
content = content.replace("'supplier-transaction-deleted',", "'supplier-bill-deleted',")

with open('preload.js', 'w') as f:
    f.write(content)

print("Preload updated")
