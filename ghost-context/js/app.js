document.addEventListener('DOMContentLoaded', () => {
    const headerUploadBtn = document.getElementById('headerUploadBtn');
    const uploadBtnBottom = document.getElementById('uploadBtn_Bottom');
    const folderInput = document.getElementById('folderInput');

    if (headerUploadBtn) {
        headerUploadBtn.addEventListener('click', () => {
            folderInput.click();
        });
    }

    if (uploadBtnBottom) {
        uploadBtnBottom.addEventListener('click', () => {
            folderInput.click();
        });
    }
    const outputModal = document.getElementById('outputModal');
    const outputText = document.getElementById('outputText');
    const copyBtn = document.getElementById('copyBtn');
    const closeModal = document.getElementById('closeModal');
    const fileCountSpan = document.getElementById('fileCount');
    const totalSizeSpan = document.getElementById('totalSize');

    // UI state updates
    const updateProgress = (count, size) => {
        fileCountSpan.textContent = `${count} files processed`;
        totalSizeSpan.textContent = `${(size / 1024).toFixed(2)} KB`;
    };

    // Junk/Binary filters
    const junkPatterns = [
        '.git/', 'node_modules/', '.next/', 'dist/', 'build/', '.cache/',
        'vendor/', '.venv/', 'venv/', '__pycache__/', '.upm/', '.replit/'
    ];
    
    const binaryExtensions = [
        'png', 'jpg', 'jpeg', 'gif', 'ico', 'pdf', 'zip', 'tar', 'gz',
        'exe', 'bin', 'dll', 'so', 'dylib', 'woff', 'woff2', 'ttf', 'eot',
        'mp4', 'mp3', 'wav', 'flac', 'avi', 'mov', 'webm', 'map'
    ];

    const isJunk = (path) => {
        const lowerPath = path.toLowerCase();
        return junkPatterns.some(pattern => lowerPath.includes(pattern)) || 
               // Check specifically for common hidden files except .gitignore if you want it
               (lowerPath.split('/').pop().startsWith('.') && !lowerPath.endsWith('.gitignore'));
    };

    const isBinary = (file) => {
        const ext = file.name.split('.').pop().toLowerCase();
        // Fallback for files without extensions: check first 1024 bytes (optional, staying with extension-based for simplicity)
        return binaryExtensions.includes(ext);
    };

    folderInput.addEventListener('change', async (e) => {
        const files = Array.from(e.target.files);
        if (files.length === 0) return;

        outputModal.classList.remove('hidden');
        outputText.value = 'Analyzing files...';
        
        // Find .gitignore if any
        let gitignoreRules = [];
        const gitignoreFile = files.find(f => (f.webkitRelativePath || f.name).endsWith('.gitignore'));
        if (gitignoreFile) {
            const raw = await gitignoreFile.text();
            gitignoreRules = raw.split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('#'));
        }

        const matchesGitignore = (path) => {
            return gitignoreRules.some(rule => {
                // Simplistic glob-like check (e.g., rule "test/" matches if path contains "test/")
                const pattern = rule.replace(/\./g, '\\.').replace(/\*/g, '.*');
                return new RegExp(pattern).test(path);
            });
        };

        const totalToProcess = files.length;
        let cumulativeText = '';
        let processedCount = 0;
        let totalSize = 0;

        for (const file of files) {
            const path = file.webkitRelativePath || file.name;

            if (isJunk(path)) continue;
            if (isBinary(file)) continue;
            if (matchesGitignore(path)) continue;

            try {
                const text = await file.text();
                // Enhanced XML structure for high-reasoning models (Claude/GPT-4/Gemini)
                cumulativeText += `\n<file>\n<path>${path}</path>\n<content>\n${text}\n</content>\n</file>\n`;
                processedCount++;
                totalSize += file.size;
            } catch (err) {
                console.error(`Error reading ${path}:`, err);
            }
        }

        outputText.value = cumulativeText.trim() || 'No text files found.';
        updateProgress(processedCount, totalSize);
    });

    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            console.log('Copy button clicked');
            const text = outputText.value;
            if (!text) {
                console.log('No text to copy');
                return;
            }

            // Fallback for non-HTTPS or non-secure contexts
            const textArea = document.createElement("textarea");
            textArea.value = text;
            textArea.style.position = "fixed";
            textArea.style.left = "-9999px";
            textArea.style.top = "0";
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();

            try {
                document.execCommand('copy');
                console.log('execCommand copy success');
                
                const originalText = copyBtn.innerText;
                copyBtn.innerText = 'Copied!';
                copyBtn.classList.remove('bg-white', 'text-black');
                copyBtn.classList.add('bg-green-600', 'text-white');

                // Show Toast Popup
                let toast = document.getElementById('reverb-toast');
                if (!toast) {
                    toast = document.createElement('div');
                    toast.id = 'reverb-toast';
                    toast.className = 'fixed bottom-8 left-1/2 -translate-x-1/2 bg-white text-black px-6 py-3 rounded-full font-bold text-sm shadow-2xl z-[100]';
                    document.body.appendChild(toast);
                }
                toast.innerText = 'Copied to clipboard! 🚀';
                toast.style.display = 'block';
                
                setTimeout(() => {
                    copyBtn.innerText = originalText;
                    copyBtn.classList.remove('bg-green-600', 'text-white');
                    copyBtn.classList.add('bg-white', 'text-black');
                    toast.style.display = 'none';
                }, 2000);
            } catch (err) {
                console.error('Copy fallback failed:', err);
            }

            document.body.removeChild(textArea);
        });
    }

    closeModal.addEventListener('click', () => {
        outputModal.classList.add('hidden');
    });
});
