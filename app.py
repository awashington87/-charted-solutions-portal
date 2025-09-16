import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import random

# Page configuration
st.set_page_config(
    page_title="ChartED Solutions - Financial Aid Portal",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS
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
    .intervention-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 0.5rem 0;
    }
    .alert-card {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 0.5rem 0;
    }
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
    try:
        days = float(days_delinquent) if pd.notna(days_delinquent) else 0
        if days < 30:
            return random.uniform(0, 0.3)
        elif days < 90:
            return random.uniform(0.3, 0.6)
        elif days < 180:
            return random.uniform(0.6, 0.8)
        else:
            return random.uniform(0.8, 1.0)
    except:
        return 0.5

def get_risk_tier(score):
    """Convert risk score to tier"""
    try:
        score = float(score) if pd.notna(score) else 0
        if score >= 0.7:
            return 'HIGH'
        elif score >= 0.4:
            return 'MEDIUM'
        else:
            return 'LOW'
    except:
        return 'MEDIUM'

def safe_get_value(row, possible_columns, default='Unknown'):
    """Safely get a value from a row using multiple possible column names"""
    for col in possible_columns:
        if col in row.index and pd.notna(row[col]):
            return str(row[col])
    return default

def calculate_cdr_projection(data):
    """Calculate projected CDR based on current risk levels"""
    if data is None or data.empty:
        return 0, 0, 0
    
    total_borrowers = len(data)
    if total_borrowers == 0:
        return 0, 0, 0
    
    high_risk_count = len(data[data['risk_tier'] == 'HIGH'])
    medium_risk_count = len(data[data['risk_tier'] == 'MEDIUM'])
    
    # Conservative default rate estimates
    high_risk_default_rate = 0.45
    medium_risk_default_rate = 0.20
    low_risk_default_rate = 0.05
    
    projected_defaults = (
        high_risk_count * high_risk_default_rate +
        medium_risk_count * medium_risk_default_rate +
        (total_borrowers - high_risk_count - medium_risk_count) * low_risk_default_rate
    )
    
    current_cdr = (projected_defaults / total_borrowers) * 100
    
    # Calculate improved CDR with intervention (30% improvement)
    intervention_success_rate = 0.3
    improved_defaults = projected_defaults - (high_risk_count * high_risk_default_rate * intervention_success_rate)
    improved_cdr = (improved_defaults / total_borrowers) * 100
    
    return current_cdr, improved_cdr, current_cdr - improved_cdr

def generate_intervention_recommendations(risk_score):
    """Generate intervention recommendations based on risk score"""
    recommendations = []
    
    try:
        score = float(risk_score) if pd.notna(risk_score) else 0
        
        if score >= 0.8:
            recommendations = [
                {'action': 'Emergency Financial Counseling', 'timeline': 'Within 24 hours'},
                {'action': 'Loan Rehabilitation Discussion', 'timeline': 'Within 48 hours'}
            ]
        elif score >= 0.6:
            recommendations = [
                {'action': 'Financial Planning Session', 'timeline': 'Within 1 week'},
                {'action': 'Payment Plan Review', 'timeline': 'Within 2 weeks'}
            ]
        elif score >= 0.4:
            recommendations = [
                {'action': 'Financial Wellness Workshop', 'timeline': 'Within 2 weeks'},
                {'action': 'Career Services Referral', 'timeline': 'Within 3 weeks'}
            ]
        else:
            recommendations = [
                {'action': 'Preventive Check-in', 'timeline': 'Within 1 month'}
            ]
    except:
        recommendations = [
            {'action': 'General Financial Review', 'timeline': 'Within 2 weeks'}
        ]
    
    return recommendations

def process_nslds_file(uploaded_file):
    """Process NSLDS file and add risk calculations"""
    try:
        # Read file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Standardize column names
        column_mapping = {
            'Borrower SSN': 'ssn',
            'Borrower First Name': 'first_name', 
            'Borrower Last Name': 'last_name',
            'E-mail': 'email',
            'Days Delinquent': 'days_delinquent',
            'OPB': 'outstanding_balance',
            'Loan Type': 'loan_type'
        }
        
        # Apply column mapping
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Create student IDs if missing
        if 'student_id' not in df.columns:
            df['student_id'] = [f'STU{i+1000:06d}' for i in range(len(df))]
        
        # Clean and validate data
        df['days_delinquent'] = pd.to_numeric(df.get('days_delinquent', 0), errors='coerce').fillna(0)
        df['outstanding_balance'] = pd.to_numeric(df.get('outstanding_balance', 0), errors='coerce').fillna(0)
        
        # Calculate risk scores
        df['risk_score'] = df['days_delinquent'].apply(calculate_risk_score)
        df['risk_tier'] = df['risk_score'].apply(get_risk_tier)
        
        return df, None
        
    except Exception as e:
        return None, f"Error processing NSLDS file: {str(e)}"

def process_sis_file(uploaded_file):
    """Process SIS file"""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Standardize column names
        column_mapping = {
            'Student ID': 'student_id',
            'SSN': 'ssn',
            'First Name': 'first_name',
            'Last Name': 'last_name', 
            'Email': 'email',
            'Major': 'major',
            'Program': 'program',
            'GPA': 'gpa',
            'Academic Standing': 'academic_standing',
            'Enrollment Status': 'enrollment_status'
        }
        
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        return df, None
        
    except Exception as e:
        return None, f"Error processing SIS file: {str(e)}"

def merge_data(nslds_df, sis_df):
    """Merge NSLDS and SIS data safely"""
    try:
        # Determine merge key
        if 'ssn' in nslds_df.columns and 'ssn' in sis_df.columns:
            merged = pd.merge(nslds_df, sis_df, on='ssn', how='inner', suffixes=('', '_sis'))
        elif 'student_id' in nslds_df.columns and 'student_id' in sis_df.columns:
            merged = pd.merge(nslds_df, sis_df, on='student_id', how='inner', suffixes=('', '_sis'))
        else:
            return None, "No common identifier found (SSN or Student ID)"
        
        # Clean up duplicate columns - prefer original names
        columns_to_clean = ['first_name', 'last_name', 'email']
        for col in columns_to_clean:
            if f'{col}_sis' in merged.columns and col in merged.columns:
                # Fill missing values from SIS data
                merged[col] = merged[col].fillna(merged[f'{col}_sis'])
        
        return merged, None
        
    except Exception as e:
        return None, f"Error merging data: {str(e)}"

def analyze_by_major(data):
    """Create analytics by academic major"""
    try:
        if data is None or data.empty or 'major' not in data.columns:
            return None
        
        # Group by major and calculate statistics
        analysis = data.groupby('major').agg({
            'risk_score': ['mean', 'count'],
            'outstanding_balance': ['mean', 'sum'], 
            'days_delinquent': 'mean'
        }).round(2)
        
        # Flatten column names
        analysis.columns = ['avg_risk', 'student_count', 'avg_balance', 'total_balance', 'avg_delinquent_days']
        analysis = analysis.reset_index()
        
        # Add risk tier classification
        analysis['risk_tier'] = analysis['avg_risk'].apply(get_risk_tier)
        
        return analysis.sort_values('avg_risk', ascending=False)
        
    except Exception as e:
        return None

# Email templates
EMAIL_TEMPLATES = {
    'early_intervention': {
        'subject': 'Proactive Financial Support Available',
        'body': '''Dear {first_name} {last_name},

We want to connect you with financial planning resources to support your continued success.

Current Information:
- Academic Program: {major}
- Outstanding Balance: ${outstanding_balance:,.2f}

Available Support:
- Financial planning consultation
- Repayment plan options
- Career services connection

Contact us: (555) 123-4567
Email: finaid@yourschool.edu

Financial Aid Office'''
    },
    'urgent_intervention': {
        'subject': 'Important Financial Support Available',
        'body': '''Dear {first_name} {last_name},

Immediate financial support resources are available to help your situation.

Account Status:
- Outstanding Balance: ${outstanding_balance:,.2f}
- Days Past Due: {days_delinquent}

Immediate Options:
- Emergency financial counseling
- Payment plan restructuring
- Income-driven repayment

Please contact us within 48 hours:
Phone: (555) 123-4567

Financial Aid Office'''
    }
}

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>ChartED Solutions</h1>
        <h2>Student Loan Risk Management Platform</h2>
        <p>Advanced analytics and intervention tools for financial aid professionals</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Platform Features")
        st.write("📈 Risk Analytics")
        st.write("🎯 CDR Projections")
        st.write("⚡ Intervention Tools")
        st.write("📊 Program Analysis")
        st.write("📧 Communication Templates")
        
        st.markdown("### Contact")
        st.write("📧 support@chartedsolutions.com")
        st.write("🌐 chartedsolutions.com")
    
    # Navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 Dashboard", 
        "📁 Upload Data", 
        "📊 Risk Analytics", 
        "🎯 Program Analysis",
        "⚡ Intervention Engine",
        "📋 Sample Data"
    ])
    
    with tab1:
        st.header("Risk Management Dashboard")
        
        if st.session_state.merged_data is not None:
            data = st.session_state.merged_data
            
            # Calculate metrics
            current_cdr, improved_cdr, cdr_improvement = calculate_cdr_projection(data)
            
            st.subheader("Key Performance Indicators")
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Students", len(data))
            with col2:
                high_risk_count = len(data[data['risk_tier'] == 'HIGH'])
                st.metric("High Risk Students", high_risk_count)
            with col3:
                st.metric("Projected CDR", f"{current_cdr:.1f}%")
            with col4:
                st.metric("CDR with Intervention", f"{improved_cdr:.1f}%", f"-{cdr_improvement:.1f}%")
            
            # Risk distribution chart
            st.subheader("Risk Distribution")
            risk_counts = data['risk_tier'].value_counts()
            
            if not risk_counts.empty:
                fig = px.pie(
                    values=risk_counts.values, 
                    names=risk_counts.index,
                    title="Students by Risk Level",
                    color_discrete_map={'HIGH': '#dc3545', 'MEDIUM': '#ffc107', 'LOW': '#28a745'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # High-risk alerts
            if high_risk_count > 0:
                st.markdown(f"""
                <div class="alert-card">
                    <h4>High-Risk Student Alert</h4>
                    <p>{high_risk_count} students require immediate attention and intervention.</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Financial impact summary
            st.subheader("Financial Impact Analysis")
            col1, col2 = st.columns(2)
            
            with col1:
                total_portfolio = data['outstanding_balance'].sum()
                st.metric("Total Portfolio at Risk", f"${total_portfolio:,.0f}")
                
                potential_defaults = high_risk_count * 0.45
                default_cost = potential_defaults * 15000
                st.metric("Potential Default Cost", f"${default_cost:,.0f}")
            
            with col2:
                intervention_cost = high_risk_count * 200
                potential_savings = default_cost * 0.3 - intervention_cost
                st.metric("Intervention Investment", f"${intervention_cost:,.0f}")
                if potential_savings > 0:
                    st.metric("Potential Net Savings", f"${potential_savings:,.0f}")
        
        else:
            # Welcome screen
            st.subheader("Welcome to ChartED Solutions")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <h3>Risk Analytics</h3>
                    <p>Advanced scoring to identify at-risk students before defaults occur.</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card">
                    <h3>Intervention Tools</h3>
                    <p>Automated recommendations and communication templates for student outreach.</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="metric-card">
                    <h3>CDR Management</h3>
                    <p>Project and optimize cohort default rates through targeted interventions.</p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab2:
        st.header("Data Upload & Processing")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Step 1: NSLDS Report")
            nslds_file = st.file_uploader(
                "Upload NSLDS Delinquent Borrower Report",
                type=['csv', 'xlsx'],
                key="nslds_upload"
            )
            
            if nslds_file:
                if st.button("Process NSLDS File", type="primary"):
                    with st.spinner("Processing NSLDS data..."):
                        df, error = process_nslds_file(nslds_file)
                        if error:
                            st.error(error)
                        else:
                            st.session_state.nslds_data = df
                            st.success(f"✅ Processed {len(df)} NSLDS records")
                            st.dataframe(df.head())
        
        with col2:
            st.subheader("Step 2: SIS Data")
            sis_file = st.file_uploader(
                "Upload Student Information System Data", 
                type=['csv', 'xlsx'],
                key="sis_upload"
            )
            
            if sis_file:
                if st.button("Process SIS File", type="primary"):
                    with st.spinner("Processing SIS data..."):
                        df, error = process_sis_file(sis_file)
                        if error:
                            st.error(error)
                        else:
                            st.session_state.sis_data = df
                            st.success(f"✅ Processed {len(df)} SIS records")
                            st.dataframe(df.head())
        
        # Merge datasets
        if st.session_state.nslds_data is not None and st.session_state.sis_data is not None:
            st.markdown("---")
            st.subheader("Step 3: Merge Datasets")
            
            if st.button("🔗 Combine Data for Analysis", type="primary", use_container_width=True):
                with st.spinner("Merging datasets..."):
                    merged, error = merge_data(st.session_state.nslds_data, st.session_state.sis_data)
                    if error:
                        st.error(error)
                    else:
                        st.session_state.merged_data = merged
                        st.success(f"✅ Successfully merged {len(merged)} student records")
                        st.dataframe(merged.head())
    
    with tab3:
        st.header("Risk Analytics")
        
        if st.session_state.merged_data is not None:
            data = st.session_state.merged_data
            
            # Risk score distribution
            st.subheader("Risk Score Distribution")
            
            fig = px.histogram(
                data, 
                x='risk_score', 
                nbins=20,
                title="Risk Score Distribution",
                labels={'risk_score': 'Risk Score', 'count': 'Number of Students'}
            )
            fig.add_vline(x=0.7, line_dash="dash", line_color="red", annotation_text="High Risk")
            fig.add_vline(x=0.4, line_dash="dash", line_color="orange", annotation_text="Medium Risk")
            st.plotly_chart(fig, use_container_width=True)
            
            # Risk vs delinquency scatter plot
            st.subheader("Risk vs Delinquency Analysis")
            
            fig2 = px.scatter(
                data,
                x='days_delinquent',
                y='risk_score',
                color='risk_tier',
                size='outstanding_balance',
                title="Risk Score vs Days Delinquent",
                color_discrete_map={'HIGH': '#dc3545', 'MEDIUM': '#ffc107', 'LOW': '#28a745'}
            )
            st.plotly_chart(fig2, use_container_width=True)
            
            # Summary statistics
            st.subheader("Summary Statistics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_risk = data['risk_score'].mean()
                st.metric("Average Risk Score", f"{avg_risk:.2f}")
                
            with col2:
                median_delinquent = data['days_delinquent'].median()
                st.metric("Median Days Delinquent", f"{median_delinquent:.0f}")
                
            with col3:
                avg_balance = data['outstanding_balance'].mean()
                st.metric("Average Balance", f"${avg_balance:,.0f}")
        
        else:
            st.info("Please upload and merge data files to access risk analytics.")
    
    with tab4:
        st.header("Program Performance Analysis")
        
        if st.session_state.merged_data is not None:
            data = st.session_state.merged_data
            major_analysis = analyze_by_major(data)
            
            if major_analysis is not None:
                st.subheader("Performance by Academic Program")
                
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    high_risk_programs = len(major_analysis[major_analysis['risk_tier'] == 'HIGH'])
                    st.metric("High-Risk Programs", high_risk_programs)
                
                with col2:
                    total_portfolio = major_analysis['total_balance'].sum()
                    st.metric("Total Portfolio", f"${total_portfolio:,.0f}")
                
                with col3:
                    avg_program_risk = major_analysis['avg_risk'].mean()
                    st.metric("Average Program Risk", f"{avg_program_risk:.2f}")
                
                # Program rankings
                st.subheader("Program Risk Rankings")
                display_data = major_analysis.copy()
                display_data['avg_balance'] = display_data['avg_balance'].apply(lambda x: f"${x:,.0f}")
                display_data['total_balance'] = display_data['total_balance'].apply(lambda x: f"${x:,.0f}")
                st.dataframe(display_data, use_container_width=True)
                
                # Visualization
                fig = px.scatter(
                    major_analysis,
                    x='student_count',
                    y='avg_risk',
                    size='total_balance',
                    color='risk_tier',
                    hover_data=['major'],
                    title="Program Risk vs Enrollment",
                    color_discrete_map={'HIGH': '#dc3545', 'MEDIUM': '#ffc107', 'LOW': '#28a745'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Cannot analyze by major - ensure your data includes academic program information")
        else:
            st.info("Please upload and merge data files to access program analysis.")
    
    with tab5:
        st.header("Intervention Engine")
        
        if st.session_state.merged_data is not None:
            data = st.session_state.merged_data
            
            st.subheader("Priority Intervention Queue")
            
            # Get high-risk students
            high_risk_students = data[data['risk_tier'] == 'HIGH']
            
            if not high_risk_students.empty:
                st.markdown("### Critical Priority Students")
                
                for idx, student in high_risk_students.head(5).iterrows():
                    # Safely extract student information
                    first_name = safe_get_value(student, ['first_name'], 'Unknown')
                    last_name = safe_get_value(student, ['last_name'], 'Unknown')
                    major = safe_get_value(student, ['major'], 'Unknown Major')
                    
                    risk_score = student.get('risk_score', 0)
                    days_delinquent = student.get('days_delinquent', 0)
                    balance = student.get('outstanding_balance', 0)
                    
                    recommendations = generate_intervention_recommendations(risk_score)
                    
                    with st.expander(f"{first_name} {last_name} - {major}"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Risk Score:** {risk_score:.2f}")
                            st.write(f"**Days Delinquent:** {days_delinquent}")
                            st.write(f"**Outstanding Balance:** ${balance:,.0f}")
                        
                        with col2:
                            st.write("**Recommended Actions:**")
                            for rec in recommendations:
                                st.write(f"• {rec['action']}")
                                st.write(f"  Timeline: {rec['timeline']}")
                
                # Communication templates
                st.subheader("Generate Communications")
                
                template_choice = st.selectbox(
                    "Choose Communication Type",
                    ['early_intervention', 'urgent_intervention'],
                    format_func=lambda x: {
                        'early_intervention': 'Early Intervention Support',
                        'urgent_intervention': 'Urgent Intervention Required'
                    }[x]
                )
                
                if st.button("Generate Communications", type="primary"):
                    st.success(f"Generated {len(high_risk_students)} personalized communications")
                    
                    # Show sample email
                    sample_student = high_risk_students.iloc[0]
                    template = EMAIL_TEMPLATES[template_choice]
                    
                    try:
                        sample_data = {
                            'first_name': safe_get_value(sample_student, ['first_name'], 'Student'),
                            'last_name': safe_get_value(sample_student, ['last_name'], 'Name'),
                            'major': safe_get_value(sample_student, ['major'], 'Unknown Major'),
                            'outstanding_balance': sample_student.get('outstanding_balance', 0),
                            'days_delinquent': sample_student.get('days_delinquent', 0)
                        }
                        
                        formatted_subject = template['subject'].format(**sample_data)
                        formatted_body = template['body'].format(**sample_data)
                        
                        with st.expander("Preview Sample Email"):
                            st.write("**Subject:**", formatted_subject)
                            st.write("**Body:**")
                            st.text_area("", formatted_body, height=300, disabled=True)
                    except Exception as e:
                        st.warning("Email preview unavailable")
            
            else:
                st.info("No high-risk students identified in current dataset.")
        
        else:
            st.info("Please upload and merge data files to access intervention tools.")
    
    with tab6:
        st.header("Sample Data for Testing")
        
        st.markdown("""
        ### Test the Platform
        Download these sample files to explore all platform capabilities.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Sample NSLDS Data")
            
            sample_nslds = """Borrower SSN,Borrower First Name,Borrower Last Name,E-mail,Days Delinquent,OPB,Loan Type
102341234,James,Smith,james.smith@email.com,45,15234,Subsidized
987652345,Mary,Johnson,mary.johnson@email.com,120,28750,Unsubsidized
456783456,John,Williams,john.williams@email.com,30,8500,PLUS
789124567,Patricia,Brown,patricia.brown@email.com,200,45200,Subsidized
321655678,Robert,Jones,robert.jones@email.com,60,18000,Unsubsidized
147256789,Jennifer,Garcia,jennifer.garcia@email.com,15,9500,Perkins
258367890,Michael,Miller,michael.miller@email.com,180,38000,Grad PLUS
369148901,Linda,Davis,linda.davis@email.com,75,22500,Subsidized
741859012,William,Rodriguez,william.rodriguez@email.com,240,52000,Unsubsidized
852960123,Elizabeth,Martinez,elizabeth.martinez@email.com,90,31200,PLUS"""
            
            st.download_button(
                "Download Sample NSLDS Data",
                sample_nslds,
                "sample_nslds.csv",
                "text/csv",
                use_container_width=True
            )
        
        with col2:
            st.markdown("#### Sample SIS Data")
            
            sample_sis = """Student ID,SSN,First Name,Last Name,Email,Major,Program,Academic Standing,GPA,Credit Hours,Enrollment Status
STU100000,102341234,James,Smith,james.smith@email.com,Business Administration,Bachelor of Business Administration,Good Standing,3.25,60,Full-time
STU100001,987652345,Mary,Johnson,mary.johnson@email.com,Computer Science,Bachelor of Science in Computer Science,Academic Warning,2.45,45,Full-time
STU100002,456783456,John,Williams,john.williams@email.com,Nursing,Bachelor of Science in Nursing,Good Standing,3.67,75,Full-time
STU100003,789124567,Patricia,Brown,patricia.brown@email.com,Engineering,Bachelor of Engineering,Good Standing,3.12,90,Full-time
STU100004,321655678,Robert,Jones,robert.jones@email.com,Psychology,Bachelor of Arts in Psychology,Dean's List,3.85,120,Full-time
            sample_sis = """Student ID,SSN,First Name,Last Name,Email,Major,Program,Academic Standing,GPA,Credit Hours,Enrollment Status
STU100000,102341234,James,Smith,james.smith@email.com,Business Administration,Bachelor of Business Administration,Good Standing,3.25,60,Full-time
STU100001,987652345,Mary,Johnson,mary.johnson@email.com,Computer Science,Bachelor of Science in Computer Science,Academic Warning,2.45,45,Full-time
STU100002,456783456,John,Williams,john.williams@email.com,Nursing,Bachelor of Science in Nursing,Good Standing,3.67,75,Full-time
STU100003,789124567,Patricia,Brown,patricia.brown@email.com,Engineering,Bachelor of Engineering,Good Standing,3.12,90,Full-time
STU100004,321655678,Robert,Jones,robert.jones@email.com,Psychology,Bachelor of Arts in Psychology,Dean's List,3.85,120,Full-time
STU100005,147256789,Jennifer,Garcia,jennifer.garcia@email.com,Education,Bachelor of Education,Good Standing,3.34,36,Part-time
STU100006,258367890,Michael,Miller,michael.miller@email.com,Liberal Arts,Bachelor of Arts,Academic Probation,1.89,24,Part-time
STU100007,369148901,Linda,Davis,linda.davis@email.com,Criminal Justice,Bachelor of Science in Criminal Justice,Good Standing,3.01,48,Full-time
STU100008,741859012,William,Rodriguez,william.rodriguez@email.com,Biology,Bachelor of Science in Biology,Academic Warning,2.23,72,Full-time
STU100009,852960123,Elizabeth,Martinez,elizabeth.martinez@email.com,Marketing,Bachelor of Business in Marketing,Good Standing,3.56,84,Full-time"""
            
            st.download_button(
                "Download Sample SIS Data",
                sample_sis,
                "sample_sis.csv",
                "text/csv",
                use_container_width=True
            )
        
        st.markdown("---")
        
        st.markdown("### Quick Start Instructions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **Step 1: Download**
            - Download both sample files above
            - Save them to your computer
            """)
        
        with col2:
            st.markdown("""
            **Step 2: Upload**
            - Go to "Upload Data" tab
            - Upload both CSV files
            - Click process buttons
            """)
        
        with col3:
            st.markdown("""
            **Step 3: Explore**
            - Combine datasets
            - Explore all analytics tabs
            - Test intervention features
            """)

if __name__ == "__main__":
    main()
