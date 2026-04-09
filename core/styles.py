"""
core/styles.py
Uygulama genelindeki Qt stylesheet ve gömülü HTML/CSS stringleri.
"""

STYLE = """
* { outline: none; }
QMainWindow, QWidget {
    background: #1c1b22;
    color: #fbfbfe;
    font-family: 'SF Pro Text', 'Helvetica Neue', 'Segoe UI', sans-serif;
    font-size: 13px;
}
#toggleBtn {
    background: transparent; border: none;
    border-right: 1px solid #2a2930;
    color: #9e9db5; font-size: 17px;
    min-width: 40px; max-width: 40px;
    min-height: 40px; max-height: 40px; padding: 0;
}
#toggleBtn:hover   { background: #2a2930; color: #fbfbfe; }
#toggleBtn:pressed { background: #35343e; }
#sidebar { background: #1c1b22; border-right: 1px solid #2a2930; }
#sideBtn {
    background: transparent; border: none; border-radius: 8px;
    color: #9e9db5; font-size: 17px;
    min-width: 36px; max-width: 36px;
    min-height: 36px; max-height: 36px;
    padding: 0; margin: 2px 6px;
}
#sideBtn:hover   { background: #2a2930; color: #fbfbfe; }
#sideBtn:pressed { background: #35343e; }
#tabStrip { background: #1c1b22; min-height: 36px; max-height: 36px; }
#tabBtn {
    background: transparent; color: #9e9db5; border: none;
    border-radius: 6px; padding: 0 10px; font-size: 12px;
    min-height: 28px; max-height: 28px;
    min-width: 80px; max-width: 200px;
    text-align: left; margin: 4px 1px;
}
#tabBtn[active="true"] { background: #2a2930; color: #fbfbfe; }
#tabBtn:hover:!pressed { background: #252430; color: #c8c7de; }
#tabCloseBtn {
    background: transparent; color: transparent; border: none;
    border-radius: 4px; font-size: 10px;
    min-width: 16px; max-width: 16px;
    min-height: 16px; max-height: 16px;
    padding: 0; margin: 0 2px 0 0;
}
#tabCloseBtn:hover { background: #3d3c4e; color: #c8c7de; }
#newTabBtn {
    background: transparent; color: #6e6d85; border: none;
    border-radius: 6px; font-size: 18px;
    min-width: 28px; max-width: 28px;
    min-height: 28px; max-height: 28px;
    padding: 0; margin: 4px 4px;
}
#newTabBtn:hover { background: #2a2930; color: #c8c7de; }
#navBar {
    background: #1c1b22; border-bottom: 1px solid #2a2930;
    min-height: 44px; max-height: 44px;
}
#navBtn {
    background: transparent; color: #9e9db5; border: none;
    border-radius: 6px; font-size: 15px;
    min-width: 30px; max-width: 30px;
    min-height: 30px; max-height: 30px; padding: 0;
}
#navBtn:hover   { background: #2a2930; color: #fbfbfe; }
#navBtn:pressed { background: #35343e; }
#navBtn:disabled { color: #3a3948; }
#urlBar {
    background: #2a2930; color: #fbfbfe;
    border: 1px solid transparent; border-radius: 8px;
    padding: 0 14px; font-size: 13px;
    min-height: 32px; max-height: 32px;
    selection-background-color: #5b5bef;
}
#urlBar:focus        { border: 1px solid #5b5bef; background: #35343e; }
#urlBar:hover:!focus { background: #35343e; }

/* ── Yer imleri çubuğu ── */
#bmBar {
    background: #17161d;
    border-bottom: 1px solid #2a2930;
    min-height: 30px; max-height: 30px;
    padding: 0 6px;
}
#bmBtn {
    background: transparent; color: #9e9db5; border: none;
    border-radius: 5px; font-size: 12px;
    height: 24px; padding: 0 8px; margin: 3px 1px;
}
#bmBtn:hover   { background: #2a2930; color: #fbfbfe; }
#bmBtn:pressed { background: #35343e; }
#bmAddBtn {
    background: transparent; color: #6e6d85; border: none;
    border-radius: 5px; font-size: 16px;
    min-width: 24px; max-width: 24px;
    height: 24px; padding: 0; margin: 3px 2px;
}
#bmAddBtn:hover { background: #2a2930; color: #c8c7de; }

/* ── İndirme bildirimi ── */
#dlBar {
    background: #1e1d28; border-top: 1px solid #2a2930;
    min-height: 36px; max-height: 36px; padding: 0 12px;
}
#dlLabel { color: #9e9db5; font-size: 12px; }
#dlCloseBtn {
    background: transparent; color: #6e6d85; border: none;
    border-radius: 4px; font-size: 13px;
    min-width: 24px; max-width: 24px;
    min-height: 24px; max-height: 24px; padding: 0;
}
#dlCloseBtn:hover { background: #2a2930; color: #fbfbfe; }

/* ── Progress ── */
#progress { background: transparent; border: none; max-height: 2px; min-height: 2px; }
#progress::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #5b5bef,stop:1 #a16ef8);
    border-radius: 1px;
}
QStatusBar {
    background: #1c1b22; color: #6e6d85;
    border-top: 1px solid #2a2930;
    font-size: 11px; min-height: 20px; max-height: 20px;
}

/* ── Panel (geçmiş/indirme/ayarlar) ── */
#panel {
    background: #17161d;
    border-left: 1px solid #2a2930;
    min-width: 300px; max-width: 300px;
}
#panelTitle {
    font-size: 14px; font-weight: bold;
    color: #fbfbfe; padding: 12px 16px 8px;
    border-bottom: 1px solid #2a2930;
}
#panelList {
    background: transparent; border: none;
    font-size: 12px; color: #c8c7de;
}
#panelList::item { padding: 8px 16px; border-bottom: 1px solid #1c1b22; }
#panelList::item:hover { background: #2a2930; }
#panelList::item:selected { background: #35343e; color: #fbfbfe; }
#panelCloseBtn {
    background: transparent; color: #6e6d85; border: none;
    border-radius: 6px; font-size: 15px;
    min-width: 28px; max-width: 28px;
    min-height: 28px; max-height: 28px; padding: 0;
    margin: 8px 8px 0 0;
}
#panelCloseBtn:hover { background: #2a2930; color: #fbfbfe; }
#clearBtn {
    background: transparent; color: #6e6d85; border: none;
    border-top: 1px solid #2a2930;
    font-size: 12px; height: 32px; padding: 0 16px;
}
#clearBtn:hover { color: #e74c3c; }

/* ── Dialog ── */
QDialog {
    background: #1c1b22;
    color: #fbfbfe;
}
QMessageBox {
    background: #1c1b22;
}
QMessageBox QLabel {
    color: #fbfbfe;
}
"""

HOME_BRAND_CSS = """
<style>
.home-brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  animation: none !important;
  opacity: 1 !important;
  transform: none !important;
}
.home-logo {
  width: 42px;
  height: auto;
}
.home-title {
  color: #ffffff;
  font-size: 18px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}
</style>
"""

MENU_STYLE = (
    "QMenu{background:#2a2930;color:#fbfbfe;border:1px solid #45445a;padding:4px;}"
    "QMenu::item{padding:6px 20px;border-radius:4px;}"
    "QMenu::item:selected{background:#5b5bef;}"
)
