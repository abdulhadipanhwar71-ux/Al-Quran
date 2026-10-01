// State Variables
let currentSurahNumber = 1;
let allSurahs = [];
const currentAudio = document.getElementById("audio-element");

// Detect if running on GitHub Pages (static hosting) or local FastAPI server
const isGitHubPages = window.location.hostname.includes("github.io") || window.location.protocol === "file:";

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    loadSurahsList();
    loadSurahDetailsAndAyahs(1);
});

// Load Surahs List
async function loadSurahsList() {
    try {
        let surahsData = [];
        if (isGitHubPages) {
            // Fetch directly from live AlQuran Cloud API when on GitHub Pages
            const res = await fetch("https://api.alquran.cloud/v1/surah");
            const json = await res.json();
            surahsData = json.data.map(s => ({
                surah_number: s.number,
                name_arabic: s.name,
                name_english: s.englishName,
                english_meaning: s.englishNameTranslation,
                total_ayahs: s.numberOfAyahs,
                revelation_type: s.revelationType
            }));
        } else {
            // Local FastAPI endpoint
            const res = await fetch("/api/surahs");
            surahsData = await res.json();
        }

        allSurahs = surahsData;

        const select = document.getElementById("surah-select");
        select.innerHTML = '<option value="">سورۃ منتخب کریں...</option>';

        allSurahs.forEach(s => {
            const option = document.createElement("option");
            option.value = s.surah_number;
            option.textContent = `${s.surah_number}. ${s.name_arabic} (${s.name_english})`;
            select.appendChild(option);
        });

        select.value = "1";
    } catch (error) {
        console.error("Error loading surahs list:", error);
    }
}

// Load Surah Details and Ayahs
async function loadSurahDetailsAndAyahs(surahNumber) {
    if (surahNumber < 1 || surahNumber > 114) return;
    currentSurahNumber = parseInt(surahNumber);

    const select = document.getElementById("surah-select");
    if (select) select.value = currentSurahNumber;

    document.getElementById("search-alert").style.display = "none";
    document.getElementById("surah-card").style.display = "block";

    try {
        let surah = null;
        let ayahs = [];

        if (isGitHubPages) {
            // Fetch on GitHub Pages from Public Quran API
            const res = await fetch(`https://api.alquran.cloud/v1/surah/${currentSurahNumber}/editions/quran-uthmani,ur.jalandhry,ar.alafasy`);
            const json = await res.json();
            const d = json.data;
            const arEdition = d[0];
            const urEdition = d[1];
            const audioEdition = d[2];

            surah = {
                surah_number: arEdition.number,
                name_arabic: arEdition.name,
                name_english: arEdition.englishName,
                english_meaning: arEdition.englishNameTranslation,
                revelation_type: arEdition.revelationType,
                total_ayahs: arEdition.numberOfAyahs
            };

            for (let i = 0; i < arEdition.ayahs.length; i++) {
                ayahs.push({
                    surah_number: currentSurahNumber,
                    ayah_number_in_surah: arEdition.ayahs[i].numberInSurah,
                    global_ayah_number: arEdition.ayahs[i].number,
                    text_arabic: arEdition.ayahs[i].text.replace('\ufeff', ''),
                    text_urdu: urEdition.ayahs[i].text.replace('\ufeff', ''),
                    audio_url: audioEdition.ayahs[i].audio
                });
            }
        } else {
            // Local FastAPI
            const surahRes = await fetch(`/api/surahs/${currentSurahNumber}`);
            surah = await surahRes.json();

            const ayahsRes = await fetch(`/api/surahs/${currentSurahNumber}/ayahs`);
            ayahs = await ayahsRes.json();
        }

        // Render Surah Banner Info
        document.getElementById("surah-title-arabic").textContent = surah.name_arabic;
        document.getElementById("surah-title-english").textContent = `${surah.name_english} • ${surah.english_meaning || ''}`;
        document.getElementById("surah-type-badge").textContent = surah.revelation_type === 'Meccan' ? 'مکی' : 'مدنی';
        document.getElementById("surah-ayahs-badge").textContent = `${surah.total_ayahs} آیات`;
        document.getElementById("surah-number-badge").textContent = `نمبر: ${surah.surah_number}`;

        const bismillahBox = document.getElementById("bismillah-box");
        if (currentSurahNumber === 9) {
            bismillahBox.style.display = "none";
        } else {
            bismillahBox.style.display = "block";
        }

        renderAyahs(ayahs);
    } catch (error) {
        console.error("Error loading surah details:", error);
    }
}

function renderAyahs(ayahs) {
    const container = document.getElementById("ayahs-list");
    container.innerHTML = "";

    if (!ayahs || ayahs.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; background: white; border-radius: 12px;">
                <p style="font-size: 1.1rem; color: #0b4632;">اس سورۃ کی آیات لوڈ ہو رہی ہیں...</p>
            </div>
        `;
        return;
    }

    ayahs.forEach(a => {
        const card = document.createElement("div");
        card.className = "ayah-card";
        card.id = `ayah-${a.ayah_number_in_surah}`;

        const audioBtn = a.global_ayah_number ? `
            <button class="play-audio-btn" onclick="playAyahAudio(${a.global_ayah_number}, ${a.ayah_number_in_surah})">
                <span>▶</span> تلاوت سنیں
            </button>
        ` : '';

        card.innerHTML = `
            <div class="ayah-top-bar">
                <div class="ayah-badge-number">${a.ayah_number_in_surah}</div>
                ${audioBtn}
            </div>
            <div class="ayah-arabic-text">${a.text_arabic}</div>
            <div class="ayah-urdu-text">${a.text_urdu}</div>
        `;

        container.appendChild(card);
    });
}

function onSurahChange(val) {
    if (val) {
        loadSurahDetailsAndAyahs(val);
    }
}

function goToSurah(num) {
    if (num >= 1 && num <= 114) {
        loadSurahDetailsAndAyahs(num);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// Search Handler
async function handleSearch(event) {
    event.preventDefault();
    const query = document.getElementById("search-input").value.trim();
    if (!query) return;

    try {
        if (isGitHubPages) {
            // Client-side search on GitHub Pages
            if (/^\d+$/.test(query)) {
                const sNum = parseInt(query);
                if (sNum >= 1 && sNum <= 114) {
                    loadSurahDetailsAndAyahs(sNum);
                    return;
                }
            }

            const cleanQ = query.toLowerCase().replace(/[-'\s]/g, '');
            const matched = allSurahs.find(s => {
                const en = s.name_english.toLowerCase().replace(/[-'\s]/g, '');
                const ar = s.name_arabic.replace(/[\u0617-\u061A\u064B-\u0652\u06D6-\u06ED\u0670\u0671\s]/g, '');
                return en.includes(cleanQ) || cleanQ.includes(en) || ar.includes(cleanQ) || cleanQ.includes(ar);
            });

            if (matched) {
                loadSurahDetailsAndAyahs(matched.surah_number);
                return;
            }

            // Word search
            const res = await fetch(`https://api.alquran.cloud/v1/search/${encodeURIComponent(query)}/all/ur.jalandhry`);
            const json = await res.json();
            const matches = json.data ? json.data.matches : [];

            displaySearchResults(matches.map(m => ({
                surah_name_arabic: m.surah.name,
                surah_name_english: m.surah.englishName,
                ayah_number_in_surah: m.numberInSurah,
                global_ayah_number: m.number,
                text_arabic: '',
                text_urdu: m.text
            })), query);

        } else {
            // Local FastAPI search
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (data.type === "surah_redirect") {
                document.getElementById("search-alert").style.display = "none";
                loadSurahDetailsAndAyahs(data.surah_number);
                return;
            }

            displaySearchResults(data.results, query);
        }
    } catch (error) {
        console.error("Search failed:", error);
    }
}

function displaySearchResults(results, query) {
    const alertBox = document.getElementById("search-alert");
    const msg = document.getElementById("search-msg");
    alertBox.style.display = "flex";
    msg.textContent = `تلاش کے نتائج (${results.length}): "${query}"`;

    document.getElementById("surah-card").style.display = "none";

    const container = document.getElementById("ayahs-list");
    container.innerHTML = "";

    if (results.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; background: white; border-radius: 12px;">
                <p style="font-size: 1.1rem; color: #888;">کوئی نتیجہ نہیں ملا۔</p>
            </div>
        `;
        return;
    }

    results.forEach(a => {
        const card = document.createElement("div");
        card.className = "ayah-card";

        const audioBtn = a.global_ayah_number ? `
            <button class="play-audio-btn" onclick="playAyahAudio(${a.global_ayah_number}, ${a.ayah_number_in_surah})">
                <span>▶</span> تلاوت سنیں
            </button>
        ` : '';

        card.innerHTML = `
            <div class="ayah-top-bar">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span class="ayah-badge-number">${a.ayah_number_in_surah}</span>
                    <span style="font-weight: bold; color: #0b4632;">${a.surah_name_arabic} (${a.surah_name_english})</span>
                </div>
                ${audioBtn}
            </div>
            ${a.text_arabic ? `<div class="ayah-arabic-text">${a.text_arabic}</div>` : ''}
            <div class="ayah-urdu-text">${a.text_urdu}</div>
        `;

        container.appendChild(card);
    });
}

function clearSearch() {
    document.getElementById("search-input").value = "";
    loadSurahDetailsAndAyahs(currentSurahNumber);
}

// Audio Player Handlers
function playAyahAudio(globalAyahNumber, ayahNumberInSurah) {
    if (!globalAyahNumber) return;

    const bar = document.getElementById("global-player-bar");
    const tag = document.getElementById("player-ayah-tag");

    bar.style.display = "block";
    tag.textContent = `آیت نمبر ${ayahNumberInSurah}`;

    // On GitHub Pages, play from high-speed Islamic Network CDN; On localhost, use /api/audio
    const audioSrc = isGitHubPages 
        ? `https://cdn.islamic.network/quran/audio/128/ar.alafasy/${globalAyahNumber}.mp3`
        : `/api/audio/${globalAyahNumber}`;

    currentAudio.src = audioSrc;
    currentAudio.load();
    currentAudio.play().catch(e => {
        console.warn("Audio play issue:", e);
    });
}

function closeAudioPlayer() {
    currentAudio.pause();
    document.getElementById("global-player-bar").style.display = "none";
}
