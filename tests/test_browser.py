"""Real Chromium tests against an isolated database, never the running port 5000."""
import io
import os
import threading

import pytest
from PIL import Image
from werkzeug.serving import make_server
from test_api import client, login_as
import app as app_module
import database

pytestmark = pytest.mark.skipif(os.environ.get('RUN_BROWSER_TESTS') != '1', reason='Set RUN_BROWSER_TESTS=1 and install Chromium')


@pytest.mark.parametrize('width', [390, 1366])
def test_workspace_browser_journey(client, monkeypatch, tmp_path, width):
    from playwright.sync_api import sync_playwright, expect
    monkeypatch.setattr(app_module, 'ACTIVITIES_UPLOAD_FOLDER', str(tmp_path))
    monkeypatch.setenv('ENABLE_AI_ASSISTANT','false')
    from collections import defaultdict, deque
    monkeypatch.setattr(app_module, '_rate_limit_hits', defaultdict(deque))
    monkeypatch.setattr(app_module, 'load_carousel', lambda: [])
    server=make_server('127.0.0.1',0,app_module.app,threaded=True)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    try:
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch()
            context=browser.new_context(viewport={'width':width,'height':900})
            page=context.new_page()
            errors=[]
            page.on('pageerror', lambda error: errors.append(error.stack))
            # Real HTTP login and booking; all users belong to the fixture database.
            response=context.request.post(base+'/api/login',data={'username':'65001','password':'password'})
            assert response.ok, response.text()
            response=context.request.post(base+'/api/events/event-cap/register',data={})
            assert response.ok, response.text()
            picture=io.BytesIO()
            Image.new('RGB',(20,20),'blue').save(picture,format='PNG')
            response=context.request.post(base+'/api/student/participate',multipart={
                'event_id':'event-cap','file':{'name':'proof.png','mimeType':'image/png','buffer':picture.getvalue()}})
            assert response.ok, response.text()
            page.goto(base+'/workspace')
            expect(page.get_by_role('heading',name='ความคืบหน้าของฉัน')).to_be_visible()
            from pathlib import Path
            artifacts=Path('.test-artifacts')
            artifacts.mkdir(exist_ok=True)
            page.screenshot(path=str(artifacts/f'workspace-student-{width}.png'),full_page=True)
            page.locator('#reminders').uncheck()
            page.get_by_role('button',name='บันทึกการแจ้งเตือน').click()
            expect(page.locator('#notice')).to_have_text('บันทึกการตั้งค่าแล้ว')
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            # Admin rejects in the actual interface, then student resubmits.
            context.request.post(base+'/api/login',data={'username':'admin','password':'password'})
            page.reload()
            expect(page.locator('td input[type=checkbox]')).to_have_count(1)
            page.screenshot(path=str(artifacts/f'workspace-admin-{width}.png'),full_page=True)
            page.locator('td input').check()
            page.locator('#reason').fill('กรุณาส่งภาพให้ชัดเจน')
            page.on('dialog',lambda dialog:dialog.accept())
            page.locator('#reject').click()
            expect(page.locator('#batch-result')).to_contain_text('สำเร็จ')
            context.request.post(base+'/api/login',data={'username':'65001','password':'password'})
            page.reload()
            page.get_by_text('ประวัติการแก้ไข',exact=False).click()
            expect(page.get_by_text('เหตุผล: กรุณาส่งภาพให้ชัดเจน',exact=False)).to_be_visible()
            response=context.request.post(base+'/api/student/participate',multipart={
                'event_id':'event-cap','file':{'name':'proof.png','mimeType':'image/png','buffer':picture.getvalue()}})
            assert response.ok, response.text()
            context.request.post(base+'/api/login',data={'username':'admin','password':'password'})
            page.reload()
            page.locator('td input').check()
            page.locator('#approve').click()
            expect(page.locator('#batch-result')).to_contain_text('สำเร็จ')
            context.request.post(base+'/api/login',data={'username':'65001','password':'password'})
            page.reload()
            expect(page.locator('.scores strong').first).to_have_text('5')
            conn=database.get_db_connection()
            part=conn.execute("SELECT id FROM participations WHERE username='65001'").fetchone()[0]
            conn.close()
            page.goto(base+'/certificate?id='+part)
            expect(page.locator('#cert-verify')).to_have_attribute('href', __import__('re').compile('/verify-certificate/'))
            page.wait_for_function("document.getElementById('cert-qr').complete && document.getElementById('cert-qr').naturalWidth > 0")
            assert page.locator('.cert-footer').bounding_box()['y'] + page.locator('.cert-footer').bounding_box()['height'] < page.locator('.certificate-container').bounding_box()['y'] + page.locator('.certificate-container').bounding_box()['height']
            page.screenshot(path=str(artifacts/f'certificate-{width}.png'),full_page=True)
            for path in ['/', '/profile', '/user-info']:
                page.goto(base+path,wait_until='domcontentloaded')
                expect(page.locator('body')).to_be_visible()
            context.request.post(base+'/api/login',data={'username':'admin','password':'password'})
            page.goto(base+'/admin',wait_until='domcontentloaded')
            expect(page.get_by_role('link',name='ศูนย์งาน / รอตรวจ / รายงาน')).to_be_visible()
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        thread.join(timeout=5)
