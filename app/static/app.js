function openModal(id) {
  const modal = document.getElementById(id);
  if (modal && !modal.open) modal.showModal();
}

document.querySelectorAll("[data-open-modal]").forEach((button) => {
  button.addEventListener("click", () => openModal(button.dataset.openModal));
});

document.querySelectorAll("[data-close-modal]").forEach((button) => {
  button.addEventListener("click", () => button.closest("dialog")?.close());
});

document.querySelectorAll("dialog").forEach((dialog) => {
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
});

document.querySelectorAll("[data-confirm]").forEach((form) => {
  form.addEventListener("submit", (event) => {
    if (!confirm(form.dataset.confirm)) event.preventDefault();
  });
});

const editModal = document.getElementById("edit-event-modal");
const editForm = document.getElementById("edit-event-form");
const deleteBtn = document.getElementById("delete-event-btn");

document.querySelectorAll("[data-edit-event]").forEach((button) => {
  button.addEventListener("click", () => {
    document.getElementById("edit-person-id").value = button.dataset.personId;
    document.getElementById("edit-category").value = button.dataset.category;
    document.getElementById("edit-title").value = button.dataset.title;
    document.getElementById("edit-start-date").value = button.dataset.startDate;
    document.getElementById("edit-end-date").value = button.dataset.endDate;
    document.getElementById("edit-notes").value = button.dataset.notes;
    document.getElementById("edit-document-url").value = button.dataset.documentUrl;
    document.getElementById("edit-is-important").checked = button.dataset.isImportant === "1";
    editForm.action = `/events/${button.dataset.id}/edit`;
    deleteBtn.dataset.eventId = button.dataset.id;
    editModal.showModal();
  });
});

deleteBtn?.addEventListener("click", () => {
  const eventId = deleteBtn.dataset.eventId;
  if (!eventId || !confirm("Eintrag wirklich löschen?")) return;
  const form = document.createElement("form");
  form.method = "post";
  form.action = `/events/${eventId}/delete`;
  document.body.appendChild(form);
  form.submit();
});

const editPersonForm = document.getElementById("edit-person-form");
document.querySelectorAll("[data-edit-person]").forEach((button) => {
  button.addEventListener("click", () => {
    document.getElementById("edit-person-name").value = button.dataset.name;
    document.getElementById("edit-person-birth-date").value = button.dataset.birthDate;
    document.getElementById("edit-person-gender").value = button.dataset.gender;
    document.getElementById("edit-person-notes").value = button.dataset.notes;
    editPersonForm.action = `/people/${button.dataset.id}/edit`;
    button.closest("dialog")?.close();
    openModal("edit-person-modal");
  });
});
