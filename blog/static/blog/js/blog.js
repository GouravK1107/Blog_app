// ====== MOBILE MENU TOGGLE ======
const mobileToggle = document.getElementById("mobileToggle");
const navMenu = document.getElementById("navMenu");

mobileToggle.addEventListener("click", () => {
  mobileToggle.classList.toggle("active");
  navMenu.classList.toggle("active");
});

// ====== NAV LINK ACTIVE STATE ======
const navLinks = document.querySelectorAll(".nav-link");
navLinks.forEach((link) => {
  link.addEventListener("click", () => {
    navLinks.forEach((l) => l.classList.remove("active"));
    link.classList.add("active");
    navMenu.classList.remove("active");
    mobileToggle.classList.remove("active");
  });
});

// ====== FILTER BLOGS ======
function filterBlogs(category, chipElement) {
  const allChips = document.querySelectorAll(".chip");
  allChips.forEach((chip) => chip.classList.remove("active"));
  chipElement.classList.add("active");

  const blogCards = document.querySelectorAll(".blog-card");
  blogCards.forEach((card) => {
    const blogCategory = card
      .querySelector(".blog-category")
      .textContent.toLowerCase();

    if (category === "all" || blogCategory === category) {
      card.style.display = "block";
      setTimeout(() => (card.style.opacity = "1"), 50);
    } else {
      card.style.opacity = "0";
      setTimeout(() => (card.style.display = "none"), 200);
    }
  });
}

// ====== SEARCH FUNCTIONALITY ======
const searchInput = document.querySelector(".search-box input");
searchInput.addEventListener("input", (e) => {
  const query = e.target.value.toLowerCase();
  const blogCards = document.querySelectorAll(".blog-card");

  blogCards.forEach((card) => {
    const title = card.querySelector(".blog-title").textContent.toLowerCase();
    const excerpt = card
      .querySelector(".blog-excerpt")
      .textContent.toLowerCase();
    const author = card.querySelector(".author-name").textContent.toLowerCase();

    if (
      title.includes(query) ||
      excerpt.includes(query) ||
      author.includes(query)
    ) {
      card.style.display = "block";
      card.style.opacity = "1";
    } else {
      card.style.opacity = "0";
      setTimeout(() => (card.style.display = "none"), 200);
    }
  });
});

// ====== ACTION FUNCTIONS ======
function createBlog() {
  alert("🚀 Redirecting to blog creation page...");
  // Replace this with a real redirect:
  // window.location.href = '/create-blog.html';
}

function goToProfile() {
  alert("👤 Opening your profile...");
  // Replace this with a real redirect:
  // window.location.href = '/profile.html';
}

function viewBlog(id) {
  alert(`📖 Opening blog post #${id}...`);
  // Replace this with a real redirect:
  // window.location.href = `/blog.html?id=${id}`;
}

// ====== LIKE BUTTON FEATURE (BONUS) ======
// Optional: makes heart icon clickable and toggles color
document.querySelectorAll(".stat-item svg").forEach((icon) => {
  icon.addEventListener("click", (e) => {
    e.stopPropagation();
    icon.classList.toggle("liked");
    if (icon.classList.contains("liked")) {
      icon.style.stroke = "#ef4444"; // red
      icon.style.fill = "#ef4444";
    } else {
      icon.style.stroke = "currentColor";
      icon.style.fill = "none";
    }
  });
});

// ====== SMOOTH PAGE LOAD ======
window.addEventListener("load", () => {
  document.body.style.opacity = "1";
  document.body.style.transition = "opacity 0.3s ease";
});

