import re

with open('src/components/BillingTab.svelte', 'r') as f:
    content = f.read()

# 1. Add variable initialization
content = content.replace("let billTotal = 0;", "let billTotal = 0;\n  let billTotalCost = 0; // For user reference only")

# 2. Reset variable on form reset
content = content.replace("billTotal = 0;\n    billItems = [];", "billTotal = 0;\n    billTotalCost = 0;\n    billItems = [];")

# 3. Calculate the total cost inside calculateTotals()
old_calc_subtotal = """    billSubtotal = billItems.reduce((sum, item) => {
      item.total = item.qty * (parseFloat(item.unit_price) || 0);"""
new_calc_subtotal = """    billTotalCost = 0;
    billSubtotal = billItems.reduce((sum, item) => {
      item.total = item.qty * (parseFloat(item.unit_price) || 0);
      billTotalCost += item.qty * (parseFloat(item.buying_price) || 0);"""
content = content.replace(old_calc_subtotal, new_calc_subtotal)

# 4. Display the cost reference in the Bill Summary Card
old_summary_total = """                        <div
                            style="display: flex; justify-content: space-between; font-weight: bold; font-size: 14px; border-top: 1px solid var(--border); padding-top: 6px; color: var(--primary);">
                            <span>Total:</span>
                            <span id="bill-sum-total">₹{billTotal.toFixed(2)}</span>
                        </div>
                    </div>"""
new_summary_total = """                        <div
                            style="display: flex; justify-content: space-between; font-weight: bold; font-size: 14px; border-top: 1px solid var(--border); padding-top: 6px; color: var(--primary);">
                            <span>Total:</span>
                            <span id="bill-sum-total">₹{billTotal.toFixed(2)}</span>
                        </div>
                        <div style="font-size: 10px; color: var(--text-muted); text-align: right; margin-top: 4px; font-style: italic;">
                            (Est. Cost: ₹{billTotalCost.toFixed(2)})
                        </div>
                    </div>"""
content = content.replace(old_summary_total, new_summary_total)

with open('src/components/BillingTab.svelte', 'w') as f:
    f.write(content)
print("Added cost reference successfully.")
