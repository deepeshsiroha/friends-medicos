<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { 
    billingHistory, previewModalVisible, previewModalData, showToast, currentSettings, stockRows
  } from '../store';
  import { jsPDF } from 'jspdf';

  let billMobile = '';
  let billName = '';
  let billPaymentMethod = 'Cash';
  let billPaymentStatus = 'Paid';
  let billRemarks = '';
  let billCgstTotal = 0;
  let billSgstTotal = 0;

  let currentSubTab = 'pos'; // 'pos' or 'history'

  let billItems: any[] = [];
  
  // Custom item inputs
  let customDesc = '';
  let customQty = 1;
  let customPrice = '';

  let billDiscount = 0;
  let billSubtotal = 0;
  let billTotal = 0;

  let billSearchQuery = '';
  let debounceTimeout: any;

  let mobileSuggestions: any[] = [];
  let showMobileSuggest = false;

  const mobileRegex = /^\+91\d{10}$/;
  let inventorySearchQuery = '';
  let inventorySuggestions: any[] = [];
  let showInventorySuggest = false;

  let showStockBrowseModal = false;
  let stockBrowseQuery = '';
  $: filteredBrowseStock = $stockRows.filter(row => {
    if (row.remaining_qty <= 0) return false;
    if (stockBrowseQuery) {
      const q = stockBrowseQuery.toLowerCase();
      return (row.item_name || '').toLowerCase().includes(q) ||
             (row.batch_no || '').toLowerCase().includes(q) ||
             (row.category || '').toLowerCase().includes(q);
    }
    return true;
  });

  function onInventorySearchChange(e: Event) {
    const val = (e.target as HTMLInputElement).value.toLowerCase();
    inventorySearchQuery = val;
    if (val.length >= 2) {
      inventorySuggestions = $stockRows.filter(r => 
        r.remaining_qty > 0 && 
        ((r.item_name || '').toLowerCase().includes(val) || (r.batch_no || '').toLowerCase().includes(val))
      ).slice(0, 15);
      showInventorySuggest = true;
    } else {
      showInventorySuggest = false;
    }
  }

  function addInventoryItem(row: any) {
    billItems = [
      ...billItems,
      {
        inventory_id: row.id,
        item_name: row.item_name,
        qty: 1,
        buying_price: row.unit_price || 0,
        unit_price: row.selling_price || row.unit_price || 0,
        gst_rate: row.gst_rate ?? 12.0,
        total: row.selling_price || row.unit_price || 0,
        cgst_amount: 0,
        sgst_amount: 0,
        max_qty: row.remaining_qty
      }
    ];
    calculateTotals();
    inventorySearchQuery = '';
    showInventorySuggest = false;
    showToast(`Added ${row.item_name} to bill`);
  }

  const handleCustomerSearchData = (event: any, rows: any) => {
    if (showMobileSuggest && document.activeElement === document.getElementById('bill-mobile')) {
      mobileSuggestions = rows || [];
    }
  };

  let unsubCustomerSearch: (() => void) | undefined;

  onMount(() => {
    // Initial fetch for billing list
    ipcRenderer.send('get-bills');
    unsubCustomerSearch = ipcRenderer.on('customers-search-data', handleCustomerSearchData);
  });

  onDestroy(() => {
    if (unsubCustomerSearch) unsubCustomerSearch();
  });
  function calculateTotals() {
    billCgstTotal = 0;
    billSgstTotal = 0;
    billSubtotal = billItems.reduce((sum, item) => {
      item.total = item.qty * (parseFloat(item.unit_price) || 0);
      
      const gstRate = item.gst_rate ?? 12.0;
      const taxAmount = item.total - (item.total / (1 + (gstRate / 100)));
      item.cgst_amount = taxAmount / 2;
      item.sgst_amount = taxAmount / 2;
      
      billCgstTotal += item.cgst_amount;
      billSgstTotal += item.sgst_amount;

      return sum + item.total;
    }, 0);
    billTotal = Math.max(0, billSubtotal - (billDiscount || 0));
  }

  function addCustomBillItem() {
    if (!customDesc) {
      alert("Please enter a custom description!");
      return;
    }
    const priceFloat = parseFloat(customPrice);
    if (isNaN(priceFloat) || priceFloat < 0) {
      alert("Please enter a valid price!");
      return;
    }

    billItems = [
      ...billItems,
      {
        item_name: customDesc.trim(),
        qty: customQty,
        buying_price: priceFloat,
        unit_price: priceFloat,
        gst_rate: 12.0, // Default for custom items, could make adjustable
        total: customQty * priceFloat,
        cgst_amount: 0,
        sgst_amount: 0,
        max_qty: 9999
      }
    ];

    customDesc = '';
    customQty = 1;
    customPrice = '';
    calculateTotals();
  }

  function removeBillItem(index: number) {
    billItems = billItems.filter((_, idx) => idx !== index);
    calculateTotals();
  }

  function updateItemQty(index: number, qty: number) {
    if (qty < 1) return;
    billItems[index].qty = qty;
    billItems = [...billItems];
    calculateTotals();
  }

  function updateItemPrice(index: number, priceStr: string) {
    const price = parseFloat(priceStr) || 0;
    billItems[index].unit_price = price;
    billItems = [...billItems];
    calculateTotals();
  }



  function handleMobileInput(val: string) {
    if (val === '') return '';
    let digits = val.replace(/[^\d+]/g, '');
    if (digits === '+' || digits === '+9' || digits === '+91') return digits;
    
    if (digits.startsWith('+91')) {
      digits = digits.substring(3);
    } else if (digits.startsWith('91') && digits.length > 10) {
      digits = digits.substring(2);
    }
    
    digits = digits.replace(/[^\d]/g, '').substring(0, 10);
    return '+91' + digits;
  }

  function onMobileChange(e: Event) {
    const input = e.target as HTMLInputElement;
    billMobile = handleMobileInput(input.value);
    input.value = billMobile; // Force DOM update for truncated values

    if (billMobile.length >= 4) {
      showMobileSuggest = true;
      ipcRenderer.send('search-customers', billMobile);
    } else {
      showMobileSuggest = false;
    }
  }

  function fillBillPatient(row: any) {
    billMobile = row.mobile || '';
    billName = row.name || '';
    showMobileSuggest = false;
  }

  function submitGenerateBill() {
    if (billMobile && !mobileRegex.test(billMobile)) {
      alert("Mobile Number must start with +91 followed by exactly 10 digits");
      return;
    }
    // Patient name is not mandatory
    if (billItems.length === 0) {
      alert("Add at least one item to the invoice!");
      return;
    }

    const bill = {
      patient_mobile: billMobile,
      patient_name: billName,
      subtotal: billSubtotal,
      discount: billDiscount,
      total: billTotal,
      cgst_total: billCgstTotal,
      sgst_total: billSgstTotal,
      payment_method: billPaymentMethod,
      payment_status: billPaymentStatus,
      remarks: billRemarks
    };

    ipcRenderer.send('save-bill', { bill, items: billItems });
    clearForm();
  }

  function clearForm() {
    billMobile = '';
    billName = '';
    billPaymentMethod = 'Cash';
    billPaymentStatus = 'Paid';
    billRemarks = '';
    billItems = [];
    billDiscount = 0;
    billSubtotal = 0;
    billTotal = 0;
    showMobileSuggest = false;
  }

  function searchInvoices() {
    clearTimeout(debounceTimeout);
    debounceTimeout = setTimeout(() => {
      if (billSearchQuery.trim()) {
        ipcRenderer.send('search-bills', billSearchQuery.trim());
      } else {
        ipcRenderer.send('get-bills');
      }
    }, 300);
  }

  function togglePaymentStatus(row: any) {
    const nextStatus = row.payment_status === 'Paid' ? 'Unpaid' : 'Paid';
    if (confirm(`Do you want to change payment status of INV-${row.id} to ${nextStatus}?`)) {
      ipcRenderer.send('toggle-bill-status', { billId: row.id, status: nextStatus });
    }
  }

  function deleteInvoice(row: any) {
    if (confirm(`Are you sure you want to delete invoice INV-${row.id}?`)) {
      ipcRenderer.send('delete-bill', row.id);
      showToast("Invoice deleted successfully!");
    }
  }

  function formatDateIST(dateVal: string | Date, includeTime = false) {
    if (!dateVal) return '--';
    const date = new Date(dateVal);
    
    const dStr = date.toLocaleDateString('en-IN', {
      timeZone: 'Asia/Kolkata',
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });

    const tStr = date.toLocaleTimeString('en-IN', {
      timeZone: 'Asia/Kolkata',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    });

    return includeTime ? `${dStr} - ${tStr}` : dStr;
  }

  function compileInvoicePDF(bill: any) {
    const doc = new jsPDF({ orientation: "landscape", format: "a5" });
    const formattedDate = formatDateIST(bill.bill_date || new Date(), true);

    doc.setFont("helvetica", "bold"); doc.setFontSize(18);
    doc.text($currentSettings.pharmacy_name ?? "Friends Medicos", 105, 15, { align: "center" });
    doc.setFontSize(10); doc.setFont("helvetica", "normal");
    doc.text($currentSettings.pharmacy_address ?? "Main Bazar, Narnaul, 123001 (Haryana)", 105, 21, { align: "center" });
    doc.setFont("helvetica", "bold"); doc.text(`Contact: ${$currentSettings.pharmacy_contact ?? '+91 9999999999'}`, 105, 27, { align: "center" });
    
    let sub = [];
    if ($currentSettings.pharmacy_license) sub.push(`DL: ${$currentSettings.pharmacy_license}`);
    if ($currentSettings.pharmacy_gstin) sub.push(`GSTIN: ${$currentSettings.pharmacy_gstin}`);
    if (sub.length > 0) {
      doc.setFont("helvetica", "normal"); doc.text(sub.join(' | '), 105, 32, { align: "center" });
    }

    // Draw Watermark
    try {
      const watermarkImg = document.getElementById('pdf-watermark') as HTMLImageElement;
      if (watermarkImg && watermarkImg.complete && watermarkImg.naturalWidth !== 0) {
        const canvas = document.createElement('canvas');
        canvas.width = watermarkImg.naturalWidth;
        canvas.height = watermarkImg.naturalHeight;
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.drawImage(watermarkImg, 0, 0);
          const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
          const data = imgData.data;
          for (let i = 0; i < data.length; i += 4) {
            const r = data[i];
            const g = data[i+1];
            const b = data[i+2];
            if (r > 240 && g > 240 && b > 240) {
              data[i+3] = 0;
            } else {
              data[i+3] = Math.round(data[i+3] * 0.10);
            }
          }
          ctx.putImageData(imgData, 0, 0);
          const wmBase64 = canvas.toDataURL('image/png');
          const wmSize = 140;
          doc.addImage(wmBase64, 'PNG', (210 - wmSize)/2, (148 - wmSize)/2 + 10, wmSize, wmSize);
        }
      }
    } catch (err) {
      console.warn('Failed to add watermark to PDF', err);
    }

    doc.setFont("helvetica", "bold"); doc.setFontSize(14);
    doc.text("INVOICE RECEIPT", 105, 45, { align: "center" });

    doc.setFontSize(10); doc.setFont("helvetica", "normal");
    doc.rect(15, 52, 180, 24);
    doc.text(`Patient Name: ${bill.patient_name}`, 18, 58);
    doc.text(`Mobile Number: ${bill.patient_mobile}`, 18, 64);
    doc.text(`Invoice No: INV-${bill.id}`, 192, 58, { align: "right" });
    doc.text(`Date & Time: ${formattedDate}`, 192, 64, { align: "right" });
    doc.text(`Payment Mode: ${bill.payment_method} (${bill.payment_status})`, 18, 70);

    let y = 95;
    doc.setFont("helvetica", "bold");
    doc.line(15, 80, 195, 80);
    doc.text("S.No.", 18, 85);
    doc.text("Item Description", 35, 85);
    doc.text("Qty", 125, 85, { align: "center" });
    doc.text("Unit Price (Rs.)", 155, 85, { align: "right" });
    doc.text("Total (Rs.)", 192, 85, { align: "right" });
    doc.line(15, 88, 195, 88);

    doc.setFont("helvetica", "normal");
    const items = bill.items || [];
    items.forEach((item: any, index: number) => {
      const descriptionLines = doc.splitTextToSize(item.item_name || '', 75);
      
      doc.text((index + 1).toString(), 18, y);
      doc.text(descriptionLines[0] || '', 35, y);
      doc.text(item.qty.toString(), 125, y, { align: "center" });
      doc.text(parseFloat(item.unit_price).toFixed(2), 155, y, { align: "right" });
      doc.text(parseFloat(item.total).toFixed(2), 192, y, { align: "right" });
      
      for (let i = 1; i < descriptionLines.length; i++) {
        y += 5;
        doc.text(descriptionLines[i], 35, y);
      }
      
      y += 8;
    });

    doc.line(15, y - 3, 195, y - 3);

    y += 4;
    doc.text("Subtotal:", 145, y, { align: "right" });
    doc.text(`Rs. ${parseFloat(bill.subtotal).toFixed(2)}`, 192, y, { align: "right" });

    y += 6;
    doc.text("Discount:", 145, y, { align: "right" });
    doc.text(`Rs. ${parseFloat(bill.discount).toFixed(2)}`, 192, y, { align: "right" });

    y += 8;
    doc.setFont("helvetica", "bold");
    doc.text("Grand Total:", 145, y, { align: "right" });
    doc.text(`Rs. ${parseFloat(bill.total).toFixed(2)}`, 192, y, { align: "right" });

    doc.setFont("helvetica", "normal");
    y += 6;
    doc.setFontSize(8);
    const cgst = parseFloat(bill.cgst_total || 0).toFixed(2);
    const sgst = parseFloat(bill.sgst_total || 0).toFixed(2);
    doc.text(`(Inclusive of GST - CGST: Rs. ${cgst} | SGST: Rs. ${sgst})`, 192, y, { align: "right" });

    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.text(`Thank you for visiting ${$currentSettings.pharmacy_name ?? "Friends Medicos"}!`, 15, y + 15);
    doc.text("Authorized Signature / Seal", 195, y + 25, { align: "right" });
    doc.line(155, y + 20, 195, y + 20);

    return doc;
  }

  function viewInvoice(bill: any) {
    const doc = compileInvoicePDF(bill);
    previewModalData.set(bill);
    previewModalVisible.set(true);
    setTimeout(() => {
      const modal = document.getElementById('preview-modal');
      const iframe = document.getElementById('preview-iframe') as HTMLIFrameElement;
      if (modal) {
        const title = modal.querySelector('h3');
        if (title) title.innerText = `Invoice Preview — INV-${bill.id} | ${bill.patient_name}`;
      }
      if (iframe) {
        iframe.src = doc.output('bloburl');
      }
    }, 50);
  }

  function printInvoiceDirect(bill: any) {
    const doc = compileInvoicePDF(bill);
    const pdfData = doc.output('arraybuffer');
    const dateObj = bill.bill_date ? new Date(bill.bill_date) : new Date();
    const dd = String(dateObj.getDate()).padStart(2, '0');
    const mm = String(dateObj.getMonth() + 1).padStart(2, '0');
    const yyyy = dateObj.getFullYear();
    const dateStr = `${dd}-${mm}-${yyyy}`;
    const patientCleanName = bill.patient_name.replace(/\s+/g, '_');
    const fileName = `Receipt_INV-${bill.id}_${patientCleanName}_${dateStr}.pdf`;

    ipcRenderer.send('save-pdf', {
      fileName: fileName,
      pdfData: pdfData,
      subFolder: 'Bills'
    });
  }

  onMount(() => {
    const handleAutoPrintOnSave = (e: any) => {
      const billId = e.detail;
      ipcRenderer.send('get-bill-details', billId);
    };

    const handleBillDetailsData = (event: any, res: any) => {
      if (res.success && res.bill) {
        const billWithItems = { ...res.bill, items: res.items || [] };
        printInvoiceDirect(billWithItems);
      }
    };

    window.addEventListener('auto-print-invoice-saved', handleAutoPrintOnSave);
    const unsubBillDetails = ipcRenderer.on('bill-details-data', handleBillDetailsData);

    return () => {
      window.removeEventListener('auto-print-invoice-saved', handleAutoPrintOnSave);
      if (unsubBillDetails) unsubBillDetails();
    };
  });

  function clickOutside(node: HTMLElement, callback: () => void) {
    const handleOutsideClick = (e: MouseEvent) => {
      if (node && !node.contains(e.target as Node)) {
        callback();
      }
    };
    document.addEventListener('click', handleOutsideClick);
    return {
      destroy() {
        document.removeEventListener('click', handleOutsideClick);
      }
    };
  }
</script>

<div id="billing-tab" class="tab-content active">
    <div class="billing-top-bar" style="margin-bottom: 15px; display: flex; gap: 10px;">
        <button class="btn-sub-tab {currentSubTab === 'pos' ? 'active' : ''}" on:click={() => currentSubTab = 'pos'}>Point of Sale</button>
        <button class="btn-sub-tab {currentSubTab === 'history' ? 'active' : ''}" on:click={() => currentSubTab = 'history'}>Billing History</button>
    </div>

    {#if currentSubTab === 'pos'}
    <div class="split-viewport" style="display: flex; gap: 20px; height: calc(100% - 50px);">

        <!-- Left Side: Stock Browser Grid -->
        <div style="flex: 1.2; display: flex; flex-direction: column; gap: 15px; overflow: hidden; position: relative; z-index: 10;">
            <div class="card" style="padding: 15px; display: flex; flex-direction: column; height: 100%; gap: 10px; background: var(--bg); border: none;">
                <input type="text" placeholder="🔍 Search stock by name, batch, category..." bind:value={stockBrowseQuery} style="padding: 10px 14px; font-size: 14px; border-radius: 8px; border: 1px solid var(--border); background: var(--card-bg); color: var(--text); width: 100%;">
                
                <div style="flex: 1; overflow-y: auto; display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; align-content: start; padding-right: 5px; padding-top: 5px;">
                    {#each filteredBrowseStock as row}
                        <!-- svelte-ignore a11y-click-events-have-key-events -->
                        <!-- svelte-ignore a11y-no-static-element-interactions -->
                        <div class="stock-card" on:click={() => addInventoryItem(row)} style="border: 1px solid var(--card-border); border-radius: 8px; padding: 12px; cursor: pointer; background: var(--card-bg); transition: transform 0.1s, border-color 0.1s; display: flex; flex-direction: column; justify-content: space-between;">
                            <div>
                                <div style="font-weight: 600; margin-bottom: 4px; font-size: 14px; line-height: 1.3;">{row.item_name}</div>
                                <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 12px;">{row.category || 'Tablet'} • {row.batch_no || 'N/A'}</div>
                            </div>
                            <div style="display: flex; justify-content: space-between; align-items: flex-end;">
                                <div style="color: var(--primary); font-weight: bold; font-size: 15px;">₹{parseFloat(row.selling_price || row.unit_price || 0).toFixed(2)}</div>
                                <div style="font-size: 11px; font-weight: 600; padding: 3px 6px; border-radius: 4px; background: rgba(var(--primary-rgb), 0.1);">Stock: {row.remaining_qty}</div>
                            </div>
                        </div>
                    {/each}
                    {#if filteredBrowseStock.length === 0}
                        <div style="grid-column: 1 / -1; padding: 30px; text-align: center; color: var(--text-muted);">
                            No available stock matching your search.
                        </div>
                    {/if}
                </div>
            </div>
        </div>

        <!-- Right Side: Cart & Patient -->
        <div style="flex: 1; display: flex; flex-direction: column; gap: 15px; overflow: hidden;">

                <div style="display: flex; gap: 12px;" use:clickOutside={() => showMobileSuggest = false}>
                    <div class="form-group" style="flex: 1; position: relative;">
                        <label for="bill-mobile">Patient Mobile</label>
                        <input type="text" id="bill-mobile" placeholder="+91..." autocomplete="off" value={billMobile} on:input={onMobileChange} on:focus={() => { if (billMobile === '') billMobile = '+91'; showMobileSuggest = true; }} on:blur={() => { if (billMobile === '+' || billMobile === '+9' || billMobile === '+91') billMobile = ''; }}>
                        
                        {#if showMobileSuggest && mobileSuggestions.length > 0}
                          <div id="bill-mobile-suggest" class="suggestions-dropdown" style="display: block; top: 100%; z-index: 2000; min-width: 280px;">
                            {#each mobileSuggestions as row}
                              <!-- svelte-ignore a11y-click-events-have-key-events -->
                              <!-- svelte-ignore a11y-no-static-element-interactions -->
                              <div class="suggestion-item" on:click={() => fillBillPatient(row)}>
                                <strong>{row.mobile}</strong><span>{row.name}</span>
                              </div>
                            {/each}
                          </div>
                        {/if}
                    </div>
                    <div class="form-group" style="flex: 1.2;">
                        <label for="bill-name">Patient Name</label>
                        <input type="text" id="bill-name" placeholder="Patient Name" bind:value={billName}>
                    </div>
                </div>

            <div class="card" style="padding: 20px; flex: 1; display: flex; flex-direction: column; gap: 12px; position: relative; z-index: 5;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span class="section-label" style="margin-top: 0; margin-bottom: 0;">Basket</span>
                </div>

                <div style="flex: 1; overflow-y: auto; max-height: 250px; border: 1px solid var(--border); border-radius: 6px; background: rgba(0,0,0,0.01);">
                    <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                        <thead>
                            <tr style="background: rgba(0,0,0,0.02); text-align: left; font-size: 13px; color: var(--text-muted);">
                                <th style="padding: 8px 10px;">Item Description</th>
                                <th style="padding: 8px 10px; text-align: center; width: 60px;">Qty</th>
                                <th style="padding: 8px 10px; text-align: right; width: 80px;">Buy (₹)</th>
                                <th style="padding: 8px 10px; text-align: right; width: 90px;">Sell (₹)</th>
                                <th style="padding: 8px 10px; text-align: right; width: 100px;">Total</th>
                                <th style="padding: 8px 10px; text-align: center; width: 50px;">Remove</th>
                            </tr>
                        </thead>
                        <tbody id="bill-items-table-body">
                          {#each billItems as item, index}
                            <tr style="border-bottom: 1px solid var(--border); height: 40px;">
                              <td style="padding: 5px 10px;">{item.item_name}</td>
                              <td style="padding: 5px 10px; text-align: center;">
                                <input type="number" value={item.qty} min="1" on:input={(e) => updateItemQty(index, parseInt(e.currentTarget.value) || 1)}
                                  style="width: 50px; text-align: center; border: 1px solid var(--border); border-radius: 4px; padding: 2px; background: var(--bg); color: var(--text);" />
                              </td>
                              <td style="padding: 5px 10px; text-align: right; color: var(--text-muted); font-size: 12px; vertical-align: middle;">
                                ₹{parseFloat(item.buying_price || 0).toFixed(2)}
                              </td>
                              <td style="padding: 5px 10px; text-align: right;">
                                <input type="number" value={item.unit_price} min="0" step="any" on:input={(e) => updateItemPrice(index, e.currentTarget.value)}
                                  style="width: 70px; text-align: right; border: 1px solid var(--border); border-radius: 4px; padding: 2px; background: var(--bg); color: var(--text);" />
                              </td>
                              <td style="padding: 5px 10px; text-align: right; font-weight: 500;">₹{item.total.toFixed(2)}</td>
                              <td style="padding: 5px 10px; text-align: center;">
                                <!-- svelte-ignore a11y-click-events-have-key-events -->
                                <!-- svelte-ignore a11y-no-static-element-interactions -->
                                <span class="delete-row-btn" on:click={() => removeBillItem(index)} style="cursor: pointer; color: var(--warn); font-weight: bold;">✕</span>
                              </td>
                            </tr>
                          {/each}
                          {#if billItems.length === 0}
                            <tr>
                              <td colspan="5" style="padding: 20px; text-align: center; color: var(--text-muted);">
                                No items added. Search stock or add a custom item.
                              </td>
                            </tr>
                          {/if}
                        </tbody>
                    </table>
                </div>

                <!-- Add Custom Item Row -->
                <div style="display: flex; gap: 8px; align-items: flex-end; border-top: 1px dashed var(--border); padding-top: 12px;">
                    <div class="form-group" style="flex: 2; margin-bottom: 0;">
                        <label for="bill-custom-desc" style="font-size: 11px;">Custom Description</label>
                        <input type="text" id="bill-custom-desc" placeholder="e.g. Consultation Fee / ECG"
                            style="padding: 6px 10px; font-size: 12px;" bind:value={customDesc}>
                    </div>
                    <div class="form-group" style="flex: 0.5; margin-bottom: 0;">
                        <label for="bill-custom-qty" style="font-size: 11px;">Qty</label>
                        <input type="number" id="bill-custom-qty" min="1"
                            style="padding: 6px 10px; font-size: 12px; text-align: center;" bind:value={customQty}>
                    </div>
                    <div class="form-group" style="flex: 0.8; margin-bottom: 0;">
                        <label for="bill-custom-price" style="font-size: 11px;">Price (₹)</label>
                        <input type="number" id="bill-custom-price" placeholder="Price" min="0"
                            style="padding: 6px 10px; font-size: 12px; text-align: right;" bind:value={customPrice}>
                    </div>
                    <button class="btn-primary" on:click={addCustomBillItem}
                        style="padding: 8px 12px; margin: 0; font-size: 12px; border-radius: 6px; height: 32px;">Add</button>
                </div>
            </div>

            <div class="card" style="padding: 20px; display: flex; flex-direction: column; gap: 12px;">
                <div style="display: flex; gap: 15px;">
                    <div style="flex: 1.2; display: flex; flex-direction: column; gap: 10px;">
                        <div style="display: flex; gap: 10px;">
                            <div class="form-group" style="flex: 1; margin-bottom: 0;">
                                <label for="bill-payment-method">Method</label>
                                <select id="bill-payment-method" bind:value={billPaymentMethod}
                                    style="padding: 8px; border: 1px solid var(--border); border-radius: 6px; background: var(--card-bg); color: var(--text);">
                                    <option value="Cash">Cash</option>
                                    <option value="UPI / GPay">UPI / GPay</option>
                                    <option value="Card">Card</option>
                                </select>
                            </div>
                            <div class="form-group" style="flex: 1; margin-bottom: 0;">
                                <label for="bill-payment-status">Status</label>
                                <select id="bill-payment-status" bind:value={billPaymentStatus}
                                    style="padding: 8px; border: 1px solid var(--border); border-radius: 6px; background: var(--card-bg); color: var(--text);">
                                    <option value="Paid">Paid</option>
                                    <option value="Unpaid">Unpaid</option>
                                </select>
                            </div>
                        </div>
                        <div class="form-group" style="margin-bottom: 0;">
                            <label for="bill-remarks">Remarks / Notes</label>
                            <input type="text" id="bill-remarks" bind:value={billRemarks}
                                placeholder="Optional notes (e.g. discount applied)"
                                style="padding: 6px 10px; font-size: 12px;">
                        </div>
                    </div>

                    <!-- Bill Summary Card -->
                    <div
                        style="flex: 0.8; background: rgba(0,0,0,0.02); padding: 12px; border-radius: 8px; border: 1px solid var(--border); display: flex; flex-direction: column; gap: 8px; justify-content: center;">
                        <div
                            style="display: flex; justify-content: space-between; font-size: 12px; color: var(--text-muted);">
                            <span>Subtotal:</span>
                            <span id="bill-sum-subtotal">₹{billSubtotal.toFixed(2)}</span>
                        </div>
                        <div
                            style="display: flex; justify-content: space-between; font-size: 12px; color: var(--text-muted); align-items: center;">
                            <span>Discount (₹):</span>
                            <input type="number" id="bill-discount" min="0" bind:value={billDiscount} on:input={calculateTotals}
                                style="width: 60px; padding: 2px 4px; font-size: 12px; text-align: right; border: 1px solid var(--border); border-radius: 4px; background: var(--bg); color: var(--text);">
                        </div>
                        <div
                            style="display: flex; justify-content: space-between; font-weight: bold; font-size: 14px; border-top: 1px solid var(--border); padding-top: 6px; color: var(--primary);">
                            <span>Total:</span>
                            <span id="bill-sum-total">₹{billTotal.toFixed(2)}</span>
                        </div>
                    </div>
                </div>

                <button class="btn-primary" on:click={submitGenerateBill}
                    style="width: 100%; margin-top: 5px; font-size: 14px; padding: 10px 0; border-radius: 8px;">
                    Generate Bill & Print Receipt
                </button>
            </div>
        </div>

    </div>

    {:else}
    <!-- Billing History -->
    <div class="card" style="flex: 1; display: flex; flex-direction: column; padding: 20px; gap: 15px; height: calc(100% - 50px);">
        <header
            style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 10px;">
            <h2 style="margin: 0; font-size: 18px; font-family: 'Outfit', sans-serif;">Billing History</h2>
            <input type="text" id="bill-search-input" on:input={searchInvoices} bind:value={billSearchQuery}
                placeholder="Search patient name or mobile..."
                style="width: 230px; padding: 6px 12px; font-size: 12px; border-radius: 6px; margin: 0;">
        </header>

        <div style="flex: 1; overflow-y: auto;">
            <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                <thead>
                    <tr style="border-bottom: 2px solid var(--border); background: var(--bg); text-align: left; height: 35px;">
                        <th style="padding: 5px 8px; width: 60px;">Inv No</th>
                        <th style="padding: 5px 8px; width: 85px;">Date</th>
                        <th style="padding: 5px 8px;">Patient</th>
                        <th style="padding: 5px 8px; width: 140px;">Remarks</th>
                        <th style="padding: 5px 8px; text-align: right; width: 75px;">Amount</th>
                        <th style="padding: 5px 8px; text-align: center; width: 70px;">Method</th>
                        <th style="padding: 5px 8px; text-align: center; width: 75px;">Status</th>
                        <th style="padding: 5px 8px; text-align: right; width: 140px;">Actions</th>
                    </tr>
                </thead>
                <tbody id="billing-history-table-body">
                    {#each $billingHistory as row}
                    <tr style="border-bottom: 1px solid var(--border); height: 45px;">
                        <td style="padding: 5px 8px;">INV-{row.id}</td>
                        <td style="padding: 5px 8px;">{formatDateIST(row.bill_date)}</td>
                        <td style="padding: 5px 8px;">
                            <strong>{row.patient_name}</strong><br><small>{row.patient_mobile}</small>
                        </td>
                        <td style="padding: 5px 8px; max-width: 140px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title={row.remarks || ''}>
                            {row.remarks || '--'}
                        </td>
                        <td style="padding: 5px 8px; text-align: right; font-weight: 500;">₹{row.total.toFixed(2)}</td>
                        <td style="padding: 5px 8px; text-align: center;">{row.payment_method}</td>
                        <td style="padding: 5px 8px; text-align: center;">
                            <!-- svelte-ignore a11y-click-events-have-key-events -->
                            <!-- svelte-ignore a11y-no-static-element-interactions -->
                            <span on:click={() => togglePaymentStatus(row)} style="cursor: pointer; font-weight: bold; padding: 2px 6px; border-radius: 4px; font-size: 11px;
                            background: {row.payment_status === 'Paid' ? 'rgba(76, 175, 80, 0.1)' : 'rgba(244, 67, 54, 0.1)'};
                            color: {row.payment_status === 'Paid' ? '#4caf50' : '#f44336'};">
                            {row.payment_status}
                            </span>
                        </td>
                        <td style="padding: 5px 8px; text-align: right;">
                            <div style="display: flex; gap: 8px; justify-content: flex-end; font-size: 12px;">
                            <!-- svelte-ignore a11y-click-events-have-key-events -->
                            <!-- svelte-ignore a11y-no-static-element-interactions -->
                            <span class="action-link" on:click={() => viewInvoice(row)}>View</span>
                            <!-- svelte-ignore a11y-click-events-have-key-events -->
                            <!-- svelte-ignore a11y-no-static-element-interactions -->
                            <span class="action-link" on:click={() => printInvoiceDirect(row)}>Print</span>
                            <!-- svelte-ignore a11y-click-events-have-key-events -->
                            <!-- svelte-ignore a11y-no-static-element-interactions -->
                            <span class="delete-row-btn" on:click={() => deleteInvoice(row)}>✕</span>
                            </div>
                        </td>
                    </tr>
                    {/each}
                    {#if $billingHistory.length === 0}
                    <tr>
                        <td colspan="8" style="text-align: center; color: var(--text-muted); padding: 30px;">
                        No invoices generated.
                        </td>
                    </tr>
                    {/if}
                </tbody>
            </table>
        </div>
    </div>
    {/if}
</div>
