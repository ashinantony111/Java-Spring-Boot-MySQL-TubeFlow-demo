// ========================================================
// TubeFlow - Application Client Core
// User Switcher, Upload Studio, Navigation & Modals
// ========================================================

document.addEventListener("DOMContentLoaded", () => {
  // Initialize Lucide Icons
  if (window.lucide) {
    window.lucide.createIcons();
  }

  initUserManagement();
  initSidebar();
  initSearch();
  initUploadModal();
});

// Toast notification helper
function showToast(message, isError = false) {
  const toast = document.getElementById("toastNotification");
  const msgEl = document.getElementById("toastMessage");
  if (!toast || !msgEl) return;

  msgEl.textContent = message;
  if (isError) {
    toast.style.borderColor = "#ef4444";
  } else {
    toast.style.borderColor = "#3ea6ff";
  }

  toast.classList.add("show");
  setTimeout(() => {
    toast.classList.remove("show");
  }, 3500);
}

// --------------------------------------------------------
// USER PROFILE & SWITCHER
// --------------------------------------------------------
function getActiveUserId() {
  return parseInt(localStorage.getItem("tubeflow_user_id") || "1", 10);
}

function initUserManagement() {
  const userAvatarBtn = document.getElementById("userAvatarBtn");
  const userDropdownMenu = document.getElementById("userDropdownMenu");
  const switchItems = document.querySelectorAll(".user-switch-item");

  if (!userAvatarBtn || !userDropdownMenu) return;

  // Toggle user dropdown
  userAvatarBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    userDropdownMenu.classList.toggle("show");
  });

  document.addEventListener("click", (e) => {
    if (!userDropdownMenu.contains(e.target) && !userAvatarBtn.contains(e.target)) {
      userDropdownMenu.classList.remove("show");
    }
  });

  // Load saved active user
  const savedUserId = getActiveUserId();
  const currentItem = document.querySelector(`.user-switch-item[data-user-id="${savedUserId}"]`);
  if (currentItem) {
    applyActiveUser(currentItem);
  }

  // Handle switching
  switchItems.forEach(item => {
    item.addEventListener("click", () => {
      const newUserId = item.getAttribute("data-user-id");
      localStorage.setItem("tubeflow_user_id", newUserId);
      applyActiveUser(item);
      userDropdownMenu.classList.remove("show");
      showToast(`Switched profile to ${item.getAttribute("data-name")}`);

      // Refresh page if on channel, history, or watch page to reload user-specific states
      if (window.location.pathname.includes("/watch") ||
          window.location.pathname.includes("/subscriptions") ||
          window.location.pathname.includes("/history") ||
          window.location.pathname.includes("/liked")) {
        setTimeout(() => window.location.reload(), 400);
      }
    });
  });
}

function applyActiveUser(item) {
  const userId = item.getAttribute("data-user-id");
  const name = item.getAttribute("data-name");
  const handle = item.getAttribute("data-handle");
  const avatar = item.getAttribute("data-avatar");

  // Update navbar avatars
  const navAvatar = document.getElementById("activeUserAvatar");
  const dropdownAvatar = document.getElementById("dropdownUserAvatar");
  const dropdownName = document.getElementById("dropdownUserName");
  const dropdownHandle = document.getElementById("dropdownUserHandle");

  if (navAvatar) navAvatar.src = avatar;
  if (dropdownAvatar) dropdownAvatar.src = avatar;
  if (dropdownName) dropdownName.textContent = name;
  if (dropdownHandle) dropdownHandle.textContent = `@${handle}`;

  // Update active check in list
  document.querySelectorAll(".user-switch-item").forEach(el => {
    el.classList.toggle("active", el.getAttribute("data-user-id") === userId);
  });
}

// --------------------------------------------------------
// SIDEBAR COLLAPSE & EXPAND
// --------------------------------------------------------
function initSidebar() {
  const toggleBtn = document.getElementById("toggleSidebarBtn");
  const sidebar = document.getElementById("sidebar");
  if (!toggleBtn || !sidebar) return;

  const isCollapsed = localStorage.getItem("tubeflow_sidebar_collapsed") === "true";
  if (isCollapsed && window.innerWidth > 768) {
    sidebar.classList.add("collapsed");
  }

  toggleBtn.addEventListener("click", () => {
    if (window.innerWidth <= 768) {
      sidebar.classList.toggle("mobile-open");
    } else {
      sidebar.classList.toggle("collapsed");
      localStorage.setItem("tubeflow_sidebar_collapsed", sidebar.classList.contains("collapsed"));
    }
  });
}

// --------------------------------------------------------
// SEARCH INPUT BEHAVIOR
// --------------------------------------------------------
function initSearch() {
  const searchInput = document.getElementById("searchInput");
  const clearBtn = document.getElementById("clearSearchBtn");
  if (!searchInput || !clearBtn) return;

  function updateClearVisibility() {
    clearBtn.style.display = searchInput.value.trim().length > 0 ? "flex" : "none";
  }

  searchInput.addEventListener("input", updateClearVisibility);
  updateClearVisibility();

  clearBtn.addEventListener("click", () => {
    searchInput.value = "";
    updateClearVisibility();
    searchInput.focus();
  });
}

// --------------------------------------------------------
// UPLOAD VIDEO MODAL
// --------------------------------------------------------
function initUploadModal() {
  const openBtn = document.getElementById("openUploadModalBtn");
  const modalOverlay = document.getElementById("uploadModalOverlay");
  const closeBtn = document.getElementById("closeUploadModalBtn");
  const cancelBtn = document.getElementById("cancelUploadBtn");
  const uploadForm = document.getElementById("uploadForm");

  if (!openBtn || !modalOverlay) return;

  const openModal = () => modalOverlay.classList.add("show");
  const closeModal = () => modalOverlay.classList.remove("show");

  openBtn.addEventListener("click", openModal);
  if (closeBtn) closeBtn.addEventListener("click", closeModal);
  if (cancelBtn) cancelBtn.addEventListener("click", closeModal);

  modalOverlay.addEventListener("click", (e) => {
    if (e.target === modalOverlay) closeModal();
  });

  // Tab switching: File vs URL
  const tabUploadFileBtn = document.getElementById("tabUploadFileBtn");
  const tabVideoUrlBtn = document.getElementById("tabVideoUrlBtn");
  const videoFileGroup = document.getElementById("videoFileGroup");
  const videoUrlGroup = document.getElementById("videoUrlGroup");

  if (tabUploadFileBtn && tabVideoUrlBtn) {
    tabUploadFileBtn.addEventListener("click", () => {
      tabUploadFileBtn.classList.add("active");
      tabVideoUrlBtn.classList.remove("active");
      videoFileGroup.style.display = "block";
      videoUrlGroup.style.display = "none";
    });

    tabVideoUrlBtn.addEventListener("click", () => {
      tabVideoUrlBtn.classList.add("active");
      tabUploadFileBtn.classList.remove("active");
      videoFileGroup.style.display = "none";
      videoUrlGroup.style.display = "block";
    });
  }

  // Drag & drop file
  const dropZone = document.getElementById("videoDropZone");
  const fileInput = document.getElementById("videoFileInput");
  const selectedInfo = document.getElementById("selectedVideoInfo");
  const selectedName = document.getElementById("selectedVideoName");
  const clearFileBtn = document.getElementById("clearVideoFileBtn");

  if (dropZone && fileInput) {
    dropZone.addEventListener("click", () => fileInput.click());

    dropZone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropZone.classList.add("dragover");
    });
    dropZone.addEventListener("dragleave", () => {
      dropZone.classList.remove("dragover");
    });
    dropZone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropZone.classList.remove("dragover");
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        fileInput.files = e.dataTransfer.files;
        handleFileSelected(fileInput.files[0]);
      }
    });

    fileInput.addEventListener("change", () => {
      if (fileInput.files && fileInput.files.length > 0) {
        handleFileSelected(fileInput.files[0]);
      }
    });

    if (clearFileBtn) {
      clearFileBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        fileInput.value = "";
        selectedInfo.style.display = "none";
        dropZone.style.display = "block";
      });
    }
  }

  function handleFileSelected(file) {
    if (selectedName && selectedInfo && dropZone) {
      selectedName.textContent = `${file.name} (${(file.size / (1024 * 1024)).toFixed(1)} MB)`;
      selectedInfo.style.display = "flex";
      dropZone.style.display = "none";

      // Auto-fill title if empty
      const titleInput = document.getElementById("videoTitleInput");
      if (titleInput && !titleInput.value) {
        const cleanName = file.name.replace(/\.[^/.]+$/, "").replace(/[-_]/g, " ");
        titleInput.value = cleanName.charAt(0).toUpperCase() + cleanName.slice(1);
      }
    }
  }

  // Form submission
  if (uploadForm) {
    uploadForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const titleInput = document.getElementById("videoTitleInput");
      if (!titleInput.value.trim()) {
        showToast("Please enter a video title", true);
        return;
      }

      const activeUserId = getActiveUserId();
      const formData = new FormData(uploadForm);
      formData.append("user_id", activeUserId);

      const submitBtn = document.getElementById("submitUploadBtn");
      const progressBox = document.getElementById("uploadProgressBox");
      const progressBar = document.getElementById("uploadProgressBar");
      const statusText = document.getElementById("uploadStatusText");

      submitBtn.disabled = true;
      progressBox.style.display = "block";
      progressBar.style.width = "30%";
      statusText.textContent = "Writing video metadata to MySQL database...";

      try {
        const xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/upload", true);

        xhr.upload.onprogress = (evt) => {
          if (evt.lengthComputable) {
            const percent = Math.round((evt.loaded / evt.total) * 100);
            progressBar.style.width = `${Math.min(95, percent)}%`;
            statusText.textContent = `Uploading video file: ${percent}%`;
          }
        };

        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            const data = JSON.parse(xhr.responseText);
            progressBar.style.width = "100%";
            statusText.textContent = "Saved to MySQL successfully!";
            showToast("Video published successfully!");
            setTimeout(() => {
              window.location.href = `/watch?v=${data.video_id}`;
            }, 600);
          } else {
            showToast("Upload failed: " + xhr.responseText, true);
            submitBtn.disabled = false;
            progressBox.style.display = "none";
          }
        };

        xhr.onerror = () => {
          showToast("Network error during upload", true);
          submitBtn.disabled = false;
          progressBox.style.display = "none";
        };

        xhr.send(formData);
      } catch (err) {
        showToast("Upload error: " + err.message, true);
        submitBtn.disabled = false;
        progressBox.style.display = "none";
      }
    });
  }
}
