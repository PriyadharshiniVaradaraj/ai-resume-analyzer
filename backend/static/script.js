document.addEventListener("DOMContentLoaded", function () {
    // ---- Mobile Nav Toggle ----
    const navToggle = document.getElementById("navToggle");
    const navLinks = document.getElementById("navLinks");

    if (navToggle && navLinks) {
        navToggle.addEventListener("click", function () {
            navToggle.classList.toggle("active");
            navLinks.classList.toggle("open");
        });

        // Close menu when a link is clicked
        navLinks.querySelectorAll("a").forEach(function (link) {
            link.addEventListener("click", function () {
                navToggle.classList.remove("active");
                navLinks.classList.remove("open");
            });
        });
    }

    // ---- File Upload & Drag-and-Drop ----
    const fileInput = document.querySelector(".file-input") || document.getElementById("fileInput");
    const fileName = document.getElementById("fileName");
    const uploadCard = document.querySelector(".upload-card");
    const analyzeForm = document.querySelector("form[action='/analyze']");
    const analyzeBtn = document.querySelector(".analyze-btn");

    function formatFileSize(bytes) {
        if (!bytes) return "";
        const kb = bytes / 1024;
        if (kb < 1024) return kb.toFixed(1) + " KB";
        return (kb / 1024).toFixed(1) + " MB";
    }

    function updateFileDisplay(file) {
        if (file && fileName) {
            const sizeStr = formatFileSize(file.size);
            fileName.innerHTML = `<span style="display: inline-flex; align-items: center; gap: 8px; background: #e0e7ff; color: #4338ca; padding: 8px 16px; border-radius: 999px; font-size: 14px; font-weight: 600;">📄 ${file.name} ${sizeStr ? `<span style="opacity: 0.7; font-weight: 500;">(${sizeStr})</span>` : ''} ✓</span>`;
            fileName.style.display = "block";
        }
    }

    if (fileInput) {
        fileInput.addEventListener("change", function () {
            const file = this.files && this.files[0];
            updateFileDisplay(file);
        });
    }

    // Drag-and-drop feedback
    if (uploadCard && fileInput) {
        ["dragenter", "dragover"].forEach(function (evtName) {
            uploadCard.addEventListener(evtName, function (e) {
                e.preventDefault();
                e.stopPropagation();
                uploadCard.style.borderColor = "#6366f1";
                uploadCard.style.background = "#f5f7ff";
            }, false);
        });

        ["dragleave", "drop"].forEach(function (evtName) {
            uploadCard.addEventListener(evtName, function (e) {
                e.preventDefault();
                e.stopPropagation();
                uploadCard.style.borderColor = "#e2e8f0";
                uploadCard.style.background = "#ffffff";
            }, false);
        });

        uploadCard.addEventListener("drop", function (e) {
            const dt = e.dataTransfer;
            const files = dt && dt.files;
            if (files && files.length > 0) {
                fileInput.files = files;
                updateFileDisplay(files[0]);
            }
        }, false);
    }

    // Loading state on form submit
    if (analyzeForm && analyzeBtn) {
        analyzeForm.addEventListener("submit", function () {
            analyzeBtn.disabled = true;
            analyzeBtn.style.opacity = "0.85";
            analyzeBtn.style.cursor = "wait";
            analyzeBtn.innerHTML = `
                <span style="display: inline-flex; align-items: center; gap: 10px;">
                    <svg style="animation: spin 1s linear infinite; width: 18px; height: 18px;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <circle cx="12" cy="12" r="10" stroke-opacity="0.25"></circle>
                        <path d="M12 2a10 10 0 0 1 10 10" stroke-linecap="round"></path>
                    </svg>
                    Analyzing your resume...
                </span>
            `;
        });
    }
});

// Inject keyframe animation for spinner if not present
if (!document.getElementById("script-spinner-style")) {
    const style = document.createElement("style");
    style.id = "script-spinner-style";
    style.textContent = "@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }";
    document.head.appendChild(style);
}
