import re

with open('main-app.js', 'r') as f:
    content = f.read()

# 1. Calculate today's cash and UPI in main-app.js
calc_old = """    const todayRevenue = todayRevenueRow ? (todayRevenueRow.total || 0) : 0;"""
calc_new = """    const todayRevenue = todayRevenueRow ? (todayRevenueRow.total || 0) : 0;

    const todayPaymentRows = db.prepare(`
      SELECT payment_method, SUM(total) as total 
      FROM bills 
      WHERE date(bill_date) = date(?) AND payment_status = 'Paid'
      GROUP BY payment_method
    `).all(todayStr);
    
    let todayCash = 0;
    let todayUpi = 0;
    todayPaymentRows.forEach(row => {
      if (row.payment_method === 'Cash') todayCash = row.total || 0;
      if (row.payment_method === 'UPI' || row.payment_method === 'Online') todayUpi = row.total || 0;
    });"""

content = content.replace(calc_old, calc_new)

# 2. Add them to payload
payload_old = """    const payload = {
      todayProfit,
      allTimeProfit,
      todayRevenue,"""
payload_new = """    const payload = {
      todayProfit,
      allTimeProfit,
      todayRevenue,
      todayCash,
      todayUpi,"""
content = content.replace(payload_old, payload_new)

with open('main-app.js', 'w') as f:
    f.write(content)

with open('src/components/AnalyticsTab.svelte', 'r') as f:
    svelte = f.read()

# 3. Add to UI
ui_old = """    <div class="kpi-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white;">
      <h3>Today's Collection</h3>
      <p class="kpi-value">₹{data.todayRevenue ? parseFloat(data.todayRevenue).toLocaleString('en-IN', { minimumFractionDigits: 2 }) : '0.00'}</p>
    </div>"""

ui_new = """    <div class="kpi-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; position: relative;">
      <h3>Today's Collection</h3>
      <p class="kpi-value">₹{data.todayRevenue ? parseFloat(data.todayRevenue).toLocaleString('en-IN', { minimumFractionDigits: 2 }) : '0.00'}</p>
      <div style="font-size: 11px; margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 6px; display: flex; justify-content: space-between;">
        <span>Cash: ₹{data.todayCash ? parseFloat(data.todayCash).toLocaleString('en-IN', { minimumFractionDigits: 2 }) : '0.00'}</span>
        <span>UPI: ₹{data.todayUpi ? parseFloat(data.todayUpi).toLocaleString('en-IN', { minimumFractionDigits: 2 }) : '0.00'}</span>
      </div>
    </div>"""

svelte = svelte.replace(ui_old, ui_new)

with open('src/components/AnalyticsTab.svelte', 'w') as f:
    f.write(svelte)

print("Updated analytics logic to show cash and upi breakdown.")
