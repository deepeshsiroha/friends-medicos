import re

with open('src/components/BillingTab.svelte', 'r') as f:
    content = f.read()

# Replace let y = 65; with let y = 69;
content = content.replace("let y = 65;", "let y = 69;")

with open('src/components/BillingTab.svelte', 'w') as f:
    f.write(content)

print("Fixed first row overlap")
