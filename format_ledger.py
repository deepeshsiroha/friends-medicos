import re

with open('src/components/SuppliersTab.svelte', 'r') as f:
    content = f.read()

# 1. Update the Header Balance Display
old_header = """          <div style="font-size: 14px; color: var(--text-muted); margin-top: 4px;">Balance: 
            <strong style="color: {currentLedgerSupplier.balance > 0 ? 'var(--success)' : (currentLedgerSupplier.balance < 0 ? 'var(--danger)' : 'var(--text)')};">
              {currentLedgerSupplier.balance < 0 ? '-' : ''}₹{Math.abs(currentLedgerSupplier.balance || 0).toFixed(2)}
            </strong>
          </div>"""

new_header = """          <div style="font-size: 14px; margin-top: 4px;">
            {#if currentLedgerSupplier.balance < 0}
              <span style="color: var(--danger); font-weight: bold;">You Owe: ₹{Math.abs(currentLedgerSupplier.balance).toFixed(2)}</span>
            {:else if currentLedgerSupplier.balance > 0}
              <span style="color: var(--success); font-weight: bold;">Advance Paid: ₹{currentLedgerSupplier.balance.toFixed(2)}</span>
            {:else}
              <span style="color: var(--text-muted); font-weight: bold;">Settled (₹0)</span>
            {/if}
          </div>"""

content = content.replace(old_header, new_header)

# 2. Update Table Headers
old_thead = """              <tr>
                <th style="padding: 10px; text-align: left; border-bottom: 1px solid var(--border);">Date</th>
                <th style="padding: 10px; text-align: left; border-bottom: 1px solid var(--border);">Type</th>
                <th style="padding: 10px; text-align: left; border-bottom: 1px solid var(--border);">Remarks</th>
                <th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border);">Debit (Bill)</th>
                <th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border);">Credit (Paid)</th>
                <th style="padding: 10px; text-align: center; border-bottom: 1px solid var(--border);">Action</th>
              </tr>"""

new_thead = """              <tr>
                <th style="padding: 10px; text-align: left; border-bottom: 1px solid var(--border);">Date</th>
                <th style="padding: 10px; text-align: left; border-bottom: 1px solid var(--border);">Description</th>
                <th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border);">Bill Amount</th>
                <th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border);">Payment Given</th>
                <th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border);">Running Balance</th>
                <th style="padding: 10px; text-align: center; border-bottom: 1px solid var(--border);">Action</th>
              </tr>"""

content = content.replace(old_thead, new_thead)

# 3. Update Table Body
# First, we need to calculate running balance. We can do this in the handleSupplierLedgerData function.
old_handle_ledger = """  const handleSupplierLedgerData = (event, res) => {
    if (res.success) {
      currentLedgerItems = res.rows;
      showLedgerModal = true;
    } else {"""

new_handle_ledger = """  const handleSupplierLedgerData = (event, res) => {
    if (res.success) {
      // Calculate running balance (rows are DESC by date/id)
      let items = res.rows.slice().reverse();
      let runBal = 0;
      items = items.map(item => {
        if (item.type === 'Bill') runBal -= item.amount;
        if (item.type === 'Payment') runBal += item.amount;
        item.running_balance = runBal;
        return item;
      });
      currentLedgerItems = items.reverse();
      showLedgerModal = true;
    } else {"""

content = content.replace(old_handle_ledger, new_handle_ledger)

# Update the rows to show running balance and remove Type column
old_tbody = """              {#each currentLedgerItems as item}
                <tr>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border);">{item.transaction_date}</td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border);">
                    {#if item.type === 'Bill'}
                      <span style="color: var(--danger); font-weight: bold;">Bill</span>
                    {:else}
                      <span style="color: var(--success); font-weight: bold;">Payment</span>
                    {/if}
                  </td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border);">{item.remarks || '--'}</td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: right; color: var(--danger);">
                    {#if item.type === 'Bill'}
                      ₹{parseFloat(item.amount).toFixed(2)}
                    {:else}
                      -
                    {/if}
                  </td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: right; color: var(--success);">
                    {#if item.type === 'Payment'}
                      ₹{parseFloat(item.amount).toFixed(2)}
                    {:else}
                      -
                    {/if}
                  </td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: center;">
                    <button class="btn-danger" style="padding: 4px 8px; font-size: 11px;" on:click={() => deleteTransaction(item.id)}>🗑️</button>
                  </td>
                </tr>
              {/each}"""

new_tbody = """              {#each currentLedgerItems as item}
                <tr>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border);">{item.transaction_date}</td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border);">
                    {#if item.type === 'Bill'}
                      <span style="color: var(--danger); font-weight: bold;">[Bill]</span> {item.remarks || '--'}
                    {:else}
                      <span style="color: var(--success); font-weight: bold;">[Payment]</span> {item.remarks || '--'}
                    {/if}
                  </td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: right; color: var(--danger);">
                    {#if item.type === 'Bill'}
                      ₹{parseFloat(item.amount).toFixed(2)}
                    {:else}
                      -
                    {/if}
                  </td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: right; color: var(--success);">
                    {#if item.type === 'Payment'}
                      ₹{parseFloat(item.amount).toFixed(2)}
                    {:else}
                      -
                    {/if}
                  </td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: right; font-weight: bold; color: {item.running_balance < 0 ? 'var(--danger)' : (item.running_balance > 0 ? 'var(--success)' : 'var(--text-muted)')};">
                    {#if item.running_balance < 0}
                      ₹{Math.abs(item.running_balance).toFixed(2)} (Owe)
                    {:else if item.running_balance > 0}
                      ₹{item.running_balance.toFixed(2)} (Adv)
                    {:else}
                      ₹0
                    {/if}
                  </td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: center;">
                    <button class="btn-danger" style="padding: 4px 8px; font-size: 11px;" on:click={() => deleteTransaction(item.id)}>🗑️</button>
                  </td>
                </tr>
              {/each}"""

content = content.replace(old_tbody, new_tbody)

with open('src/components/SuppliersTab.svelte', 'w') as f:
    f.write(content)

print("Ledger UI updated!")
