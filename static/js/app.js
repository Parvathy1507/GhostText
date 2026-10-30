
// ========================================
// GHOSTTEXT - FRONTEND APPLICATION
// ========================================

const $ = (id) => document.getElementById(id);

// Authentication elements
const authSection = $("authSection");
const loginForm = $("loginForm");
const registerForm = $("registerForm");
const authStatus = $("authStatus");
const showLoginButton = $("showLoginButton");
const showRegisterButton = $("showRegisterButton");

const userSection = $("userSection");
const currentUsername = $("currentUsername");
const logoutButton = $("logoutButton");
const userStatus = $("userStatus");

// Dashboard elements
const analysisSection = $("analysisSection");
const uploadForm = $("uploadForm");
const fileInput = $("fileInput");
const analyzeButton = $("analyzeButton");
const statusMessage = $("status");

const resultsSection = $("results");
const exportButton = $("exportButton");
const summary = $("summary");
const findingsContainer = $("findings");

const historySection = $("historySection");
const historyList = $("historyList");
const clearHistoryButton = $("clearHistoryButton");

let lastAnalysisData = null;

exportButton.disabled = true;


// ========================================
// API HELPER
// ========================================

async function apiRequest(url, options = {}) {
    const response = await fetch(url, {
        credentials: "same-origin",
        ...options
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        // Do not treat incorrect login credentials as an expired session.
        if (
            response.status === 401 &&
            url !== "/api/auth/login" &&
            url !== "/api/auth/register"
        ) {
            showLoggedOut();

            throw new Error(
                "Your session has expired. Please log in again."
            );
        }

        throw new Error(
            typeof data.detail === "string"
                ? data.detail
                : "The request could not be completed."
        );
    }

    return data;
}


// ========================================
// SWITCH AUTHENTICATION FORMS
// ========================================

showLoginButton.addEventListener("click", function () {
    loginForm.hidden = false;
    registerForm.hidden = true;

    showLoginButton.classList.add("active");
    showRegisterButton.classList.remove("active");

    authStatus.textContent = "";
});

showRegisterButton.addEventListener("click", function () {
    loginForm.hidden = true;
    registerForm.hidden = false;

    showRegisterButton.classList.add("active");
    showLoginButton.classList.remove("active");

    authStatus.textContent = "";
});


// ========================================
// REGISTER ACCOUNT
// ========================================

registerForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    authStatus.textContent = "";

    const username = $("registerUsername").value.trim();
    const password = $("registerPassword").value;

    if (!/^[A-Za-z0-9_]{3,30}$/.test(username)) {
        authStatus.textContent =
            "Username must contain 3–30 letters, numbers, or underscores.";
        return;
    }

    if (password.length < 12) {
        authStatus.textContent =
            "Your password must contain at least 12 characters.";
        return;
    }

    if (password.length > 128) {
        authStatus.textContent =
            "Your password cannot exceed 128 characters.";
        return;
    }

    const button = registerForm.querySelector(
        'button[type="submit"]'
    );

    button.disabled = true;
    authStatus.textContent = "Creating your account...";

    try {
        const data = await apiRequest("/api/auth/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        registerForm.reset();
        registerForm.hidden = true;
        loginForm.hidden = false;

        $("loginUsername").value = username;
        $("loginPassword").value = "";

        authStatus.textContent =
            data.message || "Account created successfully. Please log in.";

    } catch (error) {
        authStatus.textContent = error.message;

    } finally {
        button.disabled = false;
    }
});


// ========================================
// LOGIN
// ========================================

loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    authStatus.textContent = "";

    const username = $("loginUsername").value.trim();
    const password = $("loginPassword").value;

    if (!username || !password) {
        authStatus.textContent =
            "Please enter both your username and password.";
        return;
    }

    const button = loginForm.querySelector(
        'button[type="submit"]'
    );

    button.disabled = true;
    authStatus.textContent = "Logging in...";

    try {
        const data = await apiRequest("/api/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        loginForm.reset();
        authStatus.textContent = "";

        await showLoggedIn(data.username || username);

    } catch (error) {
        if (
            error.message === "Invalid username or password." ||
            error.message === "Incorrect username or password."
        ) {
            authStatus.textContent =
                "Incorrect username or password. Please try again.";
        } else {
            authStatus.textContent = error.message;
        }

    } finally {
        button.disabled = false;
    }
});


// ========================================
// CHECK CURRENT SESSION
// ========================================

async function checkSession() {
    try {
        const data = await apiRequest("/api/auth/me");
        await showLoggedIn(data.username);

    } catch (error) {
        showLoggedOut();
    }
}


// ========================================
// SHOW LOGGED-IN DASHBOARD
// ========================================

async function showLoggedIn(username) {
    authSection.hidden = true;

    userSection.hidden = false;
    analysisSection.hidden = false;
    historySection.hidden = false;

    currentUsername.textContent = username;

    authStatus.textContent = "";
    userStatus.textContent = "";
    statusMessage.textContent = "";

    await loadHistory();
}


// ========================================
// SHOW LOGGED-OUT SCREEN
// ========================================

function showLoggedOut() {
    authSection.hidden = false;

    userSection.hidden = true;
    analysisSection.hidden = true;
    historySection.hidden = true;
    resultsSection.hidden = true;

    currentUsername.textContent = "";

    lastAnalysisData = null;
    exportButton.disabled = true;

    historyList.replaceChildren();
    summary.replaceChildren();
    findingsContainer.replaceChildren();

    statusMessage.textContent = "";
    userStatus.textContent = "";

    loginForm.hidden = false;
    registerForm.hidden = true;

    authStatus.textContent = "";
}


// ========================================
// LOGOUT
// ========================================

logoutButton.addEventListener("click", async function () {
    logoutButton.disabled = true;
    userStatus.textContent = "Logging out...";

    try {
        const data = await apiRequest("/api/auth/logout", {
            method: "POST"
        });

        showLoggedOut();

        authStatus.textContent =
            data.message || "You have logged out successfully.";

    } catch (error) {
        userStatus.textContent = error.message;

    } finally {
        logoutButton.disabled = false;
    }
});


// ========================================
// DOCUMENT ANALYSIS
// ========================================

uploadForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const file = fileInput.files[0];

    if (!file) {
        statusMessage.textContent = "Please select a document.";
        return;
    }

    const filename = file.name.toLowerCase();

    if (
        !filename.endsWith(".pdf") &&
        !filename.endsWith(".docx")
    ) {
        statusMessage.textContent =
            "Only PDF and DOCX files are supported.";
        return;
    }

    if (file.size > 5 * 1024 * 1024) {
        statusMessage.textContent =
            "File size must not exceed 5 MB.";
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    analyzeButton.disabled = true;
    statusMessage.textContent = "Analyzing document. Please wait...";

    resultsSection.hidden = true;
    summary.replaceChildren();
    findingsContainer.replaceChildren();

    try {
        const data = await apiRequest("/api/analyze", {
            method: "POST",
            body: formData
        });

        lastAnalysisData = data;
        displayResults(data);

        exportButton.disabled = false;

        statusMessage.textContent =
            "Analysis completed successfully.";

        await loadHistory();

    } catch (error) {
        statusMessage.textContent = "Error: " + error.message;

    } finally {
        analyzeButton.disabled = false;
    }
});


// ========================================
// DISPLAY ANALYSIS RESULTS
// ========================================

function displayResults(data) {
    const analysis = data.analysis;

    const risk = String(
        analysis.risk_level || "LOW"
    ).toUpperCase();

    resultsSection.hidden = false;

    $("riskStat").textContent = risk;
    $("riskStat").className = getRiskClass(risk);

    $("findingsStat").textContent =
        analysis.findings_count ?? 0;

    $("charactersStat").textContent =
        Number(data.characters_extracted).toLocaleString();

    const summaryItems = [
        ["Filename", data.filename],
        [
            "File size",
            `${Number(data.size_bytes).toLocaleString()} bytes`
        ],
        [
            "Status",
            String(analysis.status || "").replaceAll("_", " ")
        ],
        ["Report message", analysis.message || ""]
    ];

    for (const [label, value] of summaryItems) {
        const paragraph = document.createElement("p");
        const strong = document.createElement("strong");

        strong.textContent = `${label}: `;

        paragraph.append(
            strong,
            document.createTextNode(String(value))
        );

        summary.appendChild(paragraph);
    }

    const findings = Array.isArray(analysis.findings)
        ? analysis.findings
        : [];

    if (findings.length === 0) {
        const message = document.createElement("p");

        message.className = "empty-state";
        message.textContent =
            "No indicators were detected by the current checks. " +
            "This does not guarantee the document is safe.";

        findingsContainer.appendChild(message);
        return;
    }

    findings.forEach((finding, index) => {
        const card = document.createElement("article");

        const findingRisk = String(
            finding.risk || risk
        ).toUpperCase();

        card.className = `finding ${getRiskClass(findingRisk)}`;

        const title = document.createElement("h3");

        title.textContent =
            `Finding ${index + 1}: ` +
            String(finding.type || "unknown").replaceAll("_", " ");

        title.className = getRiskClass(findingRisk);
        card.appendChild(title);

        addDetail(card, "Risk", findingRisk);
        addDetail(card, "Position", finding.position);

        addDetail(
            card,
            "Matched text",
            finding.matched_text ||
            finding.character ||
            "Not available"
        );

        addDetail(card, "Reason", finding.reason);

        addDetail(
            card,
            "Recommendation",
            finding.recommendation ||
            "Review this indicator manually."
        );

        findingsContainer.appendChild(card);
    });
}


// ========================================
// RISK STYLING
// ========================================

function getRiskClass(risk) {
    if (risk === "HIGH") {
        return "risk-high";
    }

    if (risk === "MEDIUM") {
        return "risk-medium";
    }

    return "risk-low";
}


// ========================================
// DISPLAY FINDING DETAILS
// ========================================

function addDetail(container, label, value) {
    const paragraph = document.createElement("p");
    const strong = document.createElement("strong");

    strong.textContent = `${label}: `;

    paragraph.append(
        strong,
        document.createTextNode(String(value ?? "Not available"))
    );

    container.appendChild(paragraph);
}


// ========================================
// LOAD PRIVATE ANALYSIS HISTORY
// ========================================

async function loadHistory() {
    historyList.replaceChildren();

    const loading = document.createElement("p");
    loading.textContent = "Loading analysis history...";

    historyList.appendChild(loading);

    try {
        const data = await apiRequest("/api/history");
        renderHistory(data.history || []);

    } catch (error) {
        historyList.replaceChildren();

        const message = document.createElement("p");
        message.className = "history-empty";
        message.textContent = error.message;

        historyList.appendChild(message);
    }
}


// ========================================
// DISPLAY HISTORY
// ========================================

function renderHistory(history) {
    historyList.replaceChildren();

    if (history.length === 0) {
        const message = document.createElement("p");

        message.className = "history-empty";
        message.textContent = "No documents analyzed yet.";

        historyList.appendChild(message);
        return;
    }

    history.forEach(entry => {
        const card = document.createElement("article");
        card.className = "history-item";

        const title = document.createElement("h3");
        title.textContent = entry.filename;

        const risk = document.createElement("p");
        risk.textContent = `Risk Level: ${entry.risk_level}`;

        risk.className = getRiskClass(
            String(entry.risk_level || "LOW").toUpperCase()
        );

        const findings = document.createElement("p");
        findings.textContent = `Findings: ${entry.findings_count}`;

        const date = new Date(entry.analyzed_at);
        const time = document.createElement("p");

        time.textContent = `Analyzed: ${
            Number.isNaN(date.getTime())
                ? entry.analyzed_at
                : date.toLocaleString()
        }`;

        const size = document.createElement("p");
        size.textContent =
            `File size: ${Number(entry.file_size).toLocaleString()} bytes`;

        const characters = document.createElement("p");
        characters.textContent =
            `Characters analyzed: ${
                Number(entry.characters_analyzed).toLocaleString()
            }`;

        card.append(
            title,
            risk,
            findings,
            time,
            size,
            characters
        );

        historyList.appendChild(card);
    });
}


// ========================================
// CLEAR THE CURRENT USER'S HISTORY
// ========================================

clearHistoryButton.addEventListener("click", async function () {
    const confirmed = confirm(
        "Are you sure you want to permanently clear your analysis history?"
    );

    if (!confirmed) {
        return;
    }

    clearHistoryButton.disabled = true;

    try {
        const data = await apiRequest("/api/history", {
            method: "DELETE"
        });

        await loadHistory();

        statusMessage.textContent =
            data.message || "Your history has been cleared.";

    } catch (error) {
        statusMessage.textContent = "Error: " + error.message;

    } finally {
        clearHistoryButton.disabled = false;
    }
});


// ========================================
// EXPORT JSON REPORT
// ========================================

exportButton.addEventListener("click", exportReport);

function exportReport() {
    if (!lastAnalysisData) {
        statusMessage.textContent = "Analyze a document first.";
        return;
    }

    const report = {
        project: "GhostText",
        report_type: "Document Forensics Analysis",
        exported_at: new Date().toISOString(),
        filename: lastAnalysisData.filename,
        file_size_bytes: lastAnalysisData.size_bytes,
        analysis: lastAnalysisData.analysis,
        disclaimer:
            "Findings are heuristic indicators, not proof of malicious intent. " +
            "Only extracted text is analyzed by the current prototype."
    };

    const json = JSON.stringify(report, null, 2);

    const blob = new Blob(
        [json],
        { type: "application/json" }
    );

    const downloadUrl = URL.createObjectURL(blob);
    const link = document.createElement("a");

    const safeFilename = lastAnalysisData.filename
        .replace(/\.[^.]+$/, "")
        .replace(/[^a-z0-9_-]/gi, "_")
        .slice(0, 80) || "document";

    link.href = downloadUrl;
    link.download = `GhostText_Report_${safeFilename}.json`;

    document.body.appendChild(link);
    link.click();
    link.remove();

    URL.revokeObjectURL(downloadUrl);

    statusMessage.textContent =
        "Analysis report exported successfully.";
}


// ========================================
// INITIALIZE APPLICATION
// ========================================

checkSession();
