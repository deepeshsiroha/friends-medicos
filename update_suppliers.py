import re

with open('main-app.js', 'r') as f:
    content = f.read()

# Replace the get-suppliers query
old_query = "SELECT * FROM suppliers ORDER BY name ASC"
new_query = """SELECT 
      s.*, 
      COALESCE((SELECT SUM(bill_amount) FROM supplier_bills WHERE supplier_id = s.id), 0) as total_bill_amount,
      COALESCE((SELECT SUM(amount_paid) FROM supplier_bills WHERE supplier_id = s.id), 0) as total_amount_paid
    FROM suppliers s 
    ORDER BY s.name ASC"""

content = content.replace(old_query, new_query)

with open('main-app.js', 'w') as f:
    f.write(content)
print("Updated get-suppliers in main-app.js")
