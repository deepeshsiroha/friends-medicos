import re

def inject_svelte(filepath, module_name, header_regex, button_html):
    with open(filepath, 'r') as f:
        content = f.read()

    # Add function
    export_func = f"""
  async function exportToCSV() {{
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

    # Add button
    if "exportToCSV" not in content.split("</script>")[1]:
        content = re.sub(header_regex, r'\1' + button_html, content, count=1)
        
    with open(filepath, 'w') as f:
        f.write(content)


# 1. InventoryTab
# Find: <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
inv_regex = r'(<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">\s*<h2>Current Stock Ledger</h2>)'
inv_btn = """
                  <button class="btn-primary" on:click={exportToCSV} style="background: var(--primary); padding: 6px 12px; font-size: 13px; margin-left: auto;">
                    Export CSV
                  </button>"""
inject_svelte('src/components/InventoryTab.svelte', 'inventory', inv_regex, inv_btn)


# 2. BillingTab
# Find: <h2>Invoice History</h2>
bill_regex = r'(<h2>Invoice History</h2>)'
bill_btn = """
              <button class="btn-primary" on:click={exportToCSV} style="background: var(--primary); padding: 6px 12px; font-size: 13px; margin-left: auto;">
                Export CSV
              </button>"""
inject_svelte('src/components/BillingTab.svelte', 'sales', bill_regex, bill_btn)


# 3. ExpensesTab
# Find: <h2>Expense Log</h2>
exp_regex = r'(<h2>Expense Log</h2>)'
exp_btn = """
            <button class="btn-primary" on:click={exportToCSV} style="background: var(--primary); padding: 6px 12px; font-size: 13px; margin-left: auto;">
              Export CSV
            </button>"""
inject_svelte('src/components/ExpensesTab.svelte', 'expenses', exp_regex, exp_btn)


# 4. SuppliersTab
# Find: <h2>Supplier Ledger</h2>
sup_regex = r'(<h2>Supplier Ledger</h2>)'
sup_btn = """
            <button class="btn-primary" on:click={exportToCSV} style="background: var(--primary); padding: 6px 12px; font-size: 13px; margin-left: auto;">
              Export CSV
            </button>"""
inject_svelte('src/components/SuppliersTab.svelte', 'suppliers', sup_regex, sup_btn)

print("Injected buttons using regex.")
