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


function cleanupEmptyPersonGroups() {
  document.querySelectorAll(".sidebar .person-group, #medication-history-modal .person-group, #allergy-history-modal .person-group").forEach((group) => {
    const hasItems = group.querySelector("[data-event-id], [data-allergy-id]");
    if (!hasItems) group.remove();
  });

  const medHistoryHasGroups = !!document.querySelector("#medication-history-modal .person-group");
  const medEmpty = document.getElementById("medication-history-empty");
  if (medEmpty) medEmpty.hidden = medHistoryHasGroups;
  const medLink = document.getElementById("medication-history-link");
  if (medLink && !medHistoryHasGroups) medLink.hidden = true;

  const allergyHistoryHasGroups = !!document.querySelector("#allergy-history-modal .person-group");
  const allergyEmpty = document.getElementById("allergy-history-empty");
  if (allergyEmpty) allergyEmpty.hidden = allergyHistoryHasGroups;
  const allergyLink = document.getElementById("allergy-history-link");
  if (allergyLink && !allergyHistoryHasGroups) allergyLink.hidden = true;
}

function syncDeletedItem(form) {
  const source = form.closest("[data-event-id], [data-allergy-id]");
  const eventId = source?.dataset.eventId;
  const allergyId = source?.dataset.allergyId;

  if (eventId) {
    document.querySelectorAll(`[data-event-id="${eventId}"]`).forEach((node) => node.remove());
  }
  if (allergyId) {
    document.querySelectorAll(`[data-allergy-id="${allergyId}"]`).forEach((node) => node.remove());
  }
  cleanupEmptyPersonGroups();
}

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
          syncDeletedItem(form);
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
const editEventTitleLabel = document.getElementById("edit-event-title-label");
const editEventTitle = document.getElementById("edit-title");
editCategory?.addEventListener("change", () => syncMedicationFields(editCategory, editMedicationFields, editEventTitleLabel, editEventTitle));

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
    syncMedicationFields(editCategory, editMedicationFields, editEventTitleLabel, editEventTitle);
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
    // Bewusst bestätigtes Löschen ist kein ungespeicherter Datenverlust.
    // form.submit() feuert kein submit-Event, deshalb den Schutz hier explizit deaktivieren.
    formSubmissionInProgress = true;
    if (editModal) modalFormSnapshots.set(editModal, snapshotForm(editForm));
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

// v0.7.0 – Behandlungsfälle/Vorgänge verbinden zusammengehörige Timeline-Einträge.
function syncCaseSelect(select, personSelect, newTitleWrap, newTitleInput) {
  if (!select || !personSelect) return;
  const personId = String(personSelect.value || "");
  [...select.options].forEach((option) => {
    if (!option.dataset.personId) return;
    const matches = option.dataset.personId === personId;
    option.hidden = !matches;
    option.disabled = !matches;
  });
  const selected = select.selectedOptions?.[0];
  if (selected?.dataset.personId && selected.dataset.personId !== personId) select.value = "";
  const creatingNew = select.value === "__new__";
  if (newTitleWrap) newTitleWrap.hidden = !creatingNew;
  if (newTitleInput) {
    newTitleInput.required = creatingNew;
    if (!creatingNew) newTitleInput.value = "";
  }
}

const newCaseSelect = document.getElementById("new-case-id");
const newCaseTitleWrap = document.getElementById("new-case-title-wrap");
const newCaseTitle = document.getElementById("new-case-title");
newEventPerson?.addEventListener("change", () => syncCaseSelect(newCaseSelect, newEventPerson, newCaseTitleWrap, newCaseTitle));
newCaseSelect?.addEventListener("change", () => syncCaseSelect(newCaseSelect, newEventPerson, newCaseTitleWrap, newCaseTitle));
syncCaseSelect(newCaseSelect, newEventPerson, newCaseTitleWrap, newCaseTitle);

const editCaseSelect = document.getElementById("edit-case-id");
const editCaseTitleWrap = document.getElementById("edit-case-title-wrap");
const editCaseTitle = document.getElementById("edit-case-title");
const editPersonSelect = document.getElementById("edit-person-id");
editPersonSelect?.addEventListener("change", () => syncCaseSelect(editCaseSelect, editPersonSelect, editCaseTitleWrap, editCaseTitle));
editCaseSelect?.addEventListener("change", () => syncCaseSelect(editCaseSelect, editPersonSelect, editCaseTitleWrap, editCaseTitle));

// Ergänzt den bestehenden Event-Bearbeiten-Handler um die Vorgangszuordnung.
document.querySelectorAll("[data-edit-event]").forEach((button) => {
  button.addEventListener("click", () => {
    if (!editCaseSelect) return;
    syncCaseSelect(editCaseSelect, editPersonSelect, editCaseTitleWrap, editCaseTitle);
    editCaseSelect.value = button.dataset.caseId || "";
    syncCaseSelect(editCaseSelect, editPersonSelect, editCaseTitleWrap, editCaseTitle);
  });
});

function prepareRelatedEntry(button) {
  closeModal(button.closest("dialog"), { force: true });
  if (newEventPerson) newEventPerson.value = button.dataset.personId || newEventPerson.value;
  if (newEventCategory && button.dataset.category) newEventCategory.value = button.dataset.category;
  if (newCaseSelect) newCaseSelect.value = button.dataset.caseId || "";
  syncMedicationFields(newEventCategory, newMedicationFields, newEventTitleLabel, newEventTitle);
  syncIllnessFields(newEventCategory, newIllnessFields);
  syncCaseSelect(newCaseSelect, newEventPerson, newCaseTitleWrap, newCaseTitle);
  openModal("event-modal");
  setTimeout(() => newEventTitle?.focus(), 0);
}

document.querySelectorAll("[data-related-entry]").forEach((button) => {
  button.addEventListener("click", () => prepareRelatedEntry(button));
});

// v0.7.1 – Vorgangsverwaltung und skalierbare Auswahl.
function setupCaseSearch(select, personSelect, searchWrapId, searchId) {
  const wrap = document.getElementById(searchWrapId);
  const input = document.getElementById(searchId);
  if (!select || !personSelect || !wrap || !input) return;

  function refresh() {
    const personId = String(personSelect.value || "");
    const visibleCaseOptions = [...select.options].filter((option) => option.dataset.personId === personId && !option.disabled);
    wrap.hidden = visibleCaseOptions.length <= 10;
    if (wrap.hidden) input.value = "";
    const term = input.value.trim().toLowerCase();
    [...select.options].forEach((option) => {
      if (!option.dataset.personId || option.value === "__new__") return;
      const personMatches = option.dataset.personId === personId;
      const textMatches = !term || option.textContent.toLowerCase().includes(term);
      option.hidden = !(personMatches && textMatches);
    });
  }

  input.addEventListener("input", refresh);
  personSelect.addEventListener("change", refresh);
  select.addEventListener("change", refresh);
  refresh();
}

setupCaseSearch(newCaseSelect, newEventPerson, "new-case-search-wrap", "new-case-search");
setupCaseSearch(editCaseSelect, editPersonSelect, "edit-case-search-wrap", "edit-case-search");

function caseStatusLabel(status) {
  if (status === "completed") return "Abgeschlossen";
  if (status === "archived") return "Archiviert";
  return "Aktiv";
}

function updateCaseAdminStatus(item, status) {
  item.dataset.caseStatus = status;
  const chip = item.querySelector(".case-status-chip");
  if (chip) {
    chip.className = `case-status-chip case-status-${status}`;
    chip.textContent = caseStatusLabel(status);
  }
}

document.querySelectorAll("[data-case-save]").forEach((button) => {
  button.addEventListener("click", async () => {
    const item = button.closest("[data-case-admin-id]");
    const input = item?.querySelector(".case-admin-title");
    const caseId = item?.dataset.caseAdminId;
    if (!caseId || !input?.value.trim()) return;
    const body = new URLSearchParams({ title: input.value.trim() });
    const response = await fetch(`/cases/${caseId}/edit`, { method: "POST", body, headers: { "X-Requested-With": "fetch" } });
    if (!response.ok) return;
    document.querySelectorAll(`select[name="case_id"] option[value="${caseId}"]`).forEach((option) => {
      const suffix = option.dataset.caseStatus && option.dataset.caseStatus !== "active" ? ` · ${option.dataset.caseStatus === "completed" ? "abgeschlossen" : "archiviert"}` : "";
      option.textContent = input.value.trim() + suffix;
    });
    document.querySelectorAll(`[data-open-modal="case-modal-${caseId}"]`).forEach((badge) => { badge.textContent = `🔗 ${input.value.trim()}`; });
    button.textContent = "✓";
  });
});

document.querySelectorAll(".case-status-select").forEach((select) => {
  select.addEventListener("change", async () => {
    const item = select.closest("[data-case-admin-id]");
    const caseId = item?.dataset.caseAdminId;
    if (!caseId) return;
    const body = new URLSearchParams({ status: select.value });
    const response = await fetch(`/cases/${caseId}/status`, { method: "POST", body, headers: { "X-Requested-With": "fetch" } });
    if (!response.ok) return;
    updateCaseAdminStatus(item, select.value);
    document.querySelectorAll(`select[name="case_id"] option[value="${caseId}"]`).forEach((option) => {
      option.dataset.caseStatus = select.value;
      if (option.closest("#new-case-id") && select.value !== "active") option.remove();
    });
  });
});

document.querySelectorAll("[data-case-delete]").forEach((button) => {
  button.addEventListener("click", () => {
    const item = button.closest("[data-case-admin-id]");
    const caseId = item?.dataset.caseAdminId;
    const eventCount = Number(button.dataset.eventCount || 0);
    if (!caseId) return;
    const message = eventCount > 0
      ? `Dieser Vorgang ist noch mit ${eventCount} ${eventCount === 1 ? "Eintrag" : "Einträgen"} verknüpft. Der Vorgang wird gelöscht, die Einträge bleiben erhalten und verlieren nur die Zuordnung. Wirklich löschen?`
      : "Dieser Vorgang enthält keine Einträge und wird dauerhaft gelöscht. Wirklich löschen?";
    requestConfirmation(message, async () => {
      const response = await fetch(`/cases/${caseId}/delete`, { method: "POST", headers: { "X-Requested-With": "fetch" } });
      if (!response.ok) return;
      document.querySelectorAll(`select[name="case_id"] option[value="${caseId}"]`).forEach((option) => option.remove());
      document.querySelectorAll(`[data-open-modal="case-modal-${caseId}"]`).forEach((badge) => badge.remove());
      document.getElementById(`case-modal-${caseId}`)?.remove();
      item.remove();
      if (!document.querySelector("[data-case-admin-id]")) {
        const list = document.getElementById("case-admin-list");
        if (list) list.innerHTML = '<p class="muted" id="case-admin-empty">Noch keine Vorgänge angelegt.</p>';
      }
    }, "Vorgang wirklich löschen?", { okText: "Ja, Vorgang löschen", cancelText: "Nein, behalten" });
  });
});
