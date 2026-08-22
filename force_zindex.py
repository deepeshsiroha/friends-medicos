import re

with open('src/components/SuppliersTab.svelte', 'r') as f:
    content = f.read()

content = content.replace('z-index: 2000;', 'z-index: 4000;')

with open('src/components/SuppliersTab.svelte', 'w') as f:
    f.write(content)

print("z-index FORCED")
