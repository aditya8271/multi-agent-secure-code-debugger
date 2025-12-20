# app.py

import streamlit as st
import sys
import os
import google.generativeai as genai

# ✅ API KEY CONFIGURATION
API_KEY = "AIzaSyD3p1Q6G42aB6-B4VSWubaZPZjLeS2-cVs"
genai.configure(api_key=API_KEY)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.scanner import scan_code
from agents.fixer import fix_code
from agents.validator import validate_fix

# Page config
st.set_page_config(
    page_title="AI Code Analyzer Pro",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
    }
    
    /* Responsive container */
    .main-container {
        max-width: 1400px;
        margin: 0 auto;
        padding: 20px;
    }
    
    /* Header styling */
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
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.95;
    }
    
    /* Card styling */
    .info-card {
        background: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,153,76);
        margin-bottom: 20px;
        border-left: 4px solid #6366f1;
    }
    
    /* Issue severity badges */
    .severity-critical {
        background: #fee2e2;
        color: #991b1b;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .severity-high {
        background: #fed7aa;
        color: #9a3412;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .severity-medium {
        background: #fef3c7;
        color: #92400e;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .severity-low {
        background: #dbeafe;
        color: #1e40af;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 5px;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Score bars */
    .score-bar {
        width: 100%;
        height: 10px;
        background: #e5e7eb;
        border-radius: 10px;
        overflow: hidden;
        margin-top: 10px;
    }
    
    .score-fill {
        height: 100%;
        background: linear-gradient(90deg, #10b981 0%, #059669 100%);
        transition: width 0.3s ease;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.8rem;
        }
        
        .main-header p {
            font-size: 0.95rem;
        }
        
        .metric-value {
            font-size: 2rem;
        }
        
        .info-card {
            padding: 15px;
        }
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Text area */
    .stTextArea textarea {
        border-radius: 8px;
        border: 2px solid #e5e7eb;
        font-family: 'Courier New', monospace;
    }
    
    .stTextArea textarea:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #f9fafb;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Code blocks */
    .stCodeBlock {
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🤖 AI Code Analyzer Pro</h1>
    <p>Powered by Multi-Agent AI System | Detects & Fixes ALL Code Issues</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 🎯 Features")
    st.markdown("""
    <div class="info-card">
        <h4>🔍 Comprehensive Analysis</h4>
        <ul>
            <li>✅ Syntax Errors</li>
            <li>✅ Logic Bugs</li>
            <li>✅ Security Vulnerabilities</li>
            <li>✅ Performance Issues</li>
            <li>✅ Best Practices</li>
            <li>✅ Code Quality</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🤖 AI Agents")
    st.info("""
    **Scanner Agent** 🔍  
    Detects all code issues
    
    **Fixer Agent** 🔧  
    Generates fixed code
    
    **Validator Agent** ✅  
    Verifies code quality
    """)
    
    st.markdown("### 📚 Supported Languages")
    st.success("""
    • Python
    • JavaScript
    • Java
    • C/C++
    • And more!
    """)
    
    st.markdown("### 💡 Pro Tips")
    st.warning("""
    • Paste complete code blocks
    • Include imports and context
    • Try different code samples
    • Check all issue types
    """)

# Main content
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📝 **Input Code**")
    
    # Language selector
    language = st.selectbox(
        "Select Language",
        ["Python", "JavaScript", "Java", "C++", "C#", "PHP", "Ruby", "Go", "Other"],
        help="Select your programming language"
    )
    
    # Sample code based on language
    if language == "Python":
        SAMPLE_CODE = """import sqlite3
import os
import hashlib

def login(username, password)
    # Missing colon and security issues
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # SQL Injection vulnerability
    query = "SELECT * FROM users WHERE username='" + username + "' AND password='" + password + "'"
    cursor.execute(query)
    
    return cursor.fetchone()

def backup_file(filename):
    # Path traversal vulnerability
    with open("./backups/" + filename) as f:
        return f.read()

# Hardcoded secrets
API_KEY = "sk-1234567890abcdef"
SECRET = "my_secret_password"

# Weak cryptography
def hash_password(pwd):
    return hashlib.md5(pwd.encode()).hexdigest()
"""
    elif language == "JavaScript":
        SAMPLE_CODE = """// JavaScript with multiple issues
function login(username, password) {
    // SQL Injection
    const query = "SELECT * FROM users WHERE user='" + username + "'";
    
    // Missing error handling
    db.query(query, (err, result) => {
        return result
    });
}

// Infinite loop
function count() {
    let i = 0;
    while (i < 10) {
        console.log(i);
        // Missing i++
    }
}

// Hardcoded credentials
const API_KEY = "1234567890";
"""
    else:
        SAMPLE_CODE = """// Enter your code here
def example():
    print("Hello World")
"""
    
    code_input = st.text_area(
        "Paste your code here:",
        value=SAMPLE_CODE,
        height=450,
        help="Paste any code to analyze",
        placeholder="Enter your code here..."
    )
    
    # Analyze button
    analyze_button = st.button(
        "🚀 Analyze & Fix Code",
        type="primary",
        use_container_width=True
    )
    
    if analyze_button:
        if not code_input.strip():
            st.error("⚠️ Please enter some code to analyze!")
        else:
            st.session_state.code_input = code_input
            st.session_state.language = language
            st.session_state.analysis_done = True
            st.rerun()

with col2:
    st.markdown("### 📊 **Analysis Results**")
    
    if 'analysis_done' in st.session_state and st.session_state.analysis_done:
        
        # Progress indicator
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        # STEP 1: Scanner Agent
        progress_text.text("🔍 Scanner Agent analyzing code...")
        progress_bar.progress(33)
        
        with st.spinner("Scanning..."):
            scanner_result = scan_code(st.session_state.code_input)
        
        if scanner_result['success']:
            scan_data = scanner_result['data']
            progress_bar.progress(100)
            progress_text.empty()
            
            # Summary
            total = scan_data.get('total_found', 0)
            critical = scan_data.get('critical_count', 0)
            high = scan_data.get('high_count', 0)
            medium = scan_data.get('medium_count', 0)
            low = scan_data.get('low_count', 0)
            
            if total > 0:
                st.warning(f"⚠️ **{scan_data.get('summary', 'Issues detected')}**")
            else:
                st.success(f"✅ **{scan_data.get('summary', 'Code is clean!')}**")
            
            # Severity metrics
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
                # Show issues
                with st.expander(f"🔍 View Detected Issues ({total} found)", expanded=True):
                    for i, issue in enumerate(issues, 1):
                        severity = issue.get('severity', 'Unknown')
                        severity_class = f"severity-{severity.lower()}"
                        
                        st.markdown(f"""
                        <div style='background: #f9fafb; padding: 15px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid {"#ef4444" if severity=="Critical" else "#f59e0b" if severity=="High" else "#eab308" if severity=="Medium" else "#3b82f6"}'>
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
                    fixer_result = fix_code(st.session_state.code_input, scan_data)
                
                if fixer_result['success']:
                    fix_data = fixer_result['data']
                    
                    st.success("✅ **Code fixed successfully!**")
                    
                    # Show fixed code
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
                                if fix.get('before') and fix.get('after'):
                                    col_before, col_after = st.columns(2)
                                    with col_before:
                                        st.markdown("**Before:**")
                                        st.code(fix.get('before'), language=st.session_state.language.lower())
                                    with col_after:
                                        st.markdown("**After:**")
                                        st.code(fix.get('after'), language=st.session_state.language.lower())
                                st.divider()
                    
                    # STEP 3: Validator Agent
                    progress_text.text("✅ Validator Agent verifying...")
                    
                    with st.spinner("Validating fixes..."):
                        validator_result = validate_fix(
                            st.session_state.code_input,
                            fixed_code,
                            scan_data
                        )
                    
                    progress_bar.progress(100)
                    progress_text.empty()
                    
                    if validator_result['success']:
                        val_data = validator_result['data']
                        
                        # Overall status
                        status = val_data.get('validation_status', 'UNKNOWN')
                        overall_score = val_data.get('overall_score', 0)
                        
                        if status == "PASS":
                            st.success(f"✅ **Validation PASSED**")
                        else:
                            st.error(f"❌ **Validation FAILED**")
                        
                        # Score visualization
                        with st.expander("✅ View Detailed Validation Report", expanded=True):
                            # Overall score with visual bar
                            st.markdown(f"""
                            <div style='background: white; padding: 20px; border-radius: 12px; margin-bottom: 20px;'>
                                <h3 style='margin-bottom: 15px;'>Overall Quality Score</h3>
                                <div style='display: flex; align-items: center; justify-content: space-between;'>
                                    <div style='flex-grow: 1; margin-right: 20px;'>
                                        <div class='score-bar'>
                                            <div class='score-fill' style='width: {overall_score}%;'></div>
                                        </div>
                                    </div>
                                    <div style='font-size: 2.5rem; font-weight: 700; color: {"#10b981" if overall_score >= 80 else "#f59e0b" if overall_score >= 60 else "#ef4444"};'>
                                        {overall_score}/100
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Detailed scores
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
                            
                            # Summary
                            st.markdown("**📝 Summary:**")
                            st.info(val_data.get('summary', 'Validation completed'))
                            
                            # Recommendations
                            if val_data.get('recommendations'):
                                st.markdown("**💡 Recommendations:**")
                                for rec in val_data.get('recommendations', []):
                                    st.markdown(f"- {rec}")
                            
                            # Remaining issues
                            if val_data.get('remaining_issues'):
                                st.warning(f"**⚠️ Remaining Issues ({len(val_data['remaining_issues'])}):**")
                                for issue in val_data['remaining_issues']:
                                    st.markdown(f"- {issue}")
                            
                            # New issues
                            if val_data.get('new_issues'):
                                st.error(f"**🚨 New Issues Introduced ({len(val_data['new_issues'])}):**")
                                for issue in val_data['new_issues']:
                                    st.markdown(f"- {issue}")
                        
                        # Download buttons
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
                            # Generate report
                            report = f"""CODE ANALYSIS REPORT
===================

Language: {st.session_state.language}
st.write("Date:", datetime.now())


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
                    
                    else:
                        st.error(f"❌ {validator_result.get('error', 'Validation failed')}")
                        if validator_result.get('raw_response'):
                            with st.expander("View Raw Response"):
                                st.code(validator_result['raw_response'])
                
                else:
                    st.error(f"❌ {fixer_result.get('error', 'Fix generation failed')}")
                    if fixer_result.get('raw_response'):
                        with st.expander("View Raw Response"):
                            st.code(fixer_result['raw_response'])
            
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
            
            if scanner_result.get('raw_response'):
                with st.expander("🔍 View Raw AI Response (for debugging)"):
                    st.code(scanner_result['raw_response'])
            
            if scanner_result.get('details'):
                with st.expander("📋 Error Details"):
                    st.text(scanner_result['details'])

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; background: #f9fafb; border-radius: 12px;'>
    <p style='margin: 0; font-size: 1.1rem; color: #6b7280;'>
        Built By Aditya 
    </p>
    <p style='margin: 10px 0 0 0; color: #9ca3af;'>
        🤖 3 AI Agents Working Together | 🔍 Comprehensive Analysis | 🔧 Instant Fixes | ✅ Quality Validation
    </p>
</div>
""", unsafe_allow_html=True)
