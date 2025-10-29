// Invoice Forecast Demo - JavaScript
let selectedFile = null;

// Model 1: Text Prediction
async function predictModel1() {
    const input = document.getElementById('model1Input').value.trim();
    const resultBox = document.getElementById('resultBox1');
    const loading = document.getElementById('loading1');
    const resultsSection = document.getElementById('results1');
    const btn = document.getElementById('predictBtn1');

    if (!input) {
        resultBox.innerHTML = '<div class="result-text" style="color: #dc3545;">Please enter invoice data</div>';
        resultsSection.classList.add('show');
        return;
    }

    loading.classList.add('show');
    btn.disabled = true;

    try {
        const response = await fetch('/api/model1/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: input })
        });

        const data = await response.json();
        loading.classList.remove('show');

        if (data.success === false) {
            resultBox.innerHTML = '<div class="result-text" style="color: #dc3545;">' + data.message + '</div>';
        } else {
            resultBox.innerHTML = '<div class="result-text"><strong>' + data.output1 + '</strong><br><br>' + data.output2 + '</div><div class="result-confidence">Confidence: ' + (data.confidence * 100).toFixed(1) + '%</div>';
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

    if (fileUploadBtn) {
        fileUploadBtn.addEventListener('click', function () {
            fileInput.click();
        });

        fileInput.addEventListener('change', function (e) {
            selectedFile = e.target.files[0];
            if (selectedFile) {
                fileName.textContent = 'Selected: ' + selectedFile.name;
            }
        });

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
            if (files.length > 0) {
                selectedFile = files[0];
                fileInput.files = files;
                fileName.textContent = 'Selected: ' + selectedFile.name;
            }
        }, false);
    }
});

// Model 2: Image Recognition
async function predictModel2() {
    if (!selectedFile) {
        document.getElementById('resultBox2').innerHTML = '<div class="result-text" style="color: #dc3545;">Please select an image first</div>';
        document.getElementById('results2').classList.add('show');
        return;
    }

    const loading = document.getElementById('loading2');
    const resultsSection = document.getElementById('results2');
    const resultBox = document.getElementById('resultBox2');
    const btn = document.getElementById('predictBtn2');

    loading.classList.add('show');
    btn.disabled = true;

    try {
        const formData = new FormData();
        formData.append('image', selectedFile);

        const response = await fetch('/api/model2/recognize', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        loading.classList.remove('show');

        if (data.success === false) {
            resultBox.innerHTML = '<div class="result-text" style="color: #dc3545;">' + data.message + '</div>';
        } else {
            const text = data.recognized_text || 'No text recognized';
            resultBox.innerHTML = '<div class="result-text"><strong>Recognized Text:</strong><br><br>' + text.replace(/\n/g, '<br>') + '</div><div class="result-confidence">Confidence: ' + (data.confidence * 100).toFixed(1) + '%</div>';
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

// Enter key support for Model 1
document.addEventListener('DOMContentLoaded', function () {
    const model1Input = document.getElementById('model1Input');
    if (model1Input) {
        model1Input.addEventListener('keydown', function (e) {
            if (e.ctrlKey && e.key === 'Enter') {
                predictModel1();
            }
        });
    }
});

console.log('✅ Invoice Forecast Demo initialized!');
