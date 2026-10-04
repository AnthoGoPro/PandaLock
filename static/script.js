// PandaLock - makes the panda react and shows results as you type.
// The password is sent to the checker and never stored anywhere.

const input = document.getElementById("password");
const toggle = document.getElementById("toggle");
const panda = document.getElementById("panda");
const bubble = document.getElementById("bubble");
const crackTime = document.getElementById("crack-time");
const universeNote = document.getElementById("universe-note");
const meterFill = document.getElementById("meter-fill");
const rating = document.getElementById("rating");
const checks = document.getElementById("checks");
const suggestions = document.getElementById("suggestions");
const tipText = document.getElementById("tip-text");
const tipBtn = document.getElementById("tip-btn");

const CHECK_LABELS = [
  "At least 8 characters",
  "Uppercase letter",
  "Lowercase letter",
  "Number",
  "Special character",
  "Not a common password",
  "No common words or names",
];

const STATES = {
  "Easily Hackable": "state-danger",
  "Hackable": "state-warn",
  "Non-Hackable": "state-safe",
};

const LINES = {
  "state-danger": "Yikes! I could crack that before my bamboo gets cold.",
  "state-warn": "Getting there, but a patient hacker could still get in.",
  "state-safe": "Now THAT is a lock. Hackers, go home.",
};

let timer = null;
let requestId = 0;

function setState(stateClass) {
  panda.classList.remove("state-idle", "state-danger", "state-warn", "state-safe");
  panda.classList.add(stateClass);
}

// The panda covers its eyes while you type a hidden password
function updateCovering() {
  const hidden = input.type === "password";
  const focused = document.activeElement === input;
  panda.classList.toggle("covering", hidden && focused);
}

// pending = true shows neutral marks before anything has been typed
function renderChecks(list, pending) {
  checks.innerHTML = "";
  list.forEach((check) => {
    const li = document.createElement("li");
    const mark = document.createElement("span");
    mark.className = "mark";
    if (pending) {
      li.className = "pending";
      mark.textContent = "·";
    } else {
      li.className = check.passed ? "pass" : "fail";
      mark.textContent = check.passed ? "✓" : "✕";
    }
    li.append(mark, document.createTextNode(check.label));
    checks.append(li);
  });
}

function renderSuggestions(list) {
  suggestions.innerHTML = "";
  list.forEach((text) => {
    const li = document.createElement("li");
    li.textContent = text;
    suggestions.append(li);
  });
}

// Meter fills on a log scale: 1 second is near empty, 1 day is about 40%,
// 1,000 years is about 80%, and anything past 10 trillion seconds is full.
function meterPercent(seconds) {
  const percent = (Math.log10(seconds + 1) / 13) * 100;
  return Math.max(4, Math.min(100, percent));
}

function reset() {
  requestId++;
  setState("state-idle");
  crackTime.textContent = "--";
  universeNote.textContent = "";
  meterFill.style.width = "0";
  rating.textContent = "Waiting for a password";
  renderChecks(CHECK_LABELS.map((label) => ({ label, passed: false })), true);
  renderSuggestions(["Start typing to get suggestions."]);
  bubble.textContent = "Go ahead and type. I'm not looking, and I never save anything.";
}

function render(data) {
  const stateClass = STATES[data.rating];
  setState(stateClass);
  crackTime.textContent = data.crack_time;
  universeNote.textContent = data.universe_note;
  meterFill.style.width = meterPercent(data.seconds) + "%";
  rating.textContent = data.rating;
  renderChecks(data.checks);
  renderSuggestions(data.suggestions);

  if (data.found_words.length > 0) {
    bubble.textContent = 'I spotted "' + data.found_words[0] + '" in there. Hackers try that one first!';
  } else {
    bubble.textContent = LINES[stateClass];
  }
}

async function runCheck() {
  const password = input.value;
  if (password === "") {
    reset();
    return;
  }

  const myId = ++requestId;
  try {
    const response = await fetch("/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password }),
    });
    const data = await response.json();
    // Ignore old answers if you kept typing while this one was loading
    if (myId === requestId) {
      render(data);
    }
  } catch (error) {
    if (myId === requestId) {
      bubble.textContent = "Hmm, I lost my connection. Try again in a second.";
    }
  }
}

async function loadTip() {
  try {
    const response = await fetch("/tip");
    const data = await response.json();
    tipText.textContent = data.tip;
  } catch (error) {
    tipText.textContent = "Never reuse a password. One breach can unlock all your accounts.";
  }
}

// Wait until you pause typing for a moment before checking
input.addEventListener("input", () => {
  clearTimeout(timer);
  timer = setTimeout(runCheck, 180);
});

input.addEventListener("focus", updateCovering);
input.addEventListener("blur", updateCovering);

toggle.addEventListener("click", () => {
  const show = input.type === "password";
  input.type = show ? "text" : "password";
  toggle.textContent = show ? "Hide" : "Show";
  toggle.setAttribute("aria-pressed", String(show));
  input.focus();
  updateCovering();
});

tipBtn.addEventListener("click", loadTip);

reset();
loadTip();
