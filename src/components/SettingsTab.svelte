<script lang="ts">
  import { currentSettings, showToast } from '../store';

  let pharmacyName = '';
  let pharmacyAddress = '';
  let pharmacyContact = '';
  let pharmacyGstin = '';
  let pharmacyLicense = '';
  let autoDeleteExpired = false;
  let lowStockThreshold = '10';
  let expiryDaysThreshold = '90';

  $: {
    pharmacyName = $currentSettings.pharmacy_name || '';
    pharmacyAddress = $currentSettings.pharmacy_address || '';
    pharmacyContact = $currentSettings.pharmacy_contact || '';
    pharmacyGstin = $currentSettings.pharmacy_gstin || '';
    pharmacyLicense = $currentSettings.pharmacy_license || '';
    autoDeleteExpired = $currentSettings.auto_delete_expired === 'true';
    lowStockThreshold = $currentSettings.low_stock_threshold || '10';
    expiryDaysThreshold = $currentSettings.expiry_days_threshold || '90';
  }

  function submitSettings() {
    // Removed pharmacyName requirement so users can save address freely

    const config = {
      pharmacy_name: pharmacyName.trim(),
      pharmacy_address: pharmacyAddress.trim(),
      pharmacy_contact: pharmacyContact.trim(),
      pharmacy_gstin: pharmacyGstin.trim(),
      pharmacy_license: pharmacyLicense.trim(),
      auto_delete_expired: autoDeleteExpired ? 'true' : 'false',
      low_stock_threshold: lowStockThreshold.toString(),
      expiry_days_threshold: expiryDaysThreshold.toString()
    };

    ipcRenderer.send('save-settings', config);
    showToast("Settings saved successfully.");
  }
</script>

<div id="settings-tab" class="tab-content active">
    <div class="card" style="max-width: 600px; margin: 30px auto; padding: 30px;">
        <header>
            <h1 style="font-size:20px; margin-bottom:15px; font-family:'Outfit', sans-serif;">App Custom Header Settings</h1>
        </header>
        <span class="section-label">Pharmacy Information</span>
        <div class="form-group">
            <label for="set-pharmacy-name">Pharmacy Name</label>
            <input type="text" id="set-pharmacy-name" placeholder="e.g. Friends Medicos" bind:value={pharmacyName}>
        </div>
        <div class="form-group">
            <label for="set-pharmacy-address">Pharmacy Address</label>
            <input type="text" id="set-pharmacy-address" placeholder="e.g. Main Bazar, Narnaul, 123001 (Haryana)" bind:value={pharmacyAddress}>
        </div>
        <div class="form-group">
            <label for="set-pharmacy-contact">Contact Number</label>
            <input type="text" id="set-pharmacy-contact" placeholder="e.g. +91 9999999999" bind:value={pharmacyContact}>
        </div>

        <span class="section-label">Legal Information</span>
        <div class="form-group">
            <label for="set-pharmacy-license">Drug License No (DL)</label>
            <input type="text" id="set-pharmacy-license" placeholder="e.g. DL-12345-A" bind:value={pharmacyLicense}>
        </div>
        <div class="form-group">
            <label for="set-pharmacy-gstin">GSTIN Number (Optional)</label>
            <input type="text" id="set-pharmacy-gstin" placeholder="e.g. 06AAAAA0000A1Z5" bind:value={pharmacyGstin}>
        </div>

        <span class="section-label">Inventory & Alerts Settings</span>
        <div class="form-group">
            <label for="set-low-stock">Low Stock Warning Threshold (Quantity)</label>
            <input type="number" id="set-low-stock" placeholder="10" bind:value={lowStockThreshold}>
        </div>
        <div class="form-group">
            <label for="set-expiry-days">Near Expiry Warning Threshold (Days)</label>
            <input type="number" id="set-expiry-days" placeholder="90" bind:value={expiryDaysThreshold}>
        </div>
        <div class="form-group" style="display: flex; align-items: center; gap: 10px; margin-top: 10px; margin-bottom: 20px;">
            <input type="checkbox" id="set-auto-delete-expired" bind:checked={autoDeleteExpired} style="width: 18px; height: 18px; cursor: pointer; margin: 0;">
            <label for="set-auto-delete-expired" style="cursor: pointer; margin: 0; font-weight: 500; font-size: 13px; color: var(--text);">
                Auto-delete stock batches expired for more than 3 months
            </label>
        </div>

        <button class="btn-primary" on:click={submitSettings} style="margin-top: 15px; width: 100%;">
          Save Configuration Settings
        </button>
    </div>
</div>
