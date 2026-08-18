const { contextBridge, ipcRenderer } = require('electron');

// Expose a safe, whitelisted subset of IPC renderer APIs
contextBridge.exposeInMainWorld('ipcRenderer', {
    send: (channel, ...args) => {
        const allowedSendChannels = [
            'save-consultation',
            'add-stock',
            'update-stock',
            'get-inventory',
            'delete-stock',
            'search-stock-items',
            'get-records',
            'search-records',
            'save-pdf',
            'get-settings',
            'save-settings',
            'get-patient-summary',
            'get-dispensed-items',
            'return-medicine',
            'save-bill',
            'get-bills',
            'search-bills',
            'delete-bill',
            'toggle-bill-status',
            'get-latest-consultation',
            'get-opd-register',
            'get-bill-details',
            'get-analytics-data',
            'get-customers',
            'search-customers',
            'get-suppliers',
            'save-supplier',
            'add-supplier-payment',
            'get-supplier-bills',
            'save-supplier-bill',
            'pay-supplier-bill',
            'get-expenses',
            'save-expense',
            'delete-expense'
        ];
        if (allowedSendChannels.includes(channel)) {
            ipcRenderer.send(channel, ...args);
        } else {
            console.warn(`Blocked unauthorized IPC send on channel: ${channel}`);
        }
    },
    on: (channel, listener) => {
        const allowedReceiveChannels = [
            'records-data',
            'stock-suggestions',
            'inventory-data',
            'save-status',
            'settings-data',
            'patient-summary-data',
            'dispensed-items-data',
            'return-status',
            'bills-data',
            'bill-save-status',
            'latest-consultation-data',
            'opd-register-data',
            'bill-details-data',
            'analytics-data-response',
            'customers-data',
            'customers-search-data',
            'suppliers-data',
            'supplier-save-status',
            'supplier-payment-status',
            'toggle-payment-status',
            'supplier-saved',
            'supplier-payment-added',
            'supplier-bills-data',
            'supplier-bill-saved',
            'supplier-bill-paid',
            'expenses-data',
            'expense-save-status',
            'expense-delete-status'
        ];
        if (allowedReceiveChannels.includes(channel)) {
            const subscription = (event, ...args) => listener(null, ...args);
            ipcRenderer.on(channel, subscription);
            // Return clean-up function
            return () => ipcRenderer.removeListener(channel, subscription);
        } else {
            console.warn(`Blocked unauthorized IPC listener on channel: ${channel}`);
        }
    }
});
