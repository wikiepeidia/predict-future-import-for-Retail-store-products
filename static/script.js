// Invoice Forecast Demo - JavaScript
let selectedFiles = []; // Changed to array for multiple files

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

            const response = await fetch('/api/model1/predict', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (data.success !== false) {
                const text = data.recognized_text || 'No text recognized';
                invoiceResults.push({
                    filename: selectedFiles[i].name,
                    text: text,
                    confidence: data.confidence || 0.92
                });

                // Parse products from text (mock parsing - backend will do real parsing)
                const lines = text.split('\n').filter(line => line.trim());
                lines.forEach(line => {
                    // Simple parsing: look for patterns like "Product - Quantity"
                    const match = line.match(/(.+?)\s*[-:]\s*(\d+)/);
                    if (match) {
                        allProducts.push({
                            invoice: selectedFiles[i].name,
                            product: match[1].trim(),
                            quantity: parseInt(match[2])
                        });
                    }
                });
            }
        }

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
            // Show the recognized area
            recognizedArea.style.display = 'block';

            // Update summary
            recognizedSummary.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <p style="margin: 0; font-weight: 600; color: #1e3c72; font-size: 16px;">
                            📦 ${allProducts.length} Products Extracted
                        </p>
                        <p style="margin: 5px 0 0 0; font-size: 13px; color: #6c757d;">
                            From ${selectedFiles.length} invoice image(s)
                        </p>
                    </div>
                    <div style="text-align: right;">
                        <p style="margin: 0; font-size: 13px; color: #28a745; font-weight: 600;">
                            Average Confidence: ${(invoiceResults.reduce((sum, r) => sum + r.confidence, 0) / invoiceResults.length * 100).toFixed(1)}%
                        </p>
                    </div>
                </div>
            `;

            // Display products in table format in recognized area
            let tableHTML = `
                <table class="product-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Invoice Source</th>
                            <th>Product Name</th>
                            <th>Quantity</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            allProducts.forEach((product, index) => {
                tableHTML += `
                    <tr>
                        <td><strong>${index + 1}</strong></td>
                        <td>${product.invoice}</td>
                        <td>${product.product}</td>
                        <td><strong style="color: #667eea;">${product.quantity}</strong></td>
                    </tr>
                `;
            });

            tableHTML += `
                    </tbody>
                </table>
            `;

            recognizedProductTable.innerHTML = tableHTML;

            // Also keep the product list in Model 1 card (old display)
            let productListHTML = `
                <table class="product-table">
                    <thead>
                        <tr>
                            <th>Invoice</th>
                            <th>Product Name</th>
                            <th>Quantity</th>
                        </tr>
                    </thead>
                    <tbody>
            `;

            allProducts.forEach(product => {
                productListHTML += `
                    <tr>
                        <td>${product.invoice}</td>
                        <td>${product.product}</td>
                        <td><strong>${product.quantity}</strong></td>
                    </tr>
                `;
            });

            productListHTML += `
                    </tbody>
                </table>
            `;

            productList.innerHTML = productListHTML;

            // Auto-populate Model 2 with structured data
            const model2Input = document.getElementById('model2Input');
            if (model2Input) {
                const structuredData = allProducts.map(p => `${p.product} - ${p.quantity}`).join('\n');
                model2Input.value = structuredData;
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
            selectedFiles = Array.from(files);
            
            if (selectedFiles.length > 0) {
                fileName.textContent = `Selected: ${selectedFiles.length} file(s)`;
                displayPreviews();
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
        const response = await fetch('/api/model2/recognize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: input })
        });

        const data = await response.json();
        loading.classList.remove('show');

        if (data.success === false) {
            resultBox.innerHTML = '<div class="result-text" style="color: #dc3545;">' + data.message + '</div>';
        } else {
            resultBox.innerHTML = '<div class="result-text"><strong>Predicted Import Quantities (Y2):</strong><br><br>' + data.output1 + '<br><br>' + data.output2 + '</div><div class="result-confidence">Prediction Confidence: ' + (data.confidence * 100).toFixed(1) + '%</div>';
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
