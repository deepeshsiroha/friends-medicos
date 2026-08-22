import re

with open('src/components/SuppliersTab.svelte', 'r') as f:
    content = f.read()

# Replace the Footer Section to include + Add Bill
old_footer = """      <!-- Footer Section -->
      <div style="padding: 16px 24px; border-top: 1px solid var(--border); display: flex; justify-content: flex-end; background: var(--bg-color); border-radius: 0 0 12px 12px;">
        <button class="btn-secondary" style="padding: 8px 24px; font-weight: 500;" on:click={() => showLedgerModal = false}>Close Ledger</button>
      </div>"""

new_footer = """      <!-- Footer Section -->
      <div style="padding: 16px 24px; border-top: 1px solid var(--border); display: flex; justify-content: space-between; background: var(--bg-color); border-radius: 0 0 12px 12px;">
        <button class="btn-primary" style="padding: 8px 24px; font-weight: 500;" on:click={() => openAddBillModal(currentLedgerSupplier)}>+ Add Bill</button>
        <button class="btn-secondary" style="padding: 8px 24px; font-weight: 500;" on:click={() => showLedgerModal = false}>Close Ledger</button>
      </div>"""

content = content.replace(old_footer, new_footer)

with open('src/components/SuppliersTab.svelte', 'w') as f:
    f.write(content)

print("Added Add Bill button")
