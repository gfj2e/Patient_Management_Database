 let selectedPrescriptionId = null;
let selectedMedicationName = null;
let selectedDosage = null;

function openRefillModal(){
    document.getElementById('prescription-refill-popup').setAttribute('aria-hidden', 'false');
    resetSelection();
}

function closeRefillModal(){
    document.getElementById('prescription-refill-popup').setAttribute('aria-hidden', 'false');
    resetSelection();
}

function resetSelection(){
    selectedPrescriptionId = null;
    selectedDosage = null;
    selectedMedicationName = null;

    const options = document.querySelectorAll('.prescription-option');
    options.forEach(optoin => options.classList.remove('selected'));

    // Hide selected prescrip info
    document.getElementById('selected-prescription-inof').setAttribute('aria-hidden', 'true');

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

    // Here you would typically make an AJAX call to your backend
    // For now, we'll just show a confirmation and close the modal
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