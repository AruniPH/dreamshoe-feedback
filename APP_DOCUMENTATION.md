# Aviana Collection - Footwear Feedback Analyzer
## Complete Application Documentation

---

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [User Roles](#user-roles)
4. [Features & Functionality](#features--functionality)
5. [Database Structure](#database-structure)
6. [How to Use](#how-to-use)
7. [Technical Details](#technical-details)

---

## Overview

The Aviana Collection Footwear Feedback Analyzer is an AI-powered application designed to collect, analyze, and prioritize customer feedback for footwear products. The system combines Natural Language Processing (NLP), machine learning, and collective intelligence to help business owners make data-driven decisions about product improvements.

### Key Capabilities
- AI chatbot-based feedback collection
- Automated sentiment analysis using ML models
- Collective intelligence idea pooling and voting
- Statistical analysis (ANOVA, Tukey HSD tests)
- Management priority setting and comparison with NLP predictions
- Footwear-specific data filtering and analysis

---

## System Architecture

### Technology Stack
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python 3.x
- **Database**: PostgreSQL
- **AI/ML**: 
  - OpenAI GPT-4o-mini for conversational AI
  - Scikit-learn for sentiment classification
  - TF-IDF vectorization for text processing
- **Statistical Analysis**: Statsmodels (ANOVA, Tukey HSD)

### Components
1. **Authentication System**: Role-based access control (Customer/Owner)
2. **Feedback Collector**: AI chatbot interface
3. **Collective Intelligence**: Idea submission and voting system
4. **Owner Dashboard**: Visual analytics and insights
5. **Statistical Analysis**: Advanced statistical testing
6. **Management Decision Tool**: Priority setting and NLP comparison

---

## User Roles

### 1. Customer
**Access Rights:**
- Submit feedback via AI chatbot
- Select footwear items they experienced
- Submit improvement ideas
- Vote on other customers' ideas (thumbs up/down)

**Restrictions:**
- Cannot access owner dashboard
- Cannot view statistical analysis
- Cannot set management priorities

### 2. Owner
**Access Rights:**
- All customer capabilities
- View aggregated feedback analytics
- Access statistical analysis tools
- Set management priorities for improvements
- Filter data by specific footwear items or view all
- Compare management decisions with NLP predictions

---

## Features & Functionality

### 1. Authentication & Login
- Secure login system with username/password
- Password hashing (SHA-256)
- Role-based access control
- Session management
- Logout functionality

**Database Table**: `users`
- Fields: username, password_hash, role

---

### 2. Feedback Collector (Customer & Owner)

#### Footwear Selection
- Visual grid display of all footwear items from `footwear_items/` folder
- Images displayed at 150px width for consistency
- Click "Select" button to choose footwear
- Selected item shown in success message

#### AI Chatbot Conversation
- **Powered by**: OpenAI GPT-4o-mini
- **Conversation Flow**:
  1. Customer selects footwear item
  2. Customer selects feature category (Comfort & Fit, Durability & Quality, Design & Style)
  3. Customer selects sub-feature
  4. Bot asks 5 intelligent follow-up questions
  5. Each answer is analyzed and stored

#### Features Taxonomy
**Comfort & Fit:**
- Cushioning & Support
- Breathability
- Sizing Accuracy

**Durability & Quality:**
- Material Strength
- Sole & Stitching
- Longevity

**Design & Style:**
- Aesthetics
- Versatility
- Brand Identity

#### ML Classification
- **Model**: Logistic Regression (pre-trained)
- **Vectorizer**: TF-IDF
- **Classification**: 
  - "Need Improvement" (prediction = 1)
  - "No Need Improvement" (prediction = 0)
- Combines feature, sub-feature, and feedback text for prediction

#### User Experience
- Press Enter key to send feedback
- Input field clears automatically after submission
- Bot generates unique, non-repetitive questions
- Progress tracked (5 questions total)
- "Start New Feedback" button to reset conversation

**Database Table**: `feedback`
- Fields: product, feature, subfeature, feedback_text, urgency, footwear, created_at

---

### 3. Collective Intelligence (Customer & Owner)

#### For Customers:
- Must select footwear item first
- Submit improvement ideas for specific features/sub-features
- Vote on existing ideas (thumbs up/down)
- Ideas linked to selected footwear

#### For Owners:
- Select specific footwear or "All" to view ideas
- View all ideas filtered by selection
- Vote on ideas
- Monitor community sentiment

#### Voting System
- Real-time vote counting
- Thumbs up/down buttons
- Vote counts displayed next to buttons
- Immediate database updates

**Database Table**: `ideas`
- Fields: feature, subfeature, idea_text, thumbs_up, thumbs_down, footwear, created_at

---

### 4. Owner Dashboard (Owner Only)

#### Footwear Selection
- Visual selector with "All" option
- "All" shows combined data from all footwear items
- Specific selection shows item-specific data

#### Auto-Refresh
- Dashboard refreshes every 60 seconds
- Ensures real-time data visibility

#### Feature Analysis
- **Bar Chart**: Shows percentage of "Need Improvement" vs "No Need Improvement" by feature
- Color-coded visualization
- Interactive feature selection

#### Sub-Feature Analysis
- Click feature buttons to drill down
- Shows sub-feature level improvement requirements
- Percentage-based bar charts
- Helps identify specific areas needing attention

#### Data Processing
- Normalizes urgency labels (handles variations in text)
- Calculates percentages for visual representation
- Groups data by feature and sub-feature
- Filters by selected footwear

---

### 5. Statistical Analysis (Owner Only)

#### Purpose
Identify which features need more attention based on collective intelligence votes using rigorous statistical methods.

#### Footwear Selection
- Select specific footwear or "All" for combined analysis
- Analysis runs on filtered dataset

#### ANOVA (Analysis of Variance)
- **Null Hypothesis**: All features perform equally
- **Alternative Hypothesis**: Not all features perform equally
- **Interpretation**:
  - p < 0.05: Statistically significant differences exist
  - p ≥ 0.05: No significant differences

#### Tukey HSD (Honest Significant Difference) Test
- Post-hoc pairwise comparison between features
- Identifies which specific feature pairs differ
- **Interpretation**:
  - p-adj < 0.05: Significant difference between features
  - p-adj ≥ 0.05: No significant difference

#### Visualizations
1. **ANOVA Table**: Statistical test results
2. **Tukey HSD Table**: Pairwise comparison results
3. **Confidence Interval Plot**: Visual representation of differences
4. **Mean Votes Bar Chart**: Average votes per feature

#### Feature Comparison Tool
- Select two features to compare
- Automated interpretation:
  - If significant difference: Recommends which feature to focus on
  - If no difference: Suggests equal attention needed
- Shows p-value and mean difference

#### Data Transformation
- Expands vote data (each thumbs up = vote of 1, thumbs down = vote of 0)
- Creates dataset suitable for ANOVA
- Handles empty datasets gracefully

---

### 6. Management vs NLP Model (Owner Only)

#### Purpose
Allow management to set priorities and compare with data-driven NLP predictions.

#### Footwear Selection
- Select specific footwear or "All"
- Priorities can be set globally or per footwear item

#### Priority Setting Interface
- **Layout**: Organized by feature categories
- **Columns**:
  1. Sub-Feature name
  2. Current Management Priority (🔴 High / 🟢 Low / ⚪ Not Set)
  3. "High" button
  4. "Low" button
  5. NLP Model Prediction (🔴 High / 🟢 Low / ⚪ No Data)
  6. Comparison indicator (✅ Match / ⚠️ Differ)

#### Color Coding
- 🔴 **Red = High Priority**: Needs improvement urgently
- 🟢 **Green = Low Priority**: Performing well, low priority
- ⚪ **White = Not Set/No Data**: No decision or insufficient data

#### NLP Model Logic
- Analyzes feedback data for each sub-feature
- Calculates percentage of "Need Improvement" feedback
- **Rule**: 
  - ≥50% "Need Improvement" → High Priority
  - <50% "Need Improvement" → Low Priority
- Based on actual customer feedback data

#### Comparison Analysis
- **Match (✅)**: Management and NLP agree on priority
- **Differ (⚠️)**: Management and NLP disagree
  - Indicates potential misalignment between management intuition and customer data
  - Prompts discussion and review

#### Summary Dashboard
Three key metrics:
1. **Matches**: Number of sub-features where management and NLP agree
2. **Differences**: Number of sub-features with disagreement
3. **Not Set**: Number of sub-features without management decision

#### Use Cases
- Validate management decisions with data
- Identify blind spots in priority setting
- Balance business strategy with customer needs
- Track alignment over time

**Database Table**: `priorities`
- Fields: footwear, feature, subfeature, priority, updated_at
- Unique constraint: (footwear, feature, subfeature)

---

## Database Structure

### PostgreSQL Database: `feedback_db`

#### Table: `users`
```sql
- id: SERIAL PRIMARY KEY
- username: VARCHAR(50) UNIQUE NOT NULL
- password_hash: VARCHAR(255) NOT NULL
- role: VARCHAR(20) CHECK (role IN ('customer', 'owner'))
```

#### Table: `feedback`
```sql
- id: SERIAL PRIMARY KEY
- product: VARCHAR(100)
- feature: VARCHAR(100)
- subfeature: VARCHAR(100)
- feedback_text: TEXT
- urgency: VARCHAR(50)
- footwear: VARCHAR(100)
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

#### Table: `ideas`
```sql
- id: SERIAL PRIMARY KEY
- feature: VARCHAR(100)
- subfeature: VARCHAR(100)
- idea_text: TEXT
- thumbs_up: INTEGER DEFAULT 0
- thumbs_down: INTEGER DEFAULT 0
- footwear: VARCHAR(100)
- created_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
```

#### Table: `priorities`
```sql
- id: SERIAL PRIMARY KEY
- footwear: VARCHAR(100)
- feature: VARCHAR(100)
- subfeature: VARCHAR(100)
- priority: VARCHAR(50) CHECK (priority IN ('High', 'Low'))
- updated_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- UNIQUE(footwear, feature, subfeature)
```

---

## How to Use

### Installation & Setup

1. **Install Dependencies**:
```bash
pip install streamlit pandas openai joblib pillow streamlit-option-menu streamlit-autorefresh statsmodels psycopg2-binary python-dotenv
```

2. **Database Setup**:
```bash
# Install PostgreSQL
sudo apt install python3-psycopg2

# Configure database in .env file
DB_HOST=localhost
DB_NAME=feedback_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
```

3. **Initialize Database**:
```bash
python3 -c "from database import init_database; init_database()"
```

4. **Add Footwear Images**:
- Place footwear images in `footwear_items/` folder
- Supported formats: .jpg, .png
- Images will be displayed in alphabetical order

5. **Run Application**:
```bash
streamlit run main.py
```

### Creating Users

Use `init_db.py` or database functions to create users:
```python
from database import create_user
create_user("customer1", "password123", "customer")
create_user("owner1", "password123", "owner")
```

---

### Customer Workflow

1. **Login** with customer credentials
2. **Feedback Collector**:
   - Select footwear item from images
   - Choose feature category
   - Choose sub-feature
   - Answer 5 AI-generated questions
   - Press Enter to submit each answer
   - Complete feedback session
3. **Collective Intelligence**:
   - Select footwear item
   - Choose feature and sub-feature
   - Submit improvement idea
   - Vote on other ideas

---

### Owner Workflow

1. **Login** with owner credentials
2. **View Feedback** (Feedback Collector page):
   - Can also submit feedback like customers
3. **Collective Intelligence**:
   - Select "All" or specific footwear
   - View all ideas for selection
   - Vote on ideas
4. **Owner Dashboard**:
   - Select footwear filter
   - View feature-level analytics
   - Drill down to sub-features
   - Monitor improvement requirements
5. **Statistical Analysis**:
   - Select footwear filter
   - Review ANOVA results
   - Analyze Tukey HSD comparisons
   - Compare specific features
   - Make data-driven decisions
6. **Management vs NLP Model**:
   - Select footwear filter
   - Set priorities for each sub-feature
   - Compare with NLP predictions
   - Review match/differ indicators
   - Check summary metrics

---

## Technical Details

### File Structure
```
product_feedback_analyzer/
├── main.py                 # Main application file
├── auth.py                 # Authentication functions
├── database.py             # Database operations
├── init_db.py             # Database initialization
├── .env                   # Environment variables
├── footwear_items/        # Footwear images folder
│   ├── L01.jpg
│   ├── L02.jpg
│   └── L03.jpg
├── models/                # ML models
│   ├── model.pkl          # Logistic Regression model
│   └── vectorizer.pkl     # TF-IDF vectorizer
├── pages/                 # Streamlit pages (legacy)
└── logo.png              # Application logo
```

### Key Functions

#### Authentication (auth.py)
- `check_authentication()`: Verify user session
- `login_page()`: Display login interface
- `logout()`: Clear session and logout
- `require_role()`: Check user role permissions

#### Database (database.py)
- `init_database()`: Create all tables
- `save_feedback()`: Store customer feedback
- `get_feedback()`: Retrieve feedback with filters
- `save_idea()`: Store improvement ideas
- `get_ideas()`: Retrieve ideas with filters
- `update_idea_vote()`: Increment vote counts
- `set_priority()`: Set management priority
- `get_priority()`: Get priority for sub-feature
- `get_all_priorities()`: Get all priorities
- `verify_user()`: Authenticate user credentials
- `create_user()`: Create new user account

#### Main Application (main.py)
- `display_footwear_selector()`: Show footwear selection UI
- `generate_question()`: AI-generated follow-up questions
- `classify_subfeature()`: AI-based sub-feature classification

### Security Features
- Password hashing (SHA-256)
- SQL injection prevention (parameterized queries)
- Session-based authentication
- Role-based access control
- Environment variable for sensitive data

### Performance Optimizations
- Auto-refresh limited to 60 seconds
- Database connection pooling with context managers
- Efficient query filtering
- Cached session state
- Lazy loading of ML models

---

## Business Value

### For Customers
- Easy, conversational feedback submission
- Voice heard through collective intelligence
- Influence product improvements
- Engaging voting system

### For Business Owners
- Data-driven decision making
- Automated sentiment analysis
- Statistical validation of priorities
- Alignment check between management and customer needs
- Product-specific insights
- Real-time monitoring
- Reduced manual analysis time

### ROI Indicators
- Faster identification of improvement areas
- Reduced product development costs
- Improved customer satisfaction
- Evidence-based resource allocation
- Competitive advantage through customer-centric approach

---

## Future Enhancement Possibilities

1. **Advanced Analytics**:
   - Trend analysis over time
   - Predictive modeling for future issues
   - Customer segmentation

2. **Enhanced AI**:
   - Sentiment intensity scoring
   - Emotion detection
   - Multi-language support

3. **Reporting**:
   - PDF report generation
   - Email notifications
   - Scheduled reports

4. **Integration**:
   - CRM system integration
   - Product management tools
   - E-commerce platforms

5. **Mobile Support**:
   - Responsive design improvements
   - Mobile app version
   - Push notifications

---

## Support & Maintenance

### Regular Tasks
- Database backup (recommended: daily)
- Monitor disk space for images
- Review and archive old feedback
- Update ML models periodically
- Security updates for dependencies

### Troubleshooting
- Check database connection in .env
- Verify PostgreSQL service is running
- Ensure footwear_items folder exists
- Confirm ML model files are present
- Check OpenAI API key validity

---

## Conclusion

The Aviana Collection Footwear Feedback Analyzer is a comprehensive solution that bridges the gap between customer feedback and business decisions. By combining AI-powered conversation, machine learning classification, collective intelligence, and statistical analysis, it provides a robust platform for continuous product improvement and customer satisfaction enhancement.

---

**Version**: 1.0  
**Last Updated**: December 8, 2025  
**Developed for**: Aviana Collection - Footwear Store
