import re

with open('main-app.js', 'r') as f:
    content = f.read()

# 1. Clean up save-supplier-bill
old_save_bill = re.search(r"ipcMain\.on\('save-supplier-bill'.*?\}\);", content, re.DOTALL)
if old_save_bill:
    new_save_bill = """ipcMain.on('save-supplier-bill', (event, bill) => {
  try {
    const status = bill.amount_paid >= bill.bill_amount ? 'Paid' : (bill.amount_paid > 0 ? 'Partial' : 'Pending');
    db.transaction(() => {
      db.prepare('INSERT INTO supplier_bills (supplier_id, bill_date, bill_amount, amount_paid, status, remarks) VALUES (?, ?, ?, ?, ?, ?)')
        .run(bill.supplier_id, bill.bill_date, bill.bill_amount, bill.amount_paid, status, bill.remarks);
      
      const unpaidAmount = bill.bill_amount - bill.amount_paid;
      // Adding a bill decreases the balance (negative balance = we owe them)
      db.prepare('UPDATE suppliers SET balance = balance - ? WHERE id = ?').run(unpaidAmount, bill.supplier_id);
    })();
    event.reply('supplier-bill-saved', { success: true });
  } catch(e) {
    event.reply('supplier-bill-saved', { success: false, error: e.message });
  }
});"""
    content = content.replace(old_save_bill.group(0), new_save_bill)

# 2. Clean up pay-supplier-bill
old_pay_bill = re.search(r"ipcMain\.on\('pay-supplier-bill'.*?\}\);", content, re.DOTALL)
if old_pay_bill:
    new_pay_bill = """ipcMain.on('pay-supplier-bill', (event, data) => {
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
    content = content.replace(old_pay_bill.group(0), new_pay_bill)

# 3. Replace delete-supplier-transaction with delete-supplier-bill
old_del_trx = re.search(r"ipcMain\.on\('delete-supplier-transaction'.*?\}\);", content, re.DOTALL)
if old_del_trx:
    new_del_bill = """ipcMain.on('delete-supplier-bill', (event, id) => {
  try {
    db.transaction(() => {
      const bill = db.prepare('SELECT * FROM supplier_bills WHERE id = ?').get(id);
      if (bill) {
        const unpaidAmount = bill.bill_amount - bill.amount_paid;
        // Reverse the balance impact: we owed them (so we subtracted), now we add it back.
        db.prepare('UPDATE suppliers SET balance = balance + ? WHERE id = ?').run(unpaidAmount, bill.supplier_id);
        db.prepare('DELETE FROM supplier_bills WHERE id = ?').run(id);
      }
    })();
    event.reply('supplier-bill-deleted', { success: true });
  } catch(e) {
    event.reply('supplier-bill-deleted', { success: false, error: e.message });
  }
});"""
    content = content.replace(old_del_trx.group(0), new_del_bill)

with open('main-app.js', 'w') as f:
    f.write(content)

print("Backend refactored")
