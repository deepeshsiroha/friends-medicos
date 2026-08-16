const { app, BrowserWindow, ipcMain, shell, Menu, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const Database = require('better-sqlite3');

// Initialize the SQLite database connection in the user data directory
const dbPath = path.join(app.getPath('userData'), 'jeevanrekha_data.db');
const db = new Database(dbPath);

let mainWindow;

function getISTDateTimeString() {
  const utcDate = new Date();
  const istDate = new Date(utcDate.getTime() + (5.5 * 60 * 60 * 1000));
  const isoStr = istDate.toISOString();
  return isoStr.substring(0, 10) + ' ' + isoStr.substring(11, 19);
}

// --- 1. DATABASE SCHEMA SETUP ---
db.exec(`
  CREATE TABLE IF NOT EXISTS customers (
    mobile TEXT PRIMARY KEY,
    name TEXT,
    total_visits INTEGER DEFAULT 1,
    total_spent REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_visit DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    category TEXT DEFAULT 'Tablet',
    batch_no TEXT,
    pharmacy_name TEXT,
    received_date TEXT,
    received_qty INTEGER,
    expiry_date TEXT,
    issued_qty INTEGER DEFAULT 0,
    remaining_qty INTEGER,
    unit_price REAL NOT NULL,
    mrp REAL,
    supplier_id INTEGER,
    gst_rate REAL DEFAULT 12.0,
    remarks TEXT
  );

  CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact TEXT,
    gstin TEXT,
    balance REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_date TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    description TEXT,
    payment_method TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS inventory_issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inventory_id INTEGER,
    item_name TEXT,
    issued_to_mobile TEXT,
    issued_to_name TEXT,
    issued_qty INTEGER,
    issue_date DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
  );

  CREATE TABLE IF NOT EXISTS bills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    consultation_id INTEGER,
    patient_mobile TEXT NOT NULL,
    patient_name TEXT NOT NULL,
    subtotal REAL NOT NULL,
    discount REAL DEFAULT 0,
    total REAL NOT NULL,
    cgst_total REAL DEFAULT 0,
    sgst_total REAL DEFAULT 0,
    payment_method TEXT,
    payment_status TEXT,
    remarks TEXT,
    bill_date TEXT
  );

  CREATE TABLE IF NOT EXISTS bill_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER NOT NULL,
    item_name TEXT NOT NULL,
    qty INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    total REAL NOT NULL,
    cgst_amount REAL DEFAULT 0,
    sgst_amount REAL DEFAULT 0,
    inventory_id INTEGER,
    FOREIGN KEY(bill_id) REFERENCES bills(id) ON DELETE CASCADE
  );

  -- Performance Indexes
  CREATE INDEX IF NOT EXISTS idx_inventory_item_name ON inventory(item_name);
  CREATE INDEX IF NOT EXISTS idx_bills_patient_mobile ON bills(patient_mobile);
  CREATE INDEX IF NOT EXISTS idx_bills_patient_name ON bills(patient_name);
`);

try {
  db.exec('ALTER TABLE inventory ADD COLUMN batch_no TEXT;');
} catch (e) {
  // column already exists, safe to ignore
}

try {
  db.exec('ALTER TABLE inventory ADD COLUMN pharmacy_name TEXT;');
} catch (e) {
  // column already exists, safe to ignore
}

try {
  db.exec('ALTER TABLE inventory_issues ADD COLUMN consultation_id INTEGER;');
} catch (e) {
  // column already exists, safe to ignore
}

try {
  db.exec('ALTER TABLE inventory_issues ADD COLUMN returned_qty INTEGER DEFAULT 0;');
} catch (e) {
  // column already exists, safe to ignore
}

try {
  db.exec('ALTER TABLE inventory_issues ADD COLUMN return_date TEXT;');
} catch (e) {
  // column already exists, safe to ignore
}

try {
  db.exec('ALTER TABLE consultations ADD COLUMN history TEXT;');
} catch (e) {
  // column already exists, safe to ignore
}

try {
  db.exec('ALTER TABLE consultations ADD COLUMN examination TEXT;');
} catch (e) {
  // column already exists, safe to ignore
}

try {
  db.exec('ALTER TABLE inventory ADD COLUMN unit_price REAL DEFAULT 0.0;');
} catch (e) {
  // column already exists, safe to ignore
}

try {
  db.exec('ALTER TABLE inventory ADD COLUMN category TEXT DEFAULT "Tablet";');
} catch (e) {
  // column already exists, safe to ignore
}

try {
  db.exec('ALTER TABLE bill_items ADD COLUMN inventory_id INTEGER;');
} catch (e) {
  // column already exists, safe to ignore
}

// Seed default settings if empty
try {
  const configCount = db.prepare('SELECT COUNT(*) as count FROM settings').get().count;
  if (configCount === 0) {
    const insert = db.prepare('INSERT INTO settings (key, value) VALUES (?, ?)');
    insert.run('pharmacy_name', 'Friends Medicos');
    insert.run('pharmacy_address', 'Main Bazar, Narnaul, 123001 (Haryana)');
    insert.run('pharmacy_contact', '+91 9999999999');
    insert.run('pharmacy_gstin', '06AAAAA0000A1Z5');
    insert.run('pharmacy_license', 'DL-12345-A');
  }
} catch (e) {
  console.error("Failed to seed settings:", e);
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1300,
    height: 900,
    title: "Friends Medicos Pharmacy Management",
    icon: path.join(__dirname, 'build', 'icon.png'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
    console.log(`[FRONTEND CONSOLE] ${message} (line ${line})`);
  });

  // Run simple migrations for new columns
  try { db.exec("ALTER TABLE inventory ADD COLUMN gst_rate REAL DEFAULT 12.0;"); } catch (e) {}
  try { db.exec("ALTER TABLE inventory ADD COLUMN supplier_id INTEGER;"); } catch (e) {}
  try { db.exec("ALTER TABLE inventory ADD COLUMN mrp REAL;"); } catch (e) {}
  try { db.exec("ALTER TABLE inventory ADD COLUMN selling_price REAL DEFAULT 0.0;"); } catch (e) {}

  try { db.exec("ALTER TABLE bills ADD COLUMN cgst_total REAL DEFAULT 0;"); } catch (e) {}
  try { db.exec("ALTER TABLE bills ADD COLUMN sgst_total REAL DEFAULT 0;"); } catch (e) {}

  try { db.exec("ALTER TABLE bill_items ADD COLUMN cgst_amount REAL DEFAULT 0;"); } catch (e) {}
  try { db.exec("ALTER TABLE bill_items ADD COLUMN sgst_amount REAL DEFAULT 0;"); } catch (e) {}
  try { db.exec("ALTER TABLE bill_items ADD COLUMN inventory_id INTEGER;"); } catch (e) {}

  const isDev = process.env.NODE_ENV === 'development';
  if (isDev) {
    mainWindow.webContents.openDevTools();
    mainWindow.loadURL('http://localhost:5173').catch(err => {
      console.warn("Vite server not running, falling back to local build...");
      if (!mainWindow.isDestroyed()) {
        mainWindow.loadFile(path.join(__dirname, 'dist-frontend', 'index.html'));
      }
    });
  } else {
    mainWindow.loadFile(path.join(__dirname, 'dist-frontend', 'index.html'));
  }
}

function setupApplicationMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Open Prescriptions Folder',
          click() {
            const folderPath = path.join(app.getPath('documents'), 'FriendsMedicos', 'Prescriptions');
            if (!fs.existsSync(folderPath)) {
              fs.mkdirSync(folderPath, { recursive: true });
            }
            shell.openPath(folderPath).catch(err => console.error(err));
          }
        },
        {
          label: 'Open Bills Folder',
          click() {
            const folderPath = path.join(app.getPath('documents'), 'FriendsMedicos', 'Bills');
            if (!fs.existsSync(folderPath)) {
              fs.mkdirSync(folderPath, { recursive: true });
            }
            shell.openPath(folderPath).catch(err => console.error(err));
          }
        },
        { type: 'separator' },
        { role: 'quit' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload' },
        { role: 'forceReload' },
        { type: 'separator' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { role: 'resetZoom' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About Friends Medicos',
          click(menuItem, browserWindow) {
            dialog.showMessageBox(browserWindow, {
              type: 'info',
              title: 'About Friends Medicos',
              message: 'Friends Medicos Pharmacy Management',
              detail: 'Version: 1.2.0\nAuthor: Deepesh Siroha\n\nA modern pharmacy management suite.',
              buttons: ['OK']
            });
          }
        }
      ]
    }
  ];

  if (process.platform === 'darwin') {
    template.unshift({
      label: app.name,
      submenu: [
        { role: 'about' },
        { type: 'separator' },
        { role: 'services' },
        { type: 'separator' },
        { role: 'hide' },
        { role: 'hideOthers' },
        { role: 'unhide' },
        { type: 'separator' },
        { role: 'quit' }
      ]
    });
  }

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

app.disableHardwareAcceleration();
app.whenReady().then(() => {
  createWindow();
  setupApplicationMenu();
});

// --- 2. CORE WORKFLOW EVENTS ---

ipcMain.on('save-bill', (event, { bill, items, editBillId }) => {
  const insertBill = db.prepare(`
    INSERT INTO bills (consultation_id, patient_mobile, patient_name, subtotal, discount, total, cgst_total, sgst_total, payment_method, payment_status, remarks, bill_date) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);

  const updateBill = db.prepare(`
    UPDATE bills SET 
      patient_mobile = ?, patient_name = ?, subtotal = ?, discount = ?, total = ?, 
      cgst_total = ?, sgst_total = ?,
      payment_method = ?, payment_status = ?, remarks = ?
    WHERE id = ?
  `);

  const insertItem = db.prepare(`
    INSERT INTO bill_items (bill_id, item_name, qty, unit_price, total, cgst_amount, sgst_amount, inventory_id) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
  `);

  const deleteItems = db.prepare(`DELETE FROM bill_items WHERE bill_id = ?`);
  const updateInventory = db.prepare(`UPDATE inventory SET issued_qty = issued_qty + ?, remaining_qty = remaining_qty - ? WHERE id = ?`);
  const logIssue = db.prepare(`INSERT INTO inventory_issues (inventory_id, item_name, issued_to_mobile, issued_to_name, issued_qty, issue_date) VALUES (?, ?, ?, ?, ?, ?)`);

  const updateCustomer = db.prepare(`
    INSERT INTO customers (mobile, name, total_visits, total_spent, last_visit)
    VALUES (?, ?, 1, ?, ?)
    ON CONFLICT(mobile) DO UPDATE SET 
      name = excluded.name, 
      total_visits = total_visits + 1, 
      total_spent = total_spent + excluded.total_spent,
      last_visit = excluded.last_visit
  `);

  const executeTransaction = db.transaction(() => {
    let billId = editBillId;
    const nowStr = getISTDateTimeString();

    if (editBillId) {
      // Restore inventory from previous items before updating
      const oldItems = db.prepare('SELECT * FROM bill_items WHERE bill_id = ?').all(editBillId);
      for (const old of oldItems) {
        if (old.inventory_id) {
          db.prepare(`UPDATE inventory SET issued_qty = issued_qty - ?, remaining_qty = remaining_qty + ? WHERE id = ?`).run(old.qty, old.qty, old.inventory_id);
          db.prepare(`DELETE FROM inventory_issues WHERE inventory_id = ? AND issued_qty = ? AND issued_to_mobile = ? AND issued_to_name = ?`).run(old.inventory_id, old.qty, bill.patient_mobile, bill.patient_name);
        }
      }
      updateBill.run(
        bill.patient_mobile, bill.patient_name, bill.subtotal, bill.discount || 0,
        bill.total, bill.cgst_total || 0, bill.sgst_total || 0, bill.payment_method, bill.payment_status, bill.remarks || '', editBillId
      );
      deleteItems.run(editBillId);
    } else {
      const info = insertBill.run(
        bill.consultation_id || null,
        bill.patient_mobile,
        bill.patient_name,
        bill.subtotal,
        bill.discount || 0,
        bill.total,
        bill.cgst_total || 0,
        bill.sgst_total || 0,
        bill.payment_method,
        bill.payment_status,
        bill.remarks || '',
        nowStr
      );
      billId = info.lastInsertRowid;
    }

    // Always update customer stats for new bills (for edits, we could calculate diffs, but this is simpler for now)
    if (!editBillId && bill.patient_mobile) {
      updateCustomer.run(bill.patient_mobile, bill.patient_name, bill.total, nowStr);
    }

    const issueDate = getISTDateTimeString();
    for (const item of items) {
      insertItem.run(billId, item.item_name, item.qty, item.unit_price, item.total, item.cgst_amount || 0, item.sgst_amount || 0, item.inventory_id || null);
      if (item.inventory_id) {
        updateInventory.run(item.qty, item.qty, item.inventory_id);
        logIssue.run(item.inventory_id, item.item_name, bill.patient_mobile, bill.patient_name, item.qty, issueDate);
      }
    }
    return billId;
  });

  try {
    const billId = executeTransaction();
    event.reply('bill-save-status', { success: true, id: billId });
  } catch (err) {
    console.error("Failed to save bill:", err);
    event.reply('bill-save-status', { success: false, error: err.message });
  }
});

ipcMain.on('get-bills', (event) => {
  try {
    const bills = db.prepare('SELECT * FROM bills ORDER BY bill_date DESC LIMIT 100').all();
    for (const bill of bills) {
      bill.items = db.prepare('SELECT * FROM bill_items WHERE bill_id = ?').all(bill.id);
    }
    event.reply('bills-data', bills);
  } catch (err) {
    console.error("Failed to fetch bills:", err);
    event.reply('bills-data', []);
  }
});

ipcMain.on('get-bill-details', (event, id) => {
  try {
    const bill = db.prepare('SELECT * FROM bills WHERE id = ?').get(id);
    if (!bill) {
      event.reply('bill-details-data', { success: false, error: 'Bill not found' });
      return;
    }
    const items = db.prepare('SELECT * FROM bill_items WHERE bill_id = ?').all(id);
    event.reply('bill-details-data', { success: true, bill: bill, items: items });
  } catch (err) {
    console.error("Failed to fetch bill details:", err);
    event.reply('bill-details-data', { success: false, error: err.message });
  }
});

ipcMain.on('toggle-payment-status', (event, id, currentStatus) => {
  const newStatus = currentStatus === 'Paid' ? 'Unpaid' : 'Paid';
  try {
    db.prepare('UPDATE bills SET payment_status = ? WHERE id = ?').run(newStatus, id);
    event.reply('bill-payment-toggled', { success: true, id: id, newStatus: newStatus });
  } catch (err) {
    console.error("Failed to toggle payment status:", err);
    event.reply('bill-payment-toggled', { success: false, error: err.message });
  }
});ipcMain.on('search-bills', (event, term) => {
  try {
    const bills = db.prepare(`
      SELECT * FROM bills 
      WHERE patient_name LIKE ? OR patient_mobile LIKE ? 
      ORDER BY bill_date DESC LIMIT 50
    `).all(`%${term}%`, `%${term}%`);
    for (const bill of bills) {
      bill.items = db.prepare('SELECT * FROM bill_items WHERE bill_id = ?').all(bill.id);
    }
    event.reply('bills-data', bills);
  } catch (err) {
    console.error("Failed to search bills:", err);
    event.reply('bills-data', []);
  }
});

ipcMain.on('delete-bill', (event, billId) => {
  const executeTransaction = db.transaction(() => {
    const bill = db.prepare('SELECT * FROM bills WHERE id = ?').get(billId);
    const oldItems = db.prepare('SELECT * FROM bill_items WHERE bill_id = ?').all(billId);
    for (const old of oldItems) {
      if (old.inventory_id) {
        db.prepare(`UPDATE inventory SET issued_qty = issued_qty - ?, remaining_qty = remaining_qty + ? WHERE id = ?`).run(old.qty, old.qty, old.inventory_id);
        if (bill) {
          db.prepare(`DELETE FROM inventory_issues WHERE inventory_id = ? AND issued_qty = ? AND issued_to_mobile = ? AND issued_to_name = ?`).run(old.inventory_id, old.qty, bill.patient_mobile, bill.patient_name);
        }
      }
    }
    db.prepare('DELETE FROM bill_items WHERE bill_id = ?').run(billId);
    db.prepare('DELETE FROM bills WHERE id = ?').run(billId);
  });
  try {
    executeTransaction();
    const bills = db.prepare('SELECT * FROM bills ORDER BY bill_date DESC LIMIT 100').all();
    for (const bill of bills) {
      bill.items = db.prepare('SELECT * FROM bill_items WHERE bill_id = ?').all(bill.id);
    }
    event.reply('bills-data', bills);
  } catch (err) {
    console.error("Failed to delete bill:", err);
  }
});

ipcMain.on('toggle-bill-status', (event, { billId, status }) => {
  try {
    db.prepare('UPDATE bills SET payment_status = ? WHERE id = ?').run(status, billId);
    const bills = db.prepare('SELECT * FROM bills ORDER BY bill_date DESC LIMIT 100').all();
    for (const bill of bills) {
      bill.items = db.prepare('SELECT * FROM bill_items WHERE bill_id = ?').all(bill.id);
    }
    event.reply('bills-data', bills);
  } catch (err) {
    console.error("Failed to toggle bill status:", err);
  }
});



function cleanupExpiredStock() {
  try {
    const autoDeleteSetting = db.prepare("SELECT value FROM settings WHERE key = 'auto_delete_expired'").get();
    if (autoDeleteSetting && autoDeleteSetting.value === 'true') {
      const threeMonthsAgo = new Date();
      threeMonthsAgo.setMonth(threeMonthsAgo.getMonth() - 3);
      const yyyy = threeMonthsAgo.getFullYear();
      const mm = String(threeMonthsAgo.getMonth() + 1).padStart(2, '0');
      const dd = String(threeMonthsAgo.getDate()).padStart(2, '0');
      const limitDate = `${yyyy}-${mm}-${dd}`;
      
      db.prepare("DELETE FROM inventory WHERE expiry_date IS NOT NULL AND expiry_date != '' AND expiry_date < ?").run(limitDate);
      db.prepare("DELETE FROM inventory_issues WHERE inventory_id NOT IN (SELECT id FROM inventory)").run();
    }
  } catch (err) {
    console.error("Failed to auto-delete expired inventory:", err);
  }
}

// --- 3. INVENTORY MANAGEMENT CHANNELS ---
ipcMain.on('add-stock', (event, stock) => {
  const stmt = db.prepare(`
    INSERT INTO inventory (item_name, category, batch_no, pharmacy_name, received_date, received_qty, expiry_date, remaining_qty, remarks, unit_price, mrp, selling_price, supplier_id, gst_rate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);
  stmt.run(stock.item_name, stock.category || 'Tablet', stock.batch_no, stock.pharmacy_name, stock.received_date, stock.received_qty, stock.expiry_date, stock.received_qty, stock.remarks, stock.unit_price || 0.0, stock.mrp || 0.0, stock.selling_price || 0.0, stock.supplier_id || null, stock.gst_rate || 12.0);

  cleanupExpiredStock();

  const rows = db.prepare('SELECT * FROM inventory ORDER BY id DESC').all();
  const issueLogs = db.prepare('SELECT * FROM inventory_issues ORDER BY issue_date DESC LIMIT 100').all();
  event.reply('inventory-data', rows, issueLogs);
});

ipcMain.on('update-stock', (event, stock) => {
  // remaining_qty = received_qty - issued_qty (recalculate to keep consistent)
  const existing = db.prepare('SELECT issued_qty FROM inventory WHERE id = ?').get(stock.id);
  const issuedQty = existing ? (existing.issued_qty || 0) : 0;
  const remainingQty = stock.received_qty - issuedQty;

  db.prepare(`
    UPDATE inventory SET
      item_name = ?, category = ?, batch_no = ?, pharmacy_name = ?,
      received_date = ?, received_qty = ?, expiry_date = ?,
      remarks = ?, remaining_qty = ?, unit_price = ?, mrp = ?, selling_price = ?, supplier_id = ?, gst_rate = ?
    WHERE id = ?
  `).run(
    stock.item_name, stock.category || 'Tablet', stock.batch_no, stock.pharmacy_name,
    stock.received_date, stock.received_qty, stock.expiry_date,
    stock.remarks, remainingQty, stock.unit_price || 0.0, stock.mrp || 0.0, stock.selling_price || 0.0, stock.supplier_id || null, stock.gst_rate || 12.0,
    stock.id
  );

  cleanupExpiredStock();

  const rows = db.prepare('SELECT * FROM inventory ORDER BY id DESC').all();
  const issueLogs = db.prepare('SELECT * FROM inventory_issues ORDER BY issue_date DESC LIMIT 100').all();
  event.reply('inventory-data', rows, issueLogs);
});

ipcMain.on('get-inventory', (event) => {
  cleanupExpiredStock();
  const rows = db.prepare('SELECT * FROM inventory ORDER BY id DESC').all();
  const issueLogs = db.prepare('SELECT * FROM inventory_issues ORDER BY issue_date DESC LIMIT 100').all();
  event.reply('inventory-data', rows, issueLogs);
});

ipcMain.on('delete-stock', (event, id) => {
  const stmt = db.prepare('DELETE FROM inventory WHERE id = ?');
  stmt.run(id);
  const cleanAudit = db.prepare('DELETE FROM inventory_issues WHERE inventory_id = ?');
  cleanAudit.run(id);

  const rows = db.prepare('SELECT * FROM inventory ORDER BY id DESC').all();
  const issueLogs = db.prepare('SELECT * FROM inventory_issues ORDER BY issue_date DESC LIMIT 100').all();
  event.reply('inventory-data', rows, issueLogs);
});

ipcMain.on('search-stock-items', (event, payload) => {
  let term = '';
  let category = '';
  if (typeof payload === 'string') {
    term = payload;
  } else {
    term = payload.term || '';
    category = payload.category || '';
  }

  let rows;
  if (category) {
    if (category === 'Injection') {
      rows = db.prepare(`
        SELECT * FROM inventory 
        WHERE item_name LIKE ? AND remaining_qty > 0 AND (category = 'Injection Vial' OR category = 'Injection Ampule') 
        ORDER BY expiry_date ASC LIMIT 8
      `).all(`%${term}%`);
    } else {
      rows = db.prepare(`
        SELECT * FROM inventory 
        WHERE item_name LIKE ? AND remaining_qty > 0 AND category = ? 
        ORDER BY expiry_date ASC LIMIT 8
      `).all(`%${term}%`, category);
    }
  } else {
    rows = db.prepare(`
      SELECT * FROM inventory 
      WHERE item_name LIKE ? AND remaining_qty > 0 
      ORDER BY expiry_date ASC LIMIT 8
    `).all(`%${term}%`);
  }
  event.reply('stock-suggestions', rows);
});

// --- 4. RECORDS LOG CHANNELS ---


// --- 4.5. SETTINGS CHANNELS ---
ipcMain.on('get-settings', (event) => {
  const rows = db.prepare('SELECT * FROM settings').all();
  event.reply('settings-data', rows);
});

ipcMain.on('save-settings', (event, config) => {
  const stmt = db.prepare('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)');
  const executeTransaction = db.transaction(() => {
    for (const [key, val] of Object.entries(config)) {
      stmt.run(key, val);
    }
  });
  try {
    executeTransaction();
    
    // Perform cleanup right after setting is saved
    cleanupExpiredStock();

    const rows = db.prepare('SELECT * FROM settings').all();
    event.reply('settings-data', rows);
  } catch (err) {
    console.error("Failed to save settings:", err);
  }
});


// --- 5. STABLE PRINTER CONTROLLER ENGINE ---
let activePrintWorkerWindow = null;

function getDocumentFolder(folder) {
  const folderPath = path.join(app.getPath('documents'), 'FriendsMedicos', folder);
  if (!fs.existsSync(folderPath)) {
    fs.mkdirSync(folderPath, { recursive: true });
  }
  return folderPath;
}

ipcMain.on('save-pdf', (event, { fileName, pdfData, subFolder }) => {
  const folderPath = getDocumentFolder(subFolder || 'Prescriptions');
  const filePath = path.join(folderPath, fileName);

  // 1. Save PDF file background asset directly to disk for backup storage tracking
  fs.writeFile(filePath, Buffer.from(pdfData), (err) => {
    if (err) {
      console.error("Failed to write PDF backup to storage:", err);
      return;
    }
    console.log("PDF written to disk storage successfully:", filePath);

    // 2. Open the PDF file directly with the system's default PDF viewer (e.g. Edge, Chrome, or Adobe Reader)
    // This allows the user to see the beautifully compiled PDF and print it using the native system dialog with 100% correct layout and scaling.
    shell.openPath(filePath).catch((err) => {
      console.error("Failed to open PDF file:", err);
    });
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

// --- OPD REGISTER ---

ipcMain.on('get-analytics-data', (event) => {
  try {
    const todayStr = getISTDateTimeString().substring(0, 10);
    const thisMonthStr = todayStr.substring(0, 7);

    // 1. Today's Revenue
    const todayRevenueRow = db.prepare(`
      SELECT SUM(total) as total 
      FROM bills 
      WHERE date(bill_date) = date(?) AND payment_status = 'Paid'
    `).get(todayStr);
    const todayRevenue = todayRevenueRow ? (todayRevenueRow.total || 0) : 0;

    // 2. Outstanding Dues (Unpaid Bills)
    const unpaidRow = db.prepare(`
      SELECT COUNT(*) as count, SUM(total) as total 
      FROM bills 
      WHERE payment_status = 'Unpaid'
    `).get();
    const unpaidCount = unpaidRow ? (unpaidRow.count || 0) : 0;
    const unpaidTotal = unpaidRow ? (unpaidRow.total || 0) : 0;

    // 3. This Month's Collections
    const monthlyTotalRow = db.prepare(`
      SELECT SUM(total) as total 
      FROM bills 
      WHERE strftime('%Y-%m', bill_date) = ? AND payment_status = 'Paid'
    `).get(thisMonthStr);
    const thisMonthRevenue = monthlyTotalRow ? (monthlyTotalRow.total || 0) : 0;

    // 4. All-Time Collections
    const allTimeTotalRow = db.prepare(`
      SELECT SUM(total) as total 
      FROM bills 
      WHERE payment_status = 'Paid'
    `).get();
    const allTimeRevenue = allTimeTotalRow ? (allTimeTotalRow.total || 0) : 0;

    // 5. Unique Patients Count
    const uniquePatientsRow = db.prepare(`
      SELECT COUNT(DISTINCT mobile) as count FROM consultations
    `).get();
    const uniquePatients = uniquePatientsRow ? (uniquePatientsRow.count || 0) : 0;

    // 6. Average Bill Value
    const paidBillsRow = db.prepare(`
      SELECT COUNT(*) as count, SUM(total) as total FROM bills WHERE payment_status = 'Paid'
    `).get();
    const paidBillsCount = paidBillsRow ? (paidBillsRow.count || 0) : 0;
    const paidBillsTotal = paidBillsRow ? (paidBillsRow.total || 0) : 0;
    const avgBillValue = paidBillsCount > 0 ? (paidBillsTotal / paidBillsCount) : 0;

    // 7. Weekly Revenue Trend (Last 7 days of paid bills)
    const weeklyRevenue = db.prepare(`
      SELECT date(bill_date) as day, COUNT(*) as count, SUM(total) as total 
      FROM bills 
      WHERE payment_status = 'Paid' AND date(bill_date) >= date(?, '-6 days')
      GROUP BY day 
      ORDER BY day ASC
    `).all(todayStr);

    // 8. Monthly Revenue Trend (Last 6 months of paid bills)
    const monthlyRevenue = db.prepare(`
      SELECT strftime('%Y-%m', bill_date) as month, COUNT(*) as count, SUM(total) as total 
      FROM bills 
      WHERE payment_status = 'Paid' AND date(bill_date) >= date(?, '-6 months')
      GROUP BY month 
      ORDER BY month ASC
      LIMIT 6
    `).all(todayStr);

    // 9. Top 5 Dispensed Medicines (High-moving stock)
    const topMedicines = db.prepare(`
      SELECT item_name, SUM(issued_qty) as total_issued 
      FROM inventory_issues 
      GROUP BY item_name 
      ORDER BY total_issued DESC 
      LIMIT 5
    `).all();

    // 10. Top Stock Items with detail
    const topStock = db.prepare(`
      SELECT item_name, category, batch_no, expiry_date, received_qty, remaining_qty 
      FROM inventory 
      WHERE remaining_qty > 0 
      ORDER BY remaining_qty DESC 
      LIMIT 8
    `).all();

    // 11. Patient Demographics (New vs Returning)
    const newPatientsRow = db.prepare(`
      SELECT COUNT(*) as count FROM (
        SELECT mobile FROM consultations GROUP BY mobile HAVING COUNT(id) = 1
      )
    `).get();
    const newPatients = newPatientsRow ? (newPatientsRow.count || 0) : 0;

    const returningPatientsRow = db.prepare(`
      SELECT COUNT(*) as count FROM (
        SELECT mobile FROM consultations GROUP BY mobile HAVING COUNT(id) > 1
      )
    `).get();
    const returningPatients = returningPatientsRow ? (returningPatientsRow.count || 0) : 0;

    // Total Patient Visits
    const totalVisitsRow = db.prepare(`
      SELECT COUNT(*) as count FROM consultations
    `).get();
    const totalVisits = totalVisitsRow ? (totalVisitsRow.count || 0) : 0;

    const payload = {
      todayRevenue,
      unpaidCount,
      unpaidTotal,
      thisMonthRevenue,
      allTimeRevenue,
      uniquePatients,
      avgBillValue,
      weeklyRevenue,
      monthlyRevenue,
      topMedicines,
      topStock,
      patientStats: {
        newPatients,
        returningPatients,
        totalVisits
      }
    };

    event.reply('analytics-data-response', { success: true, data: payload });
  } catch (err) {
    console.error('get-analytics-data error:', err);
    event.reply('analytics-data-response', { success: false, error: err.message });
  }
});

// --- CUSTOMERS CRM CHANNELS ---
ipcMain.on('get-customers', (event) => {
  try {
    const rows = db.prepare('SELECT * FROM customers ORDER BY last_visit DESC').all();
    event.reply('customers-data', { success: true, rows });
  } catch(e) {
    console.error('get-customers error:', e);
    event.reply('customers-data', { success: false, rows: [], error: e.message });
  }
});

ipcMain.on('get-customer', (event, mobile) => {
  try {
    const row = db.prepare('SELECT * FROM customers WHERE mobile = ?').get(mobile);
    event.reply('customer-data', { success: true, data: row });
  } catch(e) {
    event.reply('customer-data', { success: false, data: null });
  }
});

ipcMain.on('search-customers', (event, term) => {
  try {
    const rows = db.prepare('SELECT * FROM customers WHERE name LIKE ? OR mobile LIKE ? ORDER BY last_visit DESC LIMIT 20').all(`%${term}%`, `%${term}%`);
    event.reply('customers-search-data', rows);
  } catch(e) {
    event.reply('customers-search-data', []);
  }
});

// --- SUPPLIER LEDGER CHANNELS ---
ipcMain.on('get-suppliers', (event) => {
  try {
    const rows = db.prepare('SELECT * FROM suppliers ORDER BY name ASC').all();
    event.reply('suppliers-data', { success: true, rows });
  } catch(e) {
    event.reply('suppliers-data', { success: false, rows: [], error: e.message });
  }
});

ipcMain.on('save-supplier', (event, supplier) => {
  try {
    if (supplier.id) {
      db.prepare('UPDATE suppliers SET name=?, contact=?, gstin=? WHERE id=?')
        .run(supplier.name, supplier.contact, supplier.gstin, supplier.id);
    } else {
      db.prepare('INSERT INTO suppliers (name, contact, gstin, balance) VALUES (?, ?, ?, 0)')
        .run(supplier.name, supplier.contact, supplier.gstin);
    }
    event.reply('supplier-saved', { success: true });
  } catch(e) {
    event.reply('supplier-saved', { success: false, error: e.message });
  }
});

ipcMain.on('add-supplier-payment', (event, supplierId, amount) => {
  try {
    db.prepare('UPDATE suppliers SET balance = balance + ? WHERE id = ?').run(amount, supplierId);
    event.reply('supplier-payment-added', { success: true });
  } catch(e) {
    event.reply('supplier-payment-added', { success: false, error: e.message });
  }
});

// --- EXPENSES CHANNELS ---
ipcMain.on('get-expenses', (event) => {
  try {
    const rows = db.prepare('SELECT * FROM expenses ORDER BY expense_date DESC, id DESC').all();
    event.reply('expenses-data', { success: true, rows });
  } catch (e) {
    event.reply('expenses-data', { success: false, rows: [], error: e.message });
  }
});

ipcMain.on('save-expense', (event, expense) => {
  try {
    if (expense.id) {
      db.prepare('UPDATE expenses SET expense_date=?, category=?, amount=?, description=?, payment_method=? WHERE id=?')
        .run(expense.expense_date, expense.category, expense.amount, expense.description, expense.payment_method, expense.id);
    } else {
      db.prepare('INSERT INTO expenses (expense_date, category, amount, description, payment_method) VALUES (?, ?, ?, ?, ?)')
        .run(expense.expense_date, expense.category, expense.amount, expense.description, expense.payment_method);
    }
    event.reply('expense-save-status', { success: true });
  } catch (e) {
    event.reply('expense-save-status', { success: false, error: e.message });
  }
});

ipcMain.on('delete-expense', (event, id) => {
  try {
    db.prepare('DELETE FROM expenses WHERE id=?').run(id);
    event.reply('expense-delete-status', { success: true });
  } catch (e) {
    event.reply('expense-delete-status', { success: false, error: e.message });
  }
});