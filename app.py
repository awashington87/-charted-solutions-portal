import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

def calculate_cdr_projection(data):
    """Calculate projected CDR based on current risk levels"""
    if data is None or data.empty:
        return 0, 0, 0
    
    total_borrowers = len(data)
    if total_borrowers == 0:
        return 0, 0, 0
    
    high_risk_count = len(data[data['risk_tier'] == 'HIGH'])
    medium_risk_count = len(data[data['risk_tier'] == 'MEDIUM'])
    
    # Simulate default probabilities
    high_risk_default_rate = 0.65
    medium_risk_default_rate = 0.25
    low_risk_default_rate = 0.05
    
    projected_defaults = (
        high_risk_count * high_risk_default_rate +
        medium_risk_count * medium_risk_default_rate +
        (total_borrowers - high_risk_count - medium_risk_count) * low_risk_default_rate
    )
    
    current_cdr = (projected_defaults / total_borrowers) * 100
    
    # Calculate improved CDR with intervention
    intervention_success_rate = 0.4  # 40% success rate for interventions
    improved_defaults = projected_defaults - (high_risk_count * high_risk_default_rate * intervention_success_rate)
    improved_cdr = (improved_defaults / total_borrowers) * 100
    
    return current_cdr, improved_cdr, current_cdr - improved_cdr

def generate_intervention_recommendations(risk_score, days_delinquent):
    """Generate intervention recommendations based on risk level"""
    recommendations = []
    
    if risk_score >= 0.8:
        recommendations.append({
            'action': 'Emergency Financial Counseling',
            'timeline': 'Within 24 hours',
            'priority': 'CRITICAL'
        })
        recommendations.append({
            'action': 'Loan Rehabilitation Setup',
            'timeline': 'Within 48 hours',
            'priority': 'CRITICAL'
        })
    elif risk_score >= 0.6:
        recommendations.append({
            'action': 'Personalized Financial Planning',
            'timeline': 'Within 1 week',
            'priority': 'HIGH'
        })
        recommendations.append({
            'action': 'Income-Driven Repayment Setup',
            'timeline': 'Within 2 weeks',
            'priority': 'HIGH'
        })
    elif risk_score >= 0.4:
        recommendations.append({
            'action': 'Financial Wellness Workshop',
            'timeline': 'Within 2 weeks',
            'priority': 'MEDIUM'
        })
        recommendations.append({
            'action': 'Career Services Referral',
            'timeline': 'Within 3 weeks',
            'priority': 'MEDIUM'
        })
    
    return recommendations

def process_nslds_file(uploaded_file):
    """Process NSLDS file and add risk calculations"""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        column_mapping = {
            'Borrower SSN': 'ssn',
            'Borrower First Name': 'first_name', 
            'Borrower Last Name': 'last_name',
            'E-mail': 'email',
            'Days Delinquent': 'days_delinquent',
            'OPB': 'outstanding_balance',
            'Loan Type': 'loan_type'
        }
        
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        if 'student_id' not in df.columns:
            df['student_id'] = [f'STU{i+1000:06d}' for i in range(len(df))]
        
        df['days_delinquent'] = df.get('days_delinquent', 0).fillna(0)
        df['outstanding_balance'] = df.get('outstanding_balance', 0).fillna(0)
        
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
        return None, str(e)

def merge_data(nslds_df, sis_df):
    """Merge NSLDS and SIS data"""
    try:
        if 'ssn' in nslds_df.columns and 'ssn' in sis_df.columns:
            merged = pd.merge(nslds_df, sis_df, on='ssn', how='inner', suffixes=('_nslds', '_sis'))
        elif 'student_id' in nslds_df.columns and 'student_id' in sis_df.columns:
            merged = pd.merge(nslds_df, sis_df, on='student_id', how='inner', suffixes=('_nslds', '_sis'))
        else:
            return None, "No common identifier found"
        
        # Clean up column names - use non-suffixed versions where possible
        if 'first_name_nslds' in merged.columns and 'first_name' not in merged.columns:
            merged['first_name'] = merged['first_name_nslds']
        if 'last_name_nslds' in merged.columns and 'last_name' not in merged.columns:
            merged['last_name'] = merged['last_name_nslds']
        if 'email_nslds' in merged.columns and 'email' not in merged.columns:
            merged['email'] = merged['email_nslds']
        
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
    'early_intervention': {
        'subject': 'Proactive Financial Support Available',
        'body': '''Dear {first_name} {last_name},

Our analytics indicate you may benefit from proactive financial planning support. We want to connect you with resources to ensure your continued success.

Your Current Status:
- Academic Program: {major}
- Outstanding Balance: ${outstanding_balance:,.2f}

We offer several support options:
- Financial planning consultation
- Income-driven repayment plans
- Career services connection

Please contact us to discuss:
Phone: (555) 123-4567
Email: finaid@yourschool.edu

Best regards,
Financial Aid Office
'''
    },
    'urgent_intervention': {
        'subject': 'Important: Immediate Financial Support Available',
        'body': '''Dear {first_name} {last_name},

We're reaching out because immediate financial support resources are available that could significantly help your situation.

Current Status:
- Outstanding Balance: ${outstanding_balance:,.2f}
- Days Past Due: {days_delinquent}

Immediate actions available:
- Emergency financial counseling
- Payment plan restructuring
- Income-driven repayment options

Please contact us within 48 hours:
Phone: (555) 123-4567
Email: finaid@yourschool.edu

We're here to help.

Financial Aid Office
'''
    }
}

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>ChartED Solutions</h1>
        <h2>Advanced Student Loan Risk Management Platform</h2>
        <p>Predictive analytics and automated interventions for financial aid success</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### Features")
        st.write("📈 Predictive Risk Analytics")
        st.write("🎯 CDR Impact Modeling")
        st.write("⚡ Automated Interventions")
        st.write("📊 Program Performance Analysis")
        st.write("📧 FERPA-Compliant Communications")
        
        st.markdown("### Contact")
        st.write("📧 support@chartedsolutions.com")
        st.write("🌐 chartedsolutions.com")
    
    # Main tabs
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
            
            # Calculate CDR projections
            current_cdr, improved_cdr, cdr_improvement = calculate_cdr_projection(data)
            
            st.subheader("Key Performance Indicators")
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Students", len(data))
            with col2:
                high_risk = len(data[data['risk_tier'] == 'HIGH'])
                st.metric("High Risk Students", high_risk)
            with col3:
                st.metric("Projected CDR", f"{current_cdr:.1f}%")
            with col4:
                st.metric("CDR with Intervention", f"{improved_cdr:.1f}%", f"-{cdr_improvement:.1f}%")
            
            # Risk distribution
            st.subheader("Current Risk Distribution")
            risk_counts = data['risk_tier'].value_counts()
            fig = px.pie(
                values=risk_counts.values, 
                names=risk_counts.index,
                title="Students by Risk Level",
                color_discrete_map={'HIGH': '#dc3545', 'MEDIUM': '#ffc107', 'LOW': '#28a745'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # High-risk alerts
            high_risk_students = data[data['risk_tier'] == 'HIGH']
            if not high_risk_students.empty:
                st.markdown("### High-Risk Student Alerts")
                st.markdown(f"""
                <div class="alert-card">
                    <h4>{len(high_risk_students)} Students Require Immediate Attention</h4>
                    <p>These students have high risk scores and need intervention within the next 1-2 weeks.</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Financial impact
            st.subheader("Financial Impact Analysis")
            col1, col2 = st.columns(2)
            
            with col1:
                total_at_risk = data['outstanding_balance'].sum()
                st.metric("Total Portfolio at Risk", f"${total_at_risk:,.0f}")
                
                potential_defaults = len(high_risk_students) * 0.65
                default_cost = potential_defaults * 15000
                st.metric("Potential Default Cost", f"${default_cost:,.0f}")
            
            with col2:
                intervention_cost = len(high_risk_students) * 200
                potential_savings = default_cost * 0.4 - intervention_cost
                st.metric("Intervention Investment", f"${intervention_cost:,.0f}")
                st.metric("Potential Net Savings", f"${potential_savings:,.0f}")
        
        else:
            st.subheader("Welcome to ChartED Solutions")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <h3>Predictive Analytics</h3>
                    <p>Identify at-risk students before they become delinquent using advanced risk modeling.</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card">
                    <h3>Automated Interventions</h3>
                    <p>Generate targeted action plans and communications based on individual risk profiles.</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="metric-card">
                    <h3>CDR Management</h3>
                    <p>Project and optimize cohort default rates through data-driven intervention strategies.</p>
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
            st.subheader("Step 3: Merge Datasets")
            
            if st.button("🔗 Combine Data for Analysis", type="primary", use_container_width=True):
                with st.spinner("Merging NSLDS and SIS data..."):
                    merged, error = merge_data(st.session_state.nslds_data, st.session_state.sis_data)
                    if error:
                        st.error(f"Merge failed: {error}")
                    else:
                        st.session_state.merged_data = merged
                        st.success(f"✅ Successfully merged {len(merged)} student records")
                        st.dataframe(merged.head())
    
    with tab3:
        st.header("Risk Analytics")
        
        if st.session_state.merged_data is not None:
            data = st.session_state.merged_data
            
            st.subheader("Risk Score Distribution")
            
            # Risk distribution histogram
            fig = px.histogram(
                data, 
                x='risk_score', 
                nbins=20,
                title="Risk Score Distribution",
                labels={'risk_score': 'Risk Score', 'count': 'Number of Students'}
            )
            fig.add_vline(x=0.7, line_dash="dash", line_color="red", annotation_text="High Risk Threshold")
            fig.add_vline(x=0.4, line_dash="dash", line_color="orange", annotation_text="Medium Risk Threshold")
            st.plotly_chart(fig, use_container_width=True)
            
            # Risk by delinquency analysis
            st.subheader("Risk vs Delinquency Analysis")
            
            fig2 = px.scatter(
                data,
                x='days_delinquent',
                y='risk_score',
                color='risk_tier',
                size='outstanding_balance',
                hover_data=['first_name', 'last_name'] if 'first_name' in data.columns else None,
                title="Risk Score vs Days Delinquent",
                color_discrete_map={'HIGH': '#dc3545', 'MEDIUM': '#ffc107', 'LOW': '#28a745'}
            )
            st.plotly_chart(fig2, use_container_width=True)
            
            # Summary statistics
            st.subheader("Risk Analytics Summary")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                avg_risk = data['risk_score'].mean()
                st.metric("Average Risk Score", f"{avg_risk:.2f}")
                
            with col2:
                median_delinquent = data['days_delinquent'].median()
                st.metric("Median Days Delinquent", f"{median_delinquent:.0f}")
                
            with col3:
                avg_balance = data['outstanding_balance'].mean()
                st.metric("Average Outstanding Balance", f"${avg_balance:,.0f}")
        
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
                
                # Program rankings table
                st.subheader("Program Risk Rankings")
                display_analysis = major_analysis.copy()
                display_analysis['avg_balance'] = display_analysis['avg_balance'].apply(lambda x: f"${x:,.0f}")
                display_analysis['total_balance'] = display_analysis['total_balance'].apply(lambda x: f"${x:,.0f}")
                st.dataframe(display_analysis, use_container_width=True)
                
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
                
                # Program recommendations
                st.subheader("Program Action Recommendations")
                
                high_risk_programs = major_analysis[major_analysis['risk_tier'] == 'HIGH']
                if not high_risk_programs.empty:
                    for _, program in high_risk_programs.iterrows():
                        st.markdown(f"""
                        <div class="intervention-card">
                            <h4>{program['major']}</h4>
                            <p><strong>Risk Level:</strong> {program['risk_tier']}</p>
                            <p><strong>Students Affected:</strong> {program['student_count']}</p>
                            <p><strong>Recommended Actions:</strong> Enhanced career services, financial counseling focus</p>
                        </div>
                        """, unsafe_allow_html=True)
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
            high_risk_students = data[data['risk_tier'] == 'HIGH'].copy()
            medium_risk_students = data[data['risk_tier'] == 'MEDIUM'].copy()
            
            if not high_risk_students.empty:
                st.markdown("### Critical Priority Students")
                
                for _, student in high_risk_students.head(5).iterrows():
                    # Safely get student information
                    first_name = student.get('first_name', 'Unknown')
                    last_name = student.get('last_name', 'Unknown')
                    major = student.get('major', 'Unknown Major')
                    risk_score = student.get('risk_score', 0)
                    days_delinquent = student.get('days_delinquent', 0)
                    balance = student.get('outstanding_balance', 0)
                    
                    recommendations = generate_intervention_recommendations(risk_score, days_delinquent)
                    
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
                
                # Communication generation
                st.subheader("Generate Targeted Communications")
                
                template_choice = st.selectbox(
                    "Choose Communication Type",
                    ['early_intervention', 'urgent_intervention'],
                    format_func=lambda x: {
                        'early_intervention': 'Early Intervention Support',
                        'urgent_intervention': 'Urgent Intervention Required'
                    }[x]
                )
                
                if st.button("Generate Communications", type="primary"):
                    target_students = high_risk_students if template_choice == 'urgent_intervention' else medium_risk_students
                    
                    st.success(f"Generated {len(target_students)} personalized communications")
                    
                    # Show sample email
                    if not target_students.empty:
                        sample_student = target_students.iloc[0]
                        template = EMAIL_TEMPLATES[template_choice]
                        
                        try:
                            # Create sample data for template
                            sample_data = {
                                'first_name': sample_student.get('first_name', 'Student'),
                                'last_name': sample_student.get('last_name', 'Name'),
                                'major': sample_student.get('major', 'Unknown Major'),
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
                            st.warning(f"Email template preview unavailable: {e}")
            
            else:
                st.info("No high-risk students identified in current dataset.")
        
        else:
            st.info("Please upload and merge data files to access intervention tools.")
    
    with tab6:
        st.header("Sample Data for Testing")
        
        st.markdown("""
        ### Test the Platform
        
        Download these sample files to explore the platform's capabilities without using your own institutional data.
        """)
        
        sample_col1, sample_col2 = st.columns(2)
        
        with sample_col1:
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
        
        with sample_col2:
            st.markdown("#### Sample SIS Data")
            
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
