const micBtn = document.getElementById("micBtn");
const speechText = document.getElementById("speechText");
const highlightedText = document.getElementById("highlightedText");
const analyzeBtn = document.getElementById("analyzeBtn");

const optionsBtn = document.getElementById("optionsBtn");
const dropdownMenu = document.getElementById("dropdownMenu");
const editOption = document.getElementById("editOption");
const resetOption = document.getElementById("resetOption");
const optionsWrapper = document.getElementById("optionsWrapper");
if (optionsWrapper) {
    optionsWrapper.style.display="none";
}
console.log("Options Wrapper:", optionsWrapper);

const riskCircle = document.getElementById("riskCircle");
const riskInner = document.getElementById("riskInner");

const viewBtn = document.getElementById("viewDetailsBtn");
const modal = document.getElementById("detailsModal");
const closeModal = document.getElementById("closeModal");


// LOADER
window.addEventListener("load", () => {
    const loader = document.getElementById("loader");

    setTimeout(() => {
        loader.style.opacity = "0";
        loader.style.transition = "0.5s";

        setTimeout(() => {
            loader.style.display = "none";
        }, 500);
    }, 1200); // how long it shows
});

// SPEECH
const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

const recognition = new SpeechRecognition();
recognition.lang = "en-IN";

micBtn.addEventListener("click", () => {
    recognition.start();
    micBtn.textContent="🎙 Listening...";
    micBtn.classList.add("listening");
});

recognition.onresult = (e)=>{
    speechText.value = e.results[0][0].transcript;
};

recognition.onend = ()=>{
    micBtn.textContent="🎙 Start Recording";
    micBtn.classList.remove("listening");
};

// GAUGE
function updateGaugeAnimated(targetScore){
    let current = 0;

    const interval = setInterval(()=>{
        if(current >= targetScore){
            clearInterval(interval);
            return;
        }

        current++;

        const deg = current * 3.6;

        let color="#22c55e";
        let icon="✓";

        if(current > 40){
            color="#eab308";
            icon="⚠";
        }

        if(current > 70){
            color="#ef4444";
            icon="⛔";
        }

        riskCircle.style.background =
            `conic-gradient(${color} ${deg}deg,
            rgba(255,255,255,0.08) ${deg}deg)`;

        riskInner.textContent = `${icon} ${current}%`;

    }, 12);
}
// API
const API_URL = "https://hackathon-voice-scam-guardian.onrender.com/analyze";

// ANALYZE
analyzeBtn.addEventListener("click", async () => {

    const text = speechText.value.trim();
    if(!text) return alert("Enter text first");

    // STATE 1 → LOADING
    analyzeBtn.textContent = "🔍 Analyzing...";
    analyzeBtn.disabled = true;

    try {
        const response = await fetch(API_URL,{
            method:"POST",
            headers:{ "Content-Type":"application/json" },
            body: JSON.stringify({ message: text })
        });

        const result = await response.json();

        let highlighted = text;

        if (Array.isArray(result.flagged_keywords)) {
            result.flagged_keywords.forEach(word=>{
                const regex = new RegExp(`\\b(${word})\\b`, "gi");
                highlighted = highlighted.replace(regex,
                  `<span class="flag">$1</span>`);
            });
        }

        speechText.classList.add("hidden");
        highlightedText.classList.remove("hidden");
        highlightedText.innerHTML = highlighted;

        document.getElementById("risk").textContent = result.risk_level || "--";
        document.getElementById("type").textContent = result.scam_type || "None";

        document.getElementById("explain").textContent = result.explanation || "--";
        document.getElementById("confidence").textContent = result.confidence_percent + "%" || "--";
        document.getElementById("ml-prob").textContent = result.ml_probability || "--";
        document.getElementById("words").textContent =
            result.flagged_keywords?.length
            ? result.flagged_keywords.join(", ")
            : "None";

        updateGaugeAnimated(result.risk_score || 0);

        optionsWrapper.style.display = "flex";
        optionsBtn.classList.remove("hidden");
        viewBtn.classList.remove("hidden");

        // ✅ STATE 2 → DONE
        analyzeBtn.textContent = "✅ Analyzed";

    } catch(err){
        alert("waking up server... Please try again in a moment🚀");
        console.error(err);

        // ERROR STATE 
        analyzeBtn.textContent = "Try Again";
    }

    // re-enable button after short delay
    setTimeout(() => {
        analyzeBtn.disabled = false;
    }, 800);
});


// MODAL
viewBtn.addEventListener("click", () => {
    modal.classList.remove("hidden");
    setTimeout(() => modal.classList.add("show"), 10);
});

closeModal.addEventListener("click", () => {
    modal.classList.remove("show");
    setTimeout(() => modal.classList.add("hidden"), 200);
});

modal.addEventListener("click", (e) => {
    if (e.target === modal) {
        modal.classList.remove("show");
        setTimeout(() => modal.classList.add("hidden"), 200);
    }
});


// OPTIONS DROPDOWN
optionsBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    dropdownMenu.classList.toggle("hidden");
});

document.addEventListener("click", (e) => {
    if (!optionsWrapper.contains(e.target)) {
        dropdownMenu.classList.add("hidden");
    }
});

//EDIT 
editOption.addEventListener("click", () => {
    speechText.classList.remove("hidden");
    highlightedText.classList.add("hidden");
    dropdownMenu.classList.add("hidden");
});

// RESET
resetOption.addEventListener("click", () => {

    speechText.value = "";
    speechText.classList.remove("hidden");
    highlightedText.classList.add("hidden");
    highlightedText.innerHTML = "";

    document.getElementById("risk").textContent = "";
    document.getElementById("type").textContent = "";
    document.getElementById("words").textContent = "";
    document.getElementById("explain").textContent = "";
    document.getElementById("confidence").textContent = "";
    document.getElementById("ml-prob").textContent = "";
    analyzeBtn.textContent = "Analyze";

    riskCircle.style.background =
        `conic-gradient(#22c55e 0deg, rgba(255,255,255,0.08) 0deg)`;

    riskInner.textContent = "0%";

    dropdownMenu.classList.add("hidden");
    viewBtn.classList.add("hidden");
    optionsWrapper.style.display = "none";

});

window.addEventListener("load", () => {
    fetch("https://hackathon-voice-scam-guardian.onrender.com");
});
