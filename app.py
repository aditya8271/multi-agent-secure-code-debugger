# app.py - WORKING VERSION

import streamlit as st
import sys
import os
import google.generativeai as genai
from dotenv import load_dotenv
import time

# ===== LOAD API KEY =====
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("🔑 API Key not found! Please create .env file with GOOGLE_API_KEY")
    st.stop()

genai.configure(api_key=API_KEY)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.scanner import scan_code
from agents.fixer import fix_code
from agents.validator import validate_fix

# ===== RATE LIMIT HANDLER =====
def handle_rate_limit(func, max_retries=2):
    """Handle API rate limits with automatic retry"""
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            error_msg = str(e).lower()
            if any(word in error_msg for word in ["quota", "rate", "limit", "429"]):
                if attempt < max_retries - 1:
                    wait_time = 60
                    st.warning(f"⏱️ Rate limit reached. Waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    st.error("❌ Rate limit exceeded. Please wait 1 minute and try again.")
                    return {"success": False, "error": "Rate limit exceeded"}
            else:
                return {"success": False, "error": str(e)}
    return {"success": False, "error": "Max retries reached"}

# ===== PAGE CONFIG =====
st.set_page_config(
    page_title="AI Code Analyzer Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== CUSTOM CSS =====
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 10px;
        font-weight: 700;
    }
    .severity-critical {
        background: #fee2e2;
        color: #991b1b;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
    }
    .severity-high {
        background: #fed7aa;
        color: #9a3412;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
    }
    .severity-medium {
        background: #fef3c7;
        color: #92400e;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
    }
    .severity-low {
        background: #dbeafe;
        color: #1e40af;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
    }
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ===== HEADER =====
st.markdown("""
<div class="main-header">
    <h1>🤖 AI Code Analyzer Pro</h1>
    <p>Powered by Multi-Agent AI System | Detects & Fixes ALL Code Issues</p>
</div>
""", unsafe_allow_html=True)

# ===== SIDEBAR =====
with st.sidebar:
    st.markdown("### 🎯 Features")
    st.info("""
    **🔍 Comprehensive Analysis**
    - Syntax Errors
    - Logic Bugs
    - Security Vulnerabilities
    - Performance Issues
    - Best Practices
    """)
    
    st.markdown("### ⚠️ Rate Limits")
    st.warning("""
    **Free Tier Limits:**
    - 15 requests/minute
    - 1,500 requests/day
    
    If limit reached, wait 60 seconds.
    """)
    
    st.markdown("### 📚 Supported Languages")
    st.success("""
    Python • JavaScript • Java
    C++ • C# • PHP • Ruby • Go
    """)

# ===== MAIN CONTENT =====
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📝 **Input Code**")
    
    language = st.selectbox(
        "Select Language",
        ["Python", "JavaScript", "Java", "C++", "C#", "PHP", "Ruby", "Go", "Other"],
        help="Select your programming language"
    )
    
    # Clean sample code (no fake secrets to avoid alerts)
    SAMPLE_CODE = """import sqlite3
import os

def login(username, password):
    # SQL Injection vulnerability
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
    cursor.execute(query)
    return cursor.fetchone()

def run_command(user_input):
    # Command Injection vulnerability
    os.system("ping " + user_input)

def read_file(filename):
    # Path Traversal vulnerability
    with open("./files/" + filename) as f:
        return f.read()
"""
    
    code_input = st.text_area(
        "Paste your code here:",
        value=SAMPLE_CODE,
        height=450,
        help="Paste any code to analyze",
        placeholder="Enter your code here..."
    )
    
    analyze_button = st.button(
        "🚀 Analyze & Fix Code",
        type="primary",
        use_container_width=True
    )
    
    # SIMPLIFIED - NO SECURITY CHECK ISSUES
    if analyze_button:
        if not code_input.strip():
            st.error("⚠️ Please enter some code to analyze!")
        else:
            # Store in session state and trigger analysis
            st.session_state.code_input = code_input
            st.session_state.language = language
            st.session_state.analysis_done = True
            st.rerun()

with col2:
    st.markdown("### 📊 **Analysis Results**")
    
    if 'analysis_done' in st.session_state and st.session_state.analysis_done:
        
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        # STEP 1: Scanner Agent
        progress_text.text("🔍 Scanner Agent analyzing code...")
        progress_bar.progress(33)
        
        with st.spinner("Scanning..."):
            scanner_result = handle_rate_limit(lambda: scan_code(st.session_state.code_input))
        
        if scanner_result and scanner_result.get('success'):
            scan_data = scanner_result['data']
            progress_bar.progress(100)
            progress_text.empty()
            
            total = scan_data.get('total_found', 0)
            critical = scan_data.get('critical_count', 0)
            high = scan_data.get('high_count', 0)
            medium = scan_data.get('medium_count', 0)
            low = scan_data.get('low_count', 0)
            
            if total > 0:
                st.warning(f"⚠️ **{scan_data.get('summary', 'Issues detected')}**")
            else:
                st.success(f"✅ **{scan_data.get('summary', 'Code is clean!')}**")
            
            if total > 0:
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    st.metric("🔴 Critical", critical)
                with col_b:
                    st.metric("🟠 High", high)
                with col_c:
                    st.metric("🟡 Medium", medium)
                with col_d:
                    st.metric("🔵 Low", low)
            
            issues = scan_data.get('issues', [])
            
            if issues:
                with st.expander(f"🔍 View Detected Issues ({total} found)", expanded=True):
                    for i, issue in enumerate(issues, 1):
                        severity = issue.get('severity', 'Unknown')
                        severity_class = f"severity-{severity.lower()}"
                        color = "#ef4444" if severity=="Critical" else "#f59e0b" if severity=="High" else "#eab308" if severity=="Medium" else "#3b82f6"
                        
                        st.markdown(f"""
                        <div style='background: #f9fafb; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid {color}'>
                            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;'>
                                <strong style='font-size: 1.1rem;'>{i}. {issue.get('issue_type', 'Unknown Issue')}</strong>
                                <span class='{severity_class}'>{severity}</span>
                            </div>
                            <p style='margin: 8px 0;'><strong>Line {issue.get('line_number', 'N/A')}:</strong> {issue.get('description', 'No description')}</p>
                            <p style='margin: 8px 0; background: #ffffff; padding: 8px; border-radius: 4px; font-family: monospace; font-size: 0.9rem;'><code>{issue.get('code_snippet', 'N/A')}</code></p>
                            <p style='margin: 8px 0; color: #059669;'><strong>💡 Suggestion:</strong> {issue.get('suggestion', 'Apply recommended fix')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                
                # STEP 2: Fixer Agent
                progress_text.text("🔧 Fixer Agent generating fixes...")
                
                with st.spinner("Generating fixed code..."):
                    fixer_result = handle_rate_limit(lambda: fix_code(st.session_state.code_input, scan_data))
                
                if fixer_result and fixer_result.get('success'):
                    fix_data = fixer_result['data']
                    
                    st.success("✅ **Code fixed successfully!**")
                    
                    with st.expander("🔧 View Fixed Code", expanded=True):
                        fixed_code = fix_data.get('fixed_code', 'No fixed code available')
                        st.code(fixed_code, language=st.session_state.language.lower())
                        
                        st.markdown("**✨ Improvements Made:**")
                        st.info(fix_data.get('improvements_summary', 'Code has been improved'))
                        
                        st.markdown("**📝 Fixes Applied:**")
                        for fix in fix_data.get('fixes_applied', []):
                            with st.container():
                                st.markdown(f"**{fix.get('issue', 'Fix')}**")
                                st.markdown(f"_{fix.get('fix_description', 'Applied fix')}_")
                                st.divider()
                    
                    # STEP 3: Validator Agent
                    progress_text.text("✅ Validator Agent verifying...")
                    
                    with st.spinner("Validating fixes..."):
                        validator_result = handle_rate_limit(
                            lambda: validate_fix(st.session_state.code_input, fixed_code, scan_data)
                        )
                    
                    progress_bar.progress(100)
                    progress_text.empty()
                    
                    if validator_result and validator_result.get('success'):
                        val_data = validator_result['data']
                        
                        status = val_data.get('validation_status', 'UNKNOWN')
                        overall_score = val_data.get('overall_score', 0)
                        
                        if status == "PASS":
                            st.success(f"✅ **Validation PASSED**")
                        else:
                            st.error(f"❌ **Validation FAILED**")
                        
                        with st.expander("✅ View Detailed Validation Report", expanded=True):
                            st.markdown(f"""
                            <div style='background: white; padding: 20px; border-radius: 12px; margin-bottom: 20px;'>
                                <h3 style='margin-bottom: 15px;'>Overall Quality Score</h3>
                                <div style='display: flex; align-items: center; justify-content: space-between;'>
                                    <div style='flex-grow: 1; margin-right: 20px;'>
                                        <div style='width: 100%; height: 10px; background: #e5e7eb; border-radius: 10px;'>
                                            <div style='width: {overall_score}%; height: 100%; background: linear-gradient(90deg, #10b981 0%, #059669 100%); border-radius: 10px;'></div>
                                        </div>
                                    </div>
                                    <div style='font-size: 2.5rem; font-weight: 700; color: {"#10b981" if overall_score >= 80 else "#f59e0b" if overall_score >= 60 else "#ef4444"};'>
                                        {overall_score}/100
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown("**📊 Detailed Scores:**")
                            col_s1, col_s2, col_s3 = st.columns(3)
                            
                            with col_s1:
                                st.metric("Syntax", f"{val_data.get('syntax_score', 0)}/100")
                                st.metric("Logic", f"{val_data.get('logic_score', 0)}/100")
                            
                            with col_s2:
                                st.metric("Security", f"{val_data.get('security_score', 0)}/100")
                                st.metric("Performance", f"{val_data.get('performance_score', 0)}/100")
                            
                            with col_s3:
                                st.metric("Readability", f"{val_data.get('readability_score', 0)}/100")
                                st.metric("Issues Fixed", val_data.get('issues_fixed', 0))
                            
                            st.markdown("**📝 Summary:**")
                            st.info(val_data.get('summary', 'Validation completed'))
                            
                            if val_data.get('recommendations'):
                                st.markdown("**💡 Recommendations:**")
                                for rec in val_data.get('recommendations', []):
                                    st.markdown(f"- {rec}")
                        
                        col_d1, col_d2 = st.columns(2)
                        
                        with col_d1:
                            st.download_button(
                                label="📥 Download Fixed Code",
                                data=fixed_code,
                                file_name=f"fixed_code.{st.session_state.language.lower()}",
                                mime="text/plain",
                                use_container_width=True
                            )
                        
                        with col_d2:
                            report = f"""CODE ANALYSIS REPORT
===================

Language: {st.session_state.language}

SUMMARY:
--------
Total Issues Found: {total}
- Critical: {critical}
- High: {high}
- Medium: {medium}
- Low: {low}

VALIDATION:
-----------
Status: {status}
Overall Score: {overall_score}/100
Issues Fixed: {val_data.get('issues_fixed', 0)}

{val_data.get('summary', '')}

DETAILED SCORES:
----------------
- Syntax: {val_data.get('syntax_score', 0)}/100
- Logic: {val_data.get('logic_score', 0)}/100
- Security: {val_data.get('security_score', 0)}/100
- Performance: {val_data.get('performance_score', 0)}/100
- Readability: {val_data.get('readability_score', 0)}/100
"""
                            st.download_button(
                                label="📄 Download Report",
                                data=report,
                                file_name="analysis_report.txt",
                                mime="text/plain",
                                use_container_width=True
                            )
                        
                        # Dashboard
                        st.markdown("---")
                        st.markdown("## 📈 Security Dashboard")
                        
                        col_dash1, col_dash2, col_dash3 = st.columns(3)
                        
                        with col_dash1:
                            st.metric(
                                label="Vulnerabilities Found",
                                value=len(issues),
                                delta=f"-{len(issues)} after fix",
                                delta_color="inverse"
                            )
                        
                        with col_dash2:
                            st.metric(
                                label="Security Score",
                                value=f"{overall_score}/100",
                                delta=f"+{overall_score-20}"
                            )
                        
                        with col_dash3:
                            severity_critical = sum(1 for v in issues if v.get('severity') == 'Critical')
                            st.metric(
                                label="Critical Issues",
                                value=severity_critical,
                                delta=f"-{severity_critical}",
                                delta_color="inverse"
                            )
                    
                    else:
                        st.error(f"❌ {validator_result.get('error', 'Validation failed')}")
                
                else:
                    st.error(f"❌ {fixer_result.get('error', 'Fix generation failed')}")
            
            else:
                st.success("🎉 **Excellent! Your code is clean and well-written!**")
                st.balloons()
                st.info("""
                ✅ No syntax errors detected  
                ✅ No logic bugs found  
                ✅ No security vulnerabilities  
                ✅ Performance looks good  
                ✅ Following best practices  
                """)
        
        else:
            st.error(f"❌ {scanner_result.get('error', 'Analysis failed')}")
            if scanner_result.get('suggestion'):
                st.info(f"💡 {scanner_result['suggestion']}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; background: #f9fafb; border-radius: 12px;'>
    <p style='margin: 0; font-size: 1.1rem; color: #6b7280;'>
        Built with ❤️ for <strong>Autonomous Hackathon 2025</strong> | Powered by <strong>Google Gemini AI</strong>
    </p>
    <p style='margin: 10px 0 0 0; color: #9ca3af;'>
        🤖 3 AI Agents Working Together | 🔍 Comprehensive Analysis | 🔧 Instant Fixes | ✅ Quality Validation
    </p>
</div>
""", unsafe_allow_html=True)
