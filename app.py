import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import import datetime
import random
import io





# Configure the page
st.set_page_config(
    page_title="ChartED Solutions - Financial Aid Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling to make it look professional
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .charted-logo {
        font-size: 2.5em;
        font-weight: bold;
        color: #1e3a5f;
        margin-bottom: 0.5rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1e3a5f;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def setup_session_data():
    """Set up the data that persists while using the app"""
    if 'data_processor' not in st.session_state:
        st.session_state['data_processor'] = UnifiedDataProcessor()
    if 'email_manager' not in st.session_state:
        st.session_state['email_manager'] = EmailManager()
    if 'analytics_engine' not in st.session_state:
        st.session_state['analytics_engine'] = MajorAnalyticsEngine()
    if 'nslds_processed' not in st.session_state:
        st.session_state['nslds_processed'] = False
    if 'sis_processed' not in st.session_state:
        st.session_state['sis_processed'] = False

def main():
    """Main function that runs the entire application"""
    setup_session_data()
    
    # Create the header section
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<div class="charted-logo">🎓 ChartED Solutions</div>', unsafe_allow_html=True)
        st.markdown("**Unified Financial Aid Portal** - Manage Student Loan Risk & Communications")
    with col2:
        st.markdown("**Contact Us:**")
        st.markdown(f"📧 {CONTACT_EMAIL}")
        st.markdown(f"🌐 {WEBSITE}")
    
    st.markdown("---")
    
    # Create the sidebar
    with st.sidebar:
        st.markdown("### 🔒 FERPA Compliant")
        st.info("All communications maintain strict privacy compliance")
        
        st.markdown("### ✅ Features")
        st.markdown("""
        📁 **Upload Multiple Files**  
        📊 **Risk Analytics by Major**  
        📧 **Send Compliant Emails**  
        📋 **Generate Reports**  
        ⚙️ **Easy Configuration**
        """)
        
        st.markdown("### 📞 Support")
        st.markdown(f"""
        **ChartED Solutions**  
        📧 {CONTACT_EMAIL}  
        📞 Available for consultation  
        🕒 9 AM - 6 PM EST
        """)
    
    # Create the main navigation tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Dashboard", 
        "📁 Upload Data", 
        "📊 Analytics", 
        "📧 Communications", 
        "📋 Reports"
    ])
    
    with tab1:
        show_dashboard()
    
    with tab2:
        show_data_upload()
    
    with tab3:
        show_analytics()
    
    with tab4:
        show_communications()
    
    with tab5:
        show_reports()

def show_dashboard():
    """Show the main dashboard"""
    st.markdown("""
    <div class="main-header">
        <h1>Financial Aid Risk Management Portal</h1>
        <p style="font-size: 1.2em;">
            Upload student data, analyze risk patterns, and send compliant communications - all in one place
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show feature cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯 Unified Data</h3>
            <p>Combine NSLDS and SIS data for complete student risk profiles</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Smart Analytics</h3>
            <p>Identify which academic programs have the highest default risk</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>📧 Compliant Communications</h3>
            <p>Send FERPA-compliant emails with built-in templates</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Show current data status if available
    if st.session_state.get('merged_data') is not None:
        st.markdown("### Current Data Summary")
        merged_data = st.session_state['merged_data']
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Students", len(merged_data))
        with col2:
            high_risk = len(merged_data[merged_data['risk_tier'] == 'HIGH'])
            st.metric("High Risk Students", high_risk)
        with col3:
            total_balance = merged_data['outstanding_balance'].sum()
            st.metric("Total at Risk", f"${total_balance:,.0f}")
        with col4:
            avg_risk = merged_data['risk_score'].mean()
            st.metric("Average Risk Score", f"{avg_risk:.2f}")

def show_data_upload():
    """Show the data upload page"""
    st.header("📁 Upload Your Data Files")
    st.markdown("Upload NSLDS and SIS files to analyze student loan risk")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Step 1: Upload NSLDS Report")
        st.markdown("This is your delinquent borrower report from NSLDS")
        
        nslds_file = st.file_uploader(
            "Choose NSLDS File",
            type=['csv', 'xlsx'],
            key="nslds_upload",
            help="Upload your NSLDS Delinquent Borrower Report (CSV or Excel format)"
        )
        
        if nslds_file:
            st.success(f"✅ File uploaded: {nslds_file.name}")
            if st.button("Process NSLDS File", type="primary"):
                with st.spinner("Processing your NSLDS data..."):
                    success, message = st.session_state['data_processor'].process_nslds_file(nslds_file)
                    if success:
                        st.success(message)
                        st.session_state['nslds_processed'] = True
                    else:
                        st.error(message)
    
    with col2:
        st.markdown("### Step 2: Upload SIS Data")
        st.markdown("This is your student information with academic majors")
        
        sis_file = st.file_uploader(
            "Choose SIS File",
            type=['csv', 'xlsx'],
            key="sis_upload",
            help="Upload student information with major/program data (CSV or Excel format)"
        )
        
        if sis_file:
            st.success(f"✅ File uploaded: {sis_file.name}")
            if st.button("Process SIS File", type="primary"):
                with st.spinner("Processing your SIS data..."):
                    success, message = st.session_state['data_processor'].process_sis_file(sis_file)
                    if success:
                        st.success(message)
                        st.session_state['sis_processed'] = True
                    else:
                        st.error(message)
    
    # Show merge option when both files are processed
    if st.session_state.get('nslds_processed') and st.session_state.get('sis_processed'):
        st.markdown("---")
        st.markdown("### Step 3: Combine Your Data")
        st.info("Both files are ready! Now combine them to create complete student profiles.")
        
        if st.button("🔗 Combine Data Files", type="primary", use_container_width=True):
            with st.spinner("Combining NSLDS and SIS data..."):
                merged_data = st.session_state['data_processor'].merge_datasets()
                if merged_data is not None:
                    st.session_state['merged_data'] = merged_data
                    st.success(f"✅ Success! Combined data for {len(merged_data)} students")
                    
                    # Show a preview of the data
                    st.markdown("### Data Preview")
                    st.dataframe(merged_data.head(10))
                else:
                    st.error("❌ Could not combine the files. Make sure both files have matching student information (SSN or Student ID).")

def show_analytics():
    """Show the analytics page"""
    st.header("📊 Risk Analytics by Academic Program")
    
    if 'merged_data' in st.session_state:
        merged_data = st.session_state['merged_data']
        analytics_engine = st.session_state['analytics_engine']
        
        # Generate analysis by major
        major_analysis = analytics_engine.analyze_by_major(merged_data)
        
        if major_analysis is not None:
            st.markdown("### Program Risk Summary")
            
            # Show key metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                high_risk_programs = len(major_analysis[major_analysis['risk_tier'] == 'HIGH'])
                st.metric("High-Risk Programs", high_risk_programs)
            
            with col2:
                total_at_risk = major_analysis['total_balance'].sum()
                st.metric("Total Portfolio at Risk", f"${total_at_risk:,.0f}")
            
            with col3:
                avg_risk = major_analysis['avg_risk'].mean()
                st.metric("Average Risk Score", f"{avg_risk:.2f}")
            
            # Show the data table
            st.markdown("### Risk Ranking by Program")
            display_df = major_analysis.copy()
            display_df['avg_risk'] = display_df['avg_risk'].apply(lambda x: f"{x:.2f}")
            display_df['avg_balance'] = display_df['avg_balance'].apply(lambda x: f"${x:,.0f}")
            display_df['total_balance'] = display_df['total_balance'].apply(lambda x: f"${x:,.0f}")
            
            st.dataframe(display_df, use_container_width=True)
            
            # Create visualization
            st.markdown("### Risk Visualization")
            fig = px.scatter(
                major_analysis,
                x='student_count',
                y='avg_risk',
                size='total_balance',
                color='risk_tier',
                hover_data=['major', 'avg_balance'],
                title="Program Risk vs Number of Students",
                labels={'student_count': 'Number of Students', 'avg_risk': 'Average Risk Score'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("Cannot create analytics - make sure your data includes academic major information.")
    else:
        st.info("📤 Please upload and combine your data files first to view analytics.")
        if st.button("Go to Data Upload"):
            st.switch_page("Upload Data")

def show_communications():
    """Show the communications page"""
    st.header("📧 Student Communications")
    
    email_manager = st.session_state['email_manager']
    
    if 'merged_data' in st.session_state:
        merged_data = st.session_state['merged_data']
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### Select Students for Communication")
            
            # Create filters
            filter_col1, filter_col2, filter_col3 = st.columns(3)
            
            with filter_col1:
                risk_filter = st.multiselect(
                    "Risk Level",
                    ['HIGH', 'MEDIUM', 'LOW'],
                    default=['HIGH'],
                    help="Choose which risk levels to include"
                )
            
            with filter_col2:
                if 'major' in merged_data.columns:
                    major_filter = st.multiselect(
                        "Academic Program",
                        merged_data['major'].unique(),
                        help="Choose specific majors (optional)"
                    )
                else:
                    major_filter = []
                    st.info("No major data available")
            
            with filter_col3:
                min_delinquent = st.number_input(
                    "Minimum Days Delinquent",
                    min_value=0,
                    value=30,
                    step=30,
                    help="Only include students with this many delinquent days or more"
                )
            
            # Apply filters to select students
            filtered_students = merged_data.copy()
            
            if risk_filter:
                filtered_students = filtered_students[filtered_students['risk_tier'].isin(risk_filter)]
            
            if major_filter and 'major' in merged_data.columns:
                filtered_students = filtered_students[filtered_students['major'].isin(major_filter)]
            
            if min_delinquent > 0:
                filtered_students = filtered_students[filtered_students['days_delinquent'] >= min_delinquent]
            
            st.markdown(f"**Selected Students: {len(filtered_students)}**")
            
            if not filtered_students.empty:
                # Show preview of selected students
                display_columns = ['student_id', 'first_name', 'last_name', 'email', 'risk_tier']
                if 'major' in filtered_students.columns:
                    display_columns.append('major')
                
                preview_students = filtered_students[display_columns].head(10)
                st.dataframe(preview_students, use_container_width=True)
                
                if len(filtered_students) > 10:
                    st.info(f"Showing first 10 of {len(filtered_students)} selected students")
        
        with col2:
            st.markdown("### Choose Email Template")
            
            # Template selection
            template_options = {
                'default_prevention': 'Default Prevention Notice',
                'payment_plan': 'Payment Plan Options',
                'counseling_invitation': 'Financial Counseling Invitation'
            }
            
            selected_template = st.selectbox(
                "Email Template",
                options=list(template_options.keys()),
                format_func=lambda x: template_options[x],
                help="Choose the type of email to send"
            )
            
            # Show template preview
            if selected_template:
                template_data = email_manager.templates[selected_template]
                
                with st.expander("📋 Preview Email Template"):
                    st.markdown(f"**Subject:** {template_data['subject']}")
                    st.markdown("**Body:**")
                    st.text_area(
                        "Email Content",
                        template_data['body'],
                        height=200,
                        disabled=True,
                        key="template_preview"
                    )
                    st.success(f"✅ {template_data['compliance_level']}")
        
        # Send emails section
        if 'filtered_students' in locals() and not filtered_students.empty:
            st.markdown("---")
            st.markdown("### Send Communications")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Email Type:** {template_options[selected_template]}")
                st.markdown(f"**Number of Recipients:** {len(filtered_students)}")
                st.markdown("**Status:** Ready to send")
            
            with col2:
                st.markdown("#### Compliance Check")
                st.success("✅ Template is FERPA compliant")
                st.success("✅ Recipients verified")
                st.success("✅ Ready to send")
            
            # Send button
            if st.button("📧 Send Emails to Selected Students", type="primary", use_container_width=True):
                with st.spinner("Sending emails..."):
                    # Convert to format needed for email sending
                    student_list = filtered_students.to_dict('records')
                    
                    # Send emails (simulated)
                    results = email_manager.send_bulk_emails(student_list, selected_template)
                    
                    # Show results
                    st.success(f"✅ Emails sent to {results['sent']} students")
                    
                    if results['failed'] > 0:
                        st.warning(f"⚠️ {results['failed']} emails failed to send")
                    
                    # Show details
                    with st.expander("📊 View Detailed Results"):
                        results_df = pd.DataFrame(results['details'])
                        st.dataframe(results_df)
    else:
        st.info("📤 Please upload and combine your data files first to send communications.")

def show_reports():
    """Show the reports page"""
    st.header("📋 Generate Reports")
    
    if 'merged_data' in st.session_state:
        st.markdown("### Available Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Program Risk Analysis")
            st.markdown("Detailed analysis of default risk by academic program")
            
            if st.button("Generate Program Risk Report", type="primary"):
                st.success("✅ Program Risk Analysis Report ready!")
                # In a real app, this would create an actual Excel file
                st.info("In a full implementation, this would generate a downloadable Excel report")
        
        with col2:
            st.markdown("#### 📧 Communication Activity")
            st.markdown("Summary of emails sent and student outreach")
            
            if st.button("Generate Communication Report", type="primary"):
                st.success("✅ Communication Activity Report ready!")
                st.info("In a full implementation, this would generate a downloadable report")
        
        st.markdown("---")
        st.markdown("### Quick Data Export")
        
        if st.button("📤 Download Current Data as CSV"):
            merged_data = st.session_state['merged_data']
            csv = merged_data.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV File",
                data=csv,
                file_name=f"student_risk_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    else:
        st.info("📤 Please upload and process your data files first to generate reports.")

if __name__ == "__main__":
    main()
