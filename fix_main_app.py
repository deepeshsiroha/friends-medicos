import re

with open('main-app.js', 'r') as f:
    content = f.read()

# 1. Add supplier_transactions table
old_db = """    db.prepare(`
      CREATE TABLE IF NOT EXISTS supplier_bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER,
        bill_date TEXT,
        bill_amount REAL,
        amount_paid REAL DEFAULT 0,
        status TEXT DEFAULT 'Pending',
        remarks TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `).run();"""

new_db = """    db.prepare(`
      CREATE TABLE IF NOT EXISTS supplier_bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER,
        bill_date TEXT,
        bill_amount REAL,
        amount_paid REAL DEFAULT 0,
        status TEXT DEFAULT 'Pending',
        remarks TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `).run();

    db.prepare(`
      CREATE TABLE IF NOT EXISTS supplier_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supplier_id INTEGER,
        transaction_date TEXT,
        type TEXT, -- 'Bill' or 'Payment'
        amount REAL,
        reference_id INTEGER, -- Optional link to supplier_bills
        remarks TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `).run();"""
if "supplier_transactions" not in content:
    content = content.replace(old_db, new_db)

# 2. Add 'add-supplier-payment' modification
old_payment = """ipcMain.on('add-supplier-payment', (event, data) => {
  try {
    db.prepare('UPDATE suppliers SET balance = balance + ? WHERE id = ?').run(data.amount, data.supplierId);
    event.reply('supplier-payment-added', { success: true });
  } catch(e) {
    event.reply('supplier-payment-added', { success: false, error: e.message });
  }
});"""

new_payment = """ipcMain.on('add-supplier-payment', (event, data) => {
  try {
    db.transaction(() => {
      db.prepare('UPDATE suppliers SET balance = balance + ? WHERE id = ?').run(data.amount, data.supplierId);
      db.prepare('INSERT INTO supplier_transactions (supplier_id, transaction_date, type, amount, remarks) VALUES (?, ?, ?, ?, ?)')
        .run(data.supplierId, new Date().toISOString().split('T')[0], 'Payment', data.amount, 'Open Payment');
    })();
    event.reply('supplier-payment-added', { success: true });
  } catch(e) {
    event.reply('supplier-payment-added', { success: false, error: e.message });
  }
});"""
content = content.replace(old_payment, new_payment)

# 3. Add 'save-supplier-bill' modification
old_save_bill = """ipcMain.on('save-supplier-bill', (event, bill) => {
  try {
    const status = bill.amount_paid >= bill.bill_amount ? 'Paid' : (bill.amount_paid > 0 ? 'Partial' : 'Pending');
    db.transaction(() => {
      db.prepare('INSERT INTO supplier_bills (supplier_id, bill_date, bill_amount, amount_paid, status, remarks) VALUES (?, ?, ?, ?, ?, ?)')
        .run(bill.supplier_id, bill.bill_date, bill.bill_amount, bill.amount_paid, status, bill.remarks);
      
      const unpaidAmount = bill.bill_amount - bill.amount_paid;
      // Adding a bill increases what we owe (decreases the balance)
      db.prepare('UPDATE suppliers SET balance = balance - ? WHERE id = ?').run(unpaidAmount, bill.supplier_id);
    })();
    event.reply('supplier-bill-saved', { success: true });
  } catch(e) {
    event.reply('supplier-bill-saved', { success: false, error: e.message });
  }
});"""

new_save_bill = """ipcMain.on('save-supplier-bill', (event, bill) => {
  try {
    const status = bill.amount_paid >= bill.bill_amount ? 'Paid' : (bill.amount_paid > 0 ? 'Partial' : 'Pending');
    db.transaction(() => {
      const info = db.prepare('INSERT INTO supplier_bills (supplier_id, bill_date, bill_amount, amount_paid, status, remarks) VALUES (?, ?, ?, ?, ?, ?)')
        .run(bill.supplier_id, bill.bill_date, bill.bill_amount, bill.amount_paid, status, bill.remarks);
      
      const unpaidAmount = bill.bill_amount - bill.amount_paid;
      // Adding a bill increases what we owe (decreases the balance)
      db.prepare('UPDATE suppliers SET balance = balance - ? WHERE id = ?').run(unpaidAmount, bill.supplier_id);
      
      db.prepare('INSERT INTO supplier_transactions (supplier_id, transaction_date, type, amount, reference_id, remarks) VALUES (?, ?, ?, ?, ?, ?)')
        .run(bill.supplier_id, bill.bill_date, 'Bill', bill.bill_amount, info.lastInsertRowid, bill.remarks || 'Invoice generated');
        
      if (bill.amount_paid > 0) {
        db.prepare('INSERT INTO supplier_transactions (supplier_id, transaction_date, type, amount, reference_id, remarks) VALUES (?, ?, ?, ?, ?, ?)')
          .run(bill.supplier_id, bill.bill_date, 'Payment', bill.amount_paid, info.lastInsertRowid, 'Upfront payment against invoice');
      }
    })();
    event.reply('supplier-bill-saved', { success: true });
  } catch(e) {
    event.reply('supplier-bill-saved', { success: false, error: e.message });
  }
});"""
content = content.replace(old_save_bill, new_save_bill)

# 4. Add 'get-supplier-ledger' and 'delete-supplier-transaction' and 'delete-supplier' before `ipcMain.on('get-supplier-bills'`
new_ipc_handlers = """ipcMain.on('get-supplier-ledger', (event, supplierId) => {
  try {
    const rows = db.prepare('SELECT * FROM supplier_transactions WHERE supplier_id = ? ORDER BY transaction_date DESC, id DESC').all(supplierId);
    event.reply('supplier-ledger-data', { success: true, rows });
  } catch(e) {
    event.reply('supplier-ledger-data', { success: false, error: e.message });
  }
});

ipcMain.on('delete-supplier-transaction', (event, id) => {
  try {
    db.transaction(() => {
      const trx = db.prepare('SELECT * FROM supplier_transactions WHERE id = ?').get(id);
      if (trx) {
        if (trx.type === 'Payment') {
          db.prepare('UPDATE suppliers SET balance = balance - ? WHERE id = ?').run(trx.amount, trx.supplier_id);
        } else if (trx.type === 'Bill') {
          db.prepare('UPDATE suppliers SET balance = balance + ? WHERE id = ?').run(trx.amount, trx.supplier_id);
          if (trx.reference_id) {
            db.prepare('DELETE FROM supplier_bills WHERE id = ?').run(trx.reference_id);
          }
        }
        db.prepare('DELETE FROM supplier_transactions WHERE id = ?').run(id);
      }
    })();
    event.reply('supplier-transaction-deleted', { success: true });
  } catch(e) {
    event.reply('supplier-transaction-deleted', { success: false, error: e.message });
  }
});

ipcMain.on('delete-supplier', (event, id) => {
  try {
    db.transaction(() => {
      db.prepare('DELETE FROM supplier_transactions WHERE supplier_id=?').run(id);
      db.prepare('DELETE FROM supplier_bills WHERE supplier_id=?').run(id);
      db.prepare('DELETE FROM suppliers WHERE id=?').run(id);
    })();
    event.reply('supplier-deleted', { success: true });
  } catch(e) {
    event.reply('supplier-deleted', { success: false, error: e.message });
  }
});

ipcMain.on('get-supplier-bills'"""

if "delete-supplier-transaction" not in content:
    content = content.replace("ipcMain.on('get-supplier-bills'", new_ipc_handlers)

# 5. Fix pay-supplier-bill
old_pay_bill = """ipcMain.on('pay-supplier-bill', (event, data) => {
  try {
    db.transaction(() => {
      db.prepare('UPDATE supplier_bills SET amount_paid = amount_paid + ?, status = CASE WHEN amount_paid + ? >= bill_amount THEN \\'Paid\\' ELSE \\'Partial\\' END WHERE id = ?')
        .run(data.amount, data.amount, data.billId);
      
      const bill = db.prepare('SELECT supplier_id FROM supplier_bills WHERE id = ?').get(data.billId);
      if (bill) {
        // Payment increases balance
        db.prepare('UPDATE suppliers SET balance = balance + ? WHERE id = ?').run(data.amount, bill.supplier_id);
      }
    })();
    event.reply('supplier-bill-paid', { success: true });
  } catch(e) {
    event.reply('supplier-bill-paid', { success: false, error: e.message });
  }
});"""

new_pay_bill = """ipcMain.on('pay-supplier-bill', (event, data) => {
  try {
    db.transaction(() => {
      db.prepare('UPDATE supplier_bills SET amount_paid = amount_paid + ?, status = CASE WHEN amount_paid + ? >= bill_amount THEN \\'Paid\\' ELSE \\'Partial\\' END WHERE id = ?')
        .run(data.amount, data.amount, data.billId);
      
      const bill = db.prepare('SELECT supplier_id FROM supplier_bills WHERE id = ?').get(data.billId);
      if (bill) {
        // Payment increases balance
        db.prepare('UPDATE suppliers SET balance = balance + ? WHERE id = ?').run(data.amount, bill.supplier_id);
        db.prepare('INSERT INTO supplier_transactions (supplier_id, transaction_date, type, amount, reference_id, remarks) VALUES (?, ?, ?, ?, ?, ?)')
          .run(bill.supplier_id, new Date().toISOString().split('T')[0], 'Payment', data.amount, data.billId, 'Payment against specific invoice');
      }
    })();
    event.reply('supplier-bill-paid', { success: true });
  } catch(e) {
    event.reply('supplier-bill-paid', { success: false, error: e.message });
  }
});"""
content = content.replace(old_pay_bill, new_pay_bill)

with open('main-app.js', 'w') as f:
    f.write(content)

print("Backend restored and updated!")
