/* Activate all tooltips */
[].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]')).map(trigger => new bootstrap.Tooltip(trigger));

/* Validate forms */
(function () {
  "use strict";

  // Get all forms that needs validation
  const forms = document.querySelectorAll('.needs-validation');

  // Iterate through forms and prevent submission
  Array.prototype.filter.call(forms, form => {

    form.addEventListener("submit", event => {

      // If form has invalid data
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }

      // Add validated class
      form.classList.add("was-validated");
    }, false);
  });

  // Get all inputs in forms that needs validation
  const inputs = document.querySelectorAll(".needs-validation input");

  // Iterate through inputs and validate
  Array.prototype.filter.call(inputs, input => {

    // Validator function
    function validator() {
      // Reset classes
      input.classList.remove("is-valid");
      input.classList.remove("is-invalid");

      // Validate input and add corresponding classes
      if (input.checkValidity()) {
        input.classList.add("is-valid");
      } else {
        input.classList.add("is-invalid");
      }
    }

    // Calll validator on blur and input event
    input.addEventListener("blur", validator, false);
    input.addEventListener("input", validator, false);
  });
})();
