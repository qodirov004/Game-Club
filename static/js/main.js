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