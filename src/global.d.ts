interface Window {
  ipcRenderer: {
    send(channel: string, ...args: any[]): void;
    on(channel: string, listener: (event: any, ...args: any[]) => void): () => void;
  };
  basket: any[];
  globalEditRecordId: number | null;
  lastSavedConsultation: {
    mobile: string;
    name: string;
    basket: any[];
  } | null;
  toggleDrawer: () => void;
  openDrawer: () => void;
  closeDrawer: () => void;
  toggleTheme: () => void;
  fillBillPatient: (row: any) => void;
  searchPatients: () => void;
}

declare const ipcRenderer: Window['ipcRenderer'];
