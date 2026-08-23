with open('main-app.js', 'r') as f:
    content = f.read()

# Fix all the messed up backticks
content = content.replace("db.prepare(`SELECT", "db.prepare('SELECT")
content = content.replace("ORDER BY s.name ASC`).all();", "ORDER BY s.name ASC').all();")

# Now properly fix ONLY the multi-line one
old_query = "const rows = db.prepare('SELECT \\n      s.*, \\n      COALESCE((SELECT SUM(bill_amount) FROM supplier_bills WHERE supplier_id = s.id), 0) as total_bill_amount,\\n      COALESCE((SELECT SUM(amount_paid) FROM supplier_bills WHERE supplier_id = s.id), 0) as total_amount_paid\\n    FROM suppliers s \\n    ORDER BY s.name ASC').all();"
new_query = "const rows = db.prepare(`SELECT \\n      s.*, \\n      COALESCE((SELECT SUM(bill_amount) FROM supplier_bills WHERE supplier_id = s.id), 0) as total_bill_amount,\\n      COALESCE((SELECT SUM(amount_paid) FROM supplier_bills WHERE supplier_id = s.id), 0) as total_amount_paid\\n    FROM suppliers s \\n    ORDER BY s.name ASC`).all();"

content = content.replace(old_query, new_query)

with open('main-app.js', 'w') as f:
    f.write(content)
