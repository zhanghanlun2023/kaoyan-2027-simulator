const NAV = [
  ["home","备考总览"],["universities","院校与学习方式"],["quiz","智能组卷"],
  ["papers","五年真题索引"],["syllabus","2027考纲雷达"],["about","项目说明"]
];
const state = {page:"home", mode:"全日制", track:"普通硕士", university:"", subject:"思想政治理论", data:{}, paper:[], paperVersion:0, paperCode:"", submitted:false};
const $ = (q, root=document) => root.querySelector(q);
const esc = value => String(value ?? "").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const tag = u => u?.is_985 ? "原985 / 原211" : "原211";

async function boot(){
  const [coreQuestions,managementQuestions,english2,syllabus,papers,universities] = await Promise.all([
    "data/questions.json","data/questions_199.json","data/english2_bank.json","data/syllabus.json","data/past_papers.json","data/universities.json"
  ].map(url=>fetch(url).then(r=>{if(!r.ok) throw new Error(url); return r.json()})));
  state.data={questions:[...coreQuestions,...managementQuestions],english2,syllabus,papers,universities};
  restore(); setupChrome(); route();
  $("#loading").hidden=true; $("#app").hidden=false;
}
function restore(){
  try{const saved=JSON.parse(localStorage.getItem("yantu-pref")||"{}"); Object.assign(state,{mode:saved.mode||state.mode,track:saved.track||state.track,university:saved.university||"",subject:saved.subject||state.subject});}catch{}
}
function save(){localStorage.setItem("yantu-pref",JSON.stringify({mode:state.mode,track:state.track,university:state.university,subject:state.subject}));}
function allowedSubjects(){const all=state.data.syllabus.subjects.map(s=>s.name);return state.track==="MBA 工商管理"?["管理类综合能力","英语二"]:all.filter(s=>s!=="管理类综合能力");}
function subjectCount(subject){return subject==="英语二"?state.data.english2.questions.length:state.data.questions.filter(q=>q.subject===subject).length;}
function totalCount(){return state.data.questions.length+state.data.english2.questions.length;}
function refreshSubjects(){const subjects=allowedSubjects();if(!subjects.includes(state.subject))state.subject=subjects[0];$("#subject-select").innerHTML=subjects.map(s=>`<option>${esc(s)}</option>`).join("");$("#subject-select").value=state.subject;}
function setupChrome(){
  $("#nav").innerHTML=NAV.map(([id,label],i)=>`<button data-page="${id}"><span class="num">0${i+1}</span>${label}</button>`).join("");
  $("#nav").onclick=e=>{const b=e.target.closest("button[data-page]");if(b){state.page=b.dataset.page;location.hash=b.dataset.page;render();}};
  const unis=state.data.universities.universities;
  $("#university-select").innerHTML=`<option value="">暂未确定</option>`+unis.map(u=>`<option>${esc(u.name)}</option>`).join("");
  $("#university-select").value=state.university;
  $("#university-select").onchange=e=>{state.university=e.target.value;save();render();};
  $("#track-select").value=state.track;
  $("#track-select").onchange=e=>{state.track=e.target.value;if(state.track==="MBA 工商管理"){state.mode="非全日制";state.subject="管理类综合能力";}else if(state.subject==="管理类综合能力")state.subject="思想政治理论";state.paper=[];refreshSubjects();save();render();};
  refreshSubjects();
  $("#subject-select").onchange=e=>{state.subject=e.target.value;state.paper=[];save();render();};
  $("#mode-switch").onclick=e=>{const b=e.target.closest("button[data-mode]");if(b){state.mode=b.dataset.mode;save();render();}};
}
function route(){const page=location.hash.slice(1); if(NAV.some(n=>n[0]===page))state.page=page; window.onhashchange=()=>{state.page=location.hash.slice(1)||"home";render();};}
function chrome(){
  document.querySelectorAll("#nav button").forEach(b=>b.classList.toggle("active",b.dataset.page===state.page));
  document.querySelectorAll("#mode-switch button").forEach(b=>b.classList.toggle("active",b.dataset.mode===state.mode));
  $("#track-select").value=state.track; $("#university-select").value=state.university; $("#subject-select").value=state.subject;
}
function university(){return state.data.universities.universities.find(u=>u.name===state.university);}
function title(h,sub){return `<h2>${h}</h2><p class="subtitle">${sub}</p>`;}
function render(){chrome(); const view={home,universities,quiz,papers,syllabus,about}[state.page]||home; $("#main").innerHTML=view(); bind(); $("#main").focus({preventScroll:true});}
function bind(){
  $("#generate")?.addEventListener("click",generatePaper);
  $("#submit")?.addEventListener("click",scorePaper);
  $("#tier")?.addEventListener("change",renderUniversityRows); $("#province")?.addEventListener("change",renderUniversityRows); $("#uni-search")?.addEventListener("input",renderUniversityRows);
}
function home(){
  const u=university(), tip=state.mode==="全日制"?"整段复习优先：按正式考试时长训练":"在职节奏：工作日小测 + 周末整卷", mba=state.track==="MBA 工商管理";
  return `<section class="hero"><div class="eyebrow">Postgraduate Entrance Exam · 2027</div><h1>把每一次练习，<br>变成可解释的进步。</h1><p>以五年真题结构为参照、以公开考纲为边界的原创仿真训练。先测能力，再定位章节，最后回到可执行的复习动作。</p></section>
  <div class="metrics"><div class="metric"><span>覆盖统考科目</span><b>${state.data.syllabus.subjects.length} 门</b></div><div class="metric"><span>原创训练题</span><b>${totalCount()} 道</b></div><div class="metric"><span>MBA关联题量</span><b>${subjectCount("管理类综合能力")+subjectCount("英语二")} 道</b></div><div class="metric"><span>院校招生单位/校区</span><b>116 个</b></div></div>
  <div class="notice"><b>${state.mode} · ${state.track} · ${esc(u?.name||"尚未确定目标院校")}</b><br><span class="muted">${tip}。${mba?"MBA初试重点为199管理类综合能力与204英语（二），复试通常另考思想政治理论和综合素质。":"全国统考科目使用同一题库；院校差异主要在专业目录、自命题、复试和培养安排。"}</span></div>
  <h3>今天从哪里开始</h3><div class="grid3"><div class="card"><span class="pill">01</span><h4>先看边界</h4><div class="muted">区分官方信息、沿用基线和院校自命题调整。</div></div><div class="card"><span class="pill">02</span><h4>再做诊断</h4><div class="muted">从“${esc(state.subject)}”抽取一组原创仿真题。</div></div><div class="card"><span class="pill">03</span><h4>最后复盘</h4><div class="muted">按章节准确率定位薄弱点，而不是只看总分。</div></div></div>`;
}
function universities(){
  const provinces=[...new Set(state.data.universities.universities.map(u=>u.province))].sort(); const u=university();
  return `${title("院校与学习方式","先确定招生路径，再决定练什么；统考共用，自命题与复试按学校核对。")}
  <div class="notice info">${state.track==="MBA 工商管理"?"MBA是工商管理专业学位，不等同于学习方式；本页默认按常见的非全日制在职路径展示。按2026管理规定基线：本科毕业后3年以上、高职高专或本科结业后5年以上、硕博毕业后2年以上工作经验；2027须以正式规定和院校简章复核。":state.mode==="非全日制"?"非全日制常被口语称为“在职研究生”。全日制和非全日制执行相同考试招生政策和标准；原则上非全日制硕士招收在职定向就业人员。":"全日制通常为全脱产在校学习。考试科目、学制、学费、住宿和培养校区仍需逐校逐专业核对。"}</div>
  <div class="toolbar"><div class="field"><label>历史工程标签</label><select id="tier"><option>全部原985/211</option><option>原985</option><option>原211（非985）</option></select></div><div class="field"><label>地区</label><select id="province"><option>全部地区</option>${provinces.map(p=>`<option>${p}</option>`).join("")}</select></div><div class="field"><label>搜索院校</label><input id="uni-search" placeholder="输入学校、城市或省份"></div></div>
  <div id="uni-table"></div>${u?`<div class="panel"><span class="pill">当前目标</span><h3>${esc(u.name)}</h3><div class="metrics"><div class="metric"><span>历史标签</span><b>${tag(u)}</b></div><div class="metric"><span>学习方式</span><b>${state.mode}</b></div><div class="metric"><span>统考题库</span><b>全国共用</b></div><div class="metric"><span>所在地区</span><b>${u.province}</b></div></div><p class="muted">必须核对：2027招生简章、专业目录、学习方式、自命题科目、定向要求、学制学费、授课地点与复试科目。</p><a class="link-btn" target="_blank" rel="noopener" href="https://yz.chsi.com.cn/sch/">前往研招网院校库</a></div>`:`<div class="notice">请在左侧选择目标院校。未确定院校时仍可正常练习全国统考题。</div>`}`;
}
function renderUniversityRows(){
  const tier=$("#tier")?.value||"全部原985/211",province=$("#province")?.value||"全部地区",key=$("#uni-search")?.value.trim().toLowerCase()||"";
  let rows=state.data.universities.universities.filter(u=>(tier==="全部原985/211"||(tier==="原985"?u.is_985:!u.is_985))&&(province==="全部地区"||u.province===province)&&(!key||`${u.name}${u.province}${u.city}`.toLowerCase().includes(key)));
  $("#uni-table").innerHTML=`<p class="muted">找到 ${rows.length} 个招生单位/校区；历史官方口径为112所原211，其中39所原985。</p><div class="table-wrap"><table><thead><tr><th>院校</th><th>地区</th><th>原985</th><th>原211</th></tr></thead><tbody>${rows.map(u=>`<tr><td>${esc(u.name)}</td><td>${u.province} · ${u.city}</td><td>${u.is_985?"是":"—"}</td><td>是</td></tr>`).join("")}</tbody></table></div>`;
}
function seededShuffle(items,seed){let n=0;for(const c of seed)n=(n*31+c.charCodeAt(0))>>>0;const a=[...items];for(let i=a.length-1;i>0;i--){n=(1664525*n+1013904223)>>>0;const j=n%(i+1);[a[i],a[j]]=[a[j],a[i]];}return a;}
function buildEnglish2Paper(seed){const bank=state.data.english2.questions,plan=[["英语知识运用（完形填空）",1],["阅读理解A",4],["阅读理解B（新题型）",1],["英译汉",1],["应用文写作",1],["图表/情境作文",1]],paper=[];for(const [section,count] of plan){const rows=bank.filter(q=>q.section===section),setIds=[...new Set(rows.map(q=>q.set_id))],chosen=seededShuffle(setIds,seed+section).slice(0,count);for(const setId of chosen)paper.push(...rows.filter(q=>q.set_id===setId).sort((a,b)=>a.order-b.order));}return paper;}
function buildManagementPaper(seed){const bank=state.data.questions.filter(q=>q.subject==="管理类综合能力"),plan=[["数学基础·问题求解",15],["数学基础·条件充分性判断",10],["逻辑推理",30],["写作·论证有效性分析",1],["写作·论说文",1]],paper=[];for(const [chapter,count] of plan)paper.push(...seededShuffle(bank.filter(q=>q.chapter===chapter),seed+chapter).slice(0,count));return paper;}
function paperSignature(paper){return paper.map(q=>q.set_id||q.id).join("|");}
function setFreshPaper(builder){const before=paperSignature(state.paper);let next=[],seed="";for(let attempt=0;attempt<20;attempt++){seed=`${Date.now()}-${++state.paperVersion}-${attempt}`;next=builder(seed);if(paperSignature(next)!==before)break;}state.paper=next;let n=0;for(const c of seed)n=(n*31+c.charCodeAt(0))>>>0;state.paperCode=String(n%1000000).padStart(6,"0");}
function englishQuestionListHTML(){const groups=[];for(const [index,q] of state.paper.entries()){let group=groups.at(-1);if(!group||group.id!==q.set_id){group={id:q.set_id,section:q.section,passage:q.passage_id?state.data.english2.passages[q.passage_id]:q.section==="英译汉"?q.stem:"",items:[]};groups.push(group);}group.items.push({q,index});}return groups.map(group=>{const questions=group.items.map(({q,index})=>questionHTML(group.section==="英译汉"?{...q,stem:"请将左侧英文材料完整翻译成中文。"}:q,index)).join("");if(!group.passage)return `<section class="set-heading"><span class="pill">${esc(group.section)}</span></section>${questions}`;return `<section class="english-workspace" data-set="${esc(group.id)}"><aside class="english-passage"><div class="passage-toolbar"><span class="pill">${esc(group.section)}</span><span>文章固定区</span></div><div class="passage">${esc(group.passage)}</div></aside><div class="english-questions"><div class="set-heading"><span class="pill">${esc(group.section)}</span><span class="muted">完成本题组后继续下一篇</span></div>${questions}</div></section>`;}).join("");}
function questionListHTML(){if(state.subject==="英语二")return englishQuestionListHTML();let previous="";return state.paper.map((q,i)=>{let heading="",group=state.subject==="管理类综合能力"?q.chapter:"";if(group&&group!==previous){previous=group;heading=`<section class="set-heading"><span class="pill">${esc(q.chapter)}</span></section>`;}return heading+questionHTML(q,i);}).join("");}
function quiz(){
  const isEnglish2=state.subject==="英语二",isManagement=state.subject==="管理类综合能力",pool=isEnglish2?state.data.english2.questions:state.data.questions.filter(q=>q.subject===state.subject),u=university();
  if(!state.paper.length)setFreshPaper(isEnglish2?buildEnglish2Paper:isManagement?buildManagementPaper:seed=>seededShuffle(pool,seed).slice(0,Math.min(12,pool.length)));
  const structure=isEnglish2?'<div class="notice info"><b>204英语（二）完整结构</b>：完形20题10分；阅读A 20题40分；阅读B 5题10分；翻译15分；应用文10分；图表/情境作文15分。</div>':isManagement?'<div class="notice info"><b>199管理类综合能力完整结构</b>：问题求解15题45分；条件充分性判断10题30分；逻辑推理30题60分；论证有效性分析30分；论说文35分，共57个作答项、200分。</div>':state.mode==="非全日制"?'<div class="notice info">在职训练建议：工作日做5—8题限时小测，周末再完成整卷。</div>':"";
  const fullPaper=isEnglish2||isManagement;
  return `${title("智能组卷",isEnglish2?"英语二按完整语篇与题组生成100分仿真卷。":isManagement?"管理类综合能力按199正式结构生成200分完整卷。":"按真实科目代码和客观题分值训练；写作题提供自评提示，不冒充机器阅卷。")}${u?`<p class="muted">目标：${esc(u.name)} · ${state.mode} · ${state.track} · ${state.subject}</p>`:""}${structure}<p class="muted">当前科目题库：${pool.length} 道${fullPaper?` · 本卷 ${state.paper.length} 个作答项 · 试卷编号 ${state.paperCode}`:""}</p><button id="generate" class="secondary">${fullPaper?"换一套完整卷":"换一套题"}</button><div id="question-list">${questionListHTML()}</div><button id="submit" class="primary">交卷并生成诊断</button><div id="score-box"></div>`;
}
function questionHTML(q,i){if(q.type==="essay")return `<article class="question" data-q="${q.id}"><div class="q-meta">第 ${i+1} 题 · ${esc(q.chapter)} · ${q.points}分 · ${esc(q.format_tag||"人工自评")}</div><h4>${esc(q.stem)}</h4><textarea class="essay-input" name="q_${q.id}" rows="9" placeholder="在这里完成主观题作答；提交后显示自评要点"></textarea><div class="answer" hidden></div></article>`;const multiple=q.type==="multiple",type=multiple?"checkbox":"radio";return `<article class="question" data-q="${q.id}"><div class="q-meta">第 ${i+1} 题 · ${esc(q.chapter)} · ${q.points}分 · ${esc(q.format_tag||"专项训练")} · 难度 ${"●".repeat(q.difficulty)}${"○".repeat(5-q.difficulty)}</div><h4>${esc(q.stem)}</h4>${Object.entries(q.options).map(([k,v])=>`<label class="option"><input type="${type}" name="q_${q.id}" value="${k}"><span><b>${k}.</b> ${esc(v)}</span></label>`).join("")}<div class="answer" hidden></div></article>`;}
function generatePaper(){const pool=state.data.questions.filter(q=>q.subject===state.subject);setFreshPaper(state.subject==="英语二"?buildEnglish2Paper:state.subject==="管理类综合能力"?buildManagementPaper:seed=>seededShuffle(pool,seed).slice(0,Math.min(12,pool.length)));state.submitted=false;render();}
function scorePaper(){let earned=0,total=0,correct=0,graded=0,essays=0;state.paper.forEach(q=>{const box=document.querySelector(`[data-q="${q.id}"] .answer`);box.hidden=false;if(q.type==="essay"){essays++;box.innerHTML=`<b>📝 自评要点</b><br>${esc(q.explanation)}<br><span class="muted">本题${q.points}分，需由教师或同伴依据结构、论证和语言人工评阅。</span>`;return;}total+=q.points;graded++;const picked=[...document.querySelectorAll(`input[name="q_${q.id}"]:checked`)].map(x=>x.value).sort();const expected=(Array.isArray(q.answer)?q.answer:[q.answer]).slice().sort();const ok=JSON.stringify(picked)===JSON.stringify(expected);if(ok){earned+=q.points;correct++;}box.parentElement.classList.add(ok?"correct":"incorrect");box.innerHTML=`<b>${ok?"✅ 回答正确":"❌ 需要复盘"}</b><br>正确答案：${expected.join("、")}<br>${esc(q.explanation)}`;});const accuracy=graded?correct/graded:0;$("#score-box").innerHTML=`<div class="result ${accuracy>=.8?"ok":"bad"}"><b>客观题得分 ${earned} / ${total}</b>　正确率 ${graded?Math.round(accuracy*100):0}%${essays?`<br>另有 ${essays} 道主观题待人工自评。`:""}<br><span class="muted">${accuracy>=.8?"客观题基础掌握较好，可以提高难度。":"建议逐题查看解析并回到对应章节复习。"}</span></div>`;$("#score-box").scrollIntoView({behavior:"smooth"});}
function papers(){const p=state.data.papers;return `${title("2022—2026 五年真题索引","记录结构、年份、复盘方法和合法获取路径，不转载未经授权的整套试卷。")}<div class="notice">${esc(p.copyright_note)}</div><div class="table-wrap"><table><thead><tr><th>年度</th><th>考试时间</th><th>状态</th><th>复盘重点</th></tr></thead><tbody>${p.years.map(y=>`<tr><td>${y.year}</td><td>${esc(y.exam_date)}</td><td>${y.status}</td><td>${esc(y.focus)}</td></tr>`).join("")}</tbody></table></div><h3>推荐复盘流程</h3><div class="grid3">${p.workflow.map((w,i)=>`<div class="card"><span class="pill">0${i+1}</span><p>${esc(w)}</p></div>`).join("")}</div>`;}
function syllabus(){const s=state.data.syllabus;return `${title("2027 考纲雷达","正式文件发布前，清楚地区分官方信息和复习基线。")}<div class="notice">截至 ${s.status.as_of}：${esc(s.status.message)}</div><div class="grid3">${s.subjects.map(x=>`<div class="card"><span class="pill">${x.code}</span><h4>${x.name}</h4><div class="muted">${x.score}分 · ${x.minutes}分钟</div><p>${x.sections.join(" · ")}</p><div class="muted">${esc(x.note)}</div></div>`).join("")}</div><h3>官方核验入口</h3><ul class="source-list">${s.sources.map(x=>`<li><a href="${x.url}" target="_blank" rel="noopener">${esc(x.title)}</a> — ${esc(x.role)}</li>`).join("")}</ul>`;}
function about(){return `${title("项目说明","公开、可追溯、可继续扩充的考研训练底座。")}<div class="panel"><h3>数据原则</h3><ul><li>训练题均为原创仿真，不冒充历年真题。</li><li>英语二按完整文章与题组组织：完形、阅读A、阅读B、翻译和两类写作，不使用孤立语法题冒充套卷。</li><li>客观题按对应科目的单题分值标注；主观题不做虚假的机器自动评分。</li><li>MBA是专业学位路径，不等同于非全日制；本系统支持常见的在职非全日制MBA训练配置。</li></ul><h3>当前边界</h3><p class="muted">当前覆盖${state.data.syllabus.subjects.length}门统考科目、${totalCount()}道原创训练题，其中MBA关联${subjectCount("管理类综合能力")+subjectCount("英语二")}道；另含116个原985/211招生单位或校区。</p><a class="link-btn" target="_blank" rel="noopener" href="https://github.com/zhanghanlun2023/kaoyan-2027-simulator">查看 GitHub 源码</a></div>`;}

boot().then(()=>{render();if(state.page==="universities")renderUniversityRows();}).catch(err=>{$("#loading").textContent="题库加载失败，请刷新页面。";console.error(err)});
const originalRender=render;render=function(){originalRender();if(state.page==="universities")renderUniversityRows();};


