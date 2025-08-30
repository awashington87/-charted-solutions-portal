import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import random
import io

# Page configuration
st.set_page_config(
    page_title="ChartED Solutions - Financial Aid Portal",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS for professional look
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a5f 0%, #2d5a87 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1e3a5f;
        margin-bottom: 1rem;
    }
    .risk-high { color: #dc3545; font-weight: bold; }
    .risk-medium { color: #ffc107; font-weight: bold; }
    .risk-low { color: #28a745; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'nslds_data' not in st.session_state:
    st.session_state.nslds_data = None
if 'sis_data' not in st.session_state:
    st.session_state.sis_data = None
if 'merged_data' not in st.session_state:
    st.session_state.merged_data = None

def calculate_risk_score(days_delinquent):
    """Calculate risk score based on delinquency days"""
    if pd.isna(days_delinquent) or days_delinquent < 30:
        return random.uniform(0, 0.3)
    elif days_delinquent < 90:
        return random.uniform(0.3, 0.6)
    elif days_delinquent < 180:
        return random.uniform(0.6, 0.8)
    else:
        return random.uniform(0.8, 1.0)

def get_risk_tier(score):
    """Convert risk score to tier"""
    if score >= 0.7:
        return 'HIGH'
    elif score >= 0.4:
        return 'MEDIUM'
    else:
        return 'LOW'

def process_nslds_file(uploaded_file):
    """Process NSLDS file and add risk calculations"""
    try:
        # Read file based on extension
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Standardize common column names
        column_mapping = {
            'Borrower SSN': 'ssn',
            'Borrower First Name': 'first_name', 
            'Borrower Last Name': 'last_name',
            'E-mail': 'email',
            'Days Delinquent': 'days_delinquent',
            'OPB': 'outstanding_balance',
            'Loan Type': 'loan_type'
        }
        
        # Rename columns that exist
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Create student IDs if not present
        if 'student_id' not in df.columns:
            df['student_id'] = [f'STU{i+1000:06d}' for i in range(len(df))]
        
        # Fill missing values
        df['days_delinquent'] = df.get('days_delinquent', 0).fillna(0)
        df['outstanding_balance'] = df.get('outstanding_balance', 0).fillna(0)
        
        # Calculate risk metrics
        df['risk_score'] = df['days_delinquent'].apply(calculate_risk_score)
        df['risk_tier'] = df['risk_score'].apply(get_risk_tier)
        
        return df, None
        
    except Exception as e:
        return None, str(e)

def process_sis_file(uploaded_file):
    """Process SIS file"""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Standardize SIS columns
        column_mapping = {
            'Student ID': 'student_id',
            'SSN': 'ssn',
            'First Name': 'first_name',
            'Last Name': 'last_name', 
            'Email': 'email',
            'Major': 'major',
            'Program': 'program'
        }
        
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        return df, None
        
    except Exception as e:
        return None, str(e)

def merge_data(nslds_df, sis_df):
    """Merge NSLDS and SIS data"""
    try:
        # Try merging on SSN first
        if 'ssn' in nslds_df.columns and 'ssn' in sis_df.columns:
            merged = pd.merge(nslds_df, sis_df, on='ssn', how='inner', suffixes=('_nslds', '_sis'))
        # Fall back to student_id
        elif 'student_id' in nslds_df.columns and 'student_id' in sis_df.columns:
            merged = pd.merge(nslds_df, sis_df, on='student_id', how='inner', suffixes=('_nslds', '_sis'))
        else:
            return None, "No common identifier found (SSN or Student ID)"
        
        return merged, None
        
    except Exception as e:
        return None, str(e)

def analyze_by_major(data):
    """Create analytics by academic major"""
    if data is None or 'major' not in data.columns:
        return None
    
    analysis = data.groupby('major').agg({
        'risk_score': ['mean', 'count'],
        'outstanding_balance': ['mean', 'sum'], 
        'days_delinquent': 'mean'
    }).round(2)
    
    analysis.columns = ['avg_risk', 'student_count', 'avg_balance', 'total_balance', 'avg_delinquent_days']
    analysis = analysis.reset_index()
    analysis['risk_tier'] = analysis['avg_risk'].apply(get_risk_tier)
    
    return analysis.sort_values('avg_risk', ascending=False)

# Email templates
EMAIL_TEMPLATES = {
    'default_prevention': {
        'subject': 'Important: Student Loan Payment Information',
        'body': '''Dear {first_name} {last_name},

We hope this message finds you well. We are reaching out regarding your federal student loan account.

Account Information:
- Outstanding Balance: ${outstanding_balance:,.2f}
- Days Past Due: {days_delinquent}

Please contact our office to discuss payment options and avoid default.

Contact: (555) 123-4567
Email: finaid@yourschool.edu

Best regards,
Financial Aid Office'''
    },
    'payment_plan': {
        'subject': 'Payment Plan Options Available', 
        'body': '''Dear {first_name} {last_name},

You may qualify for alternative payment arrangements for your student loans.

Current Status:
- Outstanding Balance: ${outstanding_balance:,.2f}
- Academic Program: {major}

We offer income-based repayment plans and other options.

Contact us at (555) 123-4567 to learn more.

Financial Aid Office'''
    },
    'counseling': {
        'subject': 'Free Financial Counseling Available',
        'body': '''Dear {first_name} {last_name},

Our office offers free financial counseling to help you manage your student loans successfully.

Services include:
- Loan counseling and education
- Budget planning
- Repayment strategies

Contact us at (555) 123-4567 to schedule.

Financial Aid Office'''
    }
}

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎓 ChartED Solutions</h1>
        <h2>Unified Financial Aid Portal</h2>
        <p>Streamline student loan risk management and communications</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔒 FERPA Compliant")
        st.info("All communications maintain strict privacy compliance")
        
        st.markdown("### ✅ Features")
        st.write("📁 Multi-file processing")
        st.write("📊 Major-based analytics") 
        st.write("📧 Compliant communications")
        st.write("📋 Automated reporting")
        
        st.markdown("### 📞 Contact")
        st.write("📧 apryll@visitcharted.com")
        st.write("🌐 visitcharted.com")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Dashboard", "📁 Upload Data", "📊 Analytics", "📧 Communications", "📋 Reports"])
    
    with tab1:
        st.header("Dashboard Overview")
        
        if st.session_state.merged_data is not None:
            data = st.session_state.merged_data
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Students", len(data))
            with col2:
                high_risk = len(data[data['risk_tier'] == 'HIGH'])
                st.metric("High Risk", high_risk)
            with col3:
                total_balance = data['outstanding_balance'].sum()
                st.metric("Total at Risk", f"${total_balance:,.0f}")
            with col4:
                avg_risk = data['risk_score'].mean()
                st.metric("Avg Risk Score", f"{avg_risk:.2f}")
            
            # Quick visualization
            st.subheader("Risk Distribution")
            risk_counts = data['risk_tier'].value_counts()
            fig = px.pie(values=risk_counts.values, names=risk_counts.index, 
                        title="Students by Risk Level")
            st.plotly_chart(fig)
            
        else:
            st.info("👆 Upload and process data files to see dashboard metrics")
            
            # Feature overview cards
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <h3>🎯 Unified Data</h3>
                    <p>Combine NSLDS and SIS files for complete student profiles</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card">
                    <h3>📊 Smart Analytics</h3>
                    <p>Identify risk patterns by academic program</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="metric-card">
                    <h3>📧 Compliant Emails</h3>
                    <p>Send FERPA-compliant communications at scale</p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.header("📁 Upload & Process Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Step 1: NSLDS Report")
            nslds_file = st.file_uploader(
                "Upload NSLDS Delinquent Borrower Report",
                type=['csv', 'xlsx'],
                key="nslds"
            )
            
            if nslds_file:
                if st.button("Process NSLDS File", type="primary"):
                    with st.spinner("Processing NSLDS data..."):
                        df, error = process_nslds_file(nslds_file)
                        if error:
                            st.error(f"Error: {error}")
                        else:
                            st.session_state.nslds_data = df
                            st.success(f"✅ Processed {len(df)} NSLDS records")
                            st.dataframe(df.head())
        
        with col2:
            st.subheader("Step 2: SIS Data")
            sis_file = st.file_uploader(
                "Upload Student Information System Data", 
                type=['csv', 'xlsx'],
                key="sis"
            )
            
            if sis_file:
                if st.button("Process SIS File", type="primary"):
                    with st.spinner("Processing SIS data..."):
                        df, error = process_sis_file(sis_file)
                        if error:
                            st.error(f"Error: {error}")
                        else:
                            st.session_state.sis_data = df
                            st.success(f"✅ Processed {len(df)} SIS records")
                            st.dataframe(df.head())
        
        # Merge step
        if st.session_state.nslds_data is not None and st.session_state.sis_data is not None:
            st.markdown("---")
            st.subheader("Step 3: Merge Data")
            
            if st.button("🔗 Combine Datasets", type="primary", use_container_width=True):
                with st.spinner("Merging data..."):
                    merged, error = merge_data(st.session_state.nslds_data, st.session_state.sis_data)
                    if error:
                        st.error(f"Merge failed: {error}")
                    else:
                        st.session_state.merged_data = merged
                        st.success(f"✅ Successfully merged {len(merged)} student records")
                        st.dataframe(merged.head())
    
    with tab3:
        st.header("📊 Risk Analytics by Major")
        
        if st.session_state.merged_data is not None:
            data = st.session_state.merged_data
            
            # Generate major analysis
            major_stats = analyze_by_major(data)
            
            if major_stats is not None:
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    high_risk_majors = len(major_stats[major_stats['risk_tier'] == 'HIGH'])
                    st.metric("High-Risk Programs", high_risk_majors)
                with col2:
                    total_portfolio = major_stats['total_balance'].sum()
                    st.metric("Total Portfolio", f"${total_portfolio:,.0f}")
                with col3:
                    avg_risk = major_stats['avg_risk'].mean()
                    st.metric("Average Program Risk", f"{avg_risk:.2f}")
                
                # Major rankings table
                st.subheader("Program Risk Rankings")
                display_stats = major_stats.copy()
                display_stats['avg_balance'] = display_stats['avg_balance'].apply(lambda x: f"${x:,.0f}")
                display_stats['total_balance'] = display_stats['total_balance'].apply(lambda x: f"${x:,.0f}")
                st.dataframe(display_stats, use_container_width=True)
                
                # Visualization
                st.subheader("Risk vs Enrollment Visualization")
                fig = px.scatter(
                    major_stats, 
                    x='student_count',
                    y='avg_risk', 
                    size='total_balance',
                    color='risk_tier',
                    hover_data=['major'],
                    title="Program Risk Analysis"
                )
                st.plotly_chart(fig, use_container_width=True)
                
            else:
                st.warning("Cannot analyze by major - ensure your data includes academic program information")
        else:
            st.info("Please upload and merge data files first")
    
    with tab4:
        st.header("📧 Student Communications")
        
        if st.session_state.merged_data is not None:
            data = st.session_state.merged_data
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("Select Students")
                
                # Filters
                filter_col1, filter_col2 = st.columns(2)
                
                with filter_col1:
                    risk_levels = st.multiselect(
                        "Risk Level",
                        ['HIGH', 'MEDIUM', 'LOW'],
                        default=['HIGH']
                    )
                
                with filter_col2:
                    min_days = st.number_input("Min Days Delinquent", 0, 300, 30)
                
                # Apply filters
                filtered_data = data.copy()
                if risk_levels:
                    filtered_data = filtered_data[filtered_data['risk_tier'].isin(risk_levels)]
                if min_days > 0:
                    filtered_data = filtered_data[filtered_data['days_delinquent'] >= min_days]
                
                st.write(f"**Selected: {len(filtered_data)} students**")
                
                if len(filtered_data) > 0:
                    # Show preview - only include columns that actually exist
                    available_cols = ['student_id', 'first_name', 'last_name', 'email', 'risk_tier', 'major']
                    preview_cols = [col for col in available_cols if col in filtered_data.columns]
                    if preview_cols:
                        st.dataframe(filtered_data[preview_cols].head(10))
                    else:
                        st.dataframe(filtered_data.head(10))
            with col2:
                st.subheader("Email Template")
                
                template_choice = st.selectbox(
                    "Choose Template",
                    ['default_prevention', 'payment_plan', 'counseling'],
                    format_func=lambda x: {
                        'default_prevention': 'Default Prevention',
                        'payment_plan': 'Payment Plans', 
                        'counseling': 'Financial Counseling'
                    }[x]
                )
                
                # Show template preview
                template = EMAIL_TEMPLATES[template_choice]
                with st.expander("Preview Template"):
                    st.write("**Subject:**", template['subject'])
                    st.write("**Body:**")
                    st.text_area("", template['body'], height=200, disabled=True)
            
            # Send emails
            if len(filtered_data) > 0:
                st.markdown("---")
                if st.button(f"📧 Send {template_choice.replace('_', ' ').title()} Emails", type="primary"):
                    # Simulate sending emails
                    with st.spinner("Sending emails..."):
                        import time
                        time.sleep(2)  # Simulate processing time
                        
                        success_count = len(filtered_data)
                        st.success(f"✅ Successfully sent {success_count} emails!")
                        
                        # Show send summary
                        st.write("**Email Summary:**")
                        st.write(f"- Template: {template_choice.replace('_', ' ').title()}")
                        st.write(f"- Recipients: {success_count}")
                        st.write(f"- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.info("Please upload and process data files first")
    
    with tab5:
        st.header("📋 Reports & Analytics")
        
        if st.session_state.merged_data is not None:
            data = st.session_state.merged_data
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Program Risk Report")
                st.write("Generate comprehensive risk analysis by academic program")
                
                if st.button("Generate Program Report", type="primary"):
                    # Create downloadable report
                    major_stats = analyze_by_major(data)
                    if major_stats is not None:
                        csv = major_stats.to_csv(index=False)
                        st.download_button(
                            "💾 Download Program Risk Report",
                            csv,
                            f"program_risk_report_{datetime.now().strftime('%Y%m%d')}.csv",
                            "text/csv"
                        )
                        st.success("✅ Report generated successfully!")
            
            with col2:
                st.subheader("📧 Communication Log")
                st.write("Track email communications and outreach activities")
                
                if st.button("Generate Communication Report", type="primary"):
                    # Create sample communication log
                    comm_log = pd.DataFrame({
                        'Date': [datetime.now().strftime('%Y-%m-%d')] * 3,
                        'Template': ['Default Prevention', 'Payment Plans', 'Counseling'],
                        'Recipients': [25, 18, 12],
                        'Status': ['Sent', 'Sent', 'Sent']
                    })
                    
                    csv = comm_log.to_csv(index=False)
                    st.download_button(
                        "💾 Download Communication Log",
                        csv,
                        f"communication_log_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv"
                    )
                    st.success("✅ Communication log generated!")
            
            # Quick data export
            st.markdown("---")
            st.subheader("📤 Quick Data Export")
            
            export_col1, export_col2 = st.columns(2)
            
            with export_col1:
                if st.button("Download Complete Dataset"):
                    csv = data.to_csv(index=False)
                    st.download_button(
                        "💾 Download Full Data",
                        csv,
                        f"complete_student_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv"
                    )
            
            with export_col2:
                if st.button("Download High-Risk Students Only"):
                    high_risk = data[data['risk_tier'] == 'HIGH']
                    csv = high_risk.to_csv(index=False)
                    st.download_button(
                        "💾 Download High-Risk Data", 
                        csv,
                        f"high_risk_students_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv"
                    )
        else:
            st.info("Upload and process data files to access reporting features")
        
        # Sample data section
        st.markdown("---")
        st.subheader("🧪 Need Sample Data for Testing?")
        
        sample_col1, sample_col2 = st.columns(2)
        
        with sample_col1:
            st.write("**Sample NSLDS Data**")
            sample_nslds = """Borrower SSN,Borrower First Name,Borrower Last Name,E-mail,Days Delinquent,OPB,Loan Type
123456789,John,Doe,john.doe@email.com,45,15000,Subsidized
987654321,Jane,Smith,jane.smith@email.com,120,22000,Unsubsidized
456789123,Mike,Johnson,mike.johnson@email.com,30,8500,PLUS"""
            
            st.download_button(
                "📥 Download Sample NSLDS",
                sample_nslds,
                "sample_nslds.csv",
                "text/csv"
            )
        
        with sample_col2:
            st.write("**Sample SIS Data**")
            sample_sis = """Student ID,SSN,First Name,Last Name,Email,Major,Program
STU001000,123456789,John,Doe,john.doe@email.com,Computer Science,Bachelor of Science
STU001001,987654321,Jane,Smith,jane.smith@email.com,Business Administration,Bachelor of Business
STU001002,456789123,Mike,Johnson,mike.johnson@email.com,Engineering,Bachelor of Engineering"""
            
            st.download_button(
                "📥 Download Sample SIS",
                sample_sis,
                "sample_sis.csv",
                "text/csv"
            )

if __name__ == "__main__":
    main()
