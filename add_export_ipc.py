with open('main-app.js', 'r') as f:
    content = f.read()

export_logic = """
// --- EXPORT TO CSV CHANNELS ---
ipcMain.handle('export-csv', async (event, moduleName) => {
  try {
    let data = [];
    let headers = [];
    let defaultFilename = `${moduleName}_export_${getISTDateTimeString().substring(0, 10)}.csv`;

    if (moduleName === 'inventory') {
      const rows = db.prepare('SELECT * FROM inventory ORDER BY item_name ASC').all();
      headers = ['Item Name', 'Category', 'Batch No', 'Remaining Qty', 'Buying Price', 'Selling Price', 'GST Rate', 'Expiry Date'];
      data = rows.map(r => [
        r.item_name, r.category, r.batch_no, r.remaining_qty, r.unit_price, r.selling_price, r.gst_rate, r.expiry_date
      ]);
    } else if (moduleName === 'sales') {
      const rows = db.prepare('SELECT * FROM bills ORDER BY bill_date DESC').all();
      headers = ['Date', 'Invoice No', 'Customer Name', 'Mobile', 'Subtotal', 'Discount', 'Total', 'Payment Mode'];
      data = rows.map(r => [
        r.bill_date, r.id, r.patient_name, r.patient_mobile, r.subtotal, r.discount, r.total, r.payment_method
      ]);
    } else if (moduleName === 'expenses') {
      const rows = db.prepare('SELECT * FROM expenses ORDER BY expense_date DESC').all();
      headers = ['Date', 'Category', 'Amount', 'Description', 'Payment Method'];
      data = rows.map(r => [
        r.expense_date, r.category, r.amount, r.description, r.payment_method
      ]);
    } else if (moduleName === 'suppliers') {
      const rows = db.prepare(`SELECT 
        s.*, 
        COALESCE((SELECT SUM(bill_amount) FROM supplier_bills WHERE supplier_id = s.id), 0) as total_bill_amount,
        COALESCE((SELECT SUM(amount_paid) FROM supplier_bills WHERE supplier_id = s.id), 0) as total_amount_paid
      FROM suppliers s ORDER BY s.name ASC`).all();
      headers = ['Supplier Name', 'Contact', 'GSTIN', 'Total Billed', 'Total Paid', 'Balance Owed'];
      data = rows.map(r => [
        r.name, r.contact, r.gstin, r.total_bill_amount, r.total_amount_paid, Math.max(0, r.total_bill_amount - r.total_amount_paid)
      ]);
    } else {
      throw new Error("Unknown module for export");
    }

    const csvLines = [headers.map(h => `"${h}"`).join(',')];
    data.forEach(row => {
      const line = row.map(cell => {
        let str = cell === null || cell === undefined ? '' : String(cell);
        str = str.replace(/"/g, '""'); // escape double quotes
        return `"${str}"`;
      });
      csvLines.push(line.join(','));
    });
    const csvContent = csvLines.join('\\n');

    const { filePath } = await dialog.showSaveDialog(mainWindow, {
      title: 'Save CSV Export',
      defaultPath: path.join(app.getPath('documents'), defaultFilename),
      filters: [{ name: 'CSV Files', extensions: ['csv'] }]
    });

    if (filePath) {
      fs.writeFileSync(filePath, csvContent, 'utf-8');
      return { success: true, filePath };
    } else {
      return { success: false, cancelled: true };
    }
  } catch (error) {
    return { success: false, error: error.message };
  }
});
"""

if "ipcMain.handle('export-csv'" not in content:
    content += "\n" + export_logic

with open('main-app.js', 'w') as f:
    f.write(content)
print("Export IPC added.")
