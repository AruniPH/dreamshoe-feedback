# Internal Process Report: Product Feedback Analyzer System
## A Comprehensive Analysis for Thesis Documentation

---

## Executive Summary

This report documents the internal processes of the Product Feedback Analyzer System, a multi-layered application that integrates conversational AI, machine learning classification, statistical analysis, and collective intelligence to transform customer feedback into actionable business insights. The system employs a three-tier architecture (Presentation, Business Logic, and Data Access layers) to ensure separation of concerns, maintainability, and scalability.

**Note:** This report documents only the actively implemented and operational features of the system as of February 18, 2026. Unused or deprecated features have been removed to ensure accuracy.

---

## 1. System Architecture Overview

### 1.1 Architectural Pattern
The system follows a **Three-Layer Architecture** pattern:

```
┌─────────────────────────────────────────────────────────┐
│           PRESENTATION LAYER (Streamlit UI)             │
│  - User Interface Components                            │
│  - Session State Management                             │
│  - Input Validation & Display Logic                     │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│         BUSINESS LOGIC LAYER (Python Core)              │
│  - Authentication & Authorization                       │
│  - AI/ML Processing (OpenAI + Scikit-learn)            │
│  - Statistical Analysis (ANOVA, Tukey HSD)             │
│  - Data Transformation & Aggregation                    │
└─────────────────────────────────────────────────────────┘
                          ↕
┌─────────────────────────────────────────────────────────┐
│        DATA ACCESS LAYER (PostgreSQL + psycopg2)        │
│  - Database Connection Management                       │
│  - CRUD Operations                                      │
│  - Transaction Management                               │
│  - Data Persistence                                     │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Presentation** | Streamlit 1.x, HTML/CSS, Matplotlib |
| **Business Logic** | Python 3.x, OpenAI GPT-4o-mini, Scikit-learn, SciPy, Statsmodels |
| **Data Access** | PostgreSQL 12+, psycopg2 |
| **ML Models** | TF-IDF Vectorizer, Logistic Regression Classifier |
| **Configuration** | python-dotenv, Environment Variables |

---

## 2. Layer 1: Presentation Layer - Internal Processes

### 2.1 User Authentication Interface

**Process Flow:**
1. System checks session state for authentication token
2. If not authenticated, renders login page with username/password fields
3. Captures user input through Streamlit text input widgets
4. On submit button click, passes credentials to Business Logic Layer
5. Receives authentication result and user role
6. Stores session data: `username`, `user_role`, `authenticated`
7. Redirects to appropriate dashboard based on role

**Key Components:**
- `check_authentication()`: Validates session state
- `login_page()`: Renders login form
- Session state persistence across page reloads

### 2.2 Customer Feedback Collection Interface

**Process Flow:**

#### Step 1: Customer Information Capture
```
Display Form → Capture Name & Email → Validate Input → Store in Session State
```

**Implementation:**
- Two-column layout for name and email fields
- Real-time validation on submit button click
- Session state keys: `customer_name`, `customer_email`

#### Step 2: Feature Selection
```
Display Dropdown → User Selects Feature → Reset Conversation State → Initialize Chat
```

**Features Presented:**
- Comfort & Fit
- Durability & Quality
- Design & Style

**State Management:**
- `selected_feature`: Current feature being discussed
- `chat_history`: Array of message objects
- `questions_asked`: Counter (0 to total_questions)
- `feedback_complete`: Boolean flag

#### Step 3: Conversational Interface
```
Display Chat History → Show Text Input → Capture User Response → Submit Button → Process
```

**UI Elements:**
- Chat message containers (user/assistant roles)
- Text area with placeholder text
- Submit button with validation
- Progress indicator (Question X of Y)

#### Step 4: Feedback Submission
```
User Types → Clicks Submit → Validate Non-Empty → Send to Business Layer → Display Next Question
```

**Validation Rules:**
- Input must not be empty or whitespace-only
- ML models must be loaded successfully
- Session state must be valid


### 2.3 Collective Intelligence Interface

**Process Flow:**

#### Idea Submission
```
Select Feature → Select Sub-feature → Enter Idea Text → Submit → Store in Database
```

**UI Components:**
- Feature dropdown (3 options)
- Sub-feature dropdown (dynamic based on feature)
- Multi-line text area for idea description
- Submit button with validation

#### Voting Interface
```
Display Ideas List → Show Vote Buttons (👍/👎) → Capture Vote → Update Counter → Refresh Display
```

**Real-time Updates:**
- Vote counts displayed next to buttons
- Immediate UI refresh after vote
- Duplicate vote prevention (email-based tracking)

### 2.4 Owner Dashboard Interface

**Process Flow:**

#### Auto-Refresh Mechanism
```
Page Load → Start 60-second Timer → Fetch Latest Data → Re-render Charts → Repeat
```

**Implementation:**
- `st_autorefresh(interval=60000)` - 60-second refresh
- Ensures real-time data visibility
- Minimal performance impact

#### Data Visualization
```
Fetch Data → Transform to DataFrame → Calculate Percentages → Render Bar Charts
```

**Chart Types:**
1. **Feature-Level Bar Chart**
   - X-axis: 3 main features
   - Y-axis: Percentage of "Need Improvement"
   - Color-coded: Red (Need Improvement), Green (No Need)

2. **Sub-Feature Bar Chart**
   - X-axis: 9 sub-features
   - Y-axis: Improvement percentage
   - Drill-down capability

3. **Innovative Ideas Table**
   - Columns: Name, Email, Idea, Votes
   - Sortable by vote count
   - Pagination support

### 2.5 Statistical Analysis Interface

**Process Flow:**

#### ANOVA Results Display
```
Fetch Analysis Results → Format Tables → Display Metrics → Show Interpretation
```

**Displayed Metrics:**
- F-statistic (variance ratio)
- P-value (significance level)
- Decision (Reject/Fail to Reject H₀)
- Interpretation text

#### Tukey HSD Display
```
Receive Pairwise Comparisons → Format Table → Highlight Significant Pairs → Show Confidence Intervals
```

**Table Columns:**
- Group 1 vs Group 2
- Mean Difference
- Adjusted P-value
- Lower/Upper Confidence Interval
- Reject Decision (True/False)

#### Confidence Interval Plot
```
Generate Matplotlib Figure → Plot Intervals → Add Zero Line → Display in Streamlit
```

**Visual Elements:**
- Horizontal bars for each comparison
- Zero reference line (no difference)
- Statistical significance indicators

---

## 3. Layer 2: Business Logic Layer - Internal Processes

### 3.1 Authentication & Authorization Logic

**Process: User Login**

```python
# Pseudocode
FUNCTION verify_user(username, password):
    hashed_password = SHA256(password)
    query = "SELECT * FROM users WHERE username = ? AND password_hash = ?"
    result = execute_query(query, [username, hashed_password])
    
    IF result exists:
        RETURN (True, user_role)
    ELSE:
        RETURN (False, None)
```

**Security Measures:**
1. Password hashing using SHA-256
2. Parameterized queries (SQL injection prevention)
3. Session-based authentication
4. Role-based access control (RBAC)

**Authorization Flow:**
```
User Action → Check Session → Validate Role → Allow/Deny Access
```

**Role Permissions:**
- **Customer**: Feedback submission, idea voting
- **Owner**: All customer permissions + analytics + management tools

### 3.2 Conversational AI Integration

**Process: Question Generation**

```python
# Pseudocode
FUNCTION generate_question(sub_feature, question_number):
    system_prompt = "You are a helpful assistant for a footwear store. 
                     Ask ONE specific, short question (maximum 15 words) 
                     about '{sub_feature}' for footwear feedback."
    
    response = OpenAI.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Ask me about {sub_feature}"}
        ],
        max_tokens=50
    )
    
    RETURN response.choices[0].message.content
```

**Question Generation Strategy:**
- **Question 1**: Broad, open-ended (e.g., "How would you rate the cushioning?")
- **Question 2**: Specific, probing (e.g., "Any issues with arch support?")
- Maximum 15 words per question
- Context-aware based on sub-feature

**Error Handling:**
- API timeout: Use fallback questions
- Rate limiting: Queue requests
- Invalid response: Retry with simplified prompt

**Conversation Management:**
```
Initialize → Ask Q1 → Store Response → Ask Q2 → Store Response → Move to Next Sub-feature
```

**State Tracking:**
- `questions_asked`: Increments after each response
- `current_subfeature_index = questions_asked // 2`
- `question_number = (questions_asked % 2) + 1`
- Total questions = 3 sub-features × 2 questions = 6 per feature

### 3.3 Machine Learning Classification

**Process: Sentiment Analysis**

```python
# Pseudocode
FUNCTION classify_feedback(sub_feature, user_input):
    # Step 1: Text Preprocessing
    combined_text = f"{sub_feature} {user_input}"
    # Example: "Cushioning & Support The cushioning feels inadequate"
    
    # Step 2: Vectorization (TF-IDF)
    vectorizer = load_model("models/vectorizer.pkl")
    text_vector = vectorizer.transform([combined_text])
    # Output: Sparse matrix [0.0, 0.34, 0.0, 0.67, ...]
    
    # Step 3: Classification
    classifier = load_model("models/model.pkl")
    prediction = classifier.predict(text_vector)[0]
    # Output: 1 (Need Improvement) or 0 (No Need Improvement)
    
    # Step 4: Label Mapping
    IF prediction == 1:
        label = "Need Improvement"
    ELSE:
        label = "No Need Improvement"
    
    RETURN label
```

**Model Details:**
- **Algorithm**: Logistic Regression
- **Features**: TF-IDF vectors (text-to-numerical transformation)
- **Training**: Pre-trained on labeled feedback dataset
- **Input**: Sub-feature name + customer text
- **Output**: Binary classification (0 or 1)

**Why Combine Sub-feature with Text?**
- Provides context to the classifier
- Same phrase can have different meanings for different features
- Example: "too soft" → Negative for "Material Strength", Positive for "Cushioning"

**Classification Accuracy Factors:**
- Quality of training data
- Vocabulary coverage in TF-IDF
- Feature engineering (sub-feature inclusion)
- Model hyperparameters


### 3.4 Statistical Analysis - ANOVA

**Process: One-Way ANOVA**

```python
# Pseudocode
FUNCTION perform_anova(feedback_data):
    # Step 1: Data Preparation
    df = convert_to_dataframe(feedback_data)
    df['urgency_score'] = map_urgency_to_numeric(df['urgency'])
    # "Need Improvement" → 1, "No Need Improvement" → 0
    
    # Step 2: Group by Feature
    comfort_scores = df[df['feature'] == 'Comfort & Fit']['urgency_score']
    durability_scores = df[df['feature'] == 'Durability & Quality']['urgency_score']
    design_scores = df[df['feature'] == 'Design & Style']['urgency_score']
    
    # Step 3: Perform ANOVA
    f_statistic, p_value = scipy.stats.f_oneway(
        comfort_scores,
        durability_scores,
        design_scores
    )
    
    # Step 4: Interpret Results
    IF p_value < 0.05:
        decision = "Reject H₀: Significant differences exist"
        proceed_to_tukey = True
    ELSE:
        decision = "Fail to reject H₀: No significant differences"
        proceed_to_tukey = False
    
    RETURN {
        'f_statistic': f_statistic,
        'p_value': p_value,
        'decision': decision,
        'proceed_to_tukey': proceed_to_tukey
    }
```

**ANOVA Calculation Explained:**

**Hypotheses:**
- **H₀ (Null)**: μ₁ = μ₂ = μ₃ (All features have equal mean dissatisfaction)
- **H₁ (Alternative)**: At least one mean differs

**F-Statistic Formula:**
```
F = Between-Group Variance / Within-Group Variance

Between-Group Variance = Σ nᵢ(x̄ᵢ - x̄)² / (k - 1)
Within-Group Variance = Σ Σ (xᵢⱼ - x̄ᵢ)² / (N - k)

Where:
- nᵢ = sample size of group i
- x̄ᵢ = mean of group i
- x̄ = overall mean
- k = number of groups (3 features)
- N = total sample size
```

**Interpretation:**
- **High F-statistic**: Large differences between group means
- **Low p-value**: Differences unlikely due to chance
- **p < 0.05**: Statistically significant (95% confidence)

**Example Calculation:**
```
Comfort & Fit: [1, 1, 0, 1, 0, 1, 1, 0] → Mean = 0.625
Durability: [1, 1, 1, 0, 1, 1, 1, 1] → Mean = 0.875
Design: [0, 0, 1, 0, 0, 0, 1, 0] → Mean = 0.250

F-statistic = 12.45
P-value = 0.0003 (< 0.05, significant!)
```

### 3.5 Statistical Analysis - Tukey HSD

**Process: Post-hoc Pairwise Comparison**

```python
# Pseudocode
FUNCTION perform_tukey_hsd(feedback_data):
    # Step 1: Prepare Data
    df = prepare_dataframe(feedback_data)
    
    # Step 2: Perform Tukey HSD
    tukey_result = pairwise_tukeyhsd(
        endog=df['urgency_score'],  # Dependent variable
        groups=df['feature'],        # Independent variable (groups)
        alpha=0.05                   # Significance level
    )
    
    # Step 3: Extract Results
    comparisons = []
    FOR each pair in tukey_result:
        comparison = {
            'group1': pair.group1,
            'group2': pair.group2,
            'meandiff': pair.meandiff,
            'p_adj': pair.p_adj,
            'lower': pair.lower,
            'upper': pair.upper,
            'reject': pair.reject
        }
        comparisons.append(comparison)
    
    RETURN comparisons
```

**Tukey HSD Calculation:**

**Purpose**: Identify which specific pairs of features differ significantly

**Method**: 
- Compares all possible pairs (3 features → 3 comparisons)
- Adjusts p-values for multiple comparisons (FWER control)
- Calculates confidence intervals for mean differences

**Pairwise Comparisons:**
1. Comfort & Fit vs Durability & Quality
2. Comfort & Fit vs Design & Style
3. Durability & Quality vs Design & Style

**Interpretation Example:**
```
Comparison: Comfort & Fit vs Design & Style
Mean Difference: 0.375 (37.5% higher dissatisfaction in Comfort)
P-adjusted: 0.0012 (< 0.05, significant!)
95% CI: [0.18, 0.57] (does not include 0)
Decision: Reject H₀ (significant difference exists)
```

**Business Insight:**
- If p-adj < 0.05: Prioritize the feature with higher mean
- If p-adj ≥ 0.05: Both features have similar priority

### 3.6 Management vs NLP Comparison Logic

**Process: Dual ANOVA Comparison**

```python
# Pseudocode
FUNCTION compare_management_vs_nlp():
    # Step 1: NLP Model Analysis (Customer Feedback)
    customer_feedback = get_all_feedback()
    nlp_anova_result = perform_anova(customer_feedback)
    nlp_p_value = nlp_anova_result['p_value']
    nlp_significant = (nlp_p_value < 0.05)
    
    # Step 2: Management Decision Analysis
    management_decisions = get_all_management_decisions()
    mgmt_anova_result = perform_anova(management_decisions)
    mgmt_p_value = mgmt_anova_result['p_value']
    mgmt_significant = (mgmt_p_value < 0.05)
    
    # Step 3: Comparison Logic
    IF nlp_significant AND mgmt_significant:
        agreement = "STRONG AGREEMENT"
        interpretation = "Both analyses identify significant differences"
        confidence = "HIGH"
        recommendation = "Proceed with identified priorities"
    
    ELSE IF NOT nlp_significant AND NOT mgmt_significant:
        agreement = "AGREEMENT"
        interpretation = "Both analyses show no significant differences"
        confidence = "MEDIUM"
        recommendation = "All features performing equally"
    
    ELSE:
        agreement = "DISAGREEMENT"
        interpretation = "Analyses conflict - mismatch between data and expert judgment"
        confidence = "LOW"
        recommendation = "Review methodology or collect more data"
    
    RETURN {
        'nlp_p_value': nlp_p_value,
        'mgmt_p_value': mgmt_p_value,
        'agreement': agreement,
        'interpretation': interpretation,
        'confidence': confidence,
        'recommendation': recommendation
    }
```

**Comparison Matrix:**

| NLP Significant? | Management Significant? | Agreement | Confidence |
|------------------|------------------------|-----------|------------|
| Yes | Yes | Strong Agreement | High |
| No | No | Agreement | Medium |
| Yes | No | Disagreement | Low |
| No | Yes | Disagreement | Low |

**Business Value:**
- **Agreement**: Validates ML predictions with expert judgment
- **Disagreement**: Flags potential issues in data or methodology
- **Confidence Metric**: Guides decision-making certainty

### 3.7 Voting Logic

**Process: Idea Voting**

```python
# Pseudocode
FUNCTION handle_vote(idea_id, customer_email, vote_type):
    # Step 1: Check Duplicate Vote
    existing_vote = check_user_vote(idea_id, customer_email)
    
    IF existing_vote:
        RETURN error("You have already voted on this idea")
    
    # Step 2: Record Vote
    record_user_vote(idea_id, customer_email, vote_type)
    
    # Step 3: Update Vote Counter
    IF vote_type == "thumbs_up":
        increment_thumbs_up(idea_id)
    ELSE IF vote_type == "thumbs_down":
        increment_thumbs_down(idea_id)
    
    # Step 4: Return Updated Counts
    updated_idea = get_idea_by_id(idea_id)
    RETURN {
        'thumbs_up': updated_idea.thumbs_up,
        'thumbs_down': updated_idea.thumbs_down
    }
```

**Duplicate Vote Prevention:**
- Tracks user-vote associations in `idea_votes` table
- Unique constraint: (idea_id, customer_email)
- Database-level enforcement prevents race conditions

**Atomic Operations:**
- Vote increment uses SQL `UPDATE ... SET count = count + 1`
- Ensures consistency in concurrent environments

### 3.8 Data Aggregation & Transformation

**Process: Feature-Level Aggregation**

```python
# Pseudocode
FUNCTION aggregate_feedback_by_feature(feedback_data):
    df = convert_to_dataframe(feedback_data)
    
    # Step 1: Group by Feature
    grouped = df.groupby('feature')
    
    # Step 2: Calculate Metrics
    aggregated = []
    FOR feature, group in grouped:
        total_count = len(group)
        need_improvement_count = len(group[group['urgency'] == 'Need Improvement'])
        improvement_rate = (need_improvement_count / total_count) * 100
        
        aggregated.append({
            'feature': feature,
            'total_feedback': total_count,
            'need_improvement': need_improvement_count,
            'improvement_rate': improvement_rate
        })
    
    # Step 3: Sort by Priority
    aggregated.sort(key=lambda x: x['improvement_rate'], reverse=True)
    
    RETURN aggregated
```

**Transformation Pipeline:**
```
Raw Database Rows → DataFrame → Group By Feature → Calculate Percentages → Sort → Return
```

**Example Output:**
```json
[
    {
        "feature": "Durability & Quality",
        "total_feedback": 38,
        "need_improvement": 28,
        "improvement_rate": 73.7
    },
    {
        "feature": "Comfort & Fit",
        "total_feedback": 45,
        "need_improvement": 32,
        "improvement_rate": 71.1
    },
    {
        "feature": "Design & Style",
        "total_feedback": 42,
        "need_improvement": 15,
        "improvement_rate": 35.7
    }
]
```


---

## 4. Layer 3: Data Access Layer - Internal Processes

### 4.1 Database Connection Management

**Process: Connection Lifecycle**

```python
# Pseudocode
FUNCTION get_db_connection():
    # Step 1: Load Configuration
    config = {
        'host': ENV['DB_HOST'],
        'database': ENV['DB_NAME'],
        'user': ENV['DB_USER'],
        'password': ENV['DB_PASSWORD'],
        'port': ENV['DB_PORT']
    }
    
    # Step 2: Establish Connection
    connection = psycopg2.connect(**config)
    
    # Step 3: Context Manager (Auto-cleanup)
    TRY:
        YIELD connection
    EXCEPT Exception:
        connection.rollback()
        RAISE
    FINALLY:
        connection.close()
```

**Connection Pattern:**
```python
# Usage Example
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feedback")
    results = cursor.fetchall()
    conn.commit()
# Connection automatically closed here
```

**Benefits:**
- **Automatic cleanup**: Connection closed even if error occurs
- **Transaction management**: Auto-rollback on exceptions
- **Resource efficiency**: No connection leaks
- **Thread safety**: Each request gets new connection

### 4.2 Database Initialization

**Process: Table Creation**

```python
# Pseudocode
FUNCTION init_database():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Table 1: Users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role VARCHAR(20) CHECK (role IN ('customer', 'owner'))
            )
        """)
        
        # Table 2: Feedback
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id SERIAL PRIMARY KEY,
                product VARCHAR(100),
                feature VARCHAR(100),
                subfeature VARCHAR(100),
                feedback_text TEXT,
                urgency VARCHAR(50),
                customer_name VARCHAR(100),
                customer_email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table 3: Ideas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ideas (
                id SERIAL PRIMARY KEY,
                feature VARCHAR(100),
                subfeature VARCHAR(100),
                idea_text TEXT,
                thumbs_up INTEGER DEFAULT 0,
                thumbs_down INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table 4: Innovative Ideas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS innovative_ideas (
                id SERIAL PRIMARY KEY,
                customer_email VARCHAR(100),
                idea_text TEXT,
                customer_name VARCHAR(100),
                thumbs_up INTEGER DEFAULT 0,
                thumbs_down INTEGER DEFAULT 0,
                approved BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table 5: Idea Votes (Duplicate Prevention)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS idea_votes (
                id SERIAL PRIMARY KEY,
                idea_id INTEGER REFERENCES innovative_ideas(id),
                customer_email VARCHAR(100),
                vote_type VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(idea_id, customer_email)
            )
        """)
        
        # Table 6: Management Decisions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS management_decisions (
                id SERIAL PRIMARY KEY,
                product VARCHAR(100),
                feature VARCHAR(100),
                sub_feature VARCHAR(100),
                urgency VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
```

**Database Schema Design Principles:**
1. **Primary Keys**: Auto-incrementing SERIAL for all tables
2. **Constraints**: CHECK constraints for enum-like fields
3. **Unique Constraints**: Prevent duplicate votes
4. **Foreign Keys**: Maintain referential integrity (idea_votes → innovative_ideas)
5. **Timestamps**: Track creation/update times
6. **Defaults**: Initialize counters to 0, timestamps to NOW()

### 4.3 CRUD Operations - Feedback

**Process: Save Feedback**

```python
# Pseudocode
FUNCTION save_feedback(product, feature, subfeature, feedback_text, urgency, customer_name, customer_email):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Parameterized Query (SQL Injection Prevention)
        query = """
            INSERT INTO feedback 
            (product, feature, subfeature, feedback_text, urgency, customer_name, customer_email)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        parameters = (product, feature, subfeature, feedback_text, urgency, customer_name, customer_email)
        
        cursor.execute(query, parameters)
        conn.commit()
        
        RETURN True
```

**Security Measures:**
- **Parameterized Queries**: Values passed separately from SQL
- **No String Concatenation**: Prevents SQL injection attacks
- **Input Validation**: Performed at Business Logic Layer

**Example Attack Prevention:**
```python
# Vulnerable (DON'T DO THIS):
query = f"INSERT INTO feedback VALUES ('{user_input}')"
# If user_input = "'; DROP TABLE feedback; --"
# Result: SQL injection attack!

# Safe (CORRECT):
query = "INSERT INTO feedback VALUES (%s)"
cursor.execute(query, (user_input,))
# Result: user_input treated as data, not code
```

**Process: Retrieve Feedback**

```python
# Pseudocode
FUNCTION get_feedback(limit=100):
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
            SELECT id, product, feature, subfeature, feedback_text, urgency, 
                   customer_name, customer_email, created_at
            FROM feedback
            ORDER BY created_at DESC
            LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        
        RETURN results  # List of dictionaries
```

**RealDictCursor Benefits:**
- Returns rows as dictionaries instead of tuples
- Access columns by name: `row['feature']` instead of `row[2]`
- Easier integration with pandas DataFrames

### 4.4 CRUD Operations - Ideas & Voting

**Process: Save Idea**

```python
# Pseudocode
FUNCTION save_idea(feature, subfeature, idea_text):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = """
            INSERT INTO ideas (feature, subfeature, idea_text, thumbs_up, thumbs_down)
            VALUES (%s, %s, %s, 0, 0)
        """
        
        cursor.execute(query, (feature, subfeature, idea_text))
        conn.commit()
```

**Process: Update Vote Count**

```python
# Pseudocode
FUNCTION update_idea_vote(idea_id, vote_type):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        IF vote_type == "thumbs_up":
            query = "UPDATE ideas SET thumbs_up = thumbs_up + 1 WHERE id = %s"
        ELSE:
            query = "UPDATE ideas SET thumbs_down = thumbs_down + 1 WHERE id = %s"
        
        cursor.execute(query, (idea_id,))
        conn.commit()
```

**Atomic Increment:**
- `thumbs_up = thumbs_up + 1` is atomic at database level
- Prevents race conditions in concurrent voting
- No need for application-level locking

**Process: Check User Vote**

```python
# Pseudocode
FUNCTION check_user_vote(idea_id, customer_email):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = """
            SELECT vote_type FROM idea_votes
            WHERE idea_id = %s AND customer_email = %s
        """
        
        cursor.execute(query, (idea_id, customer_email))
        result = cursor.fetchone()
        
        IF result:
            RETURN result['vote_type']  # "thumbs_up" or "thumbs_down"
        ELSE:
            RETURN None  # User hasn't voted
```

**Process: Record User Vote**

```python
# Pseudocode
FUNCTION record_user_vote(idea_id, customer_email, vote_type):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        TRY:
            query = """
                INSERT INTO idea_votes (idea_id, customer_email, vote_type)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (idea_id, customer_email, vote_type))
            conn.commit()
            RETURN True
        
        EXCEPT UniqueViolation:
            # User already voted (UNIQUE constraint violated)
            RETURN False
```

**Duplicate Prevention:**
- UNIQUE constraint on (idea_id, customer_email)
- Database enforces rule, not application code
- Handles concurrent vote attempts correctly

### 4.5 CRUD Operations - Users

**Process: Create User**

```python
# Pseudocode
FUNCTION create_user(username, password, role):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Hash password
        password_hash = SHA256(password)
        
        TRY:
            query = """
                INSERT INTO users (username, password_hash, role)
                VALUES (%s, %s, %s)
            """
            cursor.execute(query, (username, password_hash, role))
            conn.commit()
            RETURN True
        
        EXCEPT UniqueViolation:
            # Username already exists
            RETURN False
```

**Password Security:**
- Never store plain text passwords
- SHA-256 hashing (one-way function)
- Same password always produces same hash
- Cannot reverse hash to get original password

**Process: Verify User**

```python
# Pseudocode
FUNCTION verify_user(username, password):
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Hash provided password
        password_hash = SHA256(password)
        
        query = """
            SELECT username, role FROM users
            WHERE username = %s AND password_hash = %s
        """
        
        cursor.execute(query, (username, password_hash))
        result = cursor.fetchone()
        
        IF result:
            RETURN (True, result['role'])
        ELSE:
            RETURN (False, None)
```

**Authentication Flow:**
1. User provides username + password
2. System hashes password
3. Query database for matching username + hash
4. If found: Return success + role
5. If not found: Return failure

### 4.7 Transaction Management

**Process: Multi-Step Transaction**

```python
# Pseudocode
FUNCTION complex_operation():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        TRY:
            # Step 1: Insert idea
            cursor.execute("INSERT INTO ideas (...) VALUES (...)")
            idea_id = cursor.lastrowid
            
            # Step 2: Record vote
            cursor.execute("INSERT INTO idea_votes (...) VALUES (...)")
            
            # Step 3: Update counter
            cursor.execute("UPDATE ideas SET thumbs_up = thumbs_up + 1 WHERE id = %s", (idea_id,))
            
            # All steps successful - commit
            conn.commit()
            RETURN True
        
        EXCEPT Exception as e:
            # Any step failed - rollback all
            conn.rollback()
            RAISE e
```

**ACID Properties:**
- **Atomicity**: All steps succeed or all fail (no partial updates)
- **Consistency**: Database remains in valid state
- **Isolation**: Concurrent transactions don't interfere
- **Durability**: Committed data persists even after crash

**Rollback Scenarios:**
- Database constraint violation
- Network error during query
- Application logic error
- Deadlock detection


---

## 5. End-to-End Process Flows

### 5.1 Complete Feedback Submission Flow

**Scenario**: Customer submits feedback about cushioning

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
└─────────────────────────────────────────────────────────────────┘
1. Customer enters name and email → Store in session state
2. Customer selects "Comfort & Fit" feature → Reset conversation
3. System displays first question about "Cushioning & Support"
4. Customer types: "The cushioning feels inadequate after 2 hours"
5. Customer clicks "Submit Feedback" button
6. UI validates: input not empty, models loaded
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                           │
└─────────────────────────────────────────────────────────────────┘
7. Combine text: "Cushioning & Support The cushioning feels inadequate..."
8. Load vectorizer.pkl → Transform text to TF-IDF vector
9. Load model.pkl → Predict: 1 (Need Improvement)
10. Map prediction: 1 → "Need Improvement"
11. Call save_feedback() with all parameters
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DATA ACCESS LAYER                             │
└─────────────────────────────────────────────────────────────────┘
12. Open database connection
13. Execute INSERT query with parameters:
    - product: "Footwear"
    - feature: "Comfort & Fit"
    - subfeature: "Cushioning & Support"
    - feedback_text: "The cushioning feels inadequate..."
    - urgency: "Need Improvement"
    - customer_name: "John Doe"
    - customer_email: "john@example.com"
14. Commit transaction
15. Close connection
16. Return success
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                           │
└─────────────────────────────────────────────────────────────────┘
17. Increment questions_asked counter (0 → 1)
18. Calculate next sub-feature (still "Cushioning & Support")
19. Call OpenAI API for second question
20. Receive: "Any specific issues with arch support?"
21. Add to chat_history
22. Return to Presentation Layer
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
└─────────────────────────────────────────────────────────────────┘
23. Display new question in chat
24. Clear text input field
25. Increment form counter (force re-render)
26. Wait for next customer input
```

**Time Complexity**: ~2-3 seconds per feedback submission
- OpenAI API call: 1-2 seconds
- ML classification: <100ms
- Database insert: <50ms
- UI rendering: <100ms

### 5.2 Statistical Analysis Flow (Owner Dashboard)

**Scenario**: Owner views ANOVA results for crowd ideas

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
└─────────────────────────────────────────────────────────────────┘
1. Owner clicks "Statistical Analysis - Crowd Ideas" in sidebar
2. Page loads with auto-refresh enabled (60s interval)
3. Display loading spinner
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                           │
└─────────────────────────────────────────────────────────────────┘
4. Call get_feedback(limit=1000)
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DATA ACCESS LAYER                             │
└─────────────────────────────────────────────────────────────────┘
5. Execute: SELECT * FROM feedback ORDER BY created_at DESC LIMIT 1000
6. Fetch all rows as dictionaries
7. Return list of feedback records
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                           │
└─────────────────────────────────────────────────────────────────┘
8. Convert to pandas DataFrame
9. Map urgency to scores: "Need Improvement" → 1, "No Need" → 0
10. Group by feature:
    - Comfort & Fit: [1, 1, 0, 1, 0, 1, ...]
    - Durability: [1, 0, 1, 1, 1, 1, ...]
    - Design: [0, 0, 1, 0, 0, 0, ...]
11. Perform ANOVA:
    - Calculate between-group variance
    - Calculate within-group variance
    - Compute F-statistic = 18.456
    - Compute p-value = 0.000023
12. Interpret: p < 0.05 → Significant differences exist
13. Perform Tukey HSD (since ANOVA significant):
    - Compare all pairs
    - Adjust p-values for multiple comparisons
    - Calculate confidence intervals
14. Generate matplotlib plot for confidence intervals
15. Calculate summary statistics:
    - Total feedback per feature
    - Need Improvement count per feature
    - Improvement rate percentage
16. Sort features by improvement rate (descending)
17. Return all results to Presentation Layer
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
└─────────────────────────────────────────────────────────────────┘
18. Display ANOVA results:
    - F-statistic: 18.456
    - P-value: 0.000023
    - Decision: "Reject H₀: Significant differences exist"
19. Display Tukey HSD table with all pairwise comparisons
20. Render confidence interval plot
21. Display feature statistics table
22. Show bar chart of improvement rates
23. Display interpretation:
    - "Highest priority: Durability & Quality (73.7%)"
    - "Best performing: Design & Style (35.7%)"
24. Start 60-second timer for next refresh
```

**Data Volume Handling**:
- Limit queries to prevent memory overflow
- Use pagination for large datasets
- Cache results in session state
- Incremental loading for charts

### 5.3 Management vs NLP Comparison Flow

**Scenario**: Owner compares management decisions with NLP predictions

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
└─────────────────────────────────────────────────────────────────┘
1. Owner clicks "Management vs NLP Model" in sidebar
2. Page displays two-column layout
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                           │
└─────────────────────────────────────────────────────────────────┘
3. Parallel data retrieval:
   - Thread 1: get_feedback() for NLP analysis
   - Thread 2: get_all_management_decisions() for management analysis
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DATA ACCESS LAYER                             │
└─────────────────────────────────────────────────────────────────┘
4. Query 1: SELECT * FROM feedback
5. Query 2: SELECT * FROM management_decisions
6. Return both datasets
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                   BUSINESS LOGIC LAYER                           │
└─────────────────────────────────────────────────────────────────┘
7. NLP Analysis Path:
   - Convert feedback to DataFrame
   - Map urgency to scores
   - Group by feature
   - Perform ANOVA → p_value_nlp = 0.000023
   - Determine: Significant (p < 0.05)

8. Management Analysis Path:
   - Convert decisions to DataFrame
   - Map urgency to scores
   - Group by feature
   - Perform ANOVA → p_value_mgmt = 0.000156
   - Determine: Significant (p < 0.05)

9. Comparison Logic:
   - Both significant? → "STRONG AGREEMENT"
   - Calculate agreement percentage
   - Identify matching vs differing priorities
   - Generate recommendation

10. Return comparison results
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                            │
└─────────────────────────────────────────────────────────────────┘
11. Display two-column comparison:
    
    LEFT COLUMN (NLP Model):
    - P-value: 0.000023
    - Status: ✅ Significant
    - Top Priority: Durability (73.7%)
    
    RIGHT COLUMN (Management):
    - P-value: 0.000156
    - Status: ✅ Significant
    - Top Priority: Durability (75.0%)

12. Display comparison summary:
    - Agreement: STRONG AGREEMENT
    - Confidence: HIGH
    - Recommendation: "Proceed with identified priorities"

13. Display interpretation text:
    - "Both analyses show significant differences - Strong agreement"
    - Confidence level indicator
    - Actionable recommendation

14. Show comparison table with p-values and significance status
```

**Decision Support Output**:
- Statistical p-value comparison
- Significance indicators
- Agreement/disagreement interpretation
- Actionable recommendations

---

## 6. Performance Optimization Strategies

### 6.1 Database Query Optimization

**Indexing Strategy:**
```sql
-- Index on frequently queried columns
CREATE INDEX idx_feedback_feature ON feedback(feature);
CREATE INDEX idx_feedback_created_at ON feedback(created_at DESC);
CREATE INDEX idx_ideas_votes ON ideas(thumbs_up DESC, thumbs_down DESC);
CREATE INDEX idx_priorities_lookup ON priorities(footwear, feature, subfeature);
```

**Query Optimization:**
- Use LIMIT clauses to prevent large result sets
- Avoid SELECT * when specific columns needed
- Use WHERE clauses to filter at database level
- Leverage indexes for sorting (ORDER BY)

**Connection Pooling:**
- Context managers ensure connections are closed
- No connection leaks
- Efficient resource utilization

### 6.2 Caching Strategies

**Session State Caching:**
```python
# Cache expensive computations
if 'anova_results' not in st.session_state:
    st.session_state.anova_results = perform_anova(data)
else:
    results = st.session_state.anova_results
```

**Model Loading:**
```python
# Load ML models once per session
if 'classifier' not in st.session_state:
    st.session_state.classifier = joblib.load("models/model.pkl")
    st.session_state.vectorizer = joblib.load("models/vectorizer.pkl")
```

**Benefits:**
- Reduce redundant computations
- Faster page loads
- Lower API costs (OpenAI)
- Better user experience

### 6.3 Asynchronous Processing

**Auto-Refresh Implementation:**
```python
# Non-blocking refresh
st_autorefresh(interval=60000, key="dashboard_refresh")
```

**Benefits:**
- Dashboard updates without user action
- Real-time data visibility
- No manual refresh needed

### 6.4 Error Handling & Resilience

**Graceful Degradation:**
```python
# Fallback for API failures
try:
    question = generate_question_with_openai(sub_feature)
except APIError:
    question = f"How would you rate the {sub_feature.lower()}?"
```

**Error Recovery:**
- Database connection failures → Retry with exponential backoff
- ML model loading errors → Display user-friendly message
- API timeouts → Use cached/fallback responses

**Logging Strategy:**
```python
# Log errors for debugging
try:
    result = risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    display_user_friendly_error()
```

---

## 7. Security Measures

### 7.1 Authentication Security

**Password Hashing:**
- SHA-256 one-way hashing
- No plain text storage
- Salt could be added for enhanced security

**Session Management:**
- Server-side session state
- Automatic timeout after inactivity
- Secure logout functionality

### 7.2 SQL Injection Prevention

**Parameterized Queries:**
```python
# SAFE: Parameters passed separately
cursor.execute("SELECT * FROM users WHERE username = %s", (username,))

# UNSAFE: String concatenation (DON'T DO THIS)
cursor.execute(f"SELECT * FROM users WHERE username = '{username}'")
```

**Input Validation:**
- Validate data types at Business Logic Layer
- Sanitize user inputs
- Enforce length limits

### 7.3 Access Control

**Role-Based Authorization:**
```python
if user_role != "owner":
    st.error("Access denied: Owner privileges required")
    st.stop()
```

**Page-Level Protection:**
- Check authentication before rendering
- Validate role for sensitive operations
- Hide UI elements based on permissions

### 7.4 Data Privacy

**PII Handling:**
- Customer emails stored securely
- No sensitive data in logs
- GDPR compliance considerations

**Database Security:**
- Environment variables for credentials
- No hardcoded passwords
- Encrypted connections (SSL/TLS recommended)

---

## 8. Scalability Considerations

### 8.1 Horizontal Scaling

**Database:**
- PostgreSQL supports read replicas
- Master-slave replication for high availability
- Connection pooling for concurrent users

**Application:**
- Streamlit Cloud deployment
- Load balancing across multiple instances
- Stateless design (session state in database)

### 8.2 Vertical Scaling

**Resource Optimization:**
- Efficient pandas operations
- Vectorized computations
- Minimal memory footprint

**Model Optimization:**
- Pre-trained models (no runtime training)
- Lightweight TF-IDF vectorizer
- Fast inference (<100ms)

### 8.3 Data Volume Management

**Archiving Strategy:**
- Move old feedback to archive tables
- Implement data retention policies
- Periodic cleanup jobs

**Pagination:**
- Limit query results (default: 100 rows)
- Implement offset-based pagination
- Lazy loading for large datasets

---

## 9. Testing & Quality Assurance

### 9.1 Unit Testing

**Business Logic Tests:**
```python
def test_classify_feedback():
    result = classify_feedback("Cushioning & Support", "Feels inadequate")
    assert result in ["Need Improvement", "No Need Improvement"]

def test_anova_calculation():
    data = generate_test_data()
    result = perform_anova(data)
    assert 'f_statistic' in result
    assert 'p_value' in result
```

### 9.2 Integration Testing

**Database Tests:**
```python
def test_save_and_retrieve_feedback():
    save_feedback("Footwear", "Comfort", "Cushioning", "Test", "Need Improvement")
    results = get_feedback(limit=1)
    assert len(results) == 1
    assert results[0]['feedback_text'] == "Test"
```

### 9.3 End-to-End Testing

**User Flow Tests:**
- Simulate complete feedback submission
- Test voting mechanisms
- Verify statistical calculations
- Validate UI rendering

---

## 10. Conclusion

The Product Feedback Analyzer System demonstrates a robust three-layer architecture that effectively separates concerns while maintaining cohesive functionality. The internal processes are designed with security, scalability, and user experience as primary considerations.

### Key Strengths:

1. **Modular Design**: Clear separation between presentation, logic, and data layers
2. **AI Integration**: Seamless combination of conversational AI and ML classification
3. **Statistical Rigor**: ANOVA and Tukey HSD provide scientific validation
4. **Security**: Parameterized queries, password hashing, role-based access
5. **Performance**: Caching, indexing, and efficient algorithms
6. **Scalability**: Database-driven architecture supports growth
7. **User Experience**: Real-time updates, intuitive interface, error handling

### Future Enhancements:

1. **Advanced ML**: Deep learning models for sentiment analysis
2. **Real-time Analytics**: WebSocket-based live updates
3. **Mobile Support**: Responsive design for mobile devices
4. **API Layer**: RESTful API for third-party integrations
5. **Advanced Security**: OAuth2, JWT tokens, rate limiting
6. **Monitoring**: Application performance monitoring (APM)
7. **Internationalization**: Multi-language support

This comprehensive internal process documentation provides a complete understanding of how the system operates at every layer, suitable for thesis documentation and technical reference.

---

**Document Version**: 1.0  
**Last Updated**: February 18, 2026  
**Author**: System Architecture Team  
**Purpose**: Thesis Documentation - Internal Process Analysis
