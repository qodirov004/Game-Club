document.addEventListener("DOMContentLoaded", () => {
  // Sidebar toggle for mobile
  const sidebarToggle = document.getElementById("sidebarToggle");
  const sidebar = document.getElementById("sidebar");

  if (sidebarToggle && sidebar) {
      sidebarToggle.addEventListener("click", () => {
          sidebar.classList.toggle("show");
      });
  }

  // Tariff options in start game page
  const tariffOptions = document.querySelectorAll(".tariff-option");

  if (tariffOptions.length > 0) {
      tariffOptions.forEach((option) => {
          option.addEventListener("click", function() {
              // Remove selected class from all options
              tariffOptions.forEach((opt) => {
                  opt.classList.remove("selected");
              });

              // Add selected class to clicked option
              this.classList.add("selected");

              // Check the radio button
              const radio = this.querySelector('input[type="radio"]');
              if (radio) {
                  radio.checked = true;
              }
          });
      });
  }

  // Auto-dismiss alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert');
  if (alerts.length > 0) {
      alerts.forEach(alert => {
          setTimeout(() => {
              const closeButton = alert.querySelector('.btn-close');
              if (closeButton) {
                  closeButton.click();
              }
          }, 5000);
      });
  }
});

// Dark Mode Toggle Functionality
class DarkModeManager {
  constructor() {
    this.init()
  }

  init() {
    // Check for saved theme preference or default to light mode
    const savedTheme = localStorage.getItem("theme")
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches

    if (savedTheme) {
      this.setTheme(savedTheme)
    } else if (prefersDark) {
      this.setTheme("dark")
    }

    // Listen for system theme changes
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", (e) => {
      if (!localStorage.getItem("theme")) {
        this.setTheme(e.matches ? "dark" : "light")
      }
    })

    this.setupToggleButtons()
  }

  setTheme(theme) {
    if (theme === "dark") {
      document.body.classList.add("dark-mode")
    } else {
      document.body.classList.remove("dark-mode")
    }

    localStorage.setItem("theme", theme)
    this.updateToggleButtons(theme)
  }

  toggleTheme() {
    const currentTheme = document.body.classList.contains("dark-mode") ? "dark" : "light"
    const newTheme = currentTheme === "dark" ? "light" : "dark"
    this.setTheme(newTheme)
  }

  setupToggleButtons() {
    // Create toggle button if it doesn't exist
    const existingToggle = document.querySelector(".dark-mode-toggle")
    if (!existingToggle) {
      this.createToggleButton()
    }

    // Add event listeners to all toggle buttons
    document.querySelectorAll(".dark-mode-toggle").forEach((button) => {
      button.addEventListener("click", () => this.toggleTheme())
    })
  }

  createToggleButton() {
    const toggleButton = document.createElement("button")
    toggleButton.className = "dark-mode-toggle"
    toggleButton.innerHTML = '<i class="fas fa-moon"></i>'
    toggleButton.setAttribute("aria-label", "Toggle dark mode")
    toggleButton.setAttribute("title", "Toggle dark mode")

    // Add to header actions if it exists
    const headerActions = document.querySelector(".header-actions")
    if (headerActions) {
      headerActions.appendChild(toggleButton)
    }
  }

  updateToggleButtons(theme) {
    document.querySelectorAll(".dark-mode-toggle i").forEach((icon) => {
      if (theme === "dark") {
        icon.className = "fas fa-sun"
      } else {
        icon.className = "fas fa-moon"
      }
    })

    // Update aria-label
    document.querySelectorAll(".dark-mode-toggle").forEach((button) => {
      const label = theme === "dark" ? "Switch to light mode" : "Switch to dark mode"
      button.setAttribute("aria-label", label)
      button.setAttribute("title", label)
    })
  }

  // Method to get current theme
  getCurrentTheme() {
    return document.body.classList.contains("dark-mode") ? "dark" : "light"
  }

  // Method to check if dark mode is enabled
  isDarkMode() {
    return document.body.classList.contains("dark-mode")
  }
}

// Initialize dark mode manager when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  window.darkModeManager = new DarkModeManager()
})

// Export for use in other scripts
if (typeof module !== "undefined" && module.exports) {
  module.exports = DarkModeManager
}
