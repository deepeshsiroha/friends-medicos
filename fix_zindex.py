import re

with open('src/components/SuppliersTab.svelte', 'r') as f:
    content = f.read()

content = content.replace('<div class="modal-overlay show" style="display: flex; z-index: 2000;">', '<div class="modal-overlay show" style="display: flex; z-index: 4000;">')

content = content.replace("""{#if showPayBillModal}
  <div class="modal-overlay show" style="display: flex;">
    <div class="modal-card" style="background:var(--card-bg); max-width:400px; z-index: 2000;">""", """{#if showPayBillModal}
  <div class="modal-overlay show" style="display: flex; z-index: 4000;">
    <div class="modal-card" style="background:var(--card-bg); max-width:400px;">""")

with open('src/components/SuppliersTab.svelte', 'w') as f:
    f.write(content)

print("z-index fixed")
