document.addEventListener('DOMContentLoaded', function () {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');
    const uploadForm = document.querySelector('.upload-form');
    const loadingSection = document.getElementById('loadingSection');
    const viewSummary = document.getElementById('viewSummary');

    uploadArea.addEventListener('click', () => fileInput.click());

    let selectedFiles = [];

    fileInput.addEventListener('change', () => {
        for (const file of fileInput.files) {
            const listItem = document.createElement('li');
            listItem.classList.add('file-item');

            const progressContainer = document.createElement('div');
            progressContainer.className = 'progress-container';
            progressContainer.innerHTML = `
                <svg width="80" height="80" viewBox="0 0 80 80">
                    <circle class="bg" cx="20" cy="20" r="15" />
                    <circle class="progress" cx="20" cy="20" r="15" />
                    <line class="x-line x1" x1="15" y1="15" x2="25" y2="25" />
                    <line class="x-line x2" x1="15" y1="25" x2="25" y2="15" />
                </svg>
                <div class="wheel-icon"></div>
            `;

            const fileName = document.createElement('span');
            fileName.textContent = file.name;

            const thumb = document.createElement('img');
            thumb.className = 'thumbnail';
            if (file.type.startsWith('image/')) {
                thumb.src = URL.createObjectURL(file);
            }

            listItem.appendChild(progressContainer);
            if (file.type.startsWith('image/')) listItem.appendChild(thumb);
            listItem.appendChild(fileName);
            fileList.appendChild(listItem);

            selectedFiles.push({ file, listItem, progressContainer });
        }

        fileInput.value = '';
    });

    uploadForm.addEventListener('submit', function (e) {
        e.preventDefault();

        if (selectedFiles.length === 0) {
            alert("Please select at least one file to summarize.");
            return;
        }

        let uploadSuccess = true;
        let completedUploads = 0;

        selectedFiles.forEach((entry) => {
            const { file, listItem, progressContainer } = entry;
            const formData = new FormData();
            formData.append('file', file);

            const xhr = new XMLHttpRequest();
            xhr.open('POST', '/upload');

            const progressCircle = progressContainer.querySelector('.progress');
            const wheelText = progressContainer.querySelector('.wheel-icon');
            const xLines = progressContainer.querySelectorAll('.x-line');

            xhr.upload.addEventListener('progress', function (e) {
                if (e.lengthComputable) {
                    const percent = Math.round((e.loaded / e.total) * 100);
                    const radius = 35;
                    const circumference = 2 * Math.PI * radius;
                    const offset = circumference - (percent / 100) * circumference;

                    progressCircle.style.strokeDasharray = circumference;
                    progressCircle.style.strokeDashoffset = offset;

                    if (percent >= 100) {
                        wheelText.style.display = 'none';
                        xLines.forEach(line => line.style.opacity = 1);
                    }
                }
            });

            xhr.onload = function () {
                if (xhr.status === 200) {
                    completedUploads++;
                    checkIfAllUploadsDone();
                } else {
                    uploadSuccess = false;
                    alert(`Failed to upload ${file.name}`);
                }
            };

            xhr.onerror = function () {
                uploadSuccess = false;
                alert(`Error uploading ${file.name}`);
            };

            xhr.send(formData);

            // Allow removing file after upload
            progressContainer.addEventListener('click', () => {
                if (xLines[0].style.opacity === '1') {
                    listItem.remove();
                    selectedFiles = selectedFiles.filter(f => f.file !== file);
                }
            });
        });

        // ⬇️ MODIFIED SECTION BELOW
        function checkIfAllUploadsDone() {
            if (completedUploads === selectedFiles.length && uploadSuccess) {
                loadingSection.style.display = 'flex';
                uploadForm.style.display = 'none';

                // Start summarization process
                fetch('/start_summary', { method: 'POST' });

                const pollInterval = setInterval(() => {
                    fetch('/check_progress')
                        .then(response => response.json())
                        .then(status => {
                            if (status.done) {
                                clearInterval(pollInterval);
                                loadingSection.style.display = 'none';
                                viewSummary.style.display = 'flex';
                                viewSummary.style.justifyContent = 'center';

                                // ✅ Attach event handler here ONCE, only when visible
                                const button = viewSummary.querySelector('button');
                                button.onclick = () => {
                                    window.location.href = '/download_summary';
                                };
                            }
                        });
                }, 3000);
            }
        }
    });
});
