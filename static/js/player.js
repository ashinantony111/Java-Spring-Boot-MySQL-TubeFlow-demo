// ========================================================
// TubeFlow - Video Watch Page Controller
// Likes, Subscriptions, Comments, Theater Mode, Streaming Tracking
// ========================================================

document.addEventListener("DOMContentLoaded", () => {
  const watchContainer = document.getElementById("watchContainer");
  if (!watchContainer) return;

  const videoId = parseInt(watchContainer.getAttribute("data-video-id"), 10);
  const activeUserId = getActiveUserId();

  initVideoPlayer(videoId, activeUserId);
  initWatchUserStates(videoId, activeUserId);
  initDescriptionToggle();
  initComments(videoId, activeUserId);
  initTheaterMode();
  initShare();
});

// --------------------------------------------------------
// VIDEO PLAYER & PROGRESS LOGGING
// --------------------------------------------------------
function initVideoPlayer(videoId, userId) {
  const video = document.getElementById("tubeVideoPlayer");
  if (!video) return;

  let progressLogged = false;

  video.addEventListener("timeupdate", () => {
    // Record view in database after 5 seconds of playback
    if (!progressLogged && video.currentTime > 4) {
      progressLogged = true;
      fetch(`/api/videos/${videoId}/view`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, progress_seconds: Math.floor(video.currentTime) })
      }).catch(err => console.log("View log error:", err));
    }
  });

  video.addEventListener("ended", () => {
    fetch(`/api/videos/${videoId}/view`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, progress_seconds: Math.floor(video.duration || 0) })
    }).catch(err => console.log("Progress log error:", err));
  });
}

// --------------------------------------------------------
// USER STATES (LIKE, DISLIKE, SUBSCRIBE, WATCH LATER)
// --------------------------------------------------------
async function initWatchUserStates(videoId, userId) {
  const likeBtn = document.getElementById("likeBtn");
  const dislikeBtn = document.getElementById("dislikeBtn");
  const likesCountText = document.getElementById("likesCountText");
  const subscribeBtn = document.getElementById("subscribeBtn");
  const channelSubsCount = document.getElementById("channelSubsCount");
  const watchLaterBtn = document.getElementById("watchLaterBtn");

  // Fetch video details with active user state
  try {
    const res = await fetch(`/api/videos/${videoId}?user_id=${userId}`);
    if (res.ok) {
      const data = await res.json();
      
      // Reaction state
      if (data.user_reaction === "like") {
        likeBtn.classList.add("active");
      } else if (data.user_reaction === "dislike") {
        dislikeBtn.classList.add("active");
      }

      // Subscription state
      if (subscribeBtn) {
        if (data.is_subscribed) {
          subscribeBtn.classList.add("subscribed");
          subscribeBtn.textContent = "Subscribed";
        } else {
          subscribeBtn.classList.remove("subscribed");
          subscribeBtn.textContent = "Subscribe";
        }
      }

      // Watch Later state
      if (watchLaterBtn && data.in_watch_later) {
        watchLaterBtn.classList.add("active");
        watchLaterBtn.querySelector("span").textContent = "Saved";
      }

      // Highlight user's own comments for deletion
      document.querySelectorAll(".delete-comment-btn").forEach(btn => {
        const commentUserId = parseInt(btn.getAttribute("data-user-id"), 10);
        if (commentUserId === userId) {
          btn.style.display = "inline-flex";
        }
      });
    }
  } catch (e) {
    console.error("Failed to load user states:", e);
  }

  // Handle Likes
  if (likeBtn) {
    likeBtn.addEventListener("click", async () => {
      try {
        const res = await fetch(`/api/videos/${videoId}/reaction`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: userId, reaction_type: "like" })
        });
        const data = await res.json();
        likesCountText.textContent = Number(data.likes).toLocaleString();
        
        if (data.current === "like") {
          likeBtn.classList.add("active");
          dislikeBtn.classList.remove("active");
        } else {
          likeBtn.classList.remove("active");
        }
      } catch (e) {
        showToast("Error reacting to video", true);
      }
    });
  }

  // Handle Dislikes
  if (dislikeBtn) {
    dislikeBtn.addEventListener("click", async () => {
      try {
        const res = await fetch(`/api/videos/${videoId}/reaction`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: userId, reaction_type: "dislike" })
        });
        const data = await res.json();
        likesCountText.textContent = Number(data.likes).toLocaleString();

        if (data.current === "dislike") {
          dislikeBtn.classList.add("active");
          likeBtn.classList.remove("active");
        } else {
          dislikeBtn.classList.remove("active");
        }
      } catch (e) {
        showToast("Error reacting to video", true);
      }
    });
  }

  // Handle Subscriptions
  if (subscribeBtn) {
    subscribeBtn.addEventListener("click", async () => {
      const channelId = subscribeBtn.getAttribute("data-channel-id");
      try {
        const res = await fetch(`/api/channels/${channelId}/subscribe`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: userId })
        });
        const data = await res.json();
        if (data.subscribed) {
          subscribeBtn.classList.add("subscribed");
          subscribeBtn.textContent = "Subscribed";
          showToast("Subscribed to channel!");
        } else {
          subscribeBtn.classList.remove("subscribed");
          subscribeBtn.textContent = "Subscribe";
          showToast("Unsubscribed from channel");
        }
        if (channelSubsCount) {
          channelSubsCount.textContent = `${Number(data.subscribers).toLocaleString()} subscribers`;
        }
      } catch (e) {
        showToast("Error updating subscription", true);
      }
    });
  }

  // Handle Watch Later
  if (watchLaterBtn) {
    watchLaterBtn.addEventListener("click", async () => {
      try {
        const res = await fetch(`/api/videos/${videoId}/watch-later`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: userId })
        });
        const data = await res.json();
        if (data.saved) {
          watchLaterBtn.classList.add("active");
          watchLaterBtn.querySelector("span").textContent = "Saved";
          showToast("Saved to Watch Later!");
        } else {
          watchLaterBtn.classList.remove("active");
          watchLaterBtn.querySelector("span").textContent = "Save";
          showToast("Removed from Watch Later");
        }
      } catch (e) {
        showToast("Error updating Watch Later", true);
      }
    });
  }
}

// --------------------------------------------------------
// DESCRIPTION EXPAND / COLLAPSE
// --------------------------------------------------------
function initDescriptionToggle() {
  const descBox = document.getElementById("descBox");
  const toggleText = document.getElementById("descToggleText");
  if (!descBox || !toggleText) return;

  descBox.addEventListener("click", () => {
    descBox.classList.toggle("expanded");
    toggleText.textContent = descBox.classList.contains("expanded") ? "Show less" : "Show more";
  });
}

// --------------------------------------------------------
// COMMENTS SECTION
// --------------------------------------------------------
function initComments(videoId, userId) {
  const newCommentForm = document.getElementById("newCommentForm");
  const commentInput = document.getElementById("commentContentInput");
  const formActions = document.getElementById("commentFormActions");
  const cancelBtn = document.getElementById("cancelCommentBtn");
  const commentList = document.getElementById("commentList");
  const commentTotalCount = document.getElementById("commentTotalCount");
  const userAvatar = document.getElementById("commentUserAvatar");

  // Sync commenter avatar with active user
  const activeUserItem = document.querySelector(`.user-switch-item[data-user-id="${userId}"]`);
  if (activeUserItem && userAvatar) {
    userAvatar.src = activeUserItem.getAttribute("data-avatar");
  }

  if (commentInput) {
    commentInput.addEventListener("focus", () => {
      formActions.style.display = "flex";
      commentInput.rows = 2;
    });

    cancelBtn.addEventListener("click", () => {
      commentInput.value = "";
      commentInput.rows = 1;
      formActions.style.display = "none";
    });
  }

  if (newCommentForm) {
    newCommentForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const content = commentInput.value.trim();
      if (!content) return;

      try {
        const res = await fetch(`/api/videos/${videoId}/comments`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: userId, content: content })
        });
        const data = await res.json();
        if (data.success && data.comment) {
          const c = data.comment;
          // Render new comment at top
          const commentEl = document.createElement("div");
          commentEl.className = "comment-item";
          commentEl.id = `comment-${c.id}`;
          commentEl.innerHTML = `
            <img src="${c.user.avatar_url}" class="comment-author-avatar" alt="${c.user.name}">
            <div class="comment-content-col">
              <div class="comment-header">
                <span class="comment-author-name">${c.user.name}</span>
                <span class="comment-date">Just now</span>
              </div>
              <div class="comment-body">${escapeHtml(c.content)}</div>
              <div class="comment-actions">
                <button class="comment-action-btn" title="Like comment">
                  <i data-lucide="thumbs-up" style="width: 14px; height: 14px;"></i>
                </button>
                <button class="comment-action-btn" title="Dislike comment">
                  <i data-lucide="thumbs-down" style="width: 14px; height: 14px;"></i>
                </button>
                <button class="comment-action-btn delete-comment-btn" data-comment-id="${c.id}" data-user-id="${c.user.id}" style="color: #ef4444;">
                  <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i>
                  <span>Delete</span>
                </button>
              </div>
            </div>
          `;
          commentList.prepend(commentEl);
          
          // Re-create lucide icons for new element
          if (window.lucide) window.lucide.createIcons();

          // Increment count
          if (commentTotalCount) {
            const count = parseInt(commentTotalCount.textContent || "0", 10) + 1;
            commentTotalCount.textContent = count;
          }

          // Reset input
          commentInput.value = "";
          commentInput.rows = 1;
          formActions.style.display = "none";
          showToast("Comment posted!");
        }
      } catch (err) {
        showToast("Error posting comment: " + err.message, true);
      }
    });
  }

  // Handle comment deletion (delegated)
  if (commentList) {
    commentList.addEventListener("click", async (e) => {
      const delBtn = e.target.closest(".delete-comment-btn");
      if (!delBtn) return;

      const commentId = delBtn.getAttribute("data-comment-id");
      if (!confirm("Are you sure you want to delete this comment?")) return;

      try {
        const res = await fetch(`/api/comments/${commentId}?user_id=${userId}`, {
          method: "DELETE"
        });
        if (res.ok) {
          const item = document.getElementById(`comment-${commentId}`);
          if (item) item.remove();
          if (commentTotalCount) {
            const count = Math.max(0, parseInt(commentTotalCount.textContent || "1", 10) - 1);
            commentTotalCount.textContent = count;
          }
          showToast("Comment deleted");
        } else {
          showToast("Could not delete comment", true);
        }
      } catch (e) {
        showToast("Error deleting comment", true);
      }
    });
  }
}

// --------------------------------------------------------
// THEATER MODE & SHARE
// --------------------------------------------------------
function initTheaterMode() {
  const btn = document.getElementById("theaterModeBtn");
  const watchContainer = document.getElementById("watchContainer");
  if (!btn || !watchContainer) return;

  btn.addEventListener("click", () => {
    watchContainer.classList.toggle("theater-mode");
    const isTheater = watchContainer.classList.contains("theater-mode");
    btn.innerHTML = `<i data-lucide="${isTheater ? 'minimize-2' : 'maximize-2'}"></i>`;
    if (window.lucide) window.lucide.createIcons();
  });
}

function initShare() {
  const shareBtn = document.getElementById("shareBtn");
  if (!shareBtn) return;

  shareBtn.addEventListener("click", () => {
    navigator.clipboard.writeText(window.location.href).then(() => {
      showToast("Video link copied to clipboard!");
    }).catch(() => {
      showToast("Video URL: " + window.location.href);
    });
  });
}

function escapeHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
