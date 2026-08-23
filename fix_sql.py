with open('main-app.js', 'r') as f:
    content = f.read()

content = content.replace("db.prepare('SELECT \\n      s.*,", "db.prepare(`SELECT \\n      s.*,")
content = content.replace("ORDER BY s.name ASC').all();", "ORDER BY s.name ASC`).all();")

with open('main-app.js', 'w') as f:
    f.write(content)
