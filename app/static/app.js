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

function syncMedicationFields(categorySelect, fields, titleLabel, titleInput) {
  if (!categorySelect || !fields) return;
  const isMedication = categorySelect.value === "Medikament";
  fields.hidden = !isMedication;
  if (titleLabel) titleLabel.textContent = isMedication ? "Medikament" : "Titel";
  if (titleInput) {
    titleInput.placeholder = isMedication ? "z. B. Cetirizin" : "z. B. Grippe";
  }
}

const newEventCategory = document.getElementById("new-event-category");
const newMedicationFields = document.getElementById("new-medication-fields");
const newEventTitleLabel = document.getElementById("new-event-title-label");
const newEventTitle = document.getElementById("new-event-title");
newEventCategory?.addEventListener("change", () => syncMedicationFields(newEventCategory, newMedicationFields, newEventTitleLabel, newEventTitle));
syncMedicationFields(newEventCategory, newMedicationFields, newEventTitleLabel, newEventTitle);

document.querySelectorAll("[data-new-medication]").forEach((button) => {
  button.addEventListener("click", () => {
    if (newEventCategory) newEventCategory.value = "Medikament";
    syncMedicationFields(newEventCategory, newMedicationFields, newEventTitleLabel, newEventTitle);
    openModal("event-modal");
    setTimeout(() => newEventTitle?.focus(), 0);
  });
});

const editModal = document.getElementById("edit-event-modal");
const editForm = document.getElementById("edit-event-form");
const deleteBtn = document.getElementById("delete-event-btn");
const editCategory = document.getElementById("edit-category");
const editMedicationFields = document.getElementById("edit-medication-fields");
editCategory?.addEventListener("change", () => syncMedicationFields(editCategory, editMedicationFields));

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
    document.getElementById("edit-medication-dosage").value = button.dataset.medicationDosage || "";
    document.getElementById("edit-medication-reason").value = button.dataset.medicationReason || "";
    document.getElementById("edit-medication-intolerance").checked = button.dataset.medicationIntolerance === "1";
    syncMedicationFields(editCategory, editMedicationFields);
    editForm.action = `/events/${button.dataset.id}/edit`;
    deleteBtn.dataset.eventId = button.dataset.id;
    button.closest("dialog")?.close();
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

const editAllergyForm = document.getElementById("edit-allergy-form");
document.querySelectorAll("[data-edit-allergy]").forEach((button) => {
  button.addEventListener("click", () => {
    document.getElementById("edit-allergy-person-id").value = button.dataset.personId;
    document.getElementById("edit-allergy-name").value = button.dataset.name;
    document.getElementById("edit-allergy-reaction").value = button.dataset.reaction;
    document.getElementById("edit-allergy-notes").value = button.dataset.notes;
    editAllergyForm.action = `/allergies/${button.dataset.id}/edit`;
    openModal("edit-allergy-modal");
  });
});
