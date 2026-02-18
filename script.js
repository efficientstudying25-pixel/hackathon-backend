const micBtn = document.getElementById("micBtn");
const speechText = document.getElementById("speechText");
const highlightedText = document.getElementById("highlightedText");
const analyzeBtn = document.getElementById("analyzeBtn");

const riskCircle = document.getElementById("riskCircle");
const riskInner = document.getElementById("riskInner");


// Speech Recognition
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


// SCAM WORD SCAN
const scamWords=[
"otp","password","urgent","verify","kyc",
"lottery","refund","remote","blocked",
"bank","account","link"
];

function scanText(text){
    let risk=0;
    let highlighted=text;

    scamWords.forEach(word=>{
        const regex=new RegExp(`\\b(${word})\\b`,"gi");
        if(regex.test(text)) risk++;
        highlighted=highlighted.replace(regex,
            `<span class="flag">$1</span>`);
    });

    return {risk,highlighted};
}


// GAUGE
function updateGaugeAnimated(targetScore){

    let current = 0;
    const stepTime = 12;     // speed (lower = faster)

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

    }, stepTime);
}



const API_URL = "https://hackathon-voice-scam-guardian.onrender.com/analyze";

analyzeBtn.addEventListener("click", async () => {

    const text = speechText.value.trim();
    if(!text) return alert("Enter or speak text first");

    analyzeBtn.textContent = "🔍 Analyzing...";
    analyzeBtn.disabled = true;

    try {

        const response = await fetch(API_URL,{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body: JSON.stringify({ message: text })
        });

        const result = await response.json();
        console.log(result);


        /*
        Expected format:
        {
            risk_score: 73,
            risk_level: "High",
            scam_type: "...",
            explanation: "...",
            flagged_words: [...]
        }
        */

        // Highlight
        let highlighted = text;

        if (result.flagged_keywords && Array.isArray(result.flagged_keywords)) {


           result.flagged_keywords.forEach(word=>{
              const regex = new RegExp(`\\b(${word})\\b`, "gi");
             highlighted = highlighted.replace(regex,
               `<span class="flag">$1</span>`);
    });

}

        speechText.classList.add("hidden");
        highlightedText.classList.remove("hidden");
        highlightedText.innerHTML = highlighted;

        // Fill UI
        document.getElementById("risk").textContent = result.risk_level;
        document.getElementById("type").textContent =
          result.risk_level === "Low"
              ? "None"
              : "Potential Voice Scam";

        let flagged = [];

       document.getElementById("words").textContent =
          Array.isArray(result.flagged_keywords) &&
          result.flagged_keywords.length
             ? result.flagged_keywords.join(", ")
             : "None";



        document.getElementById("explain").textContent = result.explanation;

        // Gauge
        updateGaugeAnimated(result.risk_score);

    } catch(err){
        alert("Backend error — check server");
        console.error(err);
    }

    analyzeBtn.textContent = "Analyze";
    analyzeBtn.disabled = false;

});
