import re

with open('main-app.js', 'r') as f:
    content = f.read()

profit_logic = """    // 12. Profit Calculations
    // Today's COGS
    const todayCogsRow = db.prepare(`
      SELECT SUM(bi.qty * i.unit_price) as cogs
      FROM bill_items bi
      JOIN bills b ON bi.bill_id = b.id
      JOIN inventory i ON bi.inventory_id = i.id
      WHERE date(b.bill_date) = date(?) AND b.payment_status = 'Paid'
    `).get(todayStr);
    const todayCogs = todayCogsRow ? (todayCogsRow.cogs || 0) : 0;

    // Today's Expenses
    const todayExpRow = db.prepare(`
      SELECT SUM(amount) as total
      FROM expenses
      WHERE expense_date = ?
    `).get(todayStr);
    const todayExpenses = todayExpRow ? (todayExpRow.total || 0) : 0;

    const todayProfit = todayRevenue - todayCogs - todayExpenses;

    // All-time COGS
    const allTimeCogsRow = db.prepare(`
      SELECT SUM(bi.qty * i.unit_price) as cogs
      FROM bill_items bi
      JOIN bills b ON bi.bill_id = b.id
      JOIN inventory i ON bi.inventory_id = i.id
      WHERE b.payment_status = 'Paid'
    `).get();
    const allTimeCogs = allTimeCogsRow ? (allTimeCogsRow.cogs || 0) : 0;

    // All-time Expenses
    const allTimeExpRow = db.prepare(`
      SELECT SUM(amount) as total
      FROM expenses
    `).get();
    const allTimeExpenses = allTimeExpRow ? (allTimeExpRow.total || 0) : 0;

    const allTimeProfit = allTimeRevenue - allTimeCogs - allTimeExpenses;

    const payload = {"""

payload_replace = """    const payload = {
      todayProfit,
      allTimeProfit,"""

content = content.replace("    const payload = {", profit_logic + "\n      todayProfit,\n      allTimeProfit,")

with open('main-app.js', 'w') as f:
    f.write(content)

print("Fixed profit calculation in main-app.js")
