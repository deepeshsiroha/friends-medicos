<script lang="ts">
  import { onDestroy, onMount } from 'svelte';
  import { Chart } from 'chart.js/auto';
  import { analyticsData } from '../store';

  let revenueCanvas: HTMLCanvasElement;
  let medicinesCanvas: HTMLCanvasElement;

  let revenueChart: Chart | null = null;
  let medicinesChart: Chart | null = null;

  let trendMode: 'weekly' | 'monthly' = 'weekly';

  // Watch analyticsData and trendMode changes to render/update charts
  $: if ($analyticsData && trendMode && (revenueCanvas || medicinesCanvas)) {
    setTimeout(renderCharts, 50); // slight delay to ensure canvases are in DOM
  }

  function renderCharts() {
    if (!$analyticsData) return;

    // 1. Revenue Trend Chart
    if (revenueCanvas) {
      if (revenueChart) {
        revenueChart.destroy();
      }

      let labels: string[] = [];
      let data: number[] = [];
      
      if (trendMode === 'weekly') {
        const weekly = $analyticsData.weeklyRevenue || [];
        labels = weekly.map((d: any) => d.day);
        data = weekly.map((d: any) => d.total);
      } else {
        const monthly = $analyticsData.monthlyRevenue || [];
        labels = monthly.map((d: any) => d.month);
        data = monthly.map((d: any) => d.total);
      }

      revenueChart = new Chart(revenueCanvas, {
        type: 'line',
        data: {
          labels,
          datasets: [{
            label: 'Paid Revenue (₹)',
            data,
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 2,
            tension: 0.3,
            fill: true
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                callback: (val) => '₹' + val
              }
            }
          }
        }
      });
    }

    // 2. Top Dispensed Medicines Chart
    if (medicinesCanvas) {
      if (medicinesChart) {
        medicinesChart.destroy();
      }

      const medicines = $analyticsData.topMedicines || [];
      const labels = medicines.map((m: any) => m.item_name);
      const data = medicines.map((m: any) => m.total_issued);

      medicinesChart = new Chart(medicinesCanvas, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Units Dispensed',
            data,
            backgroundColor: '#10b981',
            borderRadius: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            y: { beginAtZero: true }
          }
        }
      });
    }
  }

  function getExpiryBadgeClass(expiryDate: string | undefined) {
    if (!expiryDate) return 'badge-success';
    const today = new Date();
    today.setHours(0,0,0,0);
    const ninetyDaysLater = new Date(today.getTime() + 90 * 24 * 60 * 60 * 1000);
    const expiry = new Date(expiryDate);
    
    if (expiry < today) {
      return 'badge-danger';
    } else if (expiry <= ninetyDaysLater) {
      return 'badge-warn';
    }
    return 'badge-success';
  }

  function getExpiryLabel(expiryDate: string | undefined) {
    if (!expiryDate) return 'Active';
    const today = new Date();
    today.setHours(0,0,0,0);
    const ninetyDaysLater = new Date(today.getTime() + 90 * 24 * 60 * 60 * 1000);
    const expiry = new Date(expiryDate);
    
    if (expiry < today) {
      return 'Expired';
    } else if (expiry <= ninetyDaysLater) {
      return 'Expiring';
    }
    return 'Active';
  }

  onMount(() => {
    ipcRenderer.send('get-analytics-data');
  });

  onDestroy(() => {
    if (revenueChart) revenueChart.destroy();
    if (medicinesChart) medicinesChart.destroy();
  });
</script>

<div id="analytics-tab" class="tab-content active" style="overflow-y: auto; padding-bottom: 40px; height: 100%; box-sizing: border-box;">
    {#if !$analyticsData}
      <div style="display:flex; justify-content:center; align-items:center; height:300px; color:var(--text-muted);">
          <h3>Loading detailed dashboard analytics...</h3>
      </div>
    {:else}
      <!-- Summary KPIs Grid (6 cards for detailed metrics) -->
      <div class="kpi-grid">
          <div class="card kpi-card">
              <div class="kpi-label">TODAY'S COLLECTIONS</div>
              <div class="kpi-value" style="color: var(--success);">
                  ₹{($analyticsData.todayRevenue || 0).toFixed(2)}
              </div>
              <div class="kpi-subtext">Paid receipts today</div>
          </div>
          <div class="card kpi-card">
              <div class="kpi-label">THIS MONTH'S REVENUE</div>
              <div class="kpi-value" style="color: var(--primary);">
                  ₹{($analyticsData.thisMonthRevenue || 0).toFixed(2)}
              </div>
              <div class="kpi-subtext">Total collection this month</div>
          </div>
          <div class="card kpi-card">
              <div class="kpi-label">ALL-TIME REVENUE</div>
              <div class="kpi-value" style="color: #6366f1;">
                  ₹{($analyticsData.allTimeRevenue || 0).toFixed(2)}
              </div>
              <div class="kpi-subtext">Total historical collection</div>
          </div>
          <div class="card kpi-card">
              <div class="kpi-label">OUTSTANDING DUES</div>
              <div class="kpi-value" style="color: var(--warn);">
                  ₹{($analyticsData.unpaidTotal || 0).toFixed(2)}
              </div>
              <div class="kpi-subtext">{($analyticsData.unpaidCount || 0)} bills currently unpaid</div>
          </div>
          <div class="card kpi-card">
              <div class="kpi-label">UNIQUE CUSTOMERS</div>
              <div class="kpi-value" style="color: #a855f7;">
                  {($analyticsData.uniquePatients || 0)}
              </div>
              <div class="kpi-subtext">Total unique customers</div>
          </div>
          <div class="card kpi-card">
              <div class="kpi-label">AVG BILL VALUE (AOV)</div>
              <div class="kpi-value" style="color: #ec4899;">
                  ₹{($analyticsData.avgBillValue || 0).toFixed(2)}
              </div>
              <div class="kpi-subtext">Average paid transaction value</div>
          </div>
      </div>

      <!-- Charts Grid -->
      <div class="charts-grid" style="margin-top: 25px;">
          
          <!-- 1. Revenue Trends & Detail Table -->
          <div class="card chart-card" style="grid-column: span 3;">
              <div class="chart-header">
                  <h3>Revenue Trends</h3>
                  <div class="toggle-buttons">
                      <button class:active={trendMode === 'weekly'} on:click={() => trendMode = 'weekly'}>7 Days</button>
                      <button class:active={trendMode === 'monthly'} on:click={() => trendMode = 'monthly'}>6 Months</button>
                  </div>
              </div>
              <div class="chart-container" style="height: 220px;">
                  <canvas bind:this={revenueCanvas} id="revenue-chart-canvas"></canvas>
              </div>

              <!-- Revenue breakdown ledger -->
              <div style="margin-top: 20px; border-top: 1px solid var(--border); padding-top: 15px;">
                  <h4 style="font-size: 13px; font-weight: 600; color: var(--text-muted); margin: 0 0 10px 0;">Revenue Detail Ledger</h4>
                  <div style="max-height: 150px; overflow-y: auto;">
                      <table style="width: 100%; border-collapse: collapse; font-size: 12px;">
                          <thead>
                              <tr style="border-bottom: 2px solid var(--border); color: var(--text-muted); text-align: left;">
                                  <th style="padding: 6px 0;">Period</th>
                                  <th style="padding: 6px 0; text-align: center;">Transactions</th>
                                  <th style="padding: 6px 0; text-align: right;">Total Paid</th>
                              </tr>
                          </thead>
                          <tbody>
                              {#if trendMode === 'weekly'}
                                {#each ($analyticsData.weeklyRevenue || []).slice().reverse() as entry}
                                  <tr style="border-bottom: 1px dashed var(--border);">
                                      <td style="padding: 8px 0; font-weight: 500;">{entry.day}</td>
                                      <td style="padding: 8px 0; text-align: center;">{entry.count}</td>
                                      <td style="padding: 8px 0; text-align: right; font-weight: bold; color: var(--success);">₹{entry.total.toFixed(2)}</td>
                                  </tr>
                                {/each}
                              {:else}
                                {#each ($analyticsData.monthlyRevenue || []).slice().reverse() as entry}
                                  <tr style="border-bottom: 1px dashed var(--border);">
                                      <td style="padding: 8px 0; font-weight: 500;">{entry.month}</td>
                                      <td style="padding: 8px 0; text-align: center;">{entry.count}</td>
                                      <td style="padding: 8px 0; text-align: right; font-weight: bold; color: var(--success);">₹{entry.total.toFixed(2)}</td>
                                  </tr>
                                {/each}
                              {/if}
                          </tbody>
                      </table>
                  </div>
              </div>
          </div>



          <!-- 3. Top Moving Medicines -->
          <div class="card chart-card" style="grid-column: span 3;">
              <div class="chart-header">
                  <h3>Top Moving Medicines</h3>
              </div>
              <div class="chart-container" style="height: 240px;">
                  <canvas bind:this={medicinesCanvas} id="medicines-chart-canvas"></canvas>
              </div>
          </div>

          <!-- 4. Inventory Stock Quantity with details and progress bar -->
          <div class="card chart-card" style="grid-column: span 3; overflow-x: auto;">
              <div class="chart-header">
                  <h3>Top Stock Quantities</h3>
              </div>
              <div style="padding-top: 5px;">
                  <table style="width: 100%; border-collapse: collapse; text-align: left; min-width: 600px;">
                      <thead>
                          <tr style="border-bottom: 2px solid var(--border); color: var(--text-muted); font-size: 11px; text-transform: uppercase;">
                              <th style="padding: 10px 8px;">Medicine</th>
                              <th style="padding: 10px 8px;">Category</th>
                              <th style="padding: 10px 8px;">Batch No</th>
                              <th style="padding: 10px 8px;">Expiry</th>
                              <th style="padding: 10px 8px;">Status</th>
                              <th style="padding: 10px 8px; text-align: right;">Remaining Qty</th>
                              <th style="padding: 10px 8px; text-align: center; width: 140px;">Stock Level</th>
                          </tr>
                      </thead>
                      <tbody>
                          {#each ($analyticsData.topStock || []) as item}
                            <tr style="border-bottom: 1px solid var(--border); font-size: 13px;">
                                <td style="padding: 12px 8px; font-weight: 600; color: var(--text);">{item.item_name}</td>
                                <td style="padding: 12px 8px; color: var(--text-muted); font-size: 12px;">{item.category || 'Tablet'}</td>
                                <td style="padding: 12px 8px; font-family: monospace; font-size: 12px; color: var(--text-muted);">{item.batch_no || '--'}</td>
                                <td style="padding: 12px 8px; font-size: 12px;">{item.expiry_date || '--'}</td>
                                <td style="padding: 12px 8px;">
                                    <span class="badge {getExpiryBadgeClass(item.expiry_date)}">
                                        {getExpiryLabel(item.expiry_date)}
                                    </span>
                                </td>
                                <td style="padding: 12px 8px; text-align: right; font-weight: bold; color: var(--primary);">
                                    {item.remaining_qty} <span style="font-size:10px; font-weight:normal; color:var(--text-muted);">/ {item.received_qty}</span>
                                </td>
                                <td style="padding: 12px 8px; text-align: center;">
                                    <div class="progress-bg">
                                        <div class="progress-bar" style="width: {Math.min(100, Math.round((item.remaining_qty / (item.received_qty || 1)) * 100))}%"></div>
                                    </div>
                                </td>
                            </tr>
                          {/each}
                          {#if ($analyticsData.topStock || []).length === 0}
                            <tr>
                                <td colspan="7" style="text-align: center; color: var(--text-muted); padding: 30px;">No stock currently registered in the database.</td>
                            </tr>
                          {/if}
                      </tbody>
                  </table>
              </div>
          </div>
      </div>
    {/if}
</div>

<style>
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
  }
  .kpi-card {
    display: flex;
    flex-direction: column;
    padding: 18px 20px;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    background: var(--card-bg);
    border: 1px solid var(--border);
  }
  .kpi-label {
    font-size: 9px;
    font-weight: 700;
    color: var(--text-muted);
    letter-spacing: 1px;
    margin-bottom: 8px;
  }
  .kpi-value {
    font-size: 24px;
    font-weight: 800;
    font-family: 'Outfit', sans-serif;
    margin-bottom: 4px;
  }
  .kpi-subtext {
    font-size: 11px;
    color: var(--text-muted);
  }

  .charts-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px;
  }
  .chart-card {
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    background: var(--card-bg);
    border: 1px solid var(--border);
    display: flex;
    flex-direction: column;
  }
  .chart-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
  }
  .chart-header h3 {
    margin: 0;
    font-family: 'Outfit', sans-serif;
    font-size: 16px;
    font-weight: 600;
    color: var(--text);
  }
  .chart-container {
    position: relative;
    width: 100%;
  }

  .toggle-buttons {
    display: inline-flex;
    border: 1px solid var(--border);
    border-radius: 6px;
    overflow: hidden;
    background: var(--bg);
  }
  .toggle-buttons button {
    background: transparent;
    border: none;
    padding: 6px 12px;
    font-size: 11px;
    font-family: 'Outfit', sans-serif;
    font-weight: 500;
    color: var(--text-muted);
    cursor: pointer;
    transition: all 0.2s ease;
  }
  .toggle-buttons button.active {
    background: var(--primary);
    color: white;
  }
  .toggle-buttons button:hover:not(.active) {
    background: rgba(0,0,0,0.05);
  }

  /* Progress Bar Styles */
  .progress-bg {
    background: var(--border);
    border-radius: 4px;
    height: 8px;
    width: 100px;
    overflow: hidden;
    display: inline-block;
    vertical-align: middle;
  }
  .progress-bar {
    background: var(--primary);
    height: 100%;
    border-radius: 4px;
  }

  /* Expiry Status Badges */
  .badge {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 9px;
    font-weight: 700;
    text-transform: uppercase;
    display: inline-block;
  }
  .badge-danger {
    background: rgba(239, 68, 68, 0.15);
    color: #ef4444;
  }
  .badge-warn {
    background: rgba(245, 158, 11, 0.15);
    color: #f59e0b;
  }
  .badge-success {
    background: rgba(16, 185, 129, 0.15);
    color: #10b981;
  }
</style>
