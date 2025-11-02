// Invoice Forecast Demo - JavaScript
let selectedFiles = []; // Changed to array for multiple files
let totalInvoicesProcessed = 0; // Track total invoices across all uploads
let recognizedInvoices = []; // Store latest invoice payloads for paging
let allRecognizedProducts = []; // Flattened view for summaries
let currentInvoicePage = 0; // Track which invoice page is active

// Model 1: Image OCR (Paper Invoice → Electronic Invoice)
async function predictModel1() {
    if (selectedFiles.length === 0) {
        document.getElementById('resultBox1').innerHTML = '<div class="result-text" style="color: #dc3545;">Please select at least one paper invoice image</div>';
        document.getElementById('results1').classList.add('show');
        return;
    }

    const loading = document.getElementById('loading1');
    const resultsSection = document.getElementById('results1');
    const resultBox = document.getElementById('resultBox1');
    const productList = document.getElementById('productList');
    const btn = document.getElementById('predictBtn1');

    loading.classList.add('show');
    btn.disabled = true;
    productList.innerHTML = ''; // Clear previous results

    try {
        let allProducts = [];
        let invoiceResults = [];

        // Process each image
        for (let i = 0; i < selectedFiles.length; i++) {
            const formData = new FormData();
            formData.append('image', selectedFiles[i]);

            const response = await fetch('/api/model1/detect', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.success !== false) {
                const text = data.recognized_text || 'No text recognized';
                invoiceResults.push({
                    filename: selectedFiles[i].name,
                    text: text,
                    confidence: data.confidence || 0.92,
                    data: data.data  // Store the full invoice data
                });

                // USE REAL PRODUCT DATA FROM API, NOT TEXT PARSING!
                if (data.data && data.data.products && Array.isArray(data.data.products)) {
                    // Use actual product data from CNN model
                    data.data.products.forEach(product => {
                        allProducts.push({
                            invoice: selectedFiles[i].name,
                            product: product.product_name,
                            quantity: product.quantity,
                            unit_price: product.unit_price,
                            line_total: product.line_total
                        });
                    });
                    console.log(`✅ Extracted ${data.data.products.length} products from ${selectedFiles[i].name}`);
                    
                    // Get total history count from API response
                    if (data.total_history_count !== undefined) {
                        totalInvoicesProcessed = data.total_history_count;
                    }
                } else {
                    console.warn(`⚠️ No product data in response for ${selectedFiles[i].name}`);
                }
            }
        }

        // Update the counter after processing all files
        totalInvoicesProcessed = totalInvoicesProcessed || selectedFiles.length;
        
        loading.classList.remove('show');

        // Display summary
        resultBox.innerHTML = `
            <div class="result-text">
                <strong>✅ Processed ${selectedFiles.length} invoice(s)</strong><br>
                <strong>📊 Total products extracted: ${allProducts.length}</strong><br>
                <div style="margin-top: 10px; font-size: 12px; color: #6c757d;">
                    ${invoiceResults.map(r => `${r.filename}: ${(r.confidence * 100).toFixed(1)}% confidence`).join('<br>')}
                </div>
            </div>
        `;

        // Display products in the dedicated recognized area
        const recognizedArea = document.getElementById('recognizedArea');
        const recognizedSummary = document.getElementById('recognizedSummary');
        const recognizedProductTable = document.getElementById('recognizedProductTable');

        if (allProducts.length > 0) {
            recognizedInvoices = invoiceResults
                .filter(r => r.data && Array.isArray(r.data.products) && r.data.products.length > 0)
                .map((r, idx) => {
                    const products = r.data.products.map(prod => {
                        const quantity = prod.quantity || 0;
                        const unitPrice = prod.unit_price || 0;
                        const lineTotal = prod.line_total || quantity * unitPrice;
                        return {
                            ...prod,
                            quantity,
                            unit_price: unitPrice,
                            line_total: lineTotal
                        };
                    });
                    const computedTotal = products.reduce((sum, prod) => sum + (prod.line_total || 0), 0);
                    return {
                        filename: r.filename,
                        confidence: r.confidence || 0,
                        products,
                        invoiceId: r.data.invoice_id || `INV-${idx + 1}`,
                        storeName: r.data.store_name || 'Unknown Store',
                        totalAmount: (r.data && typeof r.data.total_amount === 'number' && r.data.total_amount > 0)
                            ? r.data.total_amount
                            : computedTotal,
                        detectionConfidence: r.data.detection_confidence || r.confidence || 0
                    };
                });

            allRecognizedProducts = allProducts.slice();
            currentInvoicePage = 0;

            renderRecognizedInvoices();

            productList.innerHTML = buildModel1ProductTable(allRecognizedProducts);

            const model2Input = document.getElementById('model2Input');
            if (model2Input) {
                const structuredData = allRecognizedProducts
                    .map(p => `${p.product} - ${p.quantity}`)
                    .join('\n');
                model2Input.value = structuredData;
            }
        } else {
            recognizedArea.style.display = 'none';
            recognizedSummary.innerHTML = '';
            recognizedProductTable.innerHTML = '';
            const pagination = document.getElementById('recognizedPagination');
            if (pagination) {
                pagination.innerHTML = '';
            }
        }

        resultsSection.classList.add('show');
    } catch (error) {
        loading.classList.remove('show');
        resultBox.innerHTML = '<div class="result-text" style="color: #dc3545;">Error: ' + error.message + '</div>';
        resultsSection.classList.add('show');
    } finally {
        btn.disabled = false;
    }
}

function renderRecognizedInvoices() {
    const recognizedArea = document.getElementById('recognizedArea');
    const recognizedProductTable = document.getElementById('recognizedProductTable');
    const pagination = document.getElementById('recognizedPagination');

    if (!recognizedArea || !recognizedProductTable || !pagination) {
        return;
    }

    if (!recognizedInvoices.length) {
        recognizedArea.style.display = 'none';
        recognizedProductTable.innerHTML = '<div class="no-result">No products extracted yet</div>';
        pagination.innerHTML = '';
        updateRecognizedSummary(null);
        return;
    }

    recognizedArea.style.display = 'block';
    renderInvoicePage(currentInvoicePage);
}

function renderInvoicePage(pageIndex) {
    if (!recognizedInvoices.length) {
        updateRecognizedSummary(null);
        return;
    }

    currentInvoicePage = Math.min(Math.max(pageIndex, 0), recognizedInvoices.length - 1);

    const recognizedProductTable = document.getElementById('recognizedProductTable');
    const pagination = document.getElementById('recognizedPagination');

    if (!recognizedProductTable || !pagination) {
        return;
    }

    const invoice = recognizedInvoices[currentInvoicePage];
    const products = invoice.products || [];
    updateRecognizedSummary(invoice);

    if (!products.length) {
        recognizedProductTable.innerHTML = '<div class="no-result">No products detected in this invoice.</div>';
    } else {
        let rowsHTML = '';
        let invoiceTotal = (typeof invoice.totalAmount === 'number' && invoice.totalAmount > 0)
            ? invoice.totalAmount
            : 0;
        const usePrecomputedTotal = invoiceTotal > 0;

        products.forEach((product, index) => {
            const quantity = product.quantity || 0;
            const unitPrice = product.unit_price || 0;
            const lineTotal = product.line_total || quantity * unitPrice;

            if (!usePrecomputedTotal) {
                invoiceTotal += lineTotal;
            }

            rowsHTML += `
                <tr style="border-bottom: 1px solid #e2e8f0;">
                    <td style="padding: 8px; text-align: center;"><strong>${index + 1}</strong></td>
                    <td style="padding: 8px;"><strong>${product.product_name || product.product || 'Unknown Product'}</strong></td>
                    <td style="padding: 8px; text-align: right; color: #667eea;"><strong>${quantity}</strong></td>
                    <td style="padding: 8px; text-align: right;">${unitPrice.toLocaleString()} VND</td>
                    <td style="padding: 8px; text-align: right; font-weight: 600;">${lineTotal.toLocaleString()} VND</td>
                </tr>
            `;
        });

        recognizedProductTable.innerHTML = `
            <div class="invoice-header">
                <div>
                    <p style="margin: 0; font-weight: 600; color: #1e3c72; font-size: 15px;">Invoice ${currentInvoicePage + 1}: ${invoice.invoiceId || invoice.filename}</p>
                    <p style="margin: 4px 0 0 0; font-size: 13px; color: #475569;">Store: ${invoice.storeName}</p>
                    <p style="margin: 4px 0 0 0; font-size: 12px; color: #64748b;">Source file: ${invoice.filename}</p>
                </div>
                <div style="text-align: right;">
                    <p style="margin: 0; font-size: 13px; color: #1e3c72; font-weight: 600;">Confidence: ${(invoice.confidence * 100).toFixed(1)}%</p>
                    <p style="margin: 4px 0 0 0; font-size: 13px; color: #475569;">Products: ${products.length}</p>
                </div>
            </div>
            <div class="table-scroll">
                <table class="product-table">
                    <thead>
                        <tr>
                            <th style="text-align: center;">#</th>
                            <th>Product Name</th>
                            <th style="text-align: right;">Quantity</th>
                            <th style="text-align: right;">Unit Price</th>
                            <th style="text-align: right;">Line Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rowsHTML}
                    </tbody>
                    <tfoot>
                        <tr>
                            <td colspan="4" style="padding: 12px; text-align: right;">Invoice Total:</td>
                            <td style="padding: 12px; text-align: right; color: #667eea; font-size: 15px; font-weight: 700;">
                                ${invoiceTotal.toLocaleString()} VND
                            </td>
                        </tr>
                    </tfoot>
                </table>
            </div>
        `;
    }

    const prevDisabled = currentInvoicePage === 0 ? 'disabled' : '';
    const nextDisabled = currentInvoicePage === recognizedInvoices.length - 1 ? 'disabled' : '';
    const pageButtonsHTML = recognizedInvoices
        .map((_, idx) => `
            <button class="pagination-button${idx === currentInvoicePage ? ' active' : ''}" onclick="goToInvoicePage(${idx})">
                ${idx + 1}
            </button>
        `)
        .join('');

    pagination.innerHTML = `
        <div class="page-buttons">
            <button class="pagination-button" onclick="changeInvoicePage(-1)" ${prevDisabled}>Prev</button>
            ${pageButtonsHTML}
            <button class="pagination-button" onclick="changeInvoicePage(1)" ${nextDisabled}>Next</button>
        </div>
        <div class="page-indicator">
            Invoice ${currentInvoicePage + 1} of ${recognizedInvoices.length}
        </div>
    `;
}

function updateRecognizedSummary(currentInvoice) {
    const recognizedSummary = document.getElementById('recognizedSummary');
    if (!recognizedSummary) {
        return;
    }

    if (!allRecognizedProducts.length) {
        recognizedSummary.innerHTML = '';
        return;
    }

    const invoicesInBatch = recognizedInvoices.length || selectedFiles.length || 0;
    const processedTotal = Math.max(totalInvoicesProcessed || 0, invoicesInBatch);

    const averageConfidence = recognizedInvoices.length
        ? recognizedInvoices.reduce((sum, inv) => sum + (inv.confidence || 0), 0) / recognizedInvoices.length
        : 0;

    const batchGrandTotal = recognizedInvoices.reduce((sum, inv) => {
        const invoiceTotal = (typeof inv.totalAmount === 'number' && inv.totalAmount > 0)
            ? inv.totalAmount
            : inv.products.reduce((subtotal, prod) => subtotal + (prod.line_total || 0), 0);
        return sum + invoiceTotal;
    }, 0);

    const viewingLine = currentInvoice
        ? `<p style="margin: 6px 0 0 0; font-size: 13px; color: #475569;">Viewing invoice ${currentInvoicePage + 1} of ${invoicesInBatch}: <strong>${currentInvoice.invoiceId || currentInvoice.filename}</strong>${currentInvoice.products ? ` (${currentInvoice.products.length} products)` : ''}</p>`
        : '';

    recognizedSummary.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; gap: 20px; flex-wrap: wrap;">
            <div>
                <p style="margin: 0; font-weight: 600; color: #1e3c72; font-size: 16px;">📦 ${allRecognizedProducts.length} products extracted</p>
                <p style="margin: 5px 0 0 0; font-size: 13px; color: #6c757d;">Invoices this run: ${invoicesInBatch} • Overall processed: ${processedTotal}</p>
                ${viewingLine}
            </div>
            <div style="text-align: right;">
                <p style="margin: 0; font-size: 13px; color: #1e3c72; font-weight: 600;">Grand total (batch): ${batchGrandTotal.toLocaleString()} VND</p>
                <p style="margin: 6px 0 0 0; font-size: 13px; color: #28a745; font-weight: 600;">Average confidence: ${(averageConfidence * 100).toFixed(1)}%</p>
            </div>
        </div>
    `;
}

function buildModel1ProductTable(products) {
    if (!products.length) {
        return '<div class="no-result">No products extracted yet</div>';
    }

    let rowsHTML = '';
    let grandTotal = 0;

    products.forEach(product => {
        const quantity = product.quantity || 0;
        const lineTotal = product.line_total || 0;
        grandTotal += lineTotal;

        rowsHTML += `
            <tr style="border-bottom: 1px solid #e2e8f0;">
                <td style="padding: 6px;">${product.product || product.product_name || 'Unknown Product'}</td>
                <td style="padding: 6px; text-align: right; color: #667eea;"><strong>${quantity}</strong></td>
                <td style="padding: 6px; text-align: right;">${lineTotal.toLocaleString()} VND</td>
            </tr>
        `;
    });

    return `
        <div class="table-scroll" style="margin-top: 15px;">
            <table class="product-table">
                <thead>
                    <tr>
                        <th>Product Name</th>
                        <th style="text-align: right;">Quantity</th>
                        <th style="text-align: right;">Total</th>
                    </tr>
                </thead>
                <tbody>
                    ${rowsHTML}
                </tbody>
                <tfoot>
                    <tr>
                        <td colspan="2" style="padding: 10px; text-align: right;">Grand Total:</td>
                        <td style="padding: 10px; text-align: right; color: #667eea; font-weight: 700;">
                            ${grandTotal.toLocaleString()} VND
                        </td>
                    </tr>
                </tfoot>
            </table>
        </div>
    `;
}

window.changeInvoicePage = function (delta) {
    if (!recognizedInvoices.length) {
        return;
    }
    renderInvoicePage(currentInvoicePage + delta);
};

window.goToInvoicePage = function (index) {
    if (!recognizedInvoices.length) {
        return;
    }
    renderInvoicePage(index);
};

// File Upload Handling
document.addEventListener('DOMContentLoaded', function () {
    const fileUploadBtn = document.getElementById('fileUploadBtn');
    const fileInput = document.getElementById('fileInput');
    const fileName = document.getElementById('fileName');
    const filePreview = document.getElementById('filePreview');

    if (fileUploadBtn) {
        fileUploadBtn.addEventListener('click', function () {
            fileInput.click();
        });

        fileInput.addEventListener('change', function (e) {
            handleFiles(e.target.files);
        });

        function handleFiles(files) {
            const incomingFiles = Array.from(files);
            const MAX_FILES = 3;
            
            // Merge with existing selection while avoiding duplicates
            const existingKeys = new Set(selectedFiles.map(f => `${f.name}-${f.size}-${f.lastModified}`));
            let duplicatesDetected = 0;
            let limitReached = false;

            incomingFiles.forEach(file => {
                const key = `${file.name}-${file.size}-${file.lastModified}`;
                
                // Check for duplicates
                if (existingKeys.has(key)) {
                    duplicatesDetected++;
                    return;
                }
                
                // Check file limit
                if (selectedFiles.length >= MAX_FILES) {
                    limitReached = true;
                    return;
                }
                
                selectedFiles.push(file);
                existingKeys.add(key);
            });

            // Show warnings for duplicates or limit
            if (duplicatesDetected > 0) {
                alert(`${duplicatesDetected} duplicate file(s) rejected.`);
            }
            if (limitReached) {
                alert(`Maximum ${MAX_FILES} images allowed. Additional files ignored.`);
            }

            if (selectedFiles.length > 0) {
                fileName.textContent = `Selected: ${selectedFiles.length} file(s) (max ${MAX_FILES})`;
                displayPreviews();
            } else {
                fileName.textContent = '';
                filePreview.innerHTML = '';
            }
        }

        function displayPreviews() {
            filePreview.innerHTML = '';
            
            selectedFiles.forEach((file, index) => {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const container = document.createElement('div');
                    container.className = 'preview-container';
                    container.innerHTML = `
                        <img src="${e.target.result}" class="preview-image" alt="${file.name}">
                        <button class="remove-image" onclick="removeFile(${index})" title="Remove">×</button>
                        <div class="file-label">${file.name}</div>
                    `;
                    filePreview.appendChild(container);
                };
                reader.readAsDataURL(file);
            });
        }

        // Make removeFile global
        window.removeFile = function(index) {
            selectedFiles.splice(index, 1);
            
            // Update file input
            const dt = new DataTransfer();
            selectedFiles.forEach(file => dt.items.add(file));
            fileInput.files = dt.files;
            
            fileName.textContent = selectedFiles.length > 0 ? 
                `Selected: ${selectedFiles.length} file(s)` : '';
            displayPreviews();
        };

        // Drag and drop support
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(function (eventName) {
            fileUploadBtn.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(function (eventName) {
            fileUploadBtn.addEventListener(eventName, function () {
                fileUploadBtn.classList.add('dragging');
            }, false);
        });

        ['dragleave', 'drop'].forEach(function (eventName) {
            fileUploadBtn.addEventListener(eventName, function () {
                fileUploadBtn.classList.remove('dragging');
            }, false);
        });

        fileUploadBtn.addEventListener('drop', function (e) {
            const files = e.dataTransfer.files;
            handleFiles(files);
        }, false);
    }
});

// Model 2: Quantity Prediction (Electronic Invoice + Historical → Forecast)
async function predictModel2() {
    const input = document.getElementById('model2Input').value.trim();
    const resultBox = document.getElementById('resultBox2');
    const loading = document.getElementById('loading2');
    const resultsSection = document.getElementById('results2');
    const btn = document.getElementById('predictBtn2');

    if (!input) {
        resultBox.innerHTML = '<div class="result-text" style="color: #dc3545;">Please enter structured invoice data</div>';
        resultsSection.classList.add('show');
        return;
    }

    loading.classList.add('show');
    btn.disabled = true;

    try {
        const response = await fetch('/api/model2/forecast', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ invoice_data: input })
        });

        const data = await response.json();
        loading.classList.remove('show');

        if (data.success === false) {
            resultBox.innerHTML = '<div class="result-text" style="color: #dc3545;">' + data.message + '</div>';
        } else {
            // Format output with proper line breaks and structure
            let formattedOutput = '<div class="result-text"><strong>Predicted Import Quantities (Y2):</strong><br><br>';
            formattedOutput += '<div style="margin-bottom: 15px; font-size: 1.1em; color: #2ecc71;">' + data.output1 + '</div>';
            
            // Format the Vietnamese recommendation text with proper line breaks
            if (data.output2) {
                const lines = data.output2.split('\n').filter(line => line.trim());
                formattedOutput += '<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; line-height: 1.8;">';
                lines.forEach(line => {
                    const trimmed = line.trim();
                    if (trimmed.startsWith('📈') || trimmed.startsWith('📉') || trimmed.startsWith('➡️')) {
                        formattedOutput += '<div style="margin: 10px 0; font-weight: bold; color: #3498db;">' + trimmed + '</div>';
                    } else if (trimmed.startsWith('Khuyến nghị:') || trimmed.startsWith('Dự đoán')) {
                        formattedOutput += '<div style="margin: 8px 0; color: #e74c3c; font-weight: 600;">' + trimmed + '</div>';
                    } else if (trimmed.startsWith('🏆')) {
                        formattedOutput += '<div style="margin: 12px 0 8px 0; font-weight: bold; color: #f39c12;">' + trimmed + '</div>';
                    } else if (trimmed.match(/^\d+\./)) {
                        formattedOutput += '<div style="margin: 5px 0 5px 20px; color: #555;">' + trimmed + '</div>';
                    } else {
                        formattedOutput += '<div style="margin: 8px 0;">' + trimmed + '</div>';
                    }
                });
                formattedOutput += '</div>';
            }
            
            formattedOutput += '</div><div class="result-confidence">Prediction Confidence: ' + (data.confidence * 100).toFixed(1) + '%</div>';
            resultBox.innerHTML = formattedOutput;
        }
        resultsSection.classList.add('show');
    } catch (error) {
        loading.classList.remove('show');
        resultBox.innerHTML = '<div class="result-text" style="color: #dc3545;">Error: ' + error.message + '</div>';
        resultsSection.classList.add('show');
    } finally {
        btn.disabled = false;
    }
}

// Enter key support for Model 2
document.addEventListener('DOMContentLoaded', function () {
    const model2Input = document.getElementById('model2Input');
    if (model2Input) {
        model2Input.addEventListener('keydown', function (e) {
            if (e.ctrlKey && e.key === 'Enter') {
                predictModel2();
            }
        });
    }
});

console.log('✅ Invoice Forecast Demo initialized!');
