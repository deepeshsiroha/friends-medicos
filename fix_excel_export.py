import re
import os

# 1. Update main-app.js
with open('main-app.js', 'r') as f:
    content = f.read()

# Replace the handler name and logic
# Since the handler spans many lines, I will just do a regex replace from ipcMain.handle('export-csv'... to the end.
# A simpler way is to find the exact block and replace it.

old_block = """// --- EXPORT TO CSV CHANNELS ---
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
});"""

new_block = """// --- EXPORT TO EXCEL CHANNELS ---
const xlsx = require('xlsx');

ipcMain.handle('export-excel', async (event, moduleName) => {
  try {
    let data = [];
    let headers = [];
    let defaultFilename = `${moduleName}_export_${getISTDateTimeString().substring(0, 10)}.xlsx`;

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

    const { filePath } = await dialog.showSaveDialog(mainWindow, {
      title: 'Save Excel Export',
      defaultPath: path.join(app.getPath('documents'), defaultFilename),
      filters: [{ name: 'Excel Files', extensions: ['xlsx'] }]
    });

    if (filePath) {
      const worksheet = xlsx.utils.aoa_to_sheet([headers, ...data]);
      const workbook = xlsx.utils.book_new();
      xlsx.utils.book_append_sheet(workbook, worksheet, "Export");
      xlsx.writeFile(workbook, filePath);
      
      return { success: true, filePath };
    } else {
      return { success: false, cancelled: true };
    }
  } catch (error) {
    return { success: false, error: error.message };
  }
});"""

if old_block in content:
    content = content.replace(old_block, new_block)
    with open('main-app.js', 'w') as f:
        f.write(content)
    print("Updated main-app.js")
else:
    print("Could not find exact old block in main-app.js. Proceeding with regex...")
    # fallback regex if indentation is slightly off
    content = re.sub(r'// --- EXPORT TO CSV CHANNELS ---.*}\);', new_block, content, flags=re.DOTALL)
    with open('main-app.js', 'w') as f:
        f.write(content)

# 2. Update all svelte files
svelte_files = [
    'src/components/InventoryTab.svelte',
    'src/components/BillingTab.svelte',
    'src/components/ExpensesTab.svelte',
    'src/components/SuppliersTab.svelte'
]

for filepath in svelte_files:
    with open(filepath, 'r') as f:
        s_content = f.read()
    
    # rename button label
    s_content = s_content.replace('>Export CSV</button>', '>Export Excel</button>')
    s_content = s_content.replace('Export CSV\n                  </button>', 'Export Excel\n                  </button>')
    s_content = s_content.replace('Export CSV\n              </button>', 'Export Excel\n              </button>')
    s_content = s_content.replace('Export CSV\n            </button>', 'Export Excel\n            </button>')

    # change ipcRenderer call
    s_content = s_content.replace("ipcRenderer.invoke('export-csv'", "ipcRenderer.invoke('export-excel'")

    # change function name exportToCSV to exportToExcel
    s_content = s_content.replace("exportToCSV", "exportToExcel")

    with open(filepath, 'w') as f:
        f.write(s_content)

print("Updated svelte files.")
