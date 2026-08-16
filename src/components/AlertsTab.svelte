<script lang="ts">
  import { lowStockItems, nearExpiryItems, activeTab } from '../store';

  // Format date helper
  function formatDate(dateString: string) {
    if (!dateString) return '--';
    const d = new Date(dateString);
    return d.toLocaleDateString('en-IN', { timeZone: 'Asia/Kolkata', day: '2-digit', month: '2-digit', year: 'numeric' });
  }
</script>

<div id="alerts-tab" class="tab-content {$activeTab === 'alerts' ? 'active' : ''}">
  <div class="table-header-controls" style="margin-bottom: 20px;">
    <h2>Actionable Alerts & Warnings</h2>
    <p style="color: var(--text-muted); font-size: 14px; margin-top: 5px;">Manage stock that requires immediate attention.</p>
  </div>

  <div style="display: grid; grid-template-columns: 1fr; gap: 20px;">
    
    <!-- Low Stock Items Table -->
    <div class="card" style="padding: 20px;">
      <h3 style="color: var(--warn); margin-top: 0; margin-bottom: 15px; font-size: 16px;">
        ⚠️ Low Stock Items ({$lowStockItems.length})
      </h3>
      {#if $lowStockItems.length === 0}
        <div style="text-align: center; color: var(--text-muted); padding: 20px;">No low stock alerts.</div>
      {:else}
        <div style="max-height: 300px; overflow-y: auto;">
          <table>
            <thead>
              <tr>
                <th>Item Name</th>
                <th>Category</th>
                <th>Supplier</th>
                <th>Remaining Qty</th>
              </tr>
            </thead>
            <tbody>
              {#each $lowStockItems as item}
                <tr>
                  <td><strong>{item.item_name}</strong></td>
                  <td>{item.category || '--'}</td>
                  <td>{item.pharmacy_name || '--'}</td>
                  <td style="color: var(--warn); font-weight: bold;">{item.remaining_qty}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </div>

    <!-- Near Expiry Items Table -->
    <div class="card" style="padding: 20px;">
      <h3 style="color: var(--warn); margin-top: 0; margin-bottom: 15px; font-size: 16px;">
        ⏳ Near Expiry / Expired Items ({$nearExpiryItems.length})
      </h3>
      {#if $nearExpiryItems.length === 0}
        <div style="text-align: center; color: var(--text-muted); padding: 20px;">No expiry alerts.</div>
      {:else}
        <div style="max-height: 300px; overflow-y: auto;">
          <table>
            <thead>
              <tr>
                <th>Item Name</th>
                <th>Batch No.</th>
                <th>Expiry Date</th>
                <th>Remaining Qty</th>
              </tr>
            </thead>
            <tbody>
              {#each $nearExpiryItems as item}
                <tr>
                  <td><strong>{item.item_name}</strong></td>
                  <td>{item.batch_no || '--'}</td>
                  <td style="color: {new Date(item.expiry_date) < new Date() ? 'var(--warn)' : 'var(--primary)'}; font-weight: bold;">
                    {formatDate(item.expiry_date)}
                  </td>
                  <td>{item.remaining_qty}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </div>
  </div>
</div>
