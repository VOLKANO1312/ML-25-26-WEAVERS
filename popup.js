document.getElementById("analyzeVideo").onclick = async () => {
    const url = document.getElementById("url").value;
    const result = document.getElementById("result");

    result.innerText = "⏳ Analyse vidéo...";

    try {
        const res = await fetch("http://127.0.0.1:8000/analyze/video/youtube", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url })
        });

        const data = await res.json();

   const virality = Math.max(0, Math.min(100, data.virality_score));
const recommendation = Math.max(0, Math.min(100, data.recommendation_probability));

result.innerHTML = `
    <div class="progress">
        🔥 Virality: <b>${virality.toFixed(1)}%</b>
        <div class="bar">
            <div class="fill" style="width:${virality}%"></div>
        </div>
    </div>

    <div class="progress">
        📈 Recommendation: <b>${recommendation.toFixed(1)}%</b>
        <div class="bar">
            <div class="fill" style="width:${recommendation}%"></div>
        </div>
    </div>
`;

    } catch (e) {
        result.innerText = "❌ Erreur analyse vidéo";
    }
};
document.getElementById("analyzeCreator").onclick = async () => {
    const url = document.getElementById("url").value;
    const result = document.getElementById("result");

    result.innerText = "⏳ Analyse créateur...";

    try {
        const res = await fetch("http://127.0.0.1:8000/analyze/creator/youtube", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ url })
        });

        const data = await res.json();

      result.innerHTML = `
    <div class="progress">
        👤 Creator Level
        <h3>${data.creator_level}</h3>
    </div>
`;

    } catch (e) {
        result.innerText = "❌ Erreur analyse créateur";
    }
};
