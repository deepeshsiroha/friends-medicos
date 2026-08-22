import re

with open('src/components/SuppliersTab.svelte', 'r') as f:
    content = f.read()

footer = """      <!-- Footer Section -->
      <div style="padding: 16px 24px; border-top: 1px solid var(--border); display: flex; justify-content: flex-end; background: var(--bg-color); border-radius: 0 0 12px 12px;">
        <button class="btn-secondary" style="padding: 8px 24px; font-weight: 500;" on:click={() => showLedgerModal = false}>Close Ledger</button>
      </div>

    </div>
  </div>
{/if}

"""

content = content.replace("{#if showPayBillModal}", footer + "{#if showPayBillModal}")

with open('src/components/SuppliersTab.svelte', 'w') as f:
    f.write(content)

print("Fixed closing divs")
