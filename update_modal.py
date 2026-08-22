import re

with open('src/components/SuppliersTab.svelte', 'r') as f:
    content = f.read()

old_modal = """{#if showLedgerModal}
  <div class="modal-overlay show" style="display: flex;">
    <div class="modal-card modal-lg" style="background:var(--card-bg);">
      <h3 style="margin-top:0;">Bill History - {viewBillsSupplierName}</h3>
      
      <div style="max-height: 400px; overflow-y: auto; margin-top: 15px;">
        {#if currentLedgerItems.length === 0}
          <div style="padding: 20px; text-align: center; color: var(--text-muted);">No bills found for this supplier.</div>
        {:else}
          <table style="width: 100%; border-collapse: collapse;">
            <thead style="background: var(--bg); position: sticky; top: 0;">
              <tr>
                <th style="padding: 10px; text-align: left; border-bottom: 1px solid var(--border);">Date</th>
                <th style="padding: 10px; text-align: left; border-bottom: 1px solid var(--border);">Remarks</th>
                <th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border);">Bill Amt</th>
                <th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border);">Paid</th>
                <th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border);">Pending</th>
                <th style="padding: 10px; text-align: center; border-bottom: 1px solid var(--border);">Status</th>
                <th style="padding: 10px; text-align: center; border-bottom: 1px solid var(--border);">Action</th>
              </tr>
            </thead>
            <tbody>
              {#each currentLedgerItems as bill}
                <tr>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border);">{bill.bill_date}</td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border);">{bill.remarks || '--'}</td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: right;">₹{parseFloat(bill.bill_amount).toFixed(2)}</td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: right;">₹{parseFloat(bill.amount_paid).toFixed(2)}</td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: right; font-weight: bold; color: var(--danger);">
                    ₹{parseFloat(bill.bill_amount - bill.amount_paid).toFixed(2)}
                  </td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: center;">
                    {#if bill.status === 'Paid'}
                      <span style="background: var(--success); color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px;">Paid</span>
                    {:else if bill.status === 'Partial'}
                      <span style="background: var(--primary); color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px;">Partial</span>
                    {:else}
                      <span style="background: var(--danger); color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px;">Pending</span>
                    {/if}
                  </td>
                  <td style="padding: 10px; border-bottom: 1px solid var(--border); text-align: center;">
                    {#if bill.status !== 'Paid'}
                      <button class="btn-primary" style="padding: 4px 8px; font-size: 11px;" on:click={() => openPayBillModal(bill)}>Pay</button>
                    {/if}
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        {/if}
      </div>
      
      <div style="margin-top: 20px; display: flex; justify-content: flex-end; gap: 10px;">
        <button class="btn-secondary" on:click={() => showLedgerModal = false}>Close</button>
      </div>
    </div>
  </div>
{/if}"""

new_modal = """{#if showLedgerModal && currentLedgerSupplier}
  <div class="modal-overlay show" style="display: flex;">
    <div class="modal-card modal-lg" style="background:var(--card-bg); width: 800px; max-width: 95%;">
      
      <!-- Ledger Header -->
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 15px; margin-bottom: 15px;">
        <div>
          <h3 style="margin: 0;">{currentLedgerSupplier.name} Ledger</h3>
          <div style="font-size: 14px; color: var(--text-muted); margin-top: 4px;">Balance: 
            <strong style="color: {currentLedgerSupplier.balance > 0 ? 'var(--success)' : (currentLedgerSupplier.balance < 0 ? 'var(--danger)' : 'var(--text)')};">
              {currentLedgerSupplier.balance < 0 ? '-' : ''}₹{Math.abs(currentLedgerSupplier.balance || 0).toFixed(2)}
            </strong>
          </div>
        </div>
        <div style="display: flex; gap: 10px;">
          <button class="btn-secondary" on:click={() => openPaymentModal(currentLedgerSupplier)}>+ Record Payment</button>
          <button class="btn-primary" on:click={() => openAddBillModal(currentLedgerSupplier)}>+ Add Bill</button>
        </div>
      </div>
      
      <div style="max-height: 400px; overflow-y: auto;">
        {#if currentLedgerItems.length === 0}
          <div style="padding: 20px; text-align: center; color: var(--text-muted);">No transactions found for this supplier.</div>
        {:else}
          <table style="width: 100%; border-collapse: collapse;">
            <thead style="background: var(--bg); position: sticky; top: 0;">
              <tr>
                <th style="padding: 10px; text-align: left; border-bottom: 1px solid var(--border);">Date</th>
                <th style="padding: 10px; text-align: left; border-bottom: 1px solid var(--border);">Type</th>
                <th style="padding: 10px; text-align: left; border-bottom: 1px solid var(--border);">Remarks</th>
                <th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border);">Debit (Bill)</th>
                <th style="padding: 10px; text-align: right; border-bottom: 1px solid var(--border);">Credit (Paid)</th>
              </tr>
            </thead>
            <tbody>
              {#each currentLedgerItems as item}
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
                </tr>
              {/each}
            </tbody>
          </table>
        {/if}
      </div>
      
      <div style="margin-top: 20px; display: flex; justify-content: flex-end;">
        <button class="btn-secondary" on:click={() => showLedgerModal = false}>Close</button>
      </div>
    </div>
  </div>
{/if}"""

if old_modal in content:
    content = content.replace(old_modal, new_modal)
    with open('src/components/SuppliersTab.svelte', 'w') as f:
        f.write(content)
    print("Success")
else:
    print("Could not find the exact old modal block. I will search for part of it.")
