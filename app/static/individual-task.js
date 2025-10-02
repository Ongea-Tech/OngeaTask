document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("addSubtaskBtn").addEventListener("click", function () {
    const input = document.getElementById("subtaskInput");
    const subtaskText = input.value.trim();

    if (subtaskText !== "") {
      // Create label
      const label = document.createElement("label");
      label.className = "checkbox";

      // Create the checkbox
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";

      // Create <p>Subtask text</p>
      const text = document.createElement("p");
      text.textContent = subtaskText;

      // Create delete icon
      const deleteLink = document.createElement("a");
      deleteLink.href = "#";
      deleteLink.className = "icon";

      const trashIcon = document.createElement("i");
      trashIcon.className = "fa-solid fa-trash-can";

      deleteLink.appendChild(trashIcon);

      // Append everything to the label
      label.appendChild(checkbox);
      label.appendChild(text);
      label.appendChild(deleteLink);

      // Append the label to the subtask list
      document.getElementById("subtaskList").appendChild(label);

      // empties the input field
      input.value = "";


      // if input is empyty      
    } else {
      alert("Please enter a new item.");
    }
  });

  // deletes a subtask 
  document.getElementById("subtaskList").addEventListener("click", function (event) {
    if (event.target.classList.contains("fa-trash-can")) {
        event.preventDefault() // Prevent link navigation
        const subtaskItem = event.target.closest(".checkbox");
        if (subtaskItem) {
        subtaskItem.remove();
        }
    }    
    });

    // checks all subtasks functionality
    document.getElementById("checkAllBox").addEventListener("change", function () {
    const isChecked = this.checked;
    const allSubtaskCheckboxes = document.querySelectorAll("#subtaskList input[type='checkbox']");
    allSubtaskCheckboxes.forEach(cb => cb.checked = isChecked);
    });

    // deletes all subtasks functionality
    document.getElementById("deleteAllBtn").addEventListener("click", function (event) {
    event.preventDefault(); // Prevent link navigation
    const confirmDelete = confirm("Are you sure you want to delete all subtasks?");
    if (confirmDelete) {
        const subtaskList = document.getElementById("subtaskList");
        subtaskList.innerHTML = ""; // Remove all subtasks

        document.getElementById("checkAllBox").checked = false;
    }
    });

});
