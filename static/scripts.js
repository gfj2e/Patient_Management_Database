let selectedPrescriptionId = null;
let selectedMedicationName = null;
let selectedDosage = null;

function openRefillModal(){
    document.getElementById('prescription-refill-popup').setAttribute('aria-hidden', 'false');
    resetSelection();
}

function closeRefillModal(){
    document.getElementById('prescription-refill-popup').setAttribute('aria-hidden', 'true');
    resetSelection();
}

function resetSelection(){
    selectedPrescriptionId = null;
    selectedDosage = null;
    selectedMedicationName = null;

    const options = document.querySelectorAll('.prescription-option');
    options.forEach(option => options.classList.remove('selected'));

    // Hide selected prescrip info
    document.getElementById('selected-prescription-info').setAttribute('aria-hidden', 'true');

    // Disable submit button
    document.getElementById('submitRefillBtn').disabled = true;
        
}

function selectPrescription(element) {
    // Remove selected class from all options
    const options = document.querySelectorAll('.prescription-option');
    options.forEach(option => option.classList.remove('selected'));
    
    // Add selected class to clicked option
    element.classList.add('selected');
    
    // Store selected prescription data
    selectedPrescriptionId = element.getAttribute('data-prescription-id');
    selectedMedicationName = element.getAttribute('data-med-name');
    selectedDosage = element.getAttribute('data-dosage');
    
    // Show selected prescription info
    document.getElementById('selected-med-name').textContent = selectedMedicationName;
    document.getElementById('selected-med-dosage').textContent = selectedDosage;
    document.getElementById('selected-prescription-info').setAttribute('aria-hidden', 'false');
    
    // Enable submit button
    document.getElementById('submitRefillBtn').disabled = false;
}

function submitRefillRequest() {
    if (!selectedPrescriptionId) {
        alert('Please select a medication first.');
        return;
    }
    alert(`Refill request submitted for ${selectedMedicationName} - ${selectedDosage}`);
    
    
    
    closeRefillModal();
}

function openContactModal() {
    document.getElementById('contact-us-popup').setAttribute('aria-hidden', 'false');
}

function closeContactModal() {
    document.getElementById('contact-us-popup').setAttribute('aria-hidden', 'true');
}

// Close modal when clicking outside
window.onclick = function(event) {
    const refillModal = document.getElementById('prescription-refill-popup');
    const contactModal = document.getElementById('contact-us-popup');
    
    if (event.target === refillModal) {
        closeRefillModal();
    }
    if (event.target === contactModal) {
        closeContactModal();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const refillCloseBtn = document.querySelector('[id="prescription-refill-popup"] .close');
    const refillCancelBtn = document.querySelector('[id="prescription-refill-popup"] .modal-btn-cancel');
    
    if (refillCloseBtn) {
        refillCloseBtn.addEventListener('click', closeRefillModal);
    }
    if (refillCancelBtn) {
        refillCancelBtn.addEventListener('click', closeRefillModal);
    }
});

// Download Modal Functions
let selectedResultId = null;

function openDownloadModal() {
    document.getElementById('downloadModal').style.display = 'block';
    selectedResultId = null;
    document.getElementById('downloadPdfBtn').disabled = true;
    
    // Fetch lab results
    fetch('/get-lab-results-json')
        .then(response => response.json())
        .then(data => {
            const resultsList = document.getElementById('resultsList');
            resultsList.innerHTML = '';
            
            if (data.success && data.results && data.results.length > 0) {
                data.results.forEach(result => {
                    const resultDiv = document.createElement('div');
                    resultDiv.className = 'result-item';
                    resultDiv.onclick = function() { selectResult(result.test_id, this); };
                    resultDiv.innerHTML = `
                        <strong>${result.test_name}</strong>
                        <br>
                        <small>Date: ${result.ordered_date}</small>
                        <br>
                        <small>Status: ${result.test_status}</small>
                    `;
                    resultsList.appendChild(resultDiv);
                });
            } else {
                resultsList.innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">No lab results available</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching results:', error);
            document.getElementById('resultsList').innerHTML = '<p style="text-align: center; color: #999; padding: 20px;">Error loading results</p>';
        });
}

function closeDownloadModal() {
    console.log('closeDownloadModal called');
    const modal = document.getElementById('downloadModal');
    if (modal) {
        modal.style.display = 'none';
    }
    selectedResultId = null;
    
    const downloadBtn = document.getElementById('downloadPdfBtn');
    if (downloadBtn) {
        downloadBtn.disabled = true;
    }
    
    // Clear selection
    const items = document.querySelectorAll('.result-item');
    items.forEach(item => item.classList.remove('selected'));
}


function selectResult(testId, element) {
    selectedResultId = testId;
    
    // Clear previous selection
    const items = document.querySelectorAll('.result-item');
    items.forEach(item => item.classList.remove('selected'));
    
    // Set new selection
    element.classList.add('selected');
    document.getElementById('downloadPdfBtn').disabled = false;
}

function downloadSelectedResult() {
    if (!selectedResultId) {
        alert('Please select a lab result to download.');
        return;
    }
    
    // Redirect to download endpoint
    window.location.href = `/download-lab-report/${selectedResultId}`;
    
    // Close modal after a short delay
    setTimeout(() => {
        closeDownloadModal();
    }, 500);
}

// Details Modal Functions
let currentDetailsTestId = null;

function openDetailsModal(button) {
    const modal = document.getElementById('detailsModal');
    currentDetailsTestId = button.getAttribute('data-test-id');
    
    // Populate the modal with data from button attributes
    document.getElementById('detailsTestNameValue').textContent = button.getAttribute('data-test-name');
    document.getElementById('detailsTestIdValue').textContent = button.getAttribute('data-test-id');
    document.getElementById('detailsStatusValue').textContent = button.getAttribute('data-test-status');
    document.getElementById('detailsOrderedDateValue').textContent = button.getAttribute('data-ordered-date');
    document.getElementById('detailsResultTimeValue').textContent = button.getAttribute('data-result-time');
    document.getElementById('detailsResultValueValue').textContent = button.getAttribute('data-result-value');
    document.getElementById('detailsUnitValue').textContent = button.getAttribute('data-unit-measure');
    document.getElementById('detailsReferenceRangeValue').textContent = button.getAttribute('data-reference-range');
    
    // Show or hide notes section
    const notes = button.getAttribute('data-result-notes');
    const notesSection = document.getElementById('detailsNotesSection');
    if (notes && notes.trim() !== '') {
        document.getElementById('detailsNotesValue').textContent = notes;
        notesSection.style.display = 'block';
    } else {
        notesSection.style.display = 'none';
    }
    
    // Update header title
    document.getElementById('detailsTestName').textContent = button.getAttribute('data-test-name') + ' Details';
    
    // Show modal
    modal.style.display = 'block';
}

function closeDetailsModal() {
    document.getElementById('detailsModal').style.display = 'none';
    currentDetailsTestId = null;
}

function downloadFromDetails() {
    if (!currentDetailsTestId) {
        alert('Error: No test selected.');
        return;
    }
    
    window.location.href = `/download-lab-report/${currentDetailsTestId}`;
    
    setTimeout(() => {
        closeDetailsModal();
    }, 500);
}

// Close details modal when clicking outside
window.addEventListener('click', function(event) {
    const detailsModal = document.getElementById('detailsModal');
    if (event.target === detailsModal) {
        closeDetailsModal();
    }
});

document.addEventListener("DOMContentLoaded", function() {
    // Ensure download modal is closed on page load
    const downloadModal = document.getElementById('downloadModal');
    if (downloadModal) {
        downloadModal.style.display = 'none';
    }
    
    const modal = document.getElementById("editModal");
    const closeModal = document.getElementById("closeModal");
    const editButtons = document.querySelectorAll(".edit-btn");
    const editForm = document.getElementById("editForm");

    editButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            document.getElementById("edit-id").value = btn.dataset.id;
            document.getElementById("edit-first").value = btn.dataset.first;
            document.getElementById("edit-last").value = btn.dataset.last;
            document.getElementById("edit-email").value = btn.dataset.email;
            document.getElementById("edit-phone").value = btn.dataset.phone;
            document.getElementById("edit-dob").value = btn.dataset.dob;
            document.getElementById("edit-address").value = btn.dataset.address;
            document.getElementById("edit-gender").value = btn.dataset.gender;
            
            editForm.action = `/admin/edit_patient/${btn.dataset.id}`;
            modal.style.display = "flex";
        });
    });

    closeModal.addEventListener("click", () => {
        modal.style.display = "none";
    });

    window.onclick = function(event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };
});

document.addEventListener("DOMContentLoaded", function() {
    const dropdownBtn = document.querySelector(".dropdown-btn");
    const dropdownContent = document.querySelector(".dropdown-content");

    if (dropdownBtn && dropdownContent) {
        dropdownBtn.addEventListener("click", function(e) {
            e.stopPropagation();
            dropdownContent.style.display =
                dropdownContent.style.display === "block" ? "none" : "block";
        });

        // Close when clicking outside
        document.addEventListener("click", function(e) {
            if (!dropdownContent.contains(e.target) && e.target !== dropdownBtn) {
                dropdownContent.style.display = "none";
            }
        });

        // Update button text based on selected checkboxes
        dropdownContent.addEventListener("change", function() {
            const checked = dropdownContent.querySelectorAll("input[type='checkbox']:checked");
            if (checked.length === 0) {
                dropdownBtn.textContent = "Select Doctor(s)";
            } else if (checked.length === 1) {
                dropdownBtn.textContent = checked[0].parentElement.textContent.trim();
            } else {
                dropdownBtn.textContent = `${checked.length} doctors selected`;
            }
        });
    }
<<<<<<< Updated upstream
});
=======
});

// set by HTML template on load
const socket = io();
let currentRoom = null;

function joinRoom(room) {
    console.log("Joining room:", room);
    socket.emit("join_room", { room: room});
    currentRoom = room;
}

// send a chat message
function sendMessage(){
    const input = document.getElementById("content") || document.getElementById("messageInput");
    const text = input.value.trim();
    if (!text) return;

    // determine if this page is doctor or patient
    const isDoctor = (senderType === "doctor");
    const isPatient = (senderType === "patient");

    let selectedDoctor = null;
    let selectedPatient = null;

    if (isDoctor){
        const p = document.getElementById("patient_id");
        selectedPatient = p.value;
        selectedDoctor  = doctorId;
    } 
    if (isPatient){
        const d = document.getElementById("doctor_id");
        selectedDoctor = d.value;
        selectedPatient = patientId;
    }

    // join room before sending
    const room = `room_${selectedDoctor}_${selectedPatient}`;
    joinRoom(room);

    // emit socket event
    socket.emit("send_message", {
        room: room,
        message: text,
        sender_type: senderType,
        doctor_id: selectedDoctor,
        patient_id : selectedPatient
    });

    input.value = "";
}

// display incoming message
socket.on("receive_message", (data) => {
    const wrapper = document.createElement("div");
    wrapper.classList.add("message");

    if(data.sender_type === senderType){
        wrapper.classList.add("sent");
    } else {
        wrapper.classList.add("received");
    }

    wrapper.innerHTML =`
    <div class = "bubble">
        <span class = "label">
            ${data.sender_type === senderType ? "Sent" : "Received"}
        </span>
        ${data.message}
    </div>
    `;

    // doctor view (multiple patients)
    if (senderType == "doctor"){
        const patientChat = document.getElementById(`chat-${data.patient_id}`);
        if (patientChat){
            patientChat.appendChild(wrapper);
            patientChat.scrollTop = patientChat.scrollHeight;
            return;
        }
    }

    // patient view (single doctor)
    const container = document.querySelector(".messages-container");
    container.appendChild(wrapper);
    container.scrollTop = container.scrollHeight;
});
>>>>>>> Stashed changes
