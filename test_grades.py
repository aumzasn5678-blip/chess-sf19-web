import sys, time, json
sys.path.insert(0, r'C:\Users\poxii\AppData\Local\hermes\skills\web\web-automation\scripts')
import cdp

URL = sys.argv[1] if len(sys.argv) > 1 else 'http://127.0.0.1:8100/index.html'
res = {}
logs = []

def grad_list(t):
    return json.loads(t.eval("(() => JSON.stringify([...document.querySelectorAll('#board .gradico')].map(e=>({sq:e.parentElement.dataset.sq, grade:e.dataset.grade, ply:e.dataset.ply}))))()"))

def click_sq(t, sq):
    t.eval(f"(() => {{ const e=document.querySelector('#board .sq[data-sq=\"{sq}\"]'); if(!e) return false; e.click(); return true; }})()")

def wait_grades(t, want_sq, timeout=14.0):
    end = time.time() + timeout
    while time.time() < end:
        g = grad_list(t)
        if len(g) == 1 and g[0]['sq'] == want_sq:
            return g
        time.sleep(0.3)
    return grad_list(t)

with cdp.Tab(timeout=180) as t:
    t.goto(URL, settle=3)
    # ล้างเกมที่จำไว้ เพื่อเริ่มจากจุดเริ่มต้นจริง
    t.eval("(() => { try{ localStorage.clear(); }catch(e){} return true; })()")
    t.goto(URL, settle=3)
    # เปิด console error hook
    t.eval("(() => { window.__errs=[]; window.onerror=(m,s,l,c,e)=>{window.__errs.push(String(m));}; return true; })()")
    res['engine_ready'] = t.eval("(() => { try { return (typeof engine !== 'undefined') && !!engine; } catch(e){ return 'err:'+e.message; } })()")
    # (ก) play e4, e5, Nf3
    click_sq(t, 'e2'); time.sleep(0.3); click_sq(t, 'e4')
    g1 = wait_grades(t, 'e4')
    logs.append(('after e4', g1))
    click_sq(t, 'e7'); time.sleep(0.3); click_sq(t, 'e5')
    g2 = wait_grades(t, 'e5')
    logs.append(('after e5', g2))
    click_sq(t, 'g1'); time.sleep(0.3); click_sq(t, 'f3')
    g3 = wait_grades(t, 'f3')
    logs.append(('after Nf3', g3))
    res['KA_count'] = len(g3)
    res['KA_grades'] = g3

    # (ข) back once -> position after e5, icon on e5
    t.eval("(() => { document.getElementById('bBack').click(); return true; })()")
    time.sleep(0.5)
    gb = grad_list(t)
    res['KB_count'] = len(gb); res['KB_grades'] = gb

    # (ค) back to start
    t.eval("(() => { document.getElementById('bStart').click(); return true; })()")
    time.sleep(0.5)
    gs = grad_list(t)
    res['KC_count'] = len(gs); res['KC_grades'] = gs

    # (ง) forward once -> position after e4
    t.eval("(() => { document.getElementById('bFwd').click(); return true; })()")
    time.sleep(0.5)
    gf = grad_list(t)
    res['KD_count'] = len(gf); res['KD_grades'] = gf

    # (จ) new game -> 0
    t.eval("(() => { document.getElementById('bNewGame').click(); return true; })()")
    time.sleep(0.3)
    t.eval("(() => { document.getElementById('bNewYes').click(); return true; })()")
    time.sleep(0.6)
    gn = grad_list(t)
    res['KJ_count'] = len(gn); res['KJ_grades'] = gn

    # (ฉ) errors + ฟีเจอร์อื่น
    res['js_errors'] = t.eval("(() => JSON.stringify(window.__errs||[]))()")
    res['board_pieces'] = t.eval("document.querySelectorAll('#board img.pcimg').length")
    res['img_failed'] = t.eval("[...document.querySelectorAll('#board img')].filter(i=>i.naturalWidth===0).length")
    # arrows / run button present
    res['has_arrows_el'] = t.eval("(() => !!document.getElementById('arrows'))()")
    res['bRun_text'] = t.eval("(() => document.getElementById('bRun').textContent.trim())()")
    # theme toggle test
    res['theme_btn'] = t.eval("(() => { const b=document.getElementById('bTheme'); return !!b; })()")

    res['LOG'] = logs

print(json.dumps(res, ensure_ascii=False, indent=1))
