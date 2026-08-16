<script lang="ts">
  import { onMount } from 'svelte';
  import { previewModalVisible, previewModalData, currentSettings } from '../store';
  import { jsPDF } from 'jspdf';

  $: {
    if ($previewModalVisible && $previewModalData) {
      setTimeout(() => {
        const iframe = document.getElementById('preview-iframe') as HTMLIFrameElement;
        if (iframe && $previewModalData) {
          const isBill = 'patient_name' in $previewModalData && !('meds' in $previewModalData);
          if (!isBill) {
            const doc = compilePDFFromRowObject($previewModalData);
            iframe.src = doc.output('bloburl');
          }
        }
      }, 50);
    }
  }

  function closePreview() {
    previewModalVisible.set(false);
    previewModalData.set(null);
    const iframe = document.getElementById('preview-iframe') as HTMLIFrameElement;
    if (iframe) iframe.src = '';
  }

  function formatDateIST(dateVal: string | Date) {
    if (!dateVal) return '--';
    const date = new Date(dateVal);
    return date.toLocaleDateString('en-IN', {
      timeZone: 'Asia/Kolkata',
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  }

  function compilePDFFromRowObject(row: any) {
    const doc = new jsPDF();
    const formattedDate = formatDateIST(row.visit_date || new Date());

    doc.setFont("helvetica", "bold"); doc.setFontSize(18);
    doc.text($currentSettings.pharmacy_name ?? "FRIENDS MEDICOS PHARMACY", 105, 15, { align: "center" });
    doc.setFontSize(10); doc.setFont("helvetica", "normal");
    doc.text($currentSettings.clinic_address ?? "NALAPUR, NARNAUL, 123001 (HARYANA)", 105, 21, { align: "center" });
    doc.setFont("helvetica", "bold"); doc.text($currentSettings.doctor_name ?? "DR. VINAY GAURAV", 105, 27, { align: "center" });
    doc.setFont("helvetica", "normal"); doc.text($currentSettings.doctor_degree ?? "M.B.B.S", 105, 32, { align: "center" });

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
              doc.addImage(wmBase64, 'PNG', (210 - wmSize)/2, (297 - wmSize)/2 + 10, wmSize, wmSize);
            }
        }
    } catch (err) {
        console.warn('Failed to add watermark to PDF', err);
    }

    doc.setFontSize(11);
    doc.text(`Patient Name: ${row.name}`, 15, 45);
    doc.text(`Address: ${row.address || ''}`, 15, 55);
    doc.text(`Date: ${formattedDate}`, 195, 35, { align: "right" });
    doc.text(`Age: ${row.age || ''}`, 195, 45, { align: "right" });
    doc.text(`Gender: ${row.gender || ''}`, 195, 55, { align: "right" });

    const gridTop = 65, gridLeft = 15, gridWidth = 180, gridHeight = 210, sidebarWidth = 50;
    doc.rect(gridLeft, gridTop, gridWidth, gridHeight);
    doc.line(gridLeft + sidebarWidth, gridTop, gridLeft + sidebarWidth, gridTop + gridHeight);

    let leftY = gridTop + 6;
    const vitals = [
        { label: "Weight (Kg)", val: row.weight },
        { label: "Body Temp. (F)", val: row.temp },
        { label: "BP (mmHg)", val: row.bp },
        { label: "SPO2 (%)", val: row.spo2 },
        { label: "Pulse (bpm)", val: row.pulse },
        { label: "Allergy (If any)", val: row.allergy },
        { label: "Investigation", val: row.investigation }
    ];

    vitals.forEach((v) => {
        if (leftY + 12 > gridTop + gridHeight) return;
        doc.setFont("helvetica", "bold"); doc.setFontSize(9);
        doc.text(v.label, gridLeft + 3, leftY);
        doc.setFont("helvetica", "normal"); doc.setFontSize(10);

        const valStr = v.val ? v.val.toString() : '--';
        const wrappedVal = doc.splitTextToSize(valStr, sidebarWidth - 6);
        doc.text(wrappedVal, gridLeft + 3, leftY + 5);

        const lines = Array.isArray(wrappedVal) ? wrappedVal.length : 1;
        leftY += 5 + (lines * 4.5) + 3;
    });

    const rightColX = gridLeft + sidebarWidth + 5;
    const rightColWidth = gridWidth - sidebarWidth - 10;
    let rightY = gridTop + 6;

    function drawRightSection(label: string, value: string) {
        if (!value || value.trim() === '') return;
        if (rightY + 10 > gridTop + gridHeight) return;
        doc.setFont("helvetica", "bold"); doc.setFontSize(9);
        doc.text(label, rightColX, rightY);
        rightY += 5;
        doc.setFont("helvetica", "normal"); doc.setFontSize(10);
        const wrapped = doc.splitTextToSize(value, rightColWidth);
        doc.text(wrapped, rightColX, rightY);
        const lines = Array.isArray(wrapped) ? wrapped.length : 1;
        rightY += (lines * 4.5) + 5;
    }

    drawRightSection("History:", row.history);
    drawRightSection("Examination:", row.examination);
    drawRightSection("Diagnosis:", row.diagnosis || 'N/A');

    if (rightY + 14 <= gridTop + gridHeight) {
        doc.setFont("times", "italic"); doc.setFontSize(22);
        doc.text("Rx", rightColX, rightY);
        rightY += 12;
        doc.setFont("helvetica", "normal"); doc.setFontSize(11);
        const medsList = doc.splitTextToSize(row.meds || '', rightColWidth);
        doc.text(medsList, rightColX, rightY);
    }

    return doc;
  }

  onMount(() => {
    const handleDirectPrint = (e: any) => {
      const row = e.detail;
      const doc = compilePDFFromRowObject(row);
      const buffer = doc.output('arraybuffer');
      const dateStr = new Date(row.visit_date || new Date()).toISOString().split('T')[0];
      const file = `${row.name.replace(/\s+/g, '_')}_${row.mobile || 'NoMobile'}_${dateStr}_Rx.pdf`;
      ipcRenderer.send('save-pdf', { fileName: file, pdfData: buffer });
    };

    window.addEventListener('direct-print-pdf', handleDirectPrint);
    return () => {
      window.removeEventListener('direct-print-pdf', handleDirectPrint);
    };
  });
</script>

{#if $previewModalVisible}
  <!-- svelte-ignore a11y-click-events-have-key-events -->
  <!-- svelte-ignore a11y-no-static-element-interactions -->
  <div id="preview-modal" class="modal-overlay show" style="display: flex;">
      <div class="modal-card">
          <div style="padding:15px; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center;">
              <h3 style="margin:0; font-family:'Outfit', sans-serif;">Prescription Layout Document Preview</h3>
              <button on:click={closePreview} style="border:none; background:none; font-size:16px; cursor:pointer;">✕</button>
          </div>
          <div style="flex:1;"><iframe id="preview-iframe" title="PDF Preview"></iframe></div>
          <div style="padding:15px; border-top:1px solid var(--border); display:flex; justify-content:flex-end; gap:10px;">
              <button class="btn-secondary" on:click={closePreview} style="padding:8px 16px;">Close Preview</button>
          </div>
      </div>
  </div>
{/if}
