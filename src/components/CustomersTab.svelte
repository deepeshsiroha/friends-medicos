<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { activeTab } from '../store';

  let customers: any[] = [];
  let searchQuery = '';
  let unsubscribes: (() => void)[] = [];

  const handleCustomersData = (event, res) => {
    if (res.success) {
      customers = res.rows || [];
    }
  };

  let unsubCustomers: (() => void);

  onMount(() => {
    ipcRenderer.send('get-customers');
    unsubCustomers = ipcRenderer.on('customers-data', handleCustomersData);
  });

  onDestroy(() => {
    if (unsubCustomers) unsubCustomers();
  });

  $: filteredCustomers = customers.filter(c => {
    if (!searchQuery) return true;
    const term = searchQuery.toLowerCase();
    return (c.name || '').toLowerCase().includes(term) || (c.mobile || '').toLowerCase().includes(term);
  });

  function formatDate(dateStr: string) {
    if (!dateStr) return '--';
    const d = new Date(dateStr);
    if (isNaN(d.getTime())) return dateStr;
    return d.toLocaleDateString('en-IN', { timeZone: 'Asia/Kolkata', day: '2-digit', month: '2-digit', year: 'numeric' });
  }
</script>

<div id="customers-tab" class="tab-content {$activeTab === 'customers' ? 'active' : ''}">
  <div class="table-header-controls" style="margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
    <div>
      <h2 style="margin: 0; font-family: 'Outfit', sans-serif;">Customer CRM Database</h2>
      <p style="color: var(--text-muted); font-size: 14px; margin-top: 5px;">Track your patient retention and total sales per customer.</p>
    </div>
    <div style="display: flex; gap: 10px; align-items: center;">
      <input type="text" placeholder="🔍 Search Name or Mobile..." bind:value={searchQuery} style="margin: 0; min-width: 250px;">
    </div>
  </div>

  <div class="card" style="padding: 20px;">
    {#if filteredCustomers.length === 0}
      <div style="text-align: center; color: var(--text-muted); padding: 40px;">No customers found. Generated bills will automatically add customers here.</div>
    {:else}
      <div style="max-height: calc(100vh - 250px); overflow-y: auto;">
        <table>
          <thead>
            <tr>
              <th>Mobile Number</th>
              <th>Customer Name</th>
              <th>Total Visits (Bills)</th>
              <th>Total Lifetime Spend</th>
              <th>First Visit</th>
              <th>Last Visit</th>
            </tr>
          </thead>
          <tbody>
            {#each filteredCustomers as cust}
              <tr>
                <td style="font-weight: 500;">{cust.mobile}</td>
                <td style="font-weight: bold; color: var(--primary);">{cust.name || '--'}</td>
                <td>{cust.total_visits}</td>
                <td style="font-weight: bold;">₹{parseFloat(cust.total_spent || '0').toFixed(2)}</td>
                <td>{formatDate(cust.created_at)}</td>
                <td>{formatDate(cust.last_visit)}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </div>
</div>
