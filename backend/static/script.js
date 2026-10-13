document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.querySelector(".file-input") || document.getElementById("fileInput");
    const fileName = document.getElementById("fileName");

    if (fileInput) {
        fileInput.addEventListener("change", function () {
            const file = this.files[0];
            if (file && fileName) {
                fileName.textContent = "📄 Selected File: " + file.name;
                fileName.style.display = "block";
            }
        });
    }
});