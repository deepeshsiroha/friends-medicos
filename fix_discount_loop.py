import re

with open('src/components/BillingTab.svelte', 'r') as f:
    content = f.read()

# Add discountMode variable
content = content.replace("let discountPercent = 0;", "let discountPercent = 0;\n  let discountMode = 'percent';")
content = content.replace("discountPercent = 0;\n    billSubtotal = 0;", "discountPercent = 0;\n    discountMode = 'percent';\n    billSubtotal = 0;")

# Fix calculateTotals
old_calc = """    // If discount percentage is being used, update absolute discount
    if (discountPercent > 0) {
      billDiscount = parseFloat(((billSubtotal * discountPercent) / 100).toFixed(2)) || 0;
    }"""
new_calc = """    if (discountMode === 'percent') {
      billDiscount = parseFloat(((billSubtotal * discountPercent) / 100).toFixed(2)) || 0;
    } else {
      if (billSubtotal > 0) {
        discountPercent = parseFloat(((billDiscount / billSubtotal) * 100).toFixed(2)) || 0;
      } else {
        discountPercent = 0;
      }
    }"""
content = content.replace(old_calc, new_calc)

# Fix onDiscountPercentChange
old_percent_change = """  function onDiscountPercentChange() {
    if (discountPercent < 0) discountPercent = 0;
    if (discountPercent > 100) discountPercent = 100;
    billDiscount = parseFloat(((billSubtotal * discountPercent) / 100).toFixed(2)) || 0;
    calculateTotals();
  }"""
new_percent_change = """  function onDiscountPercentChange() {
    discountMode = 'percent';
    if (discountPercent < 0) discountPercent = 0;
    if (discountPercent > 100) discountPercent = 100;
    billDiscount = parseFloat(((billSubtotal * discountPercent) / 100).toFixed(2)) || 0;
    calculateTotals();
  }"""
content = content.replace(old_percent_change, new_percent_change)

# Fix onDiscountAmountChange
old_amount_change = """  function onDiscountAmountChange() {
    if (billSubtotal > 0) {
      discountPercent = parseFloat(((billDiscount / billSubtotal) * 100).toFixed(2)) || 0;
    } else {
      discountPercent = 0;
    }
    calculateTotals();
  }"""
new_amount_change = """  function onDiscountAmountChange() {
    discountMode = 'amount';
    if (billSubtotal > 0) {
      discountPercent = parseFloat(((billDiscount / billSubtotal) * 100).toFixed(2)) || 0;
    } else {
      discountPercent = 0;
    }
    calculateTotals();
  }"""
content = content.replace(old_amount_change, new_amount_change)

with open('src/components/BillingTab.svelte', 'w') as f:
    f.write(content)
print("Updated discount logic to prevent feedback loop.")
