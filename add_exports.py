import re

def add_export_to_svelte(filepath, module_name, search_anchor, replacement_string):
    with open(filepath, 'r') as f:
        content = f.read()

    # Add the function
    export_func = f"""  async function exportToCSV() {{
    const res = await ipcRenderer.invoke('export-csv', '{module_name}');
    if (res.success) {{
      showToast('Export saved successfully!');
    }} else if (!res.cancelled) {{
      alert('Export failed: ' + res.error);
    }}
  }}
"""
    if "function exportToCSV" not in content:
        content = content.replace("</script>", export_func + "</script>")

    # Add the button
    if "exportToCSV" in replacement_string and replacement_string not in content:
        content = content.replace(search_anchor, replacement_string)

    with open(filepath, 'w') as f:
        f.write(content)

# 1. InventoryTab
inv_anchor = """      <div class="search-box">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input type="text" placeholder="Search medicines by name or batch..." bind:value={searchQuery}>
      </div>"""
inv_replace = inv_anchor + """
      <button class="btn-primary" on:click={exportToCSV} style="background: var(--primary); padding: 8px 16px; font-size: 14px; margin-left: 10px;">
        Export CSV
      </button>"""
add_export_to_svelte('src/components/InventoryTab.svelte', 'inventory', inv_anchor, inv_replace)

# 2. BillingTab (History subtab)
bill_anchor = """      <div class="search-box" style="flex: 1;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input type="text" placeholder="Search by Invoice No, Name, or Mobile..." bind:value={historySearchQuery}>
      </div>"""
bill_replace = bill_anchor + """
      <button class="btn-primary" on:click={exportToCSV} style="background: var(--primary); padding: 8px 16px; font-size: 14px; margin-left: 10px;">
        Export CSV
      </button>"""
add_export_to_svelte('src/components/BillingTab.svelte', 'sales', bill_anchor, bill_replace)

# 3. ExpensesTab
exp_anchor = """      <div style="font-weight: 500; font-size: 15px; display: flex; gap: 20px;">
        <div>Cash Total: <span style="color:var(--success);">₹{expenseCashTotal.toFixed(2)}</span></div>
        <div>UPI Total: <span style="color:var(--success);">₹{expenseUpiTotal.toFixed(2)}</span></div>
      </div>"""
exp_replace = exp_anchor + """
      <button class="btn-primary" on:click={exportToCSV} style="background: var(--primary); padding: 8px 16px; font-size: 14px; margin-left: 10px;">
        Export CSV
      </button>"""
add_export_to_svelte('src/components/ExpensesTab.svelte', 'expenses', exp_anchor, exp_replace)

# 4. SuppliersTab
sup_anchor = """      <div class="search-box">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input type="text" placeholder="Search suppliers..." bind:value={supplierSearchQuery}>
      </div>"""
sup_replace = sup_anchor + """
      <button class="btn-primary" on:click={exportToCSV} style="background: var(--primary); padding: 8px 16px; font-size: 14px; margin-left: 10px;">
        Export CSV
      </button>"""
add_export_to_svelte('src/components/SuppliersTab.svelte', 'suppliers', sup_anchor, sup_replace)

print("Export buttons added to Svelte components.")
