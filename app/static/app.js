const modalFormSnapshots = new WeakMap();
let peopleOrderChanged = false;
let formSubmissionInProgress = false;


function snapshotForm(form) {
  if (!form) return "";
  const values = [];
  form.querySelectorAll("input, select, textarea").forEach((field) => {
    if (!field.name) return;
    if (field.type === "file") {
      const files = [...(field.files || [])].map((file) => [file.name, file.size, file.lastModified]);
      values.push([field.name, files]);
      return;
    }
    const value = (field.type === "checkbox" || field.type === "radio") ? field.checked : field.value;
    values.push([field.name, value]);
  });
  return JSON.stringify(values);
}

function rememberModalState(modal) {
  const form = modal?.querySelector("form");
  if (form) modalFormSnapshots.set(modal, snapshotForm(form));
}

function modalHasUnsavedChanges(modal) {
  const form = modal?.querySelector("form");
  if (!form) return false;
  const initial = modalFormSnapshots.get(modal);
  return initial !== undefined && initial !== snapshotForm(form);
}

function closeModal(modal, { force = false } = {}) {
  if (!modal?.open) return true;
  if (!force && modalHasUnsavedChanges(modal)) return false;
  modal.close();
  return true;
}

function requestModalClose(modal, onClosed = null) {
  if (!modal?.open) return;
  if (!modalHasUnsavedChanges(modal)) {
    modal.close();
    onClosed?.();
    return;
  }
  requestConfirmation(
    "Ungespeicherte Änderungen wirklich verwerfen?",
    () => { modal.close(); onClosed?.(); },
    "Änderungen verwerfen?",
    { okText: "Ja, verwerfen", cancelText: "Nein, weiter bearbeiten", danger: true }
  );
}

function openModal(id) {
  const modal = document.getElementById(id);
  if (modal && !modal.open) {
    modal.showModal();
    requestAnimationFrame(() => rememberModalState(modal));
  }
}

document.querySelectorAll("[data-open-modal]").forEach((button) => {
  button.addEventListener("click", () => {
    const current = button.closest("dialog");
    if (current && current.id !== button.dataset.openModal) closeModal(current, { force: true });
    openModal(button.dataset.openModal);
  });
});

document.querySelectorAll("[data-close-modal]").forEach((button) => {
  button.addEventListener("click", () => {
    const modal = button.closest("dialog");
    const isPeopleAdmin = modal?.id === "people-admin-modal";
    requestModalClose(modal, () => {
      if (isPeopleAdmin && peopleOrderChanged) window.location.reload();
    });
  });
});

document.querySelectorAll("dialog").forEach((dialog) => {
  // Dialoge bleiben bewusst offen: kein Schließen durch Klick auf den Backdrop
  // und auch nicht durch Escape. Schließen erfolgt nur über die sichtbare Aktion.
  dialog.addEventListener("cancel", (event) => event.preventDefault());
});

window.addEventListener("beforeunload", (event) => {
  // Ein bewusst abgeschicktes Formular ist kein Datenverlust. Ohne diese
  // Ausnahme zeigte der Browser beim Speichern fälschlich „Website verlassen?“.
  if (formSubmissionInProgress) return;
  const dirtyOpenModal = [...document.querySelectorAll("dialog[open]")].some(modalHasUnsavedChanges);
  if (!dirtyOpenModal) return;
  event.preventDefault();
  event.returnValue = "";
});

const confirmModal = document.getElementById("confirm-modal");
const confirmTitle = document.getElementById("confirm-title");
const confirmMessage = document.getElementById("confirm-message");
const confirmOk = document.getElementById("confirm-ok");
const confirmCancel = document.getElementById("confirm-cancel");
let pendingConfirmAction = null;

function requestConfirmation(message, onConfirm, title = "Wirklich löschen?", options = {}) {
  if (!confirmModal) {
    // Fallback nur für den unwahrscheinlichen Fall, dass das Dialog-Markup fehlt.
    if (window.confirm(message)) onConfirm();
    return;
  }
  pendingConfirmAction = onConfirm;
  if (confirmOk) { confirmOk.textContent = options.okText || "Ja, löschen"; confirmOk.classList.toggle("danger", options.danger !== false); }
  if (confirmCancel) confirmCancel.textContent = options.cancelText || "Nein, abbrechen";
  if (confirmTitle) confirmTitle.textContent = title;
  if (confirmMessage) confirmMessage.textContent = message || "Dieser Eintrag wird dauerhaft entfernt.";
  if (!confirmModal.open) confirmModal.showModal();
  setTimeout(() => confirmCancel?.focus(), 0);
}

confirmCancel?.addEventListener("click", () => {
  pendingConfirmAction = null;
  confirmModal?.close();
});

confirmOk?.addEventListener("click", () => {
  const action = pendingConfirmAction;
  pendingConfirmAction = null;
  confirmModal?.close();
  action?.();
});

confirmModal?.addEventListener("cancel", (event) => event.preventDefault());

document.querySelectorAll("[data-confirm]").forEach((form) => {
  form.addEventListener("submit", (event) => {
    if (form.dataset.confirmed === "1") {
      delete form.dataset.confirmed;
      return;
    }
    event.preventDefault();
    requestConfirmation(form.dataset.confirm, async () => {
      if (form.hasAttribute("data-dialog-delete")) {
        try {
          const response = await fetch(form.action, { method: "POST", body: new FormData(form), headers: { "X-Requested-With": "fetch" } });
          if (!response.ok) throw new Error("Löschen fehlgeschlagen.");
          const item = form.closest(".manage-item, .history-item");
          item?.remove();
          return;
        } catch (error) {
          requestConfirmation(error.message || "Löschen fehlgeschlagen.", () => {}, "Fehler", { okText: "OK", cancelText: "Schließen", danger: false });
          return;
        }
      }
      form.dataset.confirmed = "1";
      form.requestSubmit();
    }, form.dataset.confirmTitle || "Wirklich löschen?");
  });
});

// Einheitliche Datei-Auswahl: native Browser-Schaltfläche bleibt verborgen,
// der gewählte Dateiname wird im App-Design angezeigt.
document.querySelectorAll("[data-file-input]").forEach((input) => {
  input.addEventListener("change", () => {
    const target = document.getElementById(input.dataset.fileNameTarget || "");
    if (!target) return;
    const file = input.files?.[0];
    target.textContent = file ? file.name : (input.name === "backup_file" ? "Keine Sicherung ausgewählt" : "Kein Bild ausgewählt");
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

const newEventPerson = document.getElementById("new-event-person-id");
document.querySelectorAll("[data-new-medication]").forEach((button) => {
  button.addEventListener("click", () => {
    closeModal(button.closest("dialog"), { force: true });
    if (button.dataset.personId && newEventPerson) newEventPerson.value = button.dataset.personId;
    if (newEventCategory) newEventCategory.value = "Medikament";
    syncMedicationFields(newEventCategory, newMedicationFields, newEventTitleLabel, newEventTitle);
    syncIllnessFields(newEventCategory, newIllnessFields);
    openModal("event-modal");
    setTimeout(() => newEventTitle?.focus(), 0);
  });
});

const newAllergyPerson = document.getElementById("new-allergy-person-id");
document.querySelectorAll("[data-new-allergy]").forEach((button) => {
  button.addEventListener("click", () => {
    closeModal(button.closest("dialog"), { force: true });
    if (button.dataset.personId && newAllergyPerson) newAllergyPerson.value = button.dataset.personId;
    openModal("allergy-modal");
    setTimeout(() => document.querySelector("#allergy-modal input[name='name']")?.focus(), 0);
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
    closeModal(button.closest("dialog"), { force: true });
    openModal("edit-event-modal");
  });
});

deleteBtn?.addEventListener("click", () => {
  const eventId = deleteBtn.dataset.eventId;
  if (!eventId) return;
  requestConfirmation("Eintrag wirklich löschen? Dieser Eintrag wird dauerhaft entfernt.", () => {
    const form = document.createElement("form");
    form.method = "post";
    form.action = `/events/${eventId}/delete`;
    document.body.appendChild(form);
    form.submit();
  });
});

const editPersonForm = document.getElementById("edit-person-form");
const editProfileFile = document.getElementById("edit-profile-file");
const editProfileFileName = document.getElementById("edit-profile-file-name");
const editProfilePreviewImage = document.getElementById("edit-profile-preview-image");
const editProfileInitial = document.getElementById("edit-profile-initial");
const editRemoveProfileImage = document.getElementById("edit-remove-profile-image");
let currentProfileImage = "";

function setProfilePreview(src, name = "") {
  if (src) {
    editProfilePreviewImage.src = src;
    editProfilePreviewImage.hidden = false;
    editProfileInitial.hidden = true;
  } else {
    editProfilePreviewImage.removeAttribute("src");
    editProfilePreviewImage.hidden = true;
    editProfileInitial.textContent = (name || "?").trim().charAt(0).toUpperCase() || "?";
    editProfileInitial.hidden = false;
  }
}

editProfileFile?.addEventListener("change", () => {
  const file = editProfileFile.files?.[0];
  editProfileFileName.textContent = file ? file.name : "Kein neues Bild ausgewählt";
  if (!file) {
    setProfilePreview(currentProfileImage, document.getElementById("edit-person-name")?.value);
    return;
  }
  const reader = new FileReader();
  reader.onload = () => setProfilePreview(String(reader.result || ""), document.getElementById("edit-person-name")?.value);
  reader.readAsDataURL(file);
  if (editRemoveProfileImage) editRemoveProfileImage.checked = false;
});

editRemoveProfileImage?.addEventListener("change", () => {
  if (editRemoveProfileImage.checked) setProfilePreview("", document.getElementById("edit-person-name")?.value);
  else if (!editProfileFile?.files?.length) setProfilePreview(currentProfileImage, document.getElementById("edit-person-name")?.value);
});

document.querySelectorAll("[data-edit-person]").forEach((button) => {
  button.addEventListener("click", () => {
    document.getElementById("edit-person-name").value = button.dataset.name;
    document.getElementById("edit-person-birth-date").value = button.dataset.birthDate;
    document.getElementById("edit-person-gender").value = button.dataset.gender;
    document.getElementById("edit-person-notes").value = button.dataset.notes;
    currentProfileImage = button.dataset.profileImage || "";
    if (editProfileFile) editProfileFile.value = "";
    if (editProfileFileName) editProfileFileName.textContent = "Kein neues Bild ausgewählt";
    if (editRemoveProfileImage) editRemoveProfileImage.checked = false;
    setProfilePreview(currentProfileImage, button.dataset.name);
    editPersonForm.action = `/people/${button.dataset.id}/edit`;
    closeModal(button.closest("dialog"), { force: true });
    openModal("edit-person-modal");
  });
});

const editAllergyForm = document.getElementById("edit-allergy-form");
const editAllergyResolved = document.getElementById("edit-allergy-resolved");
const allergyResolvedFields = document.getElementById("allergy-resolved-fields");
const editAllergyEndDate = document.getElementById("edit-allergy-end-date");

function syncAllergyResolvedFields() {
  if (!allergyResolvedFields || !editAllergyResolved) return;
  allergyResolvedFields.hidden = !editAllergyResolved.checked;
}
editAllergyResolved?.addEventListener("change", syncAllergyResolvedFields);

document.querySelectorAll("[data-edit-allergy]").forEach((button) => {
  button.addEventListener("click", () => {
    document.getElementById("edit-allergy-person-id").value = button.dataset.personId;
    document.getElementById("edit-allergy-name").value = button.dataset.name;
    document.getElementById("edit-allergy-reaction").value = button.dataset.reaction;
    document.getElementById("edit-allergy-notes").value = button.dataset.notes;
    document.getElementById("edit-allergy-start-date").value = button.dataset.startDate || "";
    editAllergyEndDate.value = button.dataset.endDate || "";
    document.getElementById("edit-allergy-resolved-note").value = button.dataset.resolvedNote || "";
    editAllergyResolved.checked = Boolean(button.dataset.endDate);
    syncAllergyResolvedFields();
    editAllergyForm.action = `/allergies/${button.dataset.id}/edit`;
    closeModal(button.closest("dialog"), { force: true });
    openModal("edit-allergy-modal");
  });
});

function syncIllnessFields(categorySelect, fields) {
  if (!categorySelect || !fields) return;
  fields.hidden = categorySelect.value !== "Krankheit";
}

const newIllnessFields = document.getElementById("new-illness-fields");
newEventCategory?.addEventListener("change", () => syncIllnessFields(newEventCategory, newIllnessFields));
syncIllnessFields(newEventCategory, newIllnessFields);

const editIllnessFields = document.getElementById("edit-illness-fields");
editCategory?.addEventListener("change", () => syncIllnessFields(editCategory, editIllnessFields));

// Ergänzt den bestehenden Bearbeiten-Handler um Krankschreibung/Attest.
document.querySelectorAll("[data-edit-event]").forEach((button) => {
  button.addEventListener("click", () => {
    const isSickNote = document.getElementById("edit-is-sick-note");
    const sickFrom = document.getElementById("edit-sick-from");
    const sickTo = document.getElementById("edit-sick-to");
    const hasAttest = document.getElementById("edit-has-attest");
    const attestType = document.getElementById("edit-attest-type");
    if (isSickNote) isSickNote.checked = button.dataset.isSickNote === "1";
    if (sickFrom) sickFrom.value = button.dataset.sickFrom || "";
    if (sickTo) sickTo.value = button.dataset.sickTo || "";
    if (hasAttest) hasAttest.checked = button.dataset.hasAttest === "1";
    if (attestType) attestType.value = button.dataset.attestType || "";
    syncIllnessFields(editCategory, editIllnessFields);
  });
});


// v0.6.1: Reihenfolge im Hintergrund speichern, ohne den Verwaltungsdialog zu schließen.
const peopleSortList = document.getElementById("people-sort-list");
const peopleSortStatus = document.getElementById("people-sort-status");
if (peopleSortList) {
  let dragged = null;
  let saveTimer = null;
  const rows = () => [...peopleSortList.querySelectorAll(".admin-person[data-person-id]")];

  function setPeopleSortStatus(message, type = "success") {
    if (!peopleSortStatus) return;
    peopleSortStatus.hidden = false;
    peopleSortStatus.textContent = message;
    peopleSortStatus.dataset.type = type;
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => { peopleSortStatus.hidden = true; }, 1800);
  }

  async function persistPeopleOrder() {
    const ids = rows().map((row) => Number(row.dataset.personId));
    try {
      const response = await fetch("/people/reorder", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ people: ids }),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok || payload.ok !== true) throw new Error(payload.error || "Reihenfolge konnte nicht gespeichert werden.");
      peopleOrderChanged = true;
      setPeopleSortStatus("✓ Reihenfolge gespeichert");
    } catch (error) {
      setPeopleSortStatus(error.message || "Reihenfolge konnte nicht gespeichert werden.", "error");
    }
  }

  rows().forEach((row) => {
    // Nur der sichtbare Griff startet eine Sortierung; so verschiebt man
    // Personen nicht versehentlich beim Klicken auf Bearbeiten/Löschen.
    const handle = row.querySelector(".drag-handle");
    row.draggable = false;
    handle?.addEventListener("mousedown", () => { row.draggable = true; });
    handle?.addEventListener("mouseup", () => { if (!dragged) row.draggable = false; });

    row.addEventListener("dragstart", (event) => {
      if (!row.draggable) { event.preventDefault(); return; }
      dragged = row;
      row.classList.add("dragging");
      event.dataTransfer.effectAllowed = "move";
      event.dataTransfer.setData("text/plain", row.dataset.personId);
    });
    row.addEventListener("dragend", () => {
      row.draggable = false;
      row.classList.remove("dragging");
      rows().forEach((item) => item.classList.remove("drag-over"));
      dragged = null;
    });
    row.addEventListener("dragover", (event) => {
      event.preventDefault();
      if (!dragged || dragged === row) return;
      row.classList.add("drag-over");
      const rect = row.getBoundingClientRect();
      const before = event.clientY < rect.top + rect.height / 2;
      peopleSortList.insertBefore(dragged, before ? row : row.nextSibling);
    });
    row.addEventListener("dragleave", () => row.classList.remove("drag-over"));
    row.addEventListener("drop", (event) => {
      event.preventDefault();
      rows().forEach((item) => item.classList.remove("drag-over"));
      persistPeopleOrder();
    });
  });
  peopleSortList.querySelectorAll(".sort-step").forEach((button) => {
    button.addEventListener("click", () => {
      const row = button.closest(".admin-person");
      if (!row) return;
      if (button.classList.contains("sort-up")) {
        const prev = row.previousElementSibling;
        if (prev?.matches(".admin-person")) peopleSortList.insertBefore(row, prev);
      } else {
        const next = row.nextElementSibling;
        if (next?.matches(".admin-person")) peopleSortList.insertBefore(next, row);
      }
      persistPeopleOrder();
    });
  });

}



// v0.6.2 – kommende Einträge kompakt halten, bei Bedarf aufklappen.
const futureTimeline = document.getElementById("future-timeline");
const futureToggle = document.getElementById("future-toggle");
const futureItems = futureTimeline ? Array.from(futureTimeline.querySelectorAll(":scope > .timeline-item")) : [];
const futureExtraCount = Math.max(0, futureItems.length - 5);
if (futureTimeline?.dataset.collapseFuture === "1" && futureExtraCount > 0) {
  futureItems.slice(0, futureExtraCount).forEach((item) => { item.hidden = true; item.classList.add("future-extra"); });
}
futureToggle?.addEventListener("click", () => {
  const extras = futureItems.slice(0, futureExtraCount);
  const currentlyHidden = extras.some((item) => item.hidden);
  extras.forEach((item) => { item.hidden = !currentlyHidden; });
  futureToggle.textContent = currentlyHidden
    ? "Weniger geplante Einträge anzeigen"
    : `+ Weitere ${futureToggle.dataset.extra || extras.length} geplante Einträge anzeigen`;
});

// Erst nach allen formularspezifischen Submit-Handlern entscheiden, ob die Seite
// tatsächlich verlassen wird. So bleibt die Warnung bei echtem Datenverlust aktiv,
// erscheint aber niemals beim normalen Speichern/Importieren.
document.addEventListener("submit", (event) => {
  if (event.defaultPrevented) return;
  formSubmissionInProgress = true;
  const modal = event.target.closest?.("dialog");
  if (modal) modalFormSnapshots.set(modal, snapshotForm(event.target));
});
