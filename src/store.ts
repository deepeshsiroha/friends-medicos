import { writable, derived } from 'svelte/store';

export const activeTab = writable<string>('billing');
export const basket = writable<any[]>([]);
export const globalEditRecordId = writable<number | null>(null);
export const sidebarOpen = writable<boolean>(false);

// Toast notification store
export const toastMessage = writable<string>('');
export const toastVisible = writable<boolean>(false);

export function showToast(message: string) {
  toastMessage.set(message);
  toastVisible.set(true);
  setTimeout(() => {
    toastVisible.set(false);
  }, 4000);
}


// Settings store
export const currentSettings = writable<any>({
  pharmacy_name: 'Friends Medicos',
  pharmacy_address: 'Main Bazar, Narnaul, 123001 (Haryana)',
  pharmacy_contact: '+91 9999999999',
  pharmacy_gstin: '06AAAAA0000A1Z5',
  pharmacy_license: 'DL-12345-A',
  low_stock_threshold: '10',
  expiry_days_threshold: '90'
});

// Modals visibility and data stores
export interface StockRow {
  id: number;
  item_name: string;
  category?: string;
  batch_no?: string;
  pharmacy_name?: string;
  received_date?: string;
  received_qty: number;
  expiry_date?: string;
  issued_qty: number;
  remaining_qty: number;
  remarks?: string;
}

export const editStockModalData = writable<StockRow | null>(null);


export const previewModalData = writable<any | null>(null);
export const previewModalVisible = writable<boolean>(false);

// Global records and inventory
export const stockRows = writable<StockRow[]>([]);
export const issueRows = writable<any[]>([]);
export const billingHistory = writable<any[]>([]);
export const analyticsData = writable<any>(null);
export const suppliersList = writable<any[]>([]);
export const expensesList = writable<any[]>([]);

// Low Stock and Near Expiry derived stores
export const lowStockItems = derived([stockRows, currentSettings], ([$stockRows, $currentSettings]) => {
  const threshold = parseInt($currentSettings.low_stock_threshold || '10', 10);
  return ($stockRows || []).filter((r: any) => r.remaining_qty < threshold);
});

export const nearExpiryItems = derived([stockRows, currentSettings], ([$stockRows, $currentSettings]) => {
  const days = parseInt($currentSettings.expiry_days_threshold || '90', 10);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const thresholdDate = new Date(today.getTime() + days * 24 * 60 * 60 * 1000);
  return ($stockRows || []).filter((r: any) => {
    if (!r.expiry_date || r.remaining_qty <= 0) return false;
    return new Date(r.expiry_date) <= thresholdDate;
  });
});
