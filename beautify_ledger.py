import re

with open('src/components/SuppliersTab.svelte', 'r') as f:
    content = f.read()

# Replace the entire showLedgerModal block
old_modal = re.search(r"\{\#if showLedgerModal \&\& currentLedgerSupplier\}.*?\{\/if\}", content, flags=re.DOTALL)

if old_modal:
    new_modal = """{#if showLedgerModal && currentLedgerSupplier}
  <div class="modal-overlay show" style="display: flex;">
    <div class="modal-card" style="background:var(--card-bg); width: 850px; max-width:95vw; max-height: 90vh; display: flex; flex-direction: column;">
      
      <!-- Header Section -->
      <div style="padding: 24px 24px 20px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; background: var(--bg-color); border-radius: 12px 12px 0 0;">
        <div>
          <h2 style="margin: 0; font-size: 20px; display: flex; align-items: center; gap: 10px;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--primary);"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
            {currentLedgerSupplier.name}
          </h2>
          <div style="font-size: 13px; color: var(--text-muted); margin-top: 6px;">
            GSTIN: {currentLedgerSupplier.gstin || 'N/A'} • Contact: {currentLedgerSupplier.contact || 'N/A'}
          </div>
        </div>
        
        <div style="text-align: right; background: var(--card-bg); padding: 12px 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid var(--border);">
          <div style="font-size: 12px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Total Outstanding</div>
          {#if currentLedgerSupplier.balance < 0}
            <div style="color: var(--danger); font-size: 22px; font-weight: 700;">₹{Math.abs(currentLedgerSupplier.balance).toFixed(2)}</div>
            <div style="font-size: 11px; color: var(--danger); opacity: 0.8;">You owe supplier</div>
          {:else if currentLedgerSupplier.balance > 0}
            <div style="color: var(--success); font-size: 22px; font-weight: 700;">₹{currentLedgerSupplier.balance.toFixed(2)}</div>
            <div style="font-size: 11px; color: var(--success); opacity: 0.8;">Advance paid</div>
          {:else}
            <div style="color: var(--text-muted); font-size: 22px; font-weight: 700;">₹0.00</div>
            <div style="font-size: 11px; color: var(--text-muted);">Fully Settled</div>
          {/if}
        </div>
      </div>

      <!-- Table Section -->
      <div style="padding: 24px; overflow-y: auto; flex-grow: 1;">
        {#if currentLedgerItems.length === 0}
          <div class="empty-state" style="padding: 40px; text-align: center; color: var(--text-muted);">
            <div style="font-size: 40px; margin-bottom: 16px;">📄</div>
            <h3 style="margin: 0 0 8px;">No Bills Found</h3>
            <p style="margin: 0; font-size: 14px;">Add a bill to start tracking the ledger for {currentLedgerSupplier.name}.</p>
          </div>
        {:else}
          <div style="border: 1px solid var(--border); border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
            <table class="data-table" style="width: 100%; border-collapse: collapse; background: var(--card-bg);">
              <thead>
                <tr style="background: var(--bg-color);">
                  <th style="padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--border); color: var(--text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Date</th>
                  <th style="padding: 12px 16px; text-align: left; border-bottom: 1px solid var(--border); color: var(--text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Remarks (Invoice)</th>
                  <th style="padding: 12px 16px; text-align: right; border-bottom: 1px solid var(--border); color: var(--text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Total Bill</th>
                  <th style="padding: 12px 16px; text-align: right; border-bottom: 1px solid var(--border); color: var(--text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Paid Upfront</th>
                  <th style="padding: 12px 16px; text-align: right; border-bottom: 1px solid var(--border); color: var(--text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Balance Pending</th>
                  <th style="padding: 12px 16px; text-align: center; border-bottom: 1px solid var(--border); color: var(--text-muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">Action</th>
                </tr>
              </thead>
              <tbody>
                {#each currentLedgerItems as item}
                  <tr style="transition: background 0.2s;" on:mouseover={(e) => e.currentTarget.style.background='var(--bg-color)'} on:mouseleave={(e) => e.currentTarget.style.background='transparent'}>
                    <td style="padding: 14px 16px; border-bottom: 1px solid var(--border); font-size: 14px;">{item.bill_date}</td>
                    <td style="padding: 14px 16px; border-bottom: 1px solid var(--border); font-size: 14px; font-weight: 500;">{item.remarks || '--'}</td>
                    <td style="padding: 14px 16px; border-bottom: 1px solid var(--border); text-align: right; font-size: 14px;">₹{parseFloat(item.bill_amount).toFixed(2)}</td>
                    <td style="padding: 14px 16px; border-bottom: 1px solid var(--border); text-align: right; font-size: 14px;">
                      {#if item.amount_paid > 0}
                        <span style="color: var(--success); font-weight: 500;">₹{parseFloat(item.amount_paid).toFixed(2)}</span>
                      {:else}
                        <span style="color: var(--text-muted);">₹0.00</span>
                      {/if}
                    </td>
                    <td style="padding: 14px 16px; border-bottom: 1px solid var(--border); text-align: right; font-size: 14px;">
                      {#if (item.bill_amount - item.amount_paid) > 0}
                        <span style="color: var(--danger); font-weight: 700; background: rgba(239, 68, 68, 0.1); padding: 4px 8px; border-radius: 4px;">₹{(item.bill_amount - item.amount_paid).toFixed(2)}</span>
                      {:else}
                        <span style="color: var(--success); font-weight: 600; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px;">✓ Settled</span>
                      {/if}
                    </td>
                    <td style="padding: 14px 16px; border-bottom: 1px solid var(--border); text-align: center;">
                      <div style="display: flex; gap: 6px; justify-content: center; align-items: center;">
                        {#if (item.bill_amount - item.amount_paid) > 0}
                          <button class="btn-primary" style="padding: 6px 12px; font-size: 12px; border-radius: 6px; font-weight: 600; box-shadow: 0 2px 4px rgba(59, 130, 246, 0.2);" on:click={() => openPayBillModal(item)}>Pay</button>
                        {/if}
                        <button class="btn-secondary" style="padding: 6px 10px; font-size: 14px; border-radius: 6px; color: var(--danger); border-color: transparent; background: transparent;" title="Delete Bill" on:click={() => deleteBill(item.id)}>🗑️</button>
                      </div>
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {/if}
      </div>

      <!-- Footer Section -->
      <div style="padding: 16px 24px; border-top: 1px solid var(--border); display: flex; justify-content: flex-end; background: var(--bg-color); border-radius: 0 0 12px 12px;">
        <button class="btn-secondary" style="padding: 8px 24px; font-weight: 500;" on:click={() => showLedgerModal = false}>Close Ledger</button>
      </div>

    </div>
  </div>
{/if}"""
    content = content.replace(old_modal.group(0), new_modal)

    with open('src/components/SuppliersTab.svelte', 'w') as f:
        f.write(content)
    print("Ledger beautifully styled")
else:
    print("Could not find ledger modal block to replace")
