<script lang="ts">
  import { expensesList, showToast } from '../store';

  let expenseDate = getTodayDate();
  let category = 'Tea/Coffee';
  let amount = '';
  let description = '';
  let paymentMethod = 'Cash';

  const categories = [
    'Tea/Coffee',
    'Food/Snacks',
    'Electricity',
    'Water',
    'Salary/Wages',
    'Maintenance',
    'Stationery',
    'Miscellaneous'
  ];

  function getTodayDate() {
    const today = new Date();
    return today.toISOString().split('T')[0];
  }

  function saveExpense() {
    if (!amount || isNaN(Number(amount)) || Number(amount) <= 0) {
      alert("Please enter a valid amount.");
      return;
    }

    const expense = {
      expense_date: expenseDate,
      category,
      amount: Number(amount),
      description,
      payment_method: paymentMethod
    };

    ipcRenderer.send('save-expense', expense);
    
    // Clear form after submission
    amount = '';
    description = '';
    category = 'Tea/Coffee';
    paymentMethod = 'Cash';
    
    showToast("Expense saved successfully!");
    
    // Re-fetch
    setTimeout(() => ipcRenderer.send('get-expenses'), 300);
  }

  function deleteExpense(id: number) {
    if (confirm("Are you sure you want to delete this expense record?")) {
      ipcRenderer.send('delete-expense', id);
      showToast("Expense deleted");
      setTimeout(() => ipcRenderer.send('get-expenses'), 300);
    }
  }

  $: totalExpenses = $expensesList.reduce((sum, exp) => sum + exp.amount, 0);

</script>

<div class="tab-content fade-in">
  <div class="header-container">
    <div>
      <h2>Daily Expenses</h2>
      <p class="subtitle">Track your shop's daily expenditures</p>
    </div>
  </div>

  <div class="split-layout">
    <!-- Left: Add Expense Form -->
    <div class="left-panel form-panel card" style="flex: 0.35;">
      <h3 style="margin-top:0; border-bottom: 1px solid var(--border); padding-bottom: 12px; margin-bottom: 20px;">Log New Expense</h3>
      
      <div class="form-group">
        <label>Date</label>
        <input type="date" bind:value={expenseDate}>
      </div>

      <div class="form-group">
        <label>Category</label>
        <select bind:value={category}>
          {#each categories as cat}
            <option value={cat}>{cat}</option>
          {/each}
        </select>
      </div>

      <div class="form-group">
        <label>Amount (₹)</label>
        <input type="number" bind:value={amount} placeholder="e.g. 50" min="1">
      </div>

      <div class="form-group">
        <label>Description (Optional)</label>
        <input type="text" bind:value={description} placeholder="e.g. Morning tea for staff">
      </div>

      <div class="form-group">
        <label>Payment Method</label>
        <select bind:value={paymentMethod}>
          <option value="Cash">Cash</option>
          <option value="UPI">UPI</option>
          <option value="Card">Card</option>
        </select>
      </div>

      <button class="primary-btn" on:click={saveExpense} style="width: 100%; margin-top: 10px; padding: 12px; font-size: 16px;">
        Save Expense
      </button>
    </div>

    <!-- Right: Expense List -->
    <div class="right-panel list-panel card" style="flex: 0.65; display: flex; flex-direction: column;">
      
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid var(--border); padding-bottom: 12px;">
        <h3 style="margin: 0;">Expense History</h3>
        <div style="background: var(--surface-bg); padding: 8px 16px; border-radius: 8px; border: 1px solid var(--border); font-weight: 600;">
          Total: <span style="color: var(--danger);">₹{totalExpenses.toFixed(2)}</span>
        </div>
      </div>

      <div class="table-container" style="flex: 1;">
        <table class="data-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Category</th>
              <th>Description</th>
              <th>Method</th>
              <th style="text-align: right;">Amount</th>
              <th style="text-align: center;">Actions</th>
            </tr>
          </thead>
          <tbody>
            {#if $expensesList.length === 0}
              <tr>
                <td colspan="6" style="text-align: center; padding: 40px; color: var(--text-muted);">
                  No expenses recorded yet.
                </td>
              </tr>
            {:else}
              {#each $expensesList as exp}
                <tr>
                  <td>{exp.expense_date}</td>
                  <td><span class="badge" style="background: var(--surface-bg); color: var(--text); border: 1px solid var(--border);">{exp.category}</span></td>
                  <td style="color: var(--text-muted);">{exp.description || '-'}</td>
                  <td>{exp.payment_method}</td>
                  <td style="text-align: right; font-weight: 600; color: var(--danger);">₹{exp.amount.toFixed(2)}</td>
                  <td style="text-align: center;">
                    <button class="icon-btn danger-btn" on:click={() => deleteExpense(exp.id)} title="Delete">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/>
                      </svg>
                    </button>
                  </td>
                </tr>
              {/each}
            {/if}
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<style>
  .split-layout {
    display: flex;
    gap: 24px;
    height: calc(100vh - 160px);
  }
  .card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    box-shadow: var(--shadow-sm);
  }
  .form-group {
    margin-bottom: 16px;
  }
  .form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: var(--text-muted);
  }
  .form-group input, .form-group select {
    width: 100%;
    padding: 10px 14px;
    border: 1px solid var(--border);
    border-radius: 8px;
    background: var(--surface-bg);
    color: var(--text);
  }
</style>
