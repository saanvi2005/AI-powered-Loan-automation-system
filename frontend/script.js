const API_BASE = "";
let currentSessionId = "user_" + Math.random().toString(36).substr(2, 9);
let uploadedDocuments = {
    aadhaar: false,
    pan: false,
    salary_slip: false
};

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    addChatMessage("Hello! I'm your loan assistant. I'll help you apply for a loan. Let's start with your full name.", "bot");
    updateProgress(1);
});

// ------------------ PAGE NAVIGATION ------------------
function showChatInterface() {
    document.getElementById('landing-page').classList.remove('active');
    document.getElementById('chat-interface').classList.add('active');
}

function showLandingPage() {
    document.getElementById('chat-interface').classList.remove('active');
    document.getElementById('landing-page').classList.add('active');
}

// ------------------ SIDEBAR & UI CONTROLS ------------------
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    sidebar.classList.toggle('active');
}

function toggleInfoPanel() {
    const infoPanel = document.querySelector('.info-panel');
    infoPanel.classList.toggle('active');
}

function setActiveNav(element) {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    element.classList.add('active');
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    
    const themeIcon = document.querySelector('.icon-btn .fas');
    if (themeIcon) {
        themeIcon.className = newTheme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
    }
}

// ------------------ CHAT FUNCTIONS (ORIGINAL LOGIC) ------------------
async function sendMessage() {
    const userInput = document.getElementById("user-input");
    const msg = userInput.value.trim();
    
    if (!msg) return;

    addChatMessage(msg, "user");
    userInput.value = "";

    try {
        console.log("Sending message to backend...");
        
        const response = await fetch(`${API_BASE}/sales_agent/message`, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify({ 
                session_id: currentSessionId,
                user_message: msg 
            })
        });

        console.log("Response status:", response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log("Backend response:", data);
        
        // Display agent response
        if (data.agent_reply) {
            addChatMessage(data.agent_reply, "bot");
        } else {
            addChatMessage("I didn't get a response. Please try again.", "bot");
        }

        // Handle different statuses
        handleApplicationStatus(data);

    } catch (error) {
        console.error('Error:', error);
        addChatMessage("Sorry, there was an error processing your request. Please check if the backend server is running.", "bot");
    }
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

function handleApplicationStatus(data) {
    console.log("Application status:", data.status);
    
    const status = data.status;
    
    switch(status) {
        case 'eligible_for_documents':
            showUnderwritingResults(data.underwriter_result || data.underwriting_result, true);
            showDocumentPanel();
            updateProgress(3);
            break;
            
        case 'rejected':
            showUnderwritingResults(data.underwriter_result || data.underwriting_result, false);
            showRejectionPanel();
            updateProgress(4);
            break;
            
        case 'complete':
            if (data.underwriter_result && data.underwriter_result.eligible) {
                showUnderwritingResults(data.underwriter_result, true);
                showDocumentPanel();
                updateProgress(3);
            }
            break;
            
        case 'in_progress':
            updateProgress(1);
            break;
            
        default:
            // If no specific status, check if we have underwriting result
            if (data.underwriter_result) {
                if (data.underwriter_result.eligible) {
                    showUnderwritingResults(data.underwriter_result, true);
                    showDocumentPanel();
                    updateProgress(3);
                } else {
                    showUnderwritingResults(data.underwriter_result, false);
                    showRejectionPanel();
                    updateProgress(4);
                }
            }
            break;
    }
}

// ------------------ PROGRESS TRACKING ------------------
function updateProgress(step) {
    // Reset all steps
    document.querySelectorAll('.step').forEach((el, index) => {
        if (index + 1 <= step) {
            el.classList.add('active');
        } else {
            el.classList.remove('active');
        }
    });

    // Show appropriate panel
    hideAllPanels();
    
    if (step === 1) {
        showPanel('welcome-panel');
    } else if (step === 2) {
        showPanel('underwriting-panel');
    } else if (step === 3) {
        showPanel('document-panel');
    } else if (step === 4) {
        // Determine which final panel to show
        const underwritingResult = document.getElementById('underwriting-result').innerHTML;
        if (underwritingResult.includes('eligible')) {
            showPanel('approval-panel');
        } else {
            showPanel('rejection-panel');
        }
    }
}

function hideAllPanels() {
    document.querySelectorAll('.panel').forEach(panel => {
        panel.classList.remove('active');
    });
}

function showPanel(panelId) {
    hideAllPanels();
    document.getElementById(panelId).classList.add('active');
}

// ------------------ UNDERWRITING RESULTS ------------------
function showUnderwritingResults(result, isEligible) {
    const resultDiv = document.getElementById('underwriting-result');
    const nextStepsDiv = document.getElementById('next-steps');
    
    if (!result) {
        result = {
            reason: "No underwriting result available",
            risk_score: "Unknown",
            next_step: "Pending"
        };
    }
    
    let html = `
        <div class="result-card ${isEligible ? 'eligible' : 'rejected'}">
            <h3>${isEligible ? '✅ Eligible for Loan' : '❌ Not Eligible'}</h3>
            <p><strong>Reason:</strong> ${result.reason || 'No reason provided'}</p>
            <p><strong>Risk Score:</strong> ${result.risk_score || 'Not assessed'}</p>
            <p><strong>Decision:</strong> ${result.next_step || 'Pending'}</p>
        </div>
    `;
    
    resultDiv.innerHTML = html;
    
    if (isEligible) {
        nextStepsDiv.innerHTML = `
            <div class="info-card">
                <h4>Next Steps:</h4>
                <p>Please proceed to document verification to complete your application.</p>
            </div>
        `;
    }
    
    showPanel('underwriting-panel');
    updateProgress(2);
}

function showRejectionPanel() {
    const rejectionDiv = document.getElementById('rejection-result');
    rejectionDiv.innerHTML = `
        <div class="result-card rejected">
            <h3>Application Not Approved</h3>
            <p>We're sorry, but based on the information provided, your loan application doesn't meet our current eligibility criteria.</p>
            <p>You may reapply after 6 months or contact our customer service for more information.</p>
        </div>
    `;
    showPanel('rejection-panel');
}

// ------------------ DOCUMENT VERIFICATION ------------------
function showDocumentPanel() {
    showPanel('document-panel');
    updateProgress(3);
}

async function uploadDocument(docType) {
    const fileInput = document.getElementById(`${docType}-file`);
    const statusSpan = document.getElementById(`${docType}-status`);
    
    if (!fileInput.files.length) {
        alert(`Please select a ${docType} file first!`);
        return;
    }

    statusSpan.textContent = "⏳ Uploading...";
    statusSpan.className = "status pending";

    try {
        const formData = new FormData();
        formData.append("doc_type", docType);
        formData.append("file", fileInput.files[0]);

        console.log("Uploading document:", docType);
        
        const response = await fetch(`${API_BASE}/documents/verify`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log("Document verification result:", result);
        
        if (result.result && (result.result[`${docType}_valid`] || result.result.verified)) {
            statusSpan.textContent = "✅ Verified";
            statusSpan.className = "status verified";
            uploadedDocuments[docType] = true;
            addChatMessage(`✅ ${docType.toUpperCase()} document uploaded and verified successfully!`, "bot");
        } else {
            statusSpan.textContent = "❌ Verification Failed";
            statusSpan.className = "status failed";
            addChatMessage(`❌ ${docType.toUpperCase()} document verification failed. Please upload a clear, valid document.`, "bot");
        }

        // Update document results display
        updateDocumentResults(result);
        checkAllDocumentsUploaded();

    } catch (error) {
        console.error('Upload error:', error);
        statusSpan.textContent = "❌ Upload Failed";
        statusSpan.className = "status failed";
        addChatMessage("❌ Document upload failed. Please try again.", "bot");
    }
}

function updateDocumentResults(result) {
    const resultsDiv = document.getElementById('document-results');
    resultsDiv.innerHTML = `
        <div class="info-card">
            <h4>Document Verification Result:</h4>
            <pre>${JSON.stringify(result, null, 2)}</pre>
        </div>
    `;
}

function checkAllDocumentsUploaded() {
    const allUploaded = Object.values(uploadedDocuments).every(status => status === true);
    const submitButton = document.getElementById('submit-all-docs');
    
    if (allUploaded) {
        submitButton.disabled = false;
        submitButton.textContent = "✅ Submit All Documents for Final Approval";
    } else {
        submitButton.disabled = true;
        const uploadedCount = Object.values(uploadedDocuments).filter(Boolean).length;
        const totalCount = Object.keys(uploadedDocuments).length;
        submitButton.textContent = `Upload All Documents (${uploadedCount}/${totalCount})`;
    }
}

async function submitAllDocuments() {
    addChatMessage("🎉 All documents submitted successfully! Your application is now under final review.", "bot");
    
    // Simulate final approval process
    setTimeout(() => {
        showFinalApproval();
    }, 2000);
}

function showFinalApproval() {
    const finalDiv = document.getElementById('final-result');
    finalDiv.innerHTML = `
        <div class="result-card eligible">
            <h3>✅ Application Complete!</h3>
            <p>Your loan application has been successfully processed and all documents are verified.</p>
            <p><strong>Next Steps:</strong></p>
            <ul>
                <li>Final approval within 24-48 hours</li>
                <li>You will receive an email confirmation</li>
                <li>Loan disbursement within 3-5 business days after approval</li>
            </ul>
            <p>Thank you for choosing our services!</p>
        </div>
    `;
    showPanel('approval-panel');
    updateProgress(4);
}

// ------------------ UTILITY FUNCTIONS ------------------
function addChatMessage(text, sender) {
    const chatBox = document.getElementById("chat-messages");
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", sender);
    
    const timeString = new Date().toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
    
    messageDiv.innerHTML = `
        <div class="message-bubble">
            ${text}
        </div>
        <div class="message-time">${timeString}</div>
    `;
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Debug function to check backend connection
async function checkBackendConnection() {
    try {
        const response = await fetch(`${API_BASE}/`);
        if (response.ok) {
            console.log("✅ Backend is running!");
            return true;
        }
    } catch (error) {
        console.error("❌ Backend connection failed:", error);
    }
    return false;
}

// Check backend connection on load
document.addEventListener('DOMContentLoaded', function() {
    checkBackendConnection();
});

// Reset application (for testing)
function resetApplication() {
    currentSessionId = "user_" + Math.random().toString(36).substr(2, 9);
    uploadedDocuments = {
        aadhaar: false,
        pan: false,
        salary_slip: false
    };
    
    document.getElementById('chat-messages').innerHTML = '';
    document.querySelectorAll('.status').forEach(span => {
        span.textContent = '';
        span.className = 'status';
    });
    
    document.querySelectorAll('input[type="file"]').forEach(input => {
        input.value = '';
    });
    
    document.getElementById('submit-all-docs').disabled = true;
    
    addChatMessage("Hello! I'm your loan assistant. Let's start a new application. What's your full name?", "bot");
    updateProgress(1);
}
