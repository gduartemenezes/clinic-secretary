// Global variables
let currentAppointments = [];
let currentStats = {};

// Initialize the interface when the page loads
document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
    loadTodayAppointments();
    setupEventListeners();
});

// Setup event listeners for forms and interactions
function setupEventListeners() {
    // Main message form
    document.getElementById('message-form').addEventListener('submit', handleSendMessage);
    
    // Modal forms
    document.getElementById('modal-message-form').addEventListener('submit', handleModalSendMessage);
    document.getElementById('reschedule-form').addEventListener('submit', handleReschedule);
    document.getElementById('reminder-form').addEventListener('submit', handleSendReminder);
}

// Load dashboard statistics
async function loadDashboard() {
    try {
        const response = await fetch('/appointments/statistics');
        if (response.ok) {
            currentStats = await response.json();
            updateDashboardDisplay();
        } else {
            console.error('Failed to load dashboard stats');
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showNotification('Failed to load dashboard statistics', 'error');
    }
}

// Update dashboard display with current statistics
function updateDashboardDisplay() {
    document.getElementById('today-appointments').textContent = currentStats.today_appointments || 0;
    document.getElementById('upcoming-appointments').textContent = currentStats.upcoming_appointments || 0;
    document.getElementById('total-appointments').textContent = currentStats.total_appointments || 0;
    document.getElementById('pending-messages').textContent = '0'; // Placeholder for now
}

// Load today's appointments
async function loadTodayAppointments() {
    try {
        const today = new Date().toISOString().split('T')[0];
        const response = await fetch(`/appointments/date/${today}`);
        
        if (response.ok) {
            const data = await response.json();
            currentAppointments = data.appointments || [];
            displayAppointments();
        } else {
            console.error('Failed to load today\'s appointments');
            showEmptyAppointmentsState();
        }
    } catch (error) {
        console.error('Error loading appointments:', error);
        showEmptyAppointmentsState();
    }
}

// Display appointments in the interface
function displayAppointments() {
    const appointmentsList = document.getElementById('appointments-list');
    
    if (currentAppointments.length === 0) {
        showEmptyAppointmentsState();
        return;
    }
    
    appointmentsList.innerHTML = currentAppointments.map(appointment => `
        <div class="appointment-item">
            <div class="appointment-info">
                <h4>Appointment #${appointment.id}</h4>
                <p>Patient ID: ${appointment.patient_id} | Doctor ID: ${appointment.doctor_id}</p>
                <p class="appointment-time">${formatDateTime(appointment.datetime)}</p>
                <p>Type: ${appointment.type} | Status: ${appointment.status}</p>
            </div>
            <div class="appointment-actions">
                <button class="btn-remind" onclick="sendReminder(${appointment.id})">
                    <i class="fas fa-bell"></i> Remind
                </button>
                <button class="btn-reschedule" onclick="showRescheduleModal(${appointment.id})">
                    <i class="fas fa-calendar-plus"></i> Reschedule
                </button>
            </div>
        </div>
    `).join('');
}

// Show empty state when no appointments
function showEmptyAppointmentsState() {
    const appointmentsList = document.getElementById('appointments-list');
    appointmentsList.innerHTML = `
        <div class="empty-state">
            <i class="fas fa-calendar-times"></i>
            <h3>No Appointments Today</h3>
            <p>There are no appointments scheduled for today.</p>
        </div>
    `;
}

// Format datetime for display
function formatDateTime(dateTimeString) {
    const date = new Date(dateTimeString);
    return date.toLocaleString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Handle send message from main form
async function handleSendMessage(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const phone = formData.get('patient-phone');
    const message = formData.get('message-content');
    
    await sendMessageToPatient(phone, message);
    
    // Clear form
    event.target.reset();
}

// Handle send message from modal
async function handleModalSendMessage(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const phone = formData.get('patient-phone');
    const message = formData.get('message-content');
    
    await sendMessageToPatient(phone, message);
    
    // Close modal and clear form
    closeModal('send-message-modal');
    event.target.reset();
}

// Send message to patient via WhatsApp
async function sendMessageToPatient(phone, message) {
    try {
        const response = await fetch('/test_whatsapp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                phone: phone,
                message: message
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            if (result.result.success) {
                showNotification('Message sent successfully!', 'success');
            } else {
                showNotification('Failed to send message: ' + (result.result.error || 'Unknown error'), 'error');
            }
        } else {
            showNotification('Failed to send message', 'error');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        showNotification('Error sending message', 'error');
    }
}

// Handle reschedule appointment
async function handleReschedule(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const appointmentId = formData.get('appointment-id');
    const newDate = formData.get('new-date');
    const newTime = formData.get('new-time');
    
    try {
        const newDateTime = new Date(`${newDate}T${newTime}`);
        
        const response = await fetch(`/appointments/${appointmentId}/datetime`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                new_datetime: newDateTime.toISOString()
            })
        });
        
        if (response.ok) {
            showNotification('Appointment rescheduled successfully!', 'success');
            closeModal('reschedule-modal');
            event.target.reset();
            loadTodayAppointments(); // Refresh the list
        } else {
            const error = await response.json();
            showNotification('Failed to reschedule: ' + (error.detail || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error rescheduling appointment:', error);
        showNotification('Error rescheduling appointment', 'error');
    }
}

// Handle send reminder
async function handleSendReminder(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    const appointmentId = formData.get('appointment-id');
    const phone = formData.get('patient-phone');
    
    try {
        // For now, we'll use the test endpoint
        // In production, this would call a dedicated reminder endpoint
        const response = await fetch('/test_whatsapp', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                phone: phone,
                message: `Reminder: You have an upcoming appointment. Please confirm your attendance.`
            })
        });
        
        if (response.ok) {
            showNotification('Reminder sent successfully!', 'success');
            closeModal('reminder-modal');
            event.target.reset();
        } else {
            showNotification('Failed to send reminder', 'error');
        }
    } catch (error) {
        console.error('Error sending reminder:', error);
        showNotification('Error sending reminder', 'error');
    }
}

// Send reminder for a specific appointment
async function sendReminder(appointmentId) {
    // This would typically open a modal to get patient phone number
    // For now, we'll show a notification
    showNotification('Reminder functionality requires patient phone number', 'warning');
}

// Test the AI chatbot
async function testChatbot() {
    const testMessage = "Hello, I'm a doctor testing the system. Can you help me schedule an appointment?";
    
    try {
        const response = await fetch('/test_agent', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: testMessage
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            showNotification(`AI Response: ${result.response.substring(0, 100)}...`, 'success');
        } else {
            showNotification('Failed to test chatbot', 'error');
        }
    } catch (error) {
        console.error('Error testing chatbot:', error);
        showNotification('Error testing chatbot', 'error');
    }
}

// Modal functions
function showSendMessageModal() {
    document.getElementById('send-message-modal').style.display = 'block';
}

function showRescheduleModal(appointmentId = null) {
    if (appointmentId) {
        document.getElementById('appointment-id').value = appointmentId;
    }
    document.getElementById('reschedule-modal').style.display = 'block';
}

function showReminderModal() {
    document.getElementById('reminder-modal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}

// Notification system
function showNotification(message, type = 'success') {
    const toast = document.getElementById('notification-toast');
    const messageElement = document.getElementById('notification-message');
    
    // Set message and type
    messageElement.textContent = message;
    toast.className = `notification-toast ${type}`;
    
    // Show toast
    toast.style.display = 'flex';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideNotification();
    }, 5000);
}

function hideNotification() {
    document.getElementById('notification-toast').style.display = 'none';
}

// Utility functions
function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function formatTime(time) {
    return time.substring(0, 5);
}

// Refresh data periodically
setInterval(() => {
    loadDashboard();
    loadTodayAppointments();
}, 30000); // Refresh every 30 seconds

// Export functions for global access
window.showSendMessageModal = showSendMessageModal;
window.showRescheduleModal = showRescheduleModal;
window.showReminderModal = showReminderModal;
window.closeModal = closeModal;
window.hideNotification = hideNotification;
window.testChatbot = testChatbot;
window.sendReminder = sendReminder;
