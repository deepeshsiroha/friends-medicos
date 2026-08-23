import re

with open('src/components/BillingTab.svelte', 'r') as f:
    content = f.read()

# Replace y += 6; with y += 8; inside the item loop
content = content.replace("y += 6;\n    });", "y += 8;\n    });")

with open('src/components/BillingTab.svelte', 'w') as f:
    f.write(content)
print("Fixed row overlap")
