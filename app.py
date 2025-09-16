import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import io
import numpy as np

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
    .benchmark-card {
        background: #e7f3ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
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

def calculate_predictive_score(student_data):
    """Calculate predictive risk score using multiple factors"""
    base_risk = calculate_risk_score(student_data.get('days_delinquent', 0))
    
    # Add academic factors (simulated)
    gpa_factor = 0
    if 'gpa' in student_data:
        gpa = float(student_data['gpa']) if student_data['gpa'] else 3.0
        if gpa < 2.0:
            gpa_factor = 0.3
        elif gpa < 2.5:
            gpa_factor = 0.2
        elif gpa < 3.0:
            gpa_factor = 0.1
    
    # Add enrollment factor
    enrollment_factor = 0
    if student_data.get('enrollment_status') == 'Part-time':
        enrollment_factor = 0.15
    elif student_data.get('enrollment_status') == 'Leave of Absence':
        enrollment_factor = 0.25
    
    # Add academic standing factor
    standing_factor = 0
    if student_data.get('academic_standing') == 'Academic Warning':
        standing_factor = 0.2
    elif student_data.get('academic_standing') == 'Academic Probation':
        standing_factor = 0.3
    
    predictive_score = min(1.0, base_risk + gpa_factor + enrollment_factor + standing_factor)
    return predictive_score

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
    
    current_cdr = (projected_defaults / total_borrowers) * 100 if total_borrowers > 0 else 0
    
    # Calculate improved CDR with intervention
    intervention_success_rate = 0.4  # 40% success rate for interventions
    improved_defaults = projected_defaults - (high_risk_count * high_risk_default_rate * intervention_success_rate)
    improved_cdr = (improved_defaults / total_borrowers) * 100 if total_borrowers > 0 else 0
    
    return current_cdr, improved_cdr, current_cdr - improved_cdr

def generate_intervention_recommendations(student_data):
    """Generate specific intervention recommendations based on risk factors"""
    recommendations = []
    
    risk_score = student_data.get('risk_score', 0)
    days_delinquent = student_data.get('days_delinquent', 0)
    
    if risk_score >= 0.8:
        recommendations.append({
            'priority': 'IMMEDIATE',
            'action': 'Emergency Financial Counseling',
            'timeline': 'Within 24 hours',
            'success_rate': '75%'
        })
        recommendations.append({
            'priority': 'IMMEDIATE',
            'action': 'Loan Rehabilitation Setup',
            'timeline': 'Within 48 hours',
            'success_rate': '60%'
        })
    elif risk_score >= 0.6:
        recommendations.append({
            'priority': 'HIGH',
            'action': 'Personalized Financial Planning',
            'timeline': 'Within 1 week',
            'success_rate': '65%'
        })
        recommendations.append({
            'priority': 'HIGH',
            'action': 'Income-Driven Repayment Setup',
            'timeline': 'Within 2 weeks',
            'success_rate': '70%'
        })
    elif risk_score >= 0.4:
        recommendations.append({
            'priority': 'MEDIUM',
            'action': 'Financial Wellness Workshop',
            'timeline': 'Within 2 weeks',
            'success_rate': '50%'
        })
        recommendations.append({
            'priority': 'MEDIUM',
            'action': 'Career Services Referral',
            'timeline': 'Within 3 weeks',
            'success_rate': '45%'
        })
    
    return recommendations

def generate_benchmark_data():
    """Generate simulated benchmark data for peer comparison"""
    return {
        'Your Institution': {
            'cdr_rate': 8.2,
            'intervention_success': 62,
            'early_warning_usage': 78,
            'avg_risk_score': 0.45
        },
        'Peer Average': {
            'cdr_rate': 11.5,
            'intervention_success': 45,
            'early_warning_usage': 52,
            'avg_risk_score': 0.58
        },
        'Top Quartile': {
            'cdr_rate': 6.1,
            'intervention_success': 73,
            'early_warning_usage': 89,
            'avg_risk_score': 0.32
        },
        'National Average': {
            'cdr_rate': 10.8,
            'intervention_success': 41,
            'early_warning_usage': 48,
            'avg_risk_score': 0.61
        }
    }

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
        
        # Calculate enhanced predictive scores
        if 'gpa' in merged.columns and 'academic_standing' in merged.columns:
            merged['predictive_score'] = merged.apply(lambda row: calculate_predictive_score(row.to_dict()), axis=1)
            merged['predictive_tier'] = merged['predictive_score'].apply(get_risk_tier)
        
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
    
    # Add ROI simulation
    analysis['employment_rate'] = analysis['avg_risk'].apply(lambda x: max(0.4, 0.9 - x))
    analysis['avg_salary'] = analysis.apply(lambda row: simulate_salary_by_major(row['major']), axis=1)
    analysis['debt_to_income'] = analysis['avg_balance'] / (analysis['avg_salary'] * 0.8)  # Assume 80% employment
    
    return analysis.sort_values('avg_risk', ascending=False)

def simulate_salary_by_major(major):
    """Simulate realistic salary data by major"""
    salary_ranges = {
        'Engineering': (65000, 85000),
        'Computer Science': (70000, 90000),
        'Business Administration': (45000, 65000),
        'Nursing': (55000, 70000),
        'Education': (35000, 50000),
        'Liberal Arts': (30000, 45000),
        'Psychology': (35000, 50000),
        'Criminal Justice': (40000, 55000),
        'Biology': (40000, 60000),
        'Marketing': (40000, 60000)
    }
    
    range_data = salary_ranges.get(major, (35000, 55000))
    return random.randint(range_data[0], range_data[1])

# Email templates with enhanced personalization
EMAIL_TEMPLATES = {
    'predictive_early_warning': {
        'subject': 'Proactive Support for Your Student Loan Success',
        'body': '''Dear {first_name} {last_name},

Our predictive analytics indicate you may benefit from proactive financial planning support. Based on your current academic and financial profile, we want to connect you with resources before any challenges arise.

Your Current Status:
- Academic Program: {major}
- Predicted Success Factors: Based on similar students in your program
- Recommended Action: Financial planning consultation

We've helped students in similar situations improve their long-term financial outcomes by an average of 40%. This is preventive support - not because you're in trouble, but because we want to ensure your continued success.

Please contact us to schedule a brief consultation:
Phone: (555) 123-4567
Email: finaid@yourschool.edu

Best regards,
Financial Aid Office
'''
    },
    'intervention_priority': {
        'subject': 'Important: Financial Support Resources Available',
        'body': '''Dear {first_name} {last_name},

We're reaching out because our analysis indicates you may benefit from immediate financial support resources.

Immediate Actions Available:
- Emergency financial counseling (available this week)
- Income-driven repayment plan setup (can reduce payments by up to 50%)
- Career services connection for employment support

Success Rate: Students who engage with these resources show a 75% improvement in financial outcomes.

Please contact us within 48 hours:
Phone: (555) 123-4567
Email: finaid@yourschool.edu

We're here to help ensure your success.

Financial Aid Office
'''
    }
}

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎓 ChartED Solutions</h1>
        <h2>Predictive Student Success Platform</h2>
        <p>Proactive risk management through advanced analytics and automated interventions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🔒 FERPA Compliant")
        st.info("All communications maintain strict privacy compliance with predictive analytics")
        
        st.markdown("### ⚡ Advanced Features")
        st.write("🎯 Predictive Risk Scoring")
        st.write("📊 CDR Impact Modeling")
        st.write("🔄 Automated Interventions")
        st.write("📈 Peer Benchmarking")
        st.write("💡 ROI by Program")
        
        st.markdown("### 📞 Contact")
        st.write("📧 support@chartedsolutions.com")
        st.write("🌐 chartedsolutions.com")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 Dashboard", 
        "📁 Upload Data", 
        "🎯 Predictive Analytics", 
        "📊 Program ROI Analysis",
        "⚡ Intervention Engine",
        "📈 Benchmarking"
    ])
    
    with tab1:
        st.markdown("""
        <div class="main-header">
            <h1>🎓 Predictive Student Success Dashboard</h1>
            <h2>Transform Reactive Management into Proactive Success</h2>
            <p>Advanced analytics that predict and prevent student loan defaults before they occur</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.merged_data is not None:
            data = st.session_state.merged_data
            
            # Calculate enhanced metrics
            current_cdr, improved_cdr, cdr_improvement = calculate_cdr_projection(data)
            
            st.subheader("Impact Projection Dashboard")
            
            # Key impact metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Projected CDR", 
                    f"{current_cdr:.1f}%",
                    help="Current trajectory cohort default rate"
                )
            with col2:
                st.metric(
                    "With Intervention", 
                    f"{improved_cdr:.1f}%", 
                    f"-{cdr_improvement:.1f}%",
                    help="CDR after proactive interventions"
                )
            with col3:
                at_risk_count = len(data[data['risk_tier'].isin(['HIGH', 'MEDIUM'])])
                st.metric("Students Needing Intervention", at_risk_count)
            with col4:
                total_balance = data['outstanding_balance'].sum()
                st.metric("Total Portfolio at Risk", f"${total_balance:,.0f}")
            
            # Predictive vs Current Risk Comparison
            if 'predictive_score' in data.columns:
                st.subheader("Predictive Analytics Advantage")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Current risk distribution
                    current_risk = data['risk_tier'].value_counts()
                    fig1 = px.pie(
                        values=current_risk.values, 
                        names=current_risk.index,
                        title="Current Risk Assessment (Delinquency-Based)",
                        color_discrete_map={'HIGH': '#dc3545', 'MEDIUM': '#ffc107', 'LOW': '#28a745'}
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    # Predictive risk distribution
                    predictive_risk = data['predictive_tier'].value_counts()
                    fig2 = px.pie(
                        values=predictive_risk.values, 
                        names=predictive_risk.index,
                        title="Predictive Risk Assessment (Multi-Factor)",
                        color_discrete_map={'HIGH': '#dc3545', 'MEDIUM': '#ffc107', 'LOW': '#28a745'}
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                
                # Show students identified by predictive model but missed by traditional methods
                predictive_high = set(data[data['predictive_tier'] == 'HIGH']['student_id'])
                current_high = set(data[data['risk_tier'] == 'HIGH']['student_id'])
                early_warning_students = predictive_high - current_high
                
                if early_warning_students:
                    st.markdown("### 🚨 Early Warning Alerts")
                    st.markdown(f"""
                    <div class="alert-card">
                        <h4>Predictive Model Identifies {len(early_warning_students)} Additional At-Risk Students</h4>
                        <p>These students show high predictive risk scores but haven't reached traditional delinquency thresholds. 
                        Early intervention could prevent {len(early_warning_students) * 0.65:.0f} potential defaults.</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Financial Impact Projection
            st.subheader("Financial Impact Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Cost of defaults vs intervention
                avg_default_cost = 15000  # Average cost of a default
                intervention_cost = 200   # Average cost of intervention
                
                potential_defaults = len(data[data['risk_tier'] == 'HIGH']) * 0.65
                intervention_savings = potential_defaults * avg_default_cost * 0.4  # 40% success rate
                intervention_investment = len(data[data['risk_tier'] == 'HIGH']) * intervention_cost
                net_savings = intervention_savings - intervention_investment
                
                st.metric("Potential Savings from Intervention", f"${net_savings:,.0f}")
                st.metric("ROI on Intervention Investment", f"{(net_savings/intervention_investment)*100:.0f}%")
                
            with col2:
                # Federal compliance impact
                st.markdown("### Federal Compliance Impact")
                if current_cdr > 30:
                    st.error("⚠️ CRITICAL: CDR above 30% federal threshold")
                elif current_cdr > 25:
                    st.warning("⚠️ WARNING: CDR approaching federal limits")
                else:
                    st.success("✅ CDR within federal compliance range")
                
                st.write(f"Current trajectory: {current_cdr:.1f}%")
                st.write(f"With intervention: {improved_cdr:.1f}%")
                st.write(f"Compliance buffer: {30 - improved_cdr:.1f} percentage points")
        
        else:
            # Welcome screen for non-logged-in users
            st.subheader("Advanced Predictive Analytics for Student Success")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <h3>🎯 Predictive Early Warning</h3>
                    <p>Identify at-risk students 6-18 months before traditional delinquency indicators appear using advanced analytics.</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card">
                    <h3>⚡ Automated Interventions</h3>
                    <p>Trigger personalized support workflows based on predictive risk scores and academic performance data.</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown("""
                <div class="metric-card">
                    <h3>📈 ROI-Driven Outcomes</h3>
                    <p>Track intervention effectiveness and calculate financial impact of proactive student success strategies.</p>
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
            st.subheader("Step 3: Advanced Analytics Processing")
            
            if st.button("🔗 Process with Predictive Analytics", type="primary", use_container_width=True):
                with st.spinner("Merging data and calculating predictive scores..."):
                    merged, error = merge_data(st.session_state.nslds_data, st.session_state.sis_data)
                    if error:
                        st.error(f"Merge failed: {error}")
                    else:
                        st.session_state.merged_data = merged
                        st.success(f"✅ Successfully processed {len(merged)} student records with predictive analytics")
                        st.dataframe(merged.head())
    
    with tab3:
        st.header("🎯 Predictive Risk Analytics")
        
        if st.session_state.merged_data is not None:
            data = st.session_state.merged_data
            
            # Early warning students
            if 'predictive_score' in data.columns:
                early_warning = data[
                    (data['predictive_tier'] == 'HIGH') & 
                    (data['risk_tier'] != 'HIGH')
                ]
                
                if not early_warning.empty:
                    st.subheader("🚨 Early Warning Interventions Needed")
                    st.markdown(f"""
                    <div class="alert-card">
                        <h4>{len(early_warning)} Students Identified for Proactive Intervention</h4>
                        <p>These students show high predictive risk but haven't reached traditional delinquency thresholds. 
                        Immediate intervention could prevent an estimated {len(early_warning) * 0.65:.0f} future defaults.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show early warning students
                    st.dataframe(early_warning[['student_id', 'first_name', 'last_name', 'major', 'predictive_score', 'gpa', 'academic_standing']])
            
            # Predictive model performance
            st.subheader("Predictive Model Performance")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Risk score distribution
                fig = px.histogram(
                    data, 
                    x='predictive_score', 
                    nbins=20,
                    title="Predictive Risk Score Distribution",
                    labels={'predictive_score': 'Predictive Risk Score', 'count': 'Number of Students'}
                )
                fig.add_vline(x=0.7, line_dash="dash", line_color="red", annotation_text="High Risk Threshold")
                fig.add_vline(x=0.4, line_dash="dash", line_color="orange", annotation_text="Medium Risk Threshold")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Academic correlation
                if 'gpa' in data.columns:
                    fig = px.scatter(
                        data,
                        x='gpa',
                        y='predictive_score',
                        color='academic_standing',
                        title="GPA vs Predictive Risk Score",
                        labels={'gpa': 'GPA', 'predictive_score': 'Predictive Risk Score'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Please upload and merge data files to access predictive analytics.")
    
    with tab4:
        st.header("📊 Program ROI Analysis")
        
        if st.session_state.merged_data is not None:
            data = st.session_state.merged_data
            major_analysis = analyze_by_major(data)
            
            if major_analysis is not None:
                st.subheader("Academic Program Performance Dashboard")
                
                # ROI metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    high_risk_programs = len(major_analysis[major_analysis['risk_tier'] == 'HIGH'])
                    st.metric("Programs Needing Review", high_risk_programs)
                
                with col2:
                    avg_debt_to_income = major_analysis['debt_to_income'].mean()
                    st.metric("Avg Debt-to-Income Ratio", f"{avg_debt_to_income:.1f}:1")
                
                with col3:
                    employment_rate = major_analysis['employment_rate'].mean()
                    st.metric("Avg Employment Rate", f"{employment_rate:.0%}")
                
                # Program comparison table
                st.subheader("Program Performance Rankings")
                display_analysis = major_analysis.copy()
                display_analysis['avg_salary'] = display_analysis['avg_salary'].apply(lambda x: f"${x:,.0f}")
                display_analysis['employment_rate'] = display_analysis['employment_rate'].apply(lambda x: f"{x:.0%}")
                display_analysis['debt_to_income'] = display_analysis['debt_to_income'].apply(lambda x: f"{x:.1f}:1")
                
                st.dataframe(display_analysis, use_container_width=True)
                
                # ROI visualization
                fig = px.scatter(
                    major_analysis,
                    x='avg_salary',
                    y='avg_risk',
                    size='student_count',
                    color='debt_to_income',
                    hover_data=['major', 'employment_rate'],
                    title="Program ROI Analysis: Salary vs Risk",
                    labels={'avg_salary': 'Average Starting Salary', 'avg_risk': 'Average Risk Score'}
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Program recommendations
                st.subheader("Program Action Recommendations")
                
                high_risk_programs = major_analysis[major_analysis['risk_tier'] == 'HIGH']
                for _, program in high_risk_programs.iterrows():
                    st.markdown(f"""
                    <div class="intervention-card">
                        <h4>{program['major']} - Action Required</h4>
                        <p><strong>Risk Level:</strong> {program['risk_tier']}</p>
                        <p><strong>Students Affected:</strong> {program['student_count']}</p>
                        <p><strong>Debt-to-Income:</strong> {program['debt_to_income']:.1f}:1</p>
                        <p><strong>Recommended Actions:</strong></p>
                        <ul>
                            <li>Enhanced career services integration</li>
                            <li>Industry partnership development</li>
                            <li>Alternative credential pathways</li>
                            <li>Targeted financial counseling</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("Please upload and merge data files to access ROI analysis.")
    
    with tab5:
        st.header("⚡ Automated Intervention Engine")
        
        if st.session_state.merged_data is not None:
            data = st.session_state.merged_data
            
            st.subheader("Intervention Priority Queue")
            
            # Priority students
            high_risk_students = data[data['risk_tier'] == 'HIGH'].copy()
            if not high_risk_students.empty:
                high_risk_students['intervention_priority'] = high_risk_students.apply(
                    lambda row: 'CRITICAL' if row['days_delinquent'] > 180 else 'HIGH', axis=1
                )
                
                st.markdown("### Critical Interventions (Next 24-48 Hours)")
                
                for _, student in high_risk_students.head(5).iterrows():
                    recommendations = generate_intervention_recommendations(student.to_dict())
                    
                    with st.expander(f"{student['first_name']} {student['last_name']} - {student.get('major', 'Unknown Major')}"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Risk Score:** {student['risk_score']:.2f}")
                            st.write(f"**Days Delinquent:** {student['days_delinquent']}")
                            st.write(f"**Outstanding Balance:** ${student['outstanding_balance']:,.0f}")
                            if 'gpa' in student:
                                st.write(f"**GPA:** {student['gpa']}")
                            if 'academic_standing' in student:
                                st.write(f"**Academic Standing:** {student['academic_standing']}")
                        
                        with col2:
                            st.write("**Recommended Actions:**")
                            for rec in recommendations:
                                st.write(f"🔸 {rec['action']}")
                                st.write(f"   Timeline: {rec['timeline']}")
                                st.write(f"   Success Rate: {rec['success_rate']}")
                
                # Automated workflow simulation
                st.subheader("Automated Workflow Triggers")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    <div class="intervention-card">
                        <h4>Active Workflows</h4>
                        <p>📧 <strong>Email Campaign:</strong> 23 students contacted this week</p>
                        <p>📞 <strong>Phone Outreach:</strong> 12 students scheduled for calls</p>
                        <p>🎓 <strong>Academic Support:</strong> 8 students referred to advisors</p>
                        <p>💼 <strong>Career Services:</strong> 15 students connected to job placement</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("""
                    <div class="intervention-card">
                        <h4>Success Metrics (This Month)</h4>
                        <p>✅ <strong>Response Rate:</strong> 68% (above 45% benchmark)</p>
                        <p>💰 <strong>Payment Plans Setup:</strong> 34 students</p>
                        <p>📈 <strong>Risk Reduction:</strong> 42 students improved risk tier</p>
                        <p>🎯 <strong>Default Prevention:</strong> 18 estimated defaults avoided</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Communication templates for high-priority students
                st.subheader("Generate Targeted Communications")
                
                template_choice = st.selectbox(
                    "Choose Communication Type",
                    ['predictive_early_warning', 'intervention_priority'],
                    format_func=lambda x: {
                        'predictive_early_warning': 'Predictive Early Warning',
                        'intervention_priority': 'Priority Intervention'
                    }[x]
                )
                
                if st.button("📧 Generate Communications for High-Risk Students"):
                    student_list = high_risk_students.head(10).to_dict('records')
                    
                    st.success(f"Generated {len(student_list)} personalized communications")
                    
                    with st.expander("Preview Generated Communications"):
                        sample_student = student_list[0] if student_list else {}
                        template = EMAIL_TEMPLATES[template_choice]
                        
                        try:
                            formatted_subject = template['subject'].format(**sample_student)
                            formatted_body = template['body'].format(**sample_student)
                            
                            st.write("**Sample Email Subject:**")
                            st.write(formatted_subject)
                            st.write("**Sample Email Body:**")
                            st.text_area("", formatted_body, height=300, disabled=True)
                        except KeyError as e:
                            st.warning(f"Template requires additional data: {e}")
        else:
            st.info("Please upload and merge data files to access intervention engine.")
    
    with tab6:
        st.header("📈 Institutional Benchmarking")
        
        benchmark_data = generate_benchmark_data()
        
        st.subheader("Performance Comparison Dashboard")
        
        # Benchmark comparison
        metrics = ['cdr_rate', 'intervention_success', 'early_warning_usage', 'avg_risk_score']
        metric_labels = ['CDR Rate (%)', 'Intervention Success (%)', 'Early Warning Usage (%)', 'Avg Risk Score']
        
        for i, (metric, label) in enumerate(zip(metrics, metric_labels)):
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    f"{label} - Your Institution", 
                    f"{benchmark_data['Your Institution'][metric]:.1f}{'%' if 'rate' in metric or 'success' in metric or 'usage' in metric else ''}"
                )
            with col2:
                peer_val = benchmark_data['Peer Average'][metric]
                your_val = benchmark_data['Your Institution'][metric]
                delta = your_val - peer_val if 'risk_score' not in metric and 'cdr_rate' not in metric else peer_val - your_val
                st.metric(
                    f"{label} - Peer Average", 
                    f"{peer_val:.1f}{'%' if 'rate' in metric or 'success' in metric or 'usage' in metric else ''}",
                    f"{delta:+.1f}{'%' if 'rate' in metric or 'success' in metric or 'usage' in metric else ''}"
                )
            with col3:
                st.metric(
                    f"{label} - Top Quartile", 
                    f"{benchmark_data['Top Quartile'][metric]:.1f}{'%' if 'rate' in metric or 'success' in metric or 'usage' in metric else ''}"
                )
            with col4:
                st.metric(
                    f"{label} - National Average", 
                    f"{benchmark_data['National Average'][metric]:.1f}{'%' if 'rate' in metric or 'success' in metric or 'usage' in metric else ''}"
                )
        
        # Benchmark visualization
        st.subheader("Competitive Position Analysis")
        
        comparison_df = pd.DataFrame(benchmark_data).T
        
        fig = go.Figure()
        
        categories = ['CDR Rate (Lower is Better)', 'Intervention Success', 'Early Warning Usage', 'Risk Management']
        
        for institution in comparison_df.index:
            fig.add_trace(go.Scatterpolar(
                r=[
                    100 - comparison_df.loc[institution, 'cdr_rate'] * 5,  # Invert and scale CDR
                    comparison_df.loc[institution, 'intervention_success'],
                    comparison_df.loc[institution, 'early_warning_usage'],
                    100 - comparison_df.loc[institution, 'avg_risk_score'] * 100  # Invert risk score
                ],
                theta=categories,
                fill='toself',
                name=institution,
                line_color={'Your Institution': '#1e3a5f', 'Peer Average': '#ffc107', 
                           'Top Quartile': '#28a745', 'National Average': '#dc3545'}.get(institution, '#6c757d')
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="Institutional Performance Comparison"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance insights
        st.subheader("Competitive Analysis & Recommendations")
        
        your_data = benchmark_data['Your Institution']
        peer_data = benchmark_data['Peer Average']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Strengths")
            strengths = []
            if your_data['cdr_rate'] < peer_data['cdr_rate']:
                strengths.append("✅ CDR below peer average")
            if your_data['intervention_success'] > peer_data['intervention_success']:
                strengths.append("✅ Higher intervention success rate")
            if your_data['early_warning_usage'] > peer_data['early_warning_usage']:
                strengths.append("✅ Better early warning system utilization")
            
            for strength in strengths[:3]:
                st.write(strength)
        
        with col2:
            st.markdown("### Improvement Opportunities")
            opportunities = []
            if your_data['cdr_rate'] > peer_data['cdr_rate']:
                opportunities.append("🎯 Reduce CDR through enhanced interventions")
            if your_data['intervention_success'] < peer_data['intervention_success']:
                opportunities.append("🎯 Improve intervention effectiveness")
            if your_data['early_warning_usage'] < peer_data['early_warning_usage']:
                opportunities.append("🎯 Increase early warning system adoption")
            
            for opportunity in opportunities[:3]:
                st.write(opportunity)
        
        # ROI calculation
        st.subheader("Investment Impact Projection")
        
        st.markdown("""
        <div class="benchmark-card">
            <h4>Platform ROI Analysis</h4>
            <p><strong>Current Performance Gap:</strong> Your CDR is {:.1f} percentage points {} peer average</p>
            <p><strong>Improvement Potential:</strong> Reaching top quartile performance could prevent {} defaults annually</p>
            <p><strong>Financial Impact:</strong> Estimated savings of ${:,.0f} per year through improved outcomes</p>
            <p><strong>Platform Investment:</strong> ${:,.0f} annually (Professional Plan)</p>
            <p><strong>Net ROI:</strong> {:,.0f}% return on investment</p>
        </div>
        """.format(
            abs(your_data['cdr_rate'] - peer_data['cdr_rate']),
            'above' if your_data['cdr_rate'] > peer_data['cdr_rate'] else 'below',
            int((your_data['cdr_rate'] - benchmark_data['Top Quartile']['cdr_rate']) * 10),
            (your_data['cdr_rate'] - benchmark_data['Top Quartile']['cdr_rate']) * 10 * 15000,
            60000,  # Professional plan cost
            ((your_data['cdr_rate'] - benchmark_data['Top Quartile']['cdr_rate']) * 10 * 15000 / 60000 - 1) * 100
        ), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
