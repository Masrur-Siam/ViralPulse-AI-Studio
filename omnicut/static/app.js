// OmniCut Studio Client App - Direct YouTube & AI Video Suite
document.addEventListener("DOMContentLoaded", () => {
    // State Store
    const state = {
        stitchSource: null,       // Local filename OR YouTube URL
        stitchDuration: 0,
        segments: [{ start: 0, end: 15 }],
        compA: null,              // File A or URL A
        compB: null,              // File B or URL B
        ttsVideo: null,           // File or URL
        shortsSource: null,       // File or URL
        voices: []
    };

    // --------------------------------------------------------
    // Navigation Tabs
    // --------------------------------------------------------
    const navItems = document.querySelectorAll(".nav-item");
    const tabPanes = document.querySelectorAll(".tab-pane");

    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const tabId = item.dataset.tab;
            navItems.forEach(n => n.classList.remove("active"));
            tabPanes.forEach(p => p.classList.remove("active"));

            item.classList.add("active");
            document.getElementById(`tab-${tabId}`).classList.add("active");

            if (tabId === "library") {
                loadLibrary();
            }
        });
    });

    // --------------------------------------------------------
    // UI Helpers (Toast & Modal)
    // --------------------------------------------------------
    function showToast(message, type = "info") {
        const container = document.getElementById("toast-container");
        const toast = document.createElement("div");
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 4000);
    }

    function showLoading(title = "Processing...", desc = "Fetching and rendering with FFmpeg...") {
        document.getElementById("modal-title").textContent = title;
        document.getElementById("modal-desc").textContent = desc;
        document.getElementById("loading-modal").classList.remove("hidden");
    }

    function hideLoading() {
        document.getElementById("loading-modal").classList.add("hidden");
    }

    // --------------------------------------------------------
    // Generic File Uploader Helper
    // --------------------------------------------------------
    async function uploadVideoFile(file) {
        const formData = new FormData();
        formData.append("file", file);

        showLoading("Uploading File...", `Uploading ${file.name}`);
        try {
            const res = await fetch("/api/upload", { method: "POST", body: formData });
            const data = await res.json();
            if (!data.ok) throw new Error(data.detail || "Upload failed");
            showToast(`Uploaded: ${file.name}`, "success");
            return data;
        } catch (err) {
            showToast(err.message, "error");
            return null;
        } finally {
            hideLoading();
        }
    }

    function setupDropzone(dropzoneId, inputId, onUploaded) {
        const dropzone = document.getElementById(dropzoneId);
        const input = document.getElementById(inputId);

        dropzone.addEventListener("click", () => input.click());

        dropzone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropzone.classList.add("dragover");
        });

        dropzone.addEventListener("dragleave", () => {
            dropzone.classList.remove("dragover");
        });

        dropzone.addEventListener("drop", async (e) => {
            e.preventDefault();
            dropzone.classList.remove("dragover");
            if (e.dataTransfer.files.length > 0) {
                const res = await uploadVideoFile(e.dataTransfer.files[0]);
                if (res) onUploaded(res);
            }
        });

        input.addEventListener("change", async () => {
            if (input.files.length > 0) {
                const res = await uploadVideoFile(input.files[0]);
                if (res) onUploaded(res);
            }
        });
    }

    // --------------------------------------------------------
    // TAB 1: SPLIT & STITCH (DIRECT YOUTUBE OR FILE)
    // --------------------------------------------------------
    async function loadYouTubeStitch(url) {
        if (!url || !url.trim().startsWith("http")) {
            return showToast("Please paste a valid YouTube/video link.", "error");
        }
        showLoading("Fetching YouTube Info...", "Retrieving video details without downloading...");
        try {
            const res = await fetch("/api/url-info", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url: url.trim() })
            });
            const data = await res.json();
            if (!data.ok) throw new Error(data.detail || "Could not fetch YouTube info");

            state.stitchSource = url.trim();
            state.stitchDuration = data.duration || 0;

            const box = document.getElementById("stitch-source-info");
            box.classList.remove("hidden");
            document.getElementById("stitch-yt-thumb").src = data.thumbnail || "";
            document.getElementById("stitch-source-title").textContent = data.title;
            document.getElementById("stitch-source-meta").textContent = `${data.duration}s | ${data.uploader || 'YouTube'}`;

            state.segments = [{ start: 0, end: Math.min(20, data.duration || 20) }];
            renderSegmentsTable();
            showToast("YouTube video connected! Set parts and click Cut & Stitch.", "success");
        } catch (e) {
            showToast(e.message, "error");
        } finally {
            hideLoading();
        }
    }

    document.getElementById("btn-load-yt-stitch").addEventListener("click", () => {
        loadYouTubeStitch(document.getElementById("url-stitch").value);
    });

    setupDropzone("dropzone-stitch", "file-stitch", (data) => {
        state.stitchSource = data.filename;
        state.stitchDuration = data.info.duration || 0;

        const box = document.getElementById("stitch-source-info");
        box.classList.remove("hidden");
        document.getElementById("stitch-yt-thumb").src = "";
        document.getElementById("stitch-source-title").textContent = data.original_name || data.filename;
        document.getElementById("stitch-source-meta").textContent = `${data.info.duration}s | Local Video`;

        const previewWrap = document.getElementById("wrapper-stitch-preview");
        const preview = document.getElementById("preview-stitch");
        previewWrap.classList.remove("hidden");
        preview.src = data.url;

        state.segments = [{ start: 0, end: Math.min(20, data.info.duration || 20) }];
        renderSegmentsTable();
    });

    function renderSegmentsTable() {
        const tbody = document.getElementById("segments-list");
        tbody.innerHTML = "";

        state.segments.forEach((seg, idx) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>Part #${idx + 1}</td>
                <td><input type="number" step="0.5" min="0" value="${seg.start}" data-idx="${idx}" class="seg-start"></td>
                <td><input type="number" step="0.5" min="0" value="${seg.end}" data-idx="${idx}" class="seg-end"></td>
                <td><span class="meta-tag">${(seg.end - seg.start).toFixed(1)}s</span></td>
                <td><button class="btn-del-seg" data-idx="${idx}">✕</button></td>
            `;
            tbody.appendChild(tr);
        });

        document.querySelectorAll(".seg-start").forEach(input => {
            input.addEventListener("change", (e) => {
                const idx = parseInt(e.target.dataset.idx);
                state.segments[idx].start = parseFloat(e.target.value) || 0;
                renderSegmentsTable();
            });
        });

        document.querySelectorAll(".seg-end").forEach(input => {
            input.addEventListener("change", (e) => {
                const idx = parseInt(e.target.dataset.idx);
                state.segments[idx].end = parseFloat(e.target.value) || 0;
                renderSegmentsTable();
            });
        });

        document.querySelectorAll(".btn-del-seg").forEach(btn => {
            btn.addEventListener("click", (e) => {
                const idx = parseInt(e.target.dataset.idx);
                state.segments.splice(idx, 1);
                renderSegmentsTable();
            });
        });
    }

    document.getElementById("btn-add-segment").addEventListener("click", () => {
        const lastEnd = state.segments.length > 0 ? state.segments[state.segments.length - 1].end : 0;
        state.segments.push({ start: lastEnd, end: lastEnd + 10 });
        renderSegmentsTable();
    });

    // Auto-detect active scenes
    document.getElementById("btn-auto-detect").addEventListener("click", async () => {
        const source = state.stitchSource || document.getElementById("url-stitch").value.trim();
        if (!source) return showToast("Enter a YouTube link or upload a video first.", "error");

        showLoading("Analyzing Video...", "Resolving stream, detecting speech/action and removing silence...");
        try {
            const res = await fetch("/api/auto-split", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ source: source })
            });
            const data = await res.json();
            if (!data.ok) throw new Error(data.detail || "Analysis failed");

            if (data.segments && data.segments.length > 0) {
                state.stitchSource = data.filename;
                state.segments = data.segments.map(s => ({ start: s.start, end: s.end }));
                renderSegmentsTable();
                showToast(`Auto-detected ${state.segments.length} action highlights!`, "success");
            } else {
                showToast("No silent gaps found. Video appears continuous.", "info");
            }
        } catch (e) {
            showToast(e.message, "error");
        } finally {
            hideLoading();
        }
    });

    // Render Stitch
    document.getElementById("btn-render-stitch").addEventListener("click", async () => {
        const source = state.stitchSource || document.getElementById("url-stitch").value.trim();
        if (!source) return showToast("Please paste a YouTube link or select a video first.", "error");
        if (state.segments.length === 0) return showToast("Add at least one segment.", "error");

        const voiceSelect = document.getElementById("stitch-voice-select").value;

        showLoading("Generating Stitched Video...", "Downloading/reading YouTube stream, cutting parts, and merging...");
        try {
            const res = await fetch("/api/split-and-stitch", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    source: source,
                    segments: state.segments,
                    voiceover_filename: voiceSelect || null
                })
            });
            const data = await res.json();
            if (!data.ok) throw new Error(data.detail || "Stitching failed");

            const resCard = document.getElementById("result-stitch-card");
            const resVideo = document.getElementById("result-stitch-video");
            const resBtn = document.getElementById("btn-download-stitch");

            resCard.classList.remove("hidden");
            resVideo.src = data.url;
            resBtn.href = data.url;
            resBtn.setAttribute("download", data.filename);

            showToast("Video stitched successfully!", "success");
            resCard.scrollIntoView({ behavior: "smooth" });
        } catch (e) {
            showToast(e.message, "error");
        } finally {
            hideLoading();
        }
    });

    // --------------------------------------------------------
    // TAB 2: DUAL VIDEO / GAME COMPARE (DIRECT YOUTUBE & FILES)
    // --------------------------------------------------------
    setupDropzone("dropzone-comp-a", "file-comp-a", (data) => {
        state.compA = data.filename;
        document.getElementById("label-file-comp-a").textContent = `Selected: ${data.original_name || data.filename}`;
    });

    setupDropzone("dropzone-comp-b", "file-comp-b", (data) => {
        state.compB = data.filename;
        document.getElementById("label-file-comp-b").textContent = `Selected: ${data.original_name || data.filename}`;
    });

    document.getElementById("btn-render-compare").addEventListener("click", async () => {
        const sourceA = document.getElementById("url-comp-a").value.trim() || state.compA;
        const sourceB = document.getElementById("url-comp-b").value.trim() || state.compB;

        if (!sourceA || !sourceB) {
            return showToast("Please provide Video A and Video B (paste YouTube links or upload files).", "error");
        }

        const payload = {
            video_a: sourceA,
            video_b: sourceB,
            layout: document.getElementById("compare-layout").value,
            label_a: document.getElementById("label-comp-a").value.trim(),
            label_b: document.getElementById("label-comp-b").value.trim(),
            start_a: parseFloat(document.getElementById("start-comp-a").value) || 0,
            start_b: parseFloat(document.getElementById("start-comp-b").value) || 0,
            duration: parseFloat(document.getElementById("compare-duration").value) || 15,
            audio_mode: document.getElementById("compare-audio").value
        };

        showLoading("Generating Comparison Video...", "Streaming YouTube videos, stacking layout, and rendering labels...");
        try {
            const res = await fetch("/api/compare-videos", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (!data.ok) throw new Error(data.detail || "Comparison failed");

            const card = document.getElementById("result-compare-card");
            const video = document.getElementById("result-compare-video");
            const btn = document.getElementById("btn-download-compare");

            card.classList.remove("hidden");
            video.src = data.url;
            btn.href = data.url;
            btn.setAttribute("download", data.filename);

            showToast("Comparison video rendered!", "success");
            card.scrollIntoView({ behavior: "smooth" });
        } catch (e) {
            showToast(e.message, "error");
        } finally {
            hideLoading();
        }
    });

    // --------------------------------------------------------
    // TAB 3: AI VOICEOVER (TTS)
    // --------------------------------------------------------
    let lastGeneratedVoiceFile = null;

    async function loadVoices() {
        try {
            const res = await fetch("/api/tts/voices");
            const voices = await res.json();
            state.voices = voices;

            const select = document.getElementById("tts-voice-select");
            select.innerHTML = "";

            voices.forEach(v => {
                const opt = document.createElement("option");
                opt.value = v.id;
                opt.textContent = `[${v.lang}] ${v.name}`;
                select.appendChild(opt);
            });
        } catch (e) {
            console.error("Failed to load voices", e);
        }
    }
    loadVoices();

    document.getElementById("btn-generate-tts").addEventListener("click", async () => {
        const text = document.getElementById("tts-text").value.trim();
        if (!text) return showToast("Please type text to speak.", "error");

        const payload = {
            text: text,
            voice: document.getElementById("tts-voice-select").value,
            rate: document.getElementById("tts-rate").value,
            pitch: document.getElementById("tts-pitch").value
        };

        showLoading("Generating Neural Voice...", "Communicating with Edge TTS...");
        try {
            const res = await fetch("/api/tts/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (!data.ok) throw new Error(data.detail || "TTS generation failed");

            lastGeneratedVoiceFile = data.filename;

            const playerWrap = document.getElementById("tts-player-wrapper");
            const audio = document.getElementById("tts-audio-player");
            const dl = document.getElementById("btn-download-tts");

            playerWrap.classList.remove("hidden");
            audio.src = data.url;
            dl.href = data.url;
            dl.setAttribute("download", data.filename);
            audio.play();

            const stitchVoiceSelect = document.getElementById("stitch-voice-select");
            const opt = document.createElement("option");
            opt.value = data.filename;
            opt.textContent = `Generated Voice (${data.filename})`;
            opt.selected = true;
            stitchVoiceSelect.appendChild(opt);

            showToast("Voice generated successfully!", "success");
        } catch (e) {
            showToast(e.message, "error");
        } finally {
            hideLoading();
        }
    });

    setupDropzone("dropzone-tts-video", "file-tts-video", (data) => {
        state.ttsVideo = data.filename;
        document.getElementById("label-tts-video").textContent = `Selected: ${data.original_name || data.filename}`;
    });

    document.getElementById("tts-bg-volume").addEventListener("input", (e) => {
        document.getElementById("tts-bg-vol-label").textContent = `${Math.round(e.target.value * 100)}% (Ducked)`;
    });

    document.getElementById("tts-voice-volume").addEventListener("input", (e) => {
        document.getElementById("tts-voice-vol-label").textContent = `${Math.round(e.target.value * 100)}%`;
    });

    document.getElementById("btn-overlay-tts").addEventListener("click", async () => {
        const source = document.getElementById("url-tts-video").value.trim() || state.ttsVideo;
        if (!source) return showToast("Enter a YouTube link or upload a video.", "error");
        if (!lastGeneratedVoiceFile) return showToast("Generate or select a voiceover first.", "error");

        const payload = {
            video_source: source,
            voice_filename: lastGeneratedVoiceFile,
            bg_volume: parseFloat(document.getElementById("tts-bg-volume").value),
            voice_volume: parseFloat(document.getElementById("tts-voice-volume").value)
        };

        showLoading("Overlaying Voice...", "Ducking background audio and mixing voiceover...");
        try {
            const res = await fetch("/api/tts/overlay", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (!data.ok) throw new Error(data.detail || "Overlay failed");

            const card = document.getElementById("result-voiced-card");
            const video = document.getElementById("result-voiced-video");
            const dl = document.getElementById("btn-download-voiced");

            card.classList.remove("hidden");
            video.src = data.url;
            dl.href = data.url;
            dl.setAttribute("download", data.filename);

            showToast("Voice overlaid onto video!", "success");
        } catch (e) {
            showToast(e.message, "error");
        } finally {
            hideLoading();
        }
    });

    // --------------------------------------------------------
    // TAB 4: 9:16 SHORTS CREATOR (DIRECT YOUTUBE & FILES)
    // --------------------------------------------------------
    setupDropzone("dropzone-shorts", "file-shorts", (data) => {
        state.shortsSource = data.filename;
        document.getElementById("label-shorts-file").textContent = `Selected: ${data.original_name || data.filename}`;
    });

    document.getElementById("btn-render-short").addEventListener("click", async () => {
        const source = document.getElementById("url-shorts").value.trim() || state.shortsSource;
        if (!source) return showToast("Paste a YouTube link or upload a video first.", "error");

        const payload = {
            source: source,
            start: parseFloat(document.getElementById("shorts-start").value) || 0,
            duration: parseFloat(document.getElementById("shorts-duration").value) || 30,
            mode: document.getElementById("shorts-mode").value
        };

        showLoading("Creating 9:16 Short...", "Fetching stream, applying vertical background blur and scaling...");
        try {
            const res = await fetch("/api/make-short", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (!data.ok) throw new Error(data.detail || "Short generation failed");

            document.getElementById("shorts-preview-container").classList.add("hidden");
            const resContainer = document.getElementById("shorts-result-container");
            const resVideo = document.getElementById("shorts-result-video");
            const resBtn = document.getElementById("btn-download-short");

            resContainer.classList.remove("hidden");
            resVideo.src = data.url;
            resBtn.href = data.url;
            resBtn.setAttribute("download", data.filename);

            showToast("9:16 Short created successfully!", "success");
        } catch (e) {
            showToast(e.message, "error");
        } finally {
            hideLoading();
        }
    });

    // --------------------------------------------------------
    // TAB 5: MEDIA LIBRARY
    // --------------------------------------------------------
    async function loadLibrary() {
        try {
            const res = await fetch("/api/library");
            const data = await res.json();

            const outputsGrid = document.getElementById("outputs-grid");
            const uploadsGrid = document.getElementById("uploads-grid");

            outputsGrid.innerHTML = "";
            uploadsGrid.innerHTML = "";

            if (data.outputs.length === 0) {
                outputsGrid.innerHTML = `<p class="subtext">No generated outputs yet.</p>`;
            } else {
                data.outputs.forEach(item => outputsGrid.appendChild(createMediaCard(item)));
            }

            if (data.uploads.length === 0) {
                uploadsGrid.innerHTML = `<p class="subtext">No cached/uploaded media yet.</p>`;
            } else {
                data.uploads.forEach(item => uploadsGrid.appendChild(createMediaCard(item)));
            }
        } catch (e) {
            console.error("Failed to load library", e);
        }
    }

    function createMediaCard(item) {
        const div = document.createElement("div");
        div.className = "media-item";

        const previewEl = item.is_video
            ? `<video src="${item.url}" controls class="media-thumb"></video>`
            : `<audio src="${item.url}" controls style="width: 100%; margin: 40px 0;"></audio>`;

        div.innerHTML = `
            ${previewEl}
            <div class="media-title" title="${item.name}">${item.name}</div>
            <div class="media-meta">
                <span>${item.size_mb} MB</span>
                <span>${item.created_at}</span>
            </div>
            <div class="media-actions">
                <a href="${item.url}" download="${item.name}" class="btn btn-sm btn-primary">⬇️ Download</a>
                <button class="btn btn-sm btn-danger btn-delete-media" data-folder="${item.folder}" data-name="${item.name}">🗑️</button>
            </div>
        `;

        div.querySelector(".btn-delete-media").addEventListener("click", async (e) => {
            const folder = e.currentTarget.dataset.folder;
            const name = e.currentTarget.dataset.name;
            if (confirm(`Delete ${name}?`)) {
                await fetch(`/api/library/${folder}/${name}`, { method: "DELETE" });
                loadLibrary();
                showToast("File deleted.", "info");
            }
        });

        return div;
    }

    document.getElementById("btn-refresh-library").addEventListener("click", loadLibrary);
});
