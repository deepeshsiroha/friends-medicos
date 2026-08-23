import re

with open('src/components/BillingTab.svelte', 'r') as f:
    content = f.read()

old_func_pattern = r'function compileInvoicePDF\(bill: any\) \{.*?\n  function viewInvoice\(bill: any\)'
old_func_match = re.search(old_func_pattern, content, flags=re.DOTALL)

if old_func_match:
    new_func = """function compileInvoicePDF(bill: any) {
    const doc = new jsPDF({ orientation: "landscape", format: "a5" });
    const formattedDate = formatDateIST(bill.bill_date || new Date(), true);

    doc.setFont("helvetica", "bold"); doc.setFontSize(16);
    doc.text($currentSettings.pharmacy_name ?? "Friends Medicos", 105, 12, { align: "center" });
    doc.setFontSize(9); doc.setFont("helvetica", "normal");
    doc.text($currentSettings.pharmacy_address ?? "Main Bazar, Narnaul, 123001 (Haryana)", 105, 17, { align: "center" });
    doc.setFont("helvetica", "bold"); doc.text(`Contact: ${$currentSettings.pharmacy_contact ?? '+91 9999999999'}`, 105, 22, { align: "center" });
    
    let sub = [];
    if ($currentSettings.pharmacy_license) sub.push(`DL: ${$currentSettings.pharmacy_license}`);
    if ($currentSettings.pharmacy_gstin) sub.push(`GSTIN: ${$currentSettings.pharmacy_gstin}`);
    if (sub.length > 0) {
      doc.setFont("helvetica", "normal"); doc.text(sub.join(' | '), 105, 26, { align: "center" });
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
          doc.addImage(wmBase64, 'PNG', (210 - wmSize)/2, (148 - wmSize)/2 + 5, wmSize, wmSize);
        }
      }
    } catch (err) {
      console.warn('Failed to add watermark to PDF', err);
    }

    doc.setFont("helvetica", "bold"); doc.setFontSize(12);
    doc.text("INVOICE RECEIPT", 105, 34, { align: "center" });

    doc.setFontSize(9); doc.setFont("helvetica", "normal");
    doc.rect(15, 38, 180, 18);
    doc.text(`Patient Name: ${bill.patient_name}`, 18, 44);
    doc.text(`Mobile Number: ${bill.patient_mobile}`, 18, 51);
    doc.text(`Invoice No: INV-${bill.id}`, 192, 44, { align: "right" });
    doc.text(`Date: ${formattedDate}`, 192, 51, { align: "right" });

    let y = 65;
    doc.setFont("helvetica", "bold");
    doc.line(15, 57, 195, 57);
    doc.text("S.No.", 18, 62);
    doc.text("Item Description", 35, 62);
    doc.text("Qty", 125, 62, { align: "center" });
    doc.text("Unit Price (Rs.)", 155, 62, { align: "right" });
    doc.text("Total (Rs.)", 192, 62, { align: "right" });
    doc.line(15, 64, 195, 64);

    doc.setFont("helvetica", "normal");
    const items = bill.items || [];
    items.forEach((item: any, index: number) => {
      if (y > 130) {
        doc.addPage();
        y = 15;
        doc.setFont("helvetica", "bold");
        doc.line(15, y, 195, y);
        doc.text("S.No.", 18, y + 5);
        doc.text("Item Description", 35, y + 5);
        doc.text("Qty", 125, y + 5, { align: "center" });
        doc.text("Unit Price (Rs.)", 155, y + 5, { align: "right" });
        doc.text("Total (Rs.)", 192, y + 5, { align: "right" });
        doc.line(15, y + 7, 195, y + 7);
        y += 12;
        doc.setFont("helvetica", "normal");
      }

      const descriptionLines = doc.splitTextToSize(item.item_name || '', 75);
      
      doc.text((index + 1).toString(), 18, y);
      doc.text(descriptionLines[0] || '', 35, y);
      doc.text(item.qty.toString(), 125, y, { align: "center" });
      doc.text(parseFloat(item.unit_price).toFixed(2), 155, y, { align: "right" });
      doc.text(parseFloat(item.total).toFixed(2), 192, y, { align: "right" });
      
      for (let i = 1; i < descriptionLines.length; i++) {
        y += 5;
        if (y > 135) {
          doc.addPage();
          y = 15;
          doc.setFont("helvetica", "normal");
        }
        doc.text(descriptionLines[i], 35, y);
      }
      
      y += 6;
    });

    if (y > 115) {
      doc.addPage();
      y = 15;
    }

    doc.line(15, y - 2, 195, y - 2);

    y += 4;
    doc.text("Subtotal:", 145, y, { align: "right" });
    doc.text(`Rs. ${parseFloat(bill.subtotal).toFixed(2)}`, 192, y, { align: "right" });

    y += 5;
    doc.text("Discount:", 145, y, { align: "right" });
    doc.text(`Rs. ${parseFloat(bill.discount).toFixed(2)}`, 192, y, { align: "right" });

    y += 6;
    doc.setFont("helvetica", "bold"); doc.setFontSize(10);
    doc.text("Grand Total:", 145, y, { align: "right" });
    doc.text(`Rs. ${parseFloat(bill.total).toFixed(2)}`, 192, y, { align: "right" });

    doc.setFont("helvetica", "normal"); doc.setFontSize(8);
    y += 5;
    const cgst = parseFloat(bill.cgst_total || 0).toFixed(2);
    const sgst = parseFloat(bill.sgst_total || 0).toFixed(2);
    doc.text(`(GST Inclusive - CGST: ${cgst} | SGST: ${sgst})`, 192, y, { align: "right" });
    doc.text(`Payment Mode: ${bill.payment_method} (${bill.payment_status})`, 15, y);

    y += 12;
    doc.setFontSize(9);
    doc.text(`Thank you for visiting ${$currentSettings.pharmacy_name ?? "Friends Medicos"}!`, 15, y);
    doc.text("Authorized Signature", 195, y, { align: "right" });
    doc.line(160, y - 4, 195, y - 4);

    return doc;
  }

  function viewInvoice(bill: any)"""
    content = content.replace(old_func_match.group(0), new_func)
    
    with open('src/components/BillingTab.svelte', 'w') as f:
        f.write(content)
    print("Successfully replaced compileInvoicePDF")
else:
    print("Could not find compileInvoicePDF function")
