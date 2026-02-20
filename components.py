"""Shared UI components for FUTO ULAS."""
import streamlit as st
import streamlit.components.v1 as components


APP_NAME = "FUTO ULAS"
APP_FULL = "FUTO ULAS — Unified Lecture Attendance System"
CREDIT   = "Made with Love by EPE202/26"


def footer():
    st.markdown(
        f"""<div style="position:fixed;bottom:0;left:0;right:0;text-align:center;
        padding:6px 0;background:rgba(0,0,0,0.4);z-index:9999;">
        <span style="color:#555;font-size:11px;">{CREDIT}</span>
        </div>""",
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = ""):
    st.markdown(
        f"""<div style="margin-bottom:4px">
        <span style="color:#888;font-size:12px;letter-spacing:1px">{APP_FULL}</span>
        </div>""",
        unsafe_allow_html=True,
    )
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def auto_refresh_js(interval_ms: int = 1000):
    """
    Injects a JavaScript snippet that reloads the Streamlit page every
    `interval_ms` milliseconds by clicking the hidden rerun trigger.
    Works on Streamlit Cloud without any extra packages.
    """
    components.html(
        f"""
        <script>
        (function() {{
            // Guard: only set one timer per page lifecycle
            if (window._fuloRefreshSet) return;
            window._fuloRefreshSet = true;
            setInterval(function() {{
                // Trigger Streamlit rerun by dispatching a custom event
                // that Streamlit's internal mechanism picks up
                window.parent.postMessage({{type: "streamlit:rerun"}}, "*");
            }}, {interval_ms});
        }})();
        </script>
        """,
        height=0,
        scrolling=False,
    )


def live_code_display(code: str, secs_left: float):
    """Renders the animated code + countdown tiles."""
    bar_pct = int((secs_left / 10) * 100)
    # Pick colour: green when fresh, yellow mid, red near expiry
    if secs_left > 6:
        bar_color = "#00ff88"
        code_color = "#00ff88"
    elif secs_left > 3:
        bar_color = "#ffb800"
        code_color = "#ffb800"
    else:
        bar_color = "#ff4444"
        code_color = "#ff4444"

    secs_display = f"{secs_left:.1f}"

    st.markdown(
        f"""
        <div style="display:flex;gap:16px;margin-bottom:8px">
          <!-- Code tile -->
          <div style="flex:1;background:#1a1a2e;border-radius:14px;padding:24px 20px;
               text-align:center;border:2px solid {code_color}">
            <p style="color:#888;margin:0;font-size:12px;letter-spacing:3px;text-transform:uppercase">
              Current Code
            </p>
            <h1 style="color:{code_color};font-size:68px;letter-spacing:14px;margin:8px 0 4px;
                font-family:monospace;font-weight:bold">{code}</h1>
            <p style="color:#555;font-size:11px;margin:0">
              Tell students verbally — do NOT show them your screen
            </p>
          </div>
          <!-- Timer tile -->
          <div style="flex:1;background:#1a1a2e;border-radius:14px;padding:24px 20px;
               text-align:center;border:2px solid {bar_color}">
            <p style="color:#888;margin:0;font-size:12px;letter-spacing:3px;text-transform:uppercase">
              Refreshes In
            </p>
            <h1 style="color:{bar_color};font-size:68px;margin:8px 0 4px;font-family:monospace">
              {secs_display}s
            </h1>
            <div style="background:#333;border-radius:4px;height:6px;overflow:hidden">
              <div style="background:{bar_color};width:{bar_pct}%;height:100%;
                   transition:width 0.9s linear;border-radius:4px"></div>
            </div>
            <p style="color:#555;font-size:11px;margin:6px 0 0">
              Old codes stop working immediately
            </p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
