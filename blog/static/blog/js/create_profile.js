// Character counter for bio
const bioTextarea = document.getElementById("bio");
const charCount = document.getElementById("charCount");

bioTextarea.addEventListener("input", function () {
  charCount.textContent = this.value.length;
});

// Profile picture preview
const profilePicInput = document.getElementById("profilePicture");
const avatarPreview = document.getElementById("avatarPreview");
const userIcon = document.getElementById("userIcon");

profilePicInput.addEventListener("change", function (e) {
  const file = e.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      avatarPreview.src = e.target.result;
      avatarPreview.style.display = "block";
      userIcon.style.display = "none";
    };
    reader.readAsDataURL(file);
  }
});

// Focus effect for input icons
const inputs = document.querySelectorAll("input, textarea");
inputs.forEach((input) => {
  input.addEventListener("focus", function () {
    const icon = this.parentElement.querySelector(".input-icon");
    if (icon) {
      icon.style.color = "#3b82f6";
    }
  });

  input.addEventListener("blur", function () {
    const icon = this.parentElement.querySelector(".input-icon");
    if (icon) {
      icon.style.color = "#94a3b8";
    }
  });
});
