import re

with open('src/components/SuppliersTab.svelte', 'r') as f:
    content = f.read()

# 1. Remove the restriction on amount paid when adding a bill
content = content.replace(
    'if (supplierAmountPaid < 0 || supplierAmountPaid > supplierBillAmount) return alert("Invalid amount paid");',
    'if (supplierAmountPaid < 0) return alert("Amount paid cannot be negative");'
)

# 2. Remove the restriction when paying a specific bill
content = content.replace(
    'if (payBillAmount <= 0 || payBillAmount > payBillMax) return alert("Invalid payment amount");',
    'if (payBillAmount <= 0) return alert("Invalid payment amount");'
)

# 3. Update the Suppliers Table Headers
old_headers = """              <th>ID</th>
              <th>Supplier Name</th>
              <th>Contact</th>
              <th>GSTIN</th>
              <th>Current Balance</th>
              <th>Actions</th>"""

new_headers = """              <th>ID</th>
              <th>Supplier Name</th>
              <th>Total Bill Amount</th>
              <th>Total Paid</th>
              <th>Balance to Pay</th>
              <th>Actions</th>"""
content = content.replace(old_headers, new_headers)

# 4. Update the Suppliers Table Rows
old_row = """                <td>#{sup.id}</td>
                <td style="font-weight: bold; color: var(--primary);">{sup.name}</td>
                <td>{sup.contact || '--'}</td>
                <td>{sup.gstin || '--'}</td>
                <td style="font-weight: bold; color: {sup.balance > 0 ? 'var(--success)' : (sup.balance < 0 ? 'var(--danger)' : 'var(--text)')};">
                  {sup.balance < 0 ? '-' : ''}₹{Math.abs(sup.balance || 0).toFixed(2)}
                </td>
                <td>"""

new_row = """                <td>#{sup.id}</td>
                <td style="font-weight: bold; color: var(--primary);">{sup.name}</td>
                <td style="color: var(--text-muted);">₹{parseFloat(sup.total_bill_amount || 0).toFixed(2)}</td>
                <td style="color: var(--text-muted);">₹{parseFloat(sup.total_amount_paid || 0).toFixed(2)}</td>
                <td style="font-weight: bold; color: {(sup.total_bill_amount - sup.total_amount_paid) > 0 ? 'red' : ((sup.total_bill_amount - sup.total_amount_paid) < 0 ? 'green' : 'black')};">
                  ₹{Math.abs((sup.total_bill_amount || 0) - (sup.total_amount_paid || 0)).toFixed(2)}
                  {#if (sup.total_bill_amount - sup.total_amount_paid) < 0}
                    <span style="font-size: 10px; font-weight: normal; margin-left: 4px;">(Advance)</span>
                  {/if}
                </td>
                <td>"""
content = content.replace(old_row, new_row)

# 5. Update the Ledger Table (Inner table per bill) to show advance color properly
old_ledger_balance = """                      {#if (item.bill_amount - item.amount_paid) > 0}
                        <span style="color: var(--danger); font-weight: 700; background: rgba(239, 68, 68, 0.1); padding: 4px 8px; border-radius: 4px;">₹{(item.bill_amount - item.amount_paid).toFixed(2)}</span>
                      {:else}
                        <span style="color: var(--success); font-weight: 700; background: rgba(16, 185, 129, 0.1); padding: 4px 8px; border-radius: 4px;">Settled</span>
                      {/if}"""

new_ledger_balance = """                      {#if (item.bill_amount - item.amount_paid) > 0}
                        <span style="color: red; font-weight: 700; background: rgba(239, 68, 68, 0.1); padding: 4px 8px; border-radius: 4px;">₹{(item.bill_amount - item.amount_paid).toFixed(2)}</span>
                      {:else if (item.bill_amount - item.amount_paid) < 0}
                        <span style="color: green; font-weight: 700; background: rgba(16, 185, 129, 0.1); padding: 4px 8px; border-radius: 4px;">+ ₹{Math.abs(item.bill_amount - item.amount_paid).toFixed(2)} (Advance)</span>
                      {:else}
                        <span style="color: black; font-weight: 700; background: rgba(0, 0, 0, 0.05); padding: 4px 8px; border-radius: 4px;">Settled (₹0)</span>
                      {/if}"""
content = content.replace(old_ledger_balance, new_ledger_balance)

with open('src/components/SuppliersTab.svelte', 'w') as f:
    f.write(content)
print("Updated SuppliersTab.svelte UI logic")
