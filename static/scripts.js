let selectedPrescriptionId = null;
let selectedMedicationName = null;
let selectedDosage = null;
let selectedAppointmentId = null;
let selectedAppointmentDetails = null;

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
    options.forEach(option => option.classList.remove('selected'));

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

    // Show loading state
    const submitBtn = document.getElementById('submitRefillBtn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting....'

    // Send request to server
    fetch('/request_refill', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `prescription_id=${selectedPrescriptionId}&notes=`
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if(data.success){
            alert(`Refill request submitted for ${selectedMedicationName} - ${selectedDosage}`);
            
            // Close modal and reload page to show the new refill request
            closeRefillModal();
            setTimeout(() => {
                window.location.reload();
            }, 500);
        } else {
            alert('Error: ' + (data.message || 'Unknown error occurred'));
            submitBtn.disabled = false;
            submitBtn.textContent = 'Request Refill';
        }
    })
    .catch(error => {
        console.error('Error submitting refill:', error);
        alert('An error occurred while submitting the refill request: ' + error.message);
        submitBtn.disabled = false;
        submitBtn.textContent = 'Request Refill';
    });
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

function openEditContactModal() {
    document.getElementById('editContactModal').setAttribute('aria-hidden', 'false');
}

function closeEditContactModal() {
    document.getElementById('editContactModal').setAttribute('aria-hidden', 'true');
}

function updateContactInfo() {
    openEditContactModal();
}
// Schedule Appointment Modal Functions
function openScheduleModal() {
    const modal = document.getElementById('schedule-appointment-modal');
    if (modal) {
        modal.setAttribute('aria-hidden', 'false');
        // Reset form
        document.getElementById('doctor-select').value = '';
        document.getElementById('date-select').value = '';
        document.getElementById('date-select').disabled = true;
        document.getElementById('time-select').innerHTML = '<option value="" disabled selected>-- Select a date first --</option>';
        document.getElementById('time-select').disabled = true;
        document.getElementById('submit-appointment-btn').disabled = true;
    }
}

function closeScheduleModal() {
    const modal = document.getElementById('schedule-appointment-modal');
    if (modal) {
        modal.setAttribute('aria-hidden', 'true');
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
    // Schedule Modal Functionality
    const scheduleModal = document.getElementById('schedule-appointment-modal');
    const openScheduleBtn = document.getElementById('open-schedule-modal-btn');
    const closeScheduleBtn = document.getElementById('close-schedule-modal');
    const cancelScheduleBtn = document.getElementById('cancel-schedule-btn');

    const doctorSelect = document.getElementById('doctor-select');
    const dateSelect = document.getElementById('date-select');
    const timeSelect = document.getElementById('time-select');
    const submitAppointmentBtn = document.getElementById('submit-appointment-btn');

    if (openScheduleBtn) {
        openScheduleBtn.addEventListener('click', openScheduleModal);
    }
    if (closeScheduleBtn) {
        closeScheduleBtn.addEventListener('click', closeScheduleModal);
    }
    if (cancelScheduleBtn) {
        cancelScheduleBtn.addEventListener('click', closeScheduleModal);
    }

    // Close schedule modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === scheduleModal) {
            closeScheduleModal();
        }
    });

    // Set min date to today
    if (dateSelect) {
        const today = new Date().toISOString().split('T')[0];
        dateSelect.setAttribute('min', today);
    }

    function fetchAvailableSlots() {
        const doctorId = doctorSelect.value;
        const selectedDate = dateSelect.value;

        if (!doctorId || !selectedDate) {
            return;
        }

        timeSelect.innerHTML = '<option>Loading...</option>';
        timeSelect.disabled = true;
        submitAppointmentBtn.disabled = true;

        fetch(`/patient/api/available-slots?doctor_id=${doctorId}&date=${selectedDate}`)
            .then(response => response.json())
            .then(data => {
                timeSelect.innerHTML = '';
                if (data.slots && data.slots.length > 0) {
                    timeSelect.disabled = false;
                    timeSelect.innerHTML = '<option value="" disabled selected>-- Select a time --</option>';
                    data.slots.forEach(slot => {
                        const option = document.createElement('option');
                        option.value = slot;
                        const displayTime = new Date(`1970-01-01T${slot}:00`).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                        option.textContent = displayTime;
                        timeSelect.appendChild(option);
                    });
                } else {
                    timeSelect.innerHTML = '<option>No available slots on this day</option>';
                    timeSelect.disabled = true;
                }
            })
            .catch(error => {
                console.error('Error fetching slots:', error);
                timeSelect.innerHTML = '<option>Error loading times</option>';
                timeSelect.disabled = true;
            });
    }

    if (doctorSelect) {
        doctorSelect.addEventListener('change', function() {
            if (this.value) {
                dateSelect.disabled = false;
            } else {
                dateSelect.disabled = true;
                timeSelect.disabled = true;
            }
            dateSelect.value = '';
            timeSelect.innerHTML = '<option value="" disabled selected>-- Select a date first --</option>';
            submitAppointmentBtn.disabled = true;
        });
    }

    if (dateSelect) {
        dateSelect.addEventListener('change', fetchAvailableSlots);
    }

    if (timeSelect) {
        timeSelect.addEventListener('change', function() {
            submitAppointmentBtn.disabled = !this.value;
        });
    }

    // Quick Actions Integration
    document.querySelectorAll('.action-card').forEach(card => {
        card.addEventListener('click', function(e) {
            const action = this.querySelector('div:last-child').textContent.trim();
            if (action === 'Schedule Appointment') {
                openScheduleModal();
            } else if (action === 'Reschedule') {
                // open the reschedule picker modal
                openReschedulePickerModal();
            } else if (action === 'Cancel Appointment') {
                openCancelModal();
            }
        });
    });
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

    const timestamp = new Date().toISOString(); 

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

    if (currentRoom !== room) {
        joinRoom(room);
    }


    // emit socket event
    socket.emit("send_message", {
        room: room,
        message: text,
        sender_type: senderType,
        doctor_id: selectedDoctor,
        patient_id : selectedPatient,
        timestamp: timestamp
    });

    input.value = "";
    console.log("PATIENT SENDING → doctor:", selectedDoctor, "patient:", selectedPatient);

}

function doctorNameFromDropdown(id) {
    const opt = document.querySelector(`#doctor_id option[value="${id}"]`);
    return opt ? opt.textContent.trim() : "Unknown Doctor";
}


// display incoming message
socket.on("receive_message", (data) => {

    console.log("Received message:", data);
    const formattedTime = new Date(data.timestamp).toLocaleString();
    const userIsDoctor = (senderType === "doctor");
    const userIsPatient = (senderType === "patient");

    const { message, sender_type, patient_id, doctor_id } = data;

    // patientside
    if (userIsPatient) {

        const doctorGroup = document.getElementById(`group-${doctor_id}`);
        const doctorWrapper = document.getElementById(`chat-${doctor_id}`);

        //create group if it doesnt exist
        if (!doctorWrapper) {

            const newGroup = document.createElement("div");
            newGroup.className = "doctor-message-group";
            newGroup.id = `chat-${doctor_id}`;

            newGroup.innerHTML = `
                <h3 class="doctor-name" onclick="toggleDoctorMessages('${doctor_id}')">
                    <span class="arrow" id="arrow-${doctor_id}">▼</span>
                    ${doctorNameFromDropdown(doctor_id)}
                </h3>

                <div class="message-list" id="group-${doctor_id}" style="display:block;"></div>
            `;
            const chatBox = document.getElementById("chat-box");

            chatBox.prepend(newGroup);
        }

        // add that msg to group
        const msgGroup = document.getElementById(`group-${doctor_id}`);

        const msgDiv = document.createElement("div");
        msgDiv.className = `message ${sender_type === "doctor" ? "received" : "sent"}`;
        
        msgDiv.innerHTML = `
            <div class="bubble">
                <span class="label">${sender_type === "doctor" ? "Doctor" : "You"}</span>
                ${message}
                <div class="timestamp">${formattedTime}</div>
            </div>
        `;

    msgGroup.appendChild(msgDiv);
    // scroll to bottom
    msgGroup.scrollTop = msgGroup.scrollHeight;


    msgGroup.querySelectorAll(".message").forEach(m => {
        m.style.display = "flex";
    });

    // auto-open group if it's collapsed
    const wrapper = document.getElementById(`chat-${doctor_id}`);
    const arrow = document.getElementById(`arrow-${doctor_id}`);

    if (msgGroup.style.display === "none") {
        msgGroup.style.display = "block";
        if (arrow) arrow.textContent = "▼";

        setTimeout(() => {
            msgGroup.scrollTop = msgGroup.scrollHeight;
        }, 50);
    }

    }

        // doctor side 
    if (userIsDoctor) {
        const pid = patient_id;
        let groupWrapper = document.getElementById(`chat-${pid}`);

        if (!groupWrapper) {
            const patientName = document.querySelector(`#patient_id option[value="${pid}"]`).textContent;

            groupWrapper = document.createElement("div");
            groupWrapper.className = "patient-message-group";
            groupWrapper.id = `chat-${pid}`;

            groupWrapper.innerHTML = `
                <h3 class="patient-name" onclick="toggleMessages('${pid}')">
                    <span class="arrow" id="arrow-${pid}">►</span>
                    ${patientName}
                </h3>
                <div class="message-list" id="group-${pid}" style="display:none;"></div>
            `;

            document.querySelector(".messages-container").prepend(groupWrapper);
        }

        const messageList = document.getElementById(`group-${pid}`);
        const msgDiv = document.createElement("div");

        msgDiv.className = `message ${sender_type === "doctor" ? "sent" : "received"}`;
        msgDiv.innerHTML = `
            <div class="bubble">
                <span class="label">${sender_type === "doctor" ? "Sent" : "Received"}</span>
                ${message}
                <div class="timestamp">${formattedTime}</div>
            </div>
        `;
        messageList.appendChild(msgDiv);
    messageList.scrollTop = messageList.scrollHeight;

        if (messageList.style.display === "none") {
            messageList.style.display = "block";
            document.getElementById(`arrow-${pid}`).textContent = "▼";
        }

        setTimeout(() => {
            messageList.scrollTop = messageList.scrollHeight;
        }, 50);
    }
});


// Cancel / Reschedule modal handlers 
function openCancelModal() {
    const modal = document.getElementById('cancel-appointment-modal');
    if (modal) modal.setAttribute('aria-hidden', 'false');
}

function closeCancelModal() {
    const modal = document.getElementById('cancel-appointment-modal');
    if (modal) modal.setAttribute('aria-hidden', 'true');
}

function openReschedulePickerModal() {
    const modal = document.getElementById('reschedule-picker-modal');
    if (modal) modal.setAttribute('aria-hidden', 'false');
}

function closeReschedulePickerModal() {
    const modal = document.getElementById('reschedule-picker-modal');
    if (modal) modal.setAttribute('aria-hidden', 'true');
}

document.addEventListener('DOMContentLoaded', function() {
    // Contact info form handler
    const editContactForm = document.getElementById('editContactForm');
    if (editContactForm) {
        editContactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const phone = document.getElementById('edit-phone').value.trim();
            const email = document.getElementById('edit-email').value.trim();
            const address = document.getElementById('edit-address').value.trim();

            if (!address) {
                alert('Address is required.');
                return;
            }

            const submitBtn = document.getElementById('submitEditBtn');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Saving...';

            fetch('/patient/update-contact-info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `phone_number=${encodeURIComponent(phone)}&email=${encodeURIComponent(email)}&address=${encodeURIComponent(address)}`
            })
            .then(response => {
                if (!response.ok) throw new Error('HTTP error ' + response.status);
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    alert('Contact information updated successfully!');
                    closeEditContactModal();
                    window.location.reload();
                } else {
                    alert('Error: ' + (data.message || 'Unknown error'));
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Save Changes';
                }
            })
            .catch(err => {
                console.error('Error updating contact info:', err);
                alert('An error occurred while updating contact information.');
                submitBtn.disabled = false;
                submitBtn.textContent = 'Save Changes';
            });
        });
    }

    // Cancel modal buttons
    const closeCancel = document.getElementById('close-cancel-modal');
    const cancelCloseBtn = document.getElementById('cancel-cancel-btn');
    const confirmCancelBtn = document.getElementById('confirm-cancel-btn');

    if (closeCancel) closeCancel.addEventListener('click', closeCancelModal);
    if (cancelCloseBtn) cancelCloseBtn.addEventListener('click', closeCancelModal);

    if (confirmCancelBtn) {
        confirmCancelBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (!selectedAppointmentId) {
                alert('Please select an appointment to cancel.');
                return;
            }

            confirmCancelBtn.disabled = true;
            confirmCancelBtn.textContent = 'Cancelling...';

            fetch(`/patient/cancel-appointment/${selectedAppointmentId}`, {
                method: 'POST'
            })
            .then(() => window.location.reload())
            .catch(err => {
                console.error('Error cancelling appointment', err);
                alert('Error cancelling appointment');
                confirmCancelBtn.disabled = false;
                confirmCancelBtn.textContent = 'Cancel Appointment';
            });
        });
    }

    // Reschedule modal buttons
    const closeReschedule = document.getElementById('close-reschedule-modal');
    const closeReschedulePickerBtn = document.getElementById('close-reschedule-picker-btn');
    const startRescheduleBtn = document.getElementById('start-reschedule-btn');

    if (closeReschedule) closeReschedule.addEventListener('click', closeReschedulePickerModal);
    if (closeReschedulePickerBtn) closeReschedulePickerBtn.addEventListener('click', closeReschedulePickerModal);

    if (startRescheduleBtn) {
        startRescheduleBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (!selectedAppointmentId) {
                alert('Please select an appointment to reschedule.');
                return;
            }

            // find the selected option element
            const opt = document.querySelector(`#reschedule-appointment-options .prescription-option.selected`);
            if (!opt) {
                alert('Please select an appointment to reschedule.');
                return;
            }

            const apptId = opt.getAttribute('data-appointment-id');
            const doctorId = opt.getAttribute('data-doctor-id');
            const apptDate = opt.getAttribute('data-date');
            const apptTime = opt.getAttribute('data-time');

            const doctorSelect = document.getElementById('doctor-select');
            const dateSelect = document.getElementById('date-select');
            const timeSelect = document.getElementById('time-select');
            const oldIdInput = document.getElementById('old_appointment_id');

            if (doctorSelect) {
                doctorSelect.value = doctorId;
                dateSelect.disabled = false;
            }

            if (dateSelect) {
                dateSelect.value = apptDate;
            }

            if (typeof fetchAvailableSlots === 'function') {
                fetchAvailableSlots();
                setTimeout(() => {
                    if (timeSelect) {
                        try { timeSelect.value = apptTime; } catch (e) {}
                    }
                }, 600);
            }

            if (oldIdInput) {
                oldIdInput.value = apptId;
            }

            closeReschedulePickerModal();
            openScheduleModal();
        });
    }
});

function cancelSelectedAppointment() {
    const confirmBtn = document.getElementById('confirm-cancel-btn');
    if (!selectedAppointmentId) {
        alert('Please select an appointment to cancel.');
        return;
    }

    if (confirmBtn) {
        confirmBtn.disabled = true;
        confirmBtn.textContent = 'Cancelling...';
    }

    fetch(`/patient/cancel-appointment/${selectedAppointmentId}`, { method: 'POST' })
        .then(() => window.location.reload())
        .catch(err => {
            console.error('Error cancelling appointment', err);
            alert('Error cancelling appointment');
            if (confirmBtn) {
                confirmBtn.disabled = false;
                confirmBtn.textContent = 'Cancel Appointment';
            }
        });
}

function startRescheduleFromModal() {
    if (!selectedAppointmentId) {
        alert('Please select an appointment to reschedule.');
        return;
    }

    const opt = document.querySelector(`#reschedule-appointment-options .prescription-option.selected`);
    if (!opt) {
        alert('Please select an appointment to reschedule.');
        return;
    }

    const apptId = opt.getAttribute('data-appointment-id');
    const doctorId = opt.getAttribute('data-doctor-id');
    const apptDate = opt.getAttribute('data-date');
    const apptTime = opt.getAttribute('data-time');

    const doctorSelect = document.getElementById('doctor-select');
    const dateSelect = document.getElementById('date-select');
    const timeSelect = document.getElementById('time-select');
    const oldIdInput = document.getElementById('old_appointment_id');

    if (doctorSelect) {
        doctorSelect.value = doctorId;
        dateSelect.disabled = false;
    }

    if (dateSelect) {
        dateSelect.value = apptDate;
    }

    if (typeof fetchAvailableSlots === 'function') {
        fetchAvailableSlots();
        setTimeout(() => {
            if (timeSelect) {
                try { timeSelect.value = apptTime; } catch (e) {}
            }
        }, 600);
    }

    if (oldIdInput) oldIdInput.value = apptId;
    closeReschedulePickerModal();
    openScheduleModal();
}

// selection handlers for option cards
function selectCancelAppointment(element) {
    const options = document.querySelectorAll('#cancel-appointment-options .prescription-option');
    options.forEach(opt => opt.classList.remove('selected'));
    element.classList.add('selected');
    selectedAppointmentId = element.getAttribute('data-appointment-id');
    selectedAppointmentDetails = element.textContent.trim();
    const info = document.getElementById('selected-cancel-appt');
    if (info) info.textContent = selectedAppointmentDetails;
    const infoBox = document.getElementById('selected-cancel-info');
    if (infoBox) infoBox.setAttribute('aria-hidden', 'false');
    const confirmBtn = document.getElementById('confirm-cancel-btn');
    if (confirmBtn) confirmBtn.disabled = false;
}

function selectRescheduleAppointment(element) {
    const options = document.querySelectorAll('#reschedule-appointment-options .prescription-option');
    options.forEach(opt => opt.classList.remove('selected'));
    element.classList.add('selected');
    selectedAppointmentId = element.getAttribute('data-appointment-id');
    selectedAppointmentDetails = element.textContent.trim();
    const info = document.getElementById('selected-reschedule-appt');
    if (info) info.textContent = selectedAppointmentDetails;
    const infoBox = document.getElementById('selected-reschedule-info');
    if (infoBox) infoBox.setAttribute('aria-hidden', 'false');
    const startBtn = document.getElementById('start-reschedule-btn');
    if (startBtn) startBtn.disabled = false;
}