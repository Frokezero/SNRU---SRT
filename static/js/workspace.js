'use strict';
const content = document.getElementById('content');
const notice = document.getElementById('notice');
const h = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const statusName = s => ({pending:'รอตรวจ',approved:'อนุมัติ',rejected:'ไม่อนุมัติ',failed:'ส่งไม่สำเร็จ',processing:'กำลังส่ง',completed:'ส่งแล้ว'}[s] || s);
async function api(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json();
    if (!response.ok) throw new Error(data.message || `ไม่สำเร็จ (${response.status}) กรุณาลองใหม่`);
    return data;
}
async function busy(button, action) {
    if (button.disabled) return;
    button.disabled = true;
    try { await action(); } catch (error) { notice.textContent = error.message; }
    finally { button.disabled = false; }
}
function jsonOptions(method, data) { return {method, headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)}; }
async function load() {
    content.setAttribute('aria-busy', 'true');
    try {
        const data = await api('/api/workspace');
        if (data.role === 'student') {
            content.innerHTML = `<section><h2>ความคืบหน้าของฉัน</h2><div class="scores"><div>คะแนนที่ได้รับ<strong>${h(data.approved_score)}</strong></div><div>คะแนนรออนุมัติ<strong>${h(data.pending_score)}</strong></div></div><p>คะแนนรออนุมัติยังไม่รวมในคะแนนที่ได้รับ เป้าหมายการจบให้ยึดเกณฑ์ของหลักสูตร</p><a href="/api/my/calendar.ics">ดาวน์โหลดปฏิทินการจอง (.ics)</a><label><input id="reminders" type="checkbox" ${data.reminders ? 'checked' : ''}> เตือนในระบบก่อนกิจกรรมหนึ่งวัน</label><button id="save-preferences">บันทึกการแจ้งเตือน</button></section><section><h2>หลักฐานและประวัติการตรวจ</h2>${data.participations.length ? data.participations.map(p => `<article><h3>${h(p.event_title)}</h3><p>${h(statusName(p.status))} · ${h(p.score)} คะแนน</p>${p.status==='rejected' ? '<a href="/profile">แก้ไขและส่งหลักฐานใหม่</a>' : ''}<details><summary>ประวัติการแก้ไข (${p.history.length})</summary>${p.history.map(r=>`<p>${h(r.created_at)} · ${h(statusName(r.old_status))} → ${h(statusName(r.new_status))}<br>เหตุผล: ${h(r.reason || 'ไม่ได้ระบุ')}<br>คะแนน ${h(r.old_score)} → ${h(r.new_score)}</p>`).join('') || '<p>ไม่มีประวัติการเปลี่ยนแปลงหลังเริ่มใช้ระบบประวัติ</p>'}</details></article>`).join('') : '<p>ยังไม่มีหลักฐานกิจกรรม <a href="/">ดูกิจกรรมที่เปิดรับ</a></p>'}</section>`;
            document.getElementById('save-preferences').onclick = event => busy(event.target, async () => {
                await api('/api/my/notification-preferences', jsonOptions('PUT', {reminders:document.getElementById('reminders').checked}));
                notice.textContent = 'บันทึกการตั้งค่าแล้ว';
            });
        } else {
            document.getElementById('admin-link').hidden = false;
            content.innerHTML = `<section><h2>หลักฐานรอตรวจ (${data.pending.length}${data.pending.length===200?'+':''})</h2><label>ค้นหาชื่อหรือกิจกรรม <input id="search" type="search"></label><label>เหตุผลเมื่อไม่อนุมัติ <input id="reason" maxlength="1000" placeholder="ระบุสิ่งที่นักศึกษาต้องแก้ไข"></label><div class="actions"><button id="approve">อนุมัติรายการที่เลือก</button><button id="reject">ไม่อนุมัติรายการที่เลือก</button></div><div id="batch-result" role="status"></div><div class="scroll"><table><thead><tr><th>เลือก</th><th>นักศึกษา</th><th>กิจกรรม</th><th>หลักฐาน</th></tr></thead><tbody>${data.pending.map(p=>`<tr data-search="${h((p.student_name+' '+p.event_title).toLowerCase())}"><td><input aria-label="เลือก ${h(p.student_name)}" type="checkbox" value="${h(p.id)}"></td><td>${h(p.student_name)}</td><td>${h(p.event_title)}</td><td>${p.image_url && p.image_url.startsWith('/uploads/') ? `<a href="${h(p.image_url)}" target="_blank" rel="noopener">ดูหลักฐาน</a>` : 'ไม่มีรูปหลักฐาน'}</td></tr>`).join('') || '<tr><td colspan="4">ไม่มีรายการรอตรวจ</td></tr>'}</tbody></table></div></section><section><h2>ส่งออกรายงาน</h2><form action="/api/admin/reports/activity.csv"><label>รหัสกิจกรรม <input name="event_id"></label><label>สาขา <input name="major"></label><p>เลือกช่วงวันที่เริ่มและสิ้นสุดภาคเรียนตามปฏิทินของมหาวิทยาลัย</p><label>ตั้งแต่ <input type="date" name="start"></label><label>ถึง <input type="date" name="end"></label><button>ดาวน์โหลด CSV</button></form></section>${data.role==='admin' ? '<section><h2>ติดตามการส่งแจ้งเตือน</h2><button id="load-jobs">โหลดงานแจ้งเตือน</button><div id="jobs"></div></section><section><h2>สำรองและทดสอบกู้คืน</h2><p>ไฟล์สำรองมีข้อมูลส่วนบุคคล ควรเก็บในพื้นที่จำกัดสิทธิ์</p><a href="/api/admin/backup-db">ดาวน์โหลดฐานข้อมูลพร้อมไฟล์อัปโหลด</a><label>ไฟล์สำรองสำหรับตรวจสอบ <input type="file" id="backup" accept=".zip"></label><button id="verify-backup">ทดสอบไฟล์สำรอง (ไม่เปลี่ยนข้อมูลจริง)</button></section><section><h2>ประวัติผู้ดูแล</h2><button id="load-audit">โหลดประวัติ</button><div id="audit"></div></section>' : ''}`;
            document.getElementById('search').oninput = event => {
                document.querySelectorAll('tr[data-search]').forEach(row => { row.hidden = !row.dataset.search.includes(event.target.value.toLowerCase()); if(row.hidden) row.querySelector('input').checked=false; });
            };
            for (const [buttonId,status] of [['approve','approved'],['reject','rejected']]) {
                document.getElementById(buttonId).onclick = event => busy(event.target, async () => {
                    const ids = [...content.querySelectorAll('td input:checked')].map(el=>el.value);
                    const reason = document.getElementById('reason').value.trim();
                    if (!ids.length) throw new Error('กรุณาเลือกรายการก่อน');
                    if(status==='rejected' && !reason) throw new Error('กรุณาระบุเหตุผลที่ไม่อนุมัติ');
                    if (!confirm(`ยืนยัน${statusName(status)} ${ids.length} รายการ?`)) return;
                    document.getElementById('approve').disabled = true;
                    document.getElementById('reject').disabled = true;
                    const results=[];
                    for (const id of ids) {
                        try { await api('/api/admin/participations/'+encodeURIComponent(id), jsonOptions('PUT',{status,reason})); results.push(`${id}: สำเร็จ`); }
                        catch(error) { results.push(`${id}: ${error.message}`); }
                    }
                    await load();
                    document.getElementById('batch-result').textContent = results.join(' | ');
                });
            }
            if(data.role==='admin') setupAdmin();
        }
    } catch(error) { content.textContent = error.message + ' — หากยังไม่ได้เข้าสู่ระบบ กรุณาเปิดหน้าเข้าสู่ระบบ'; }
    finally { content.setAttribute('aria-busy','false'); }
}
function setupAdmin() {
    document.getElementById('load-jobs').onclick = event => busy(event.target, async()=>{
        const data = await api('/api/admin/outbox');
        const readiness = await api('/api/admin/service-readiness');
        const jobs=document.getElementById('jobs');
        jobs.innerHTML=data.jobs.map(j=>`<article>#${h(j.id)} · ${h(j.job_type)} · ${h(statusName(j.status))} · ลอง ${h(j.attempts)} ครั้ง<p>${h(j.error)}</p>${j.status==='failed'?`<button data-retry="${h(j.id)}">ลองส่งใหม่</button>`:''}</article>`).join('') || '<p>ไม่มีงานแจ้งเตือน</p>';
        jobs.insertAdjacentHTML('afterbegin', `<p>ตั้งค่า worker: ${readiness.worker_enabled?'เปิด':'ปิด'} · AI: ${readiness.ai_enabled?'เปิด':'ปิด'}<br>${h(readiness.message)}</p>`);
        jobs.querySelectorAll('[data-retry]').forEach(button=>button.onclick=()=>busy(button,async()=>{
            if(!confirm('ลองส่งงานนี้ใหม่? หากผู้รับเคยได้รับแล้วอาจได้รับซ้ำ')) return;
            await api(`/api/admin/outbox/${button.dataset.retry}/retry`,{method:'POST'});
            button.remove(); notice.textContent='นำงานกลับเข้าคิวแล้ว';
        }));
    });
    document.getElementById('verify-backup').onclick = event=>busy(event.target,async()=>{
        const file=document.getElementById('backup').files[0];
        if(!file) throw new Error('กรุณาเลือกไฟล์สำรอง');
        const form=new FormData();form.append('file',file);
        const result=await api('/api/admin/backup/verify',{method:'POST',body:form});
        notice.textContent=result.message;
    });
    document.getElementById('load-audit').onclick = event=>busy(event.target,async()=>{
        const data=await api('/api/admin/audit-logs?limit=100');
        document.getElementById('audit').innerHTML=data.logs.map(r=>`<details><summary>${h(r.created_at)} · ${h(r.username)} · ${h(r.action)} ${h(r.resource)} · ${h(r.status_code)}</summary><p>${h(r.details_json)}</p></details>`).join('') || '<p>ยังไม่มีรายการ</p>';
    });
}
document.getElementById('refresh').onclick = event => busy(event.target, load);
load();
