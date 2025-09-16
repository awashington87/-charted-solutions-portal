# ChartED Solutions - Financial Aid Risk Management Portal

A comprehensive Streamlit application for managing student loan risk and FERPA-compliant communications.

## 🎯 Overview

The ChartED Solutions portal streamlines financial aid operations by combining NSLDS delinquent borrower data with Student Information System (SIS) data to provide comprehensive risk analysis and targeted communication capabilities.

## ✨ Key Features

### 📁 **Multi-Source Data Integration**
- Upload and process NSLDS delinquent borrower reports
- Import Student Information System (SIS) data with academic program information
- Automatically merge datasets using SSN or Student ID matching
- Handle both CSV and Excel file formats

### 📊 **Advanced Risk Analytics**
- Calculate borrower risk scores based on delinquency patterns
- Analyze risk trends by academic major/program
- Identify high-risk programs requiring intervention
- Generate interactive visualizations and dashboards

### 📧 **FERPA-Compliant Communications**
- Pre-built, compliant email templates for various scenarios
- Bulk email capabilities with targeted student selection
- Built-in FERPA validation to protect student privacy
- Templates for default prevention, payment plans, and financial counseling

### 📋 **Comprehensive Reporting**
- Program risk analysis reports
- Communication activity tracking
- Downloadable data exports in multiple formats
- Executive-level summaries for institutional decision-making

## 🚀 Quick Start

### 1. Upload Your Data
- Go to the "Upload Data" tab
- Upload your NSLDS delinquent borrower report
- Upload your SIS data with academic program information
- Click "Combine Datasets" to merge the data

### 2. Analyze Risk Patterns
- Navigate to the "Analytics" tab
- Review risk distribution by academic program
- Identify high-risk programs and student populations
- Use interactive visualizations to explore trends

### 3. Communicate with Students
- Use the "Communications" tab to select target populations
- Choose from FERPA-compliant email templates
- Send bulk communications to at-risk students
- Track communication activities and responses

### 4. Generate Reports
- Access the "Reports" tab for comprehensive analytics
- Download program risk analysis reports
- Export student data for further analysis
- Share insights with institutional leadership

## 🛠️ Technical Requirements

- **Python 3.8+**
- **Streamlit 1.28.0+**
- **Pandas 2.0.0+** for data processing
- **Plotly 5.17.0+** for interactive visualizations
- **OpenPyXL 3.1.0+** for Excel file support

## 📊 Data Requirements

### NSLDS Data Format
Required columns (with flexible naming):
- Borrower SSN / SSN
- Borrower First Name / First Name
- Borrower Last Name / Last Name
- E-mail / Email
- Days Delinquent
- Outstanding Principal Balance (OPB) / Outstanding Balance
- Loan Type

### SIS Data Format
Required columns:
- Student ID
- SSN (for matching with NSLDS)
- First Name
- Last Name
- Email
- Major / Academic Program
- Enrollment Status (optional)

## 🔒 Privacy & Compliance

### FERPA Compliance
- All email templates undergo automatic FERPA validation
- No sensitive student information (SSN, grades) included in communications
- Educational interest requirements built into system logic
- Audit trail maintenance for all communications

### Data Security
- Session-based data storage (no persistent data retention)
- Secure file upload handling
- No data transmitted outside the application environment
- Automatic data clearing when session ends

## 🎨 Customization

### Institution Branding
The application can be customized with your institution's:
- Colors and visual theme
- Contact information
- Email templates and messaging
- Logos and institutional branding

### Configuration Options
- Risk threshold adjustments
- Email template modifications
- Data field mapping for different file formats
- Custom analytics parameters

## 📞 Support & Contact

### ChartED Solutions
- **Email:** info@visitcharted.com
- **Website:** visitcharted.com
- **Consultation:** Available for implementation and training

### Support Services
- Initial setup and configuration
- Staff training and onboarding
- Custom template development
- Data integration consulting
- Ongoing technical support

## 🚀 Deployment

This application is designed for deployment on Streamlit Cloud, providing:
- **Zero infrastructure management**
- **Automatic scaling based on usage**
- **Professional web interface accessible from anywhere**
- **No software installation required for end users**

### Live Application
Once deployed, your ChartED Solutions portal will be accessible at:
`https://your-app-name.streamlit.app`

## 📈 Benefits for Financial Aid Offices

### Operational Efficiency
- Eliminate manual data processing and analysis
- Reduce time spent on risk assessment
- Streamline communication workflows
- Automate report generation

### Enhanced Decision Making
- Data-driven insights into program performance
- Early identification of at-risk student populations
- Trend analysis for proactive intervention
- Comprehensive institutional risk assessment

### Improved Student Outcomes
- Timely outreach to at-risk borrowers
- Personalized communication strategies
- Multiple intervention pathways
- Enhanced default prevention programs

## 📋 Implementation Roadmap

### Phase 1: Setup & Testing (Week 1)
- Deploy application to Streamlit Cloud
- Configure institutional branding
- Test with sample data
- Train initial users

### Phase 2: Data Integration (Week 2-3)
- Upload real NSLDS and SIS data
- Validate data merge accuracy
- Configure risk thresholds
- Customize email templates

### Phase 3: Full Deployment (Week 4)
- Roll out to financial aid staff
- Begin regular risk analysis workflows
- Implement communication campaigns
- Establish reporting schedules

### Phase 4: Optimization (Ongoing)
- Analyze usage patterns and outcomes
- Refine risk algorithms
- Enhance communication templates
- Expand analytics capabilities

## 🏆 Success Metrics

Track your implementation success with:
- **Reduced default rates** through early intervention
- **Increased communication efficiency** with bulk messaging
- **Enhanced data visibility** through integrated analytics
- **Improved staff productivity** via workflow automation
- **Better student outcomes** through targeted outreach

## 📚 Additional Resources

- **Streamlit Documentation:** https://docs.streamlit.io
- **FERPA Compliance Guidelines:** Available from Department of Education
- **NSLDS Resources:** https://nslds.ed.gov
- **ChartED Solutions Training Materials:** Available upon request

---

## 🤝 About ChartED Solutions

ChartED Solutions specializes in developing innovative technology solutions for higher education financial aid offices. Our mission is to help institutions improve student outcomes through better data analysis, streamlined operations, and effective communication strategies.

**Ready to transform your financial aid operations?** Contact us today to learn more about implementing the ChartED Solutions portal at your institution.

---

*© 2024 ChartED Solutions. All rights reserved.*
