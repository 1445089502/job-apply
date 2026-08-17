/* job-apply 前端逻辑：fetch 调 REST 接口 */
const API = "/api";

function $(id) { return document.getElementById(id); }

async function req(path, options = {}) {
    const opts = Object.assign({ headers: { "Content-Type": "application/json" } }, options);
    const resp = await fetch(API + path, opts);
    if (!resp.ok) {
        let msg = "HTTP " + resp.status;
        try { const d = await resp.json(); msg = d.detail || msg; } catch (e) { /* ignore */ }
        throw new Error(msg);
    }
    return resp.json();
}

function showMsg(el, text, isError) {
    el.textContent = text;
    el.className = "msg" + (isError ? " error" : "");
}

// ---------- Tab 切换 ----------
document.querySelectorAll(".tab").forEach((btn) => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".tab").forEach((b) => b.classList.remove("active"));
        document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
        btn.classList.add("active");
        $(btn.dataset.tab).classList.add("active");
        if (btn.dataset.tab === "jobs") loadJobs();
        if (btn.dataset.tab === "applications") loadApplications();
        if (btn.dataset.tab === "report") loadStatistics();
    });
});

// ---------- 推荐 ----------
$("btnRecommend").addEventListener("click", async () => {
    const el = $("recList");
    el.innerHTML = "";
    const prefs = {};
    if ($("city").value) prefs.city = $("city").value;
    if ($("minSalary").value) prefs.min_salary = Number($("minSalary").value);
    if ($("language").value) prefs.language = $("language").value;
    try {
        const data = await req("/recommend", {
            method: "POST",
            body: JSON.stringify({
                resume: $("resume").value,
                preference: $("preference").value,
                prefs,
                top_k: 5,
            }),
        });
        if (!data.recommendations.length) {
            el.innerHTML = '<p style="color:#999">暂无推荐，可尝试放宽筛选条件</p>';
            return;
        }
        data.recommendations.forEach((r) => el.appendChild(renderRecCard(r)));
    } catch (err) {
        el.innerHTML = `<p class="msg error">推荐失败：${err.message}</p>`;
    }
});

function renderRecCard(r) {
    const div = document.createElement("div");
    div.className = "rec-card";
    div.innerHTML = `
        <div class="head">
            <span class="title">${r.title}</span>
            <span class="score">${r.score}</span>
        </div>
        <div class="meta">${r.company} ｜ ${r.city} ｜ ${r.salary}</div>
        <div class="reasons">理由：${(r.reasons || []).join("；") || "-"}</div>
        <div class="jd">${r.jd || ""}</div>
        <div class="actions">
            <button data-act="collect">收藏</button>
            <button data-act="apply">投递</button>
            <button data-act="dislike" style="background:#ff4d4f">不感兴趣</button>
        </div>`;
    div.querySelectorAll("button[data-act]").forEach((btn) => {
        btn.addEventListener("click", async () => {
            try {
                await req("/feedback", {
                    method: "POST",
                    body: JSON.stringify({ job_id: r.job_id, action: btn.dataset.act }),
                });
                if (btn.dataset.act === "apply") {
                    await req("/applications", {
                        method: "POST",
                        body: JSON.stringify({ job_id: r.job_id, status: "CREATED" }),
                    });
                }
                btn.textContent = "✓";
                btn.disabled = true;
            } catch (err) {
                alert("操作失败：" + err.message);
            }
        });
    });
    return div;
}

// ---------- 岗位 ----------
async function loadJobs() {
    const data = await req("/jobs");
    const tbody = $("jobTable").querySelector("tbody");
    tbody.innerHTML = "";
    data.jobs.forEach((j) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${j.platform}</td><td>${j.title}</td><td>-</td><td>${j.city}</td><td>${j.salary}</td>`;
        tbody.appendChild(tr);
    });
}
$("btnLoadJobs").addEventListener("click", loadJobs);

// ---------- 投递 ----------
async function loadApplications() {
    const data = await req("/applications");
    const tbody = $("appTable").querySelector("tbody");
    tbody.innerHTML = "";
    data.applications.forEach((a) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td>${a.id}</td><td>${a.job_id}</td><td>${a.status}</td><td>${a.created_at}</td>`;
        tbody.appendChild(tr);
    });
}
$("btnLoadApps").addEventListener("click", loadApplications);
$("btnRecordApp").addEventListener("click", async () => {
    try {
        await req("/applications", {
            method: "POST",
            body: JSON.stringify({ job_id: Number($("appJobId").value), status: "CREATED" }),
        });
        loadApplications();
    } catch (err) { alert(err.message); }
});

// ---------- 报表 ----------
async function loadStatistics() {
    const data = await req("/statistics");
    const cards = $("statsCards");
    cards.innerHTML = `
        <div class="card"><div class="num">${data.total_jobs}</div><div class="lbl">岗位总数</div></div>
        <div class="card"><div class="num">${data.funnel.viewed}</div><div class="lbl">浏览/收藏</div></div>
        <div class="card"><div class="num">${data.funnel.applied}</div><div class="lbl">已投递</div></div>`;
    const chart = echarts.init($("funnelChart"));
    chart.setOption({
        title: { text: "投递漏斗", left: "center", textStyle: { fontSize: 14 } },
        tooltip: { trigger: "item" },
        series: [{
            type: "funnel",
            left: "15%", width: "70%",
            label: { show: true, formatter: "{b}: {c}" },
            data: [
                { value: data.funnel.viewed, name: "浏览/收藏" },
                { value: data.funnel.applied, name: "已投递" },
            ],
        }],
    });
}
$("btnLoadStats").addEventListener("click", loadStatistics);

// 初始化
loadStatistics();
