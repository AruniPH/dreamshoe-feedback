import streamlit as st
import pandas as pd
from openai import OpenAI
import joblib
from PIL import Image
from streamlit_option_menu import option_menu
from streamlit_autorefresh import st_autorefresh
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
from auth import check_authentication, login_page, logout
from database import save_feedback, get_feedback, save_idea, get_ideas, update_idea_vote, save_innovative_idea, update_innovative_idea_vote, get_db_connection, get_all_innovative_ideas, check_user_vote, record_user_vote, save_management_decision
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv('.env.windows')

def _get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.getenv(key)

st.set_page_config(page_title="DreamShoe - Product Feedback", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for button styling
st.markdown("""
<style>
.stButton > button {
    background-color: #f0f2f6 !important;
    border-color: #e6e9ef !important;
    color: #262730 !important;
}
.stButton > button[kind="primary"] {
    background-color: white !important;
    border-color: #e6e9ef !important;
    color: #262730 !important;
}
.stButton > button:hover {
    background-color: #e6e9ef !important;
    border-color: #d4d8e0 !important;
}
.stButton > button[kind="primary"]:hover {
    background-color: #f8f9fa !important;
    border-color: #d4d8e0 !important;
}
</style>
""", unsafe_allow_html=True)

# Hide Streamlit auto-generated pages
st.markdown("""<style>[data-testid="stSidebarNav"] {display: none;}</style>""", unsafe_allow_html=True)

# Authentication check
if not check_authentication():
    st.markdown("""<style>[data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)
    login_page()
    st.stop()

# Initialize database tables
try:
    from database import init_database
    init_database()
except Exception:
    pass  # Tables might already exist

user_role = st.session_state.user_role
logo_path = "logo.png"

# Sidebar with user info and navigation
with st.sidebar:
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.image(logo_path, width=80)
    st.title("DreamShoe")
    st.write(f"Logged in as: **{st.session_state.username}** ({user_role})")
    
    if st.button("Logout"):
        logout()
        st.rerun()
    
    # Role-based navigation
    if user_role == "customer":
        if st.button("Customer Hub", use_container_width=True):
            st.session_state.selected_page = "Customer Hub"
        selected = st.session_state.get('selected_page', 'Customer Hub')
    else:  # owner
        selected = st.session_state.get('selected_page', 'Customer Hub')
        
        if st.button("Customer Hub", use_container_width=True, type="primary" if selected == "Customer Hub" else "secondary"):
            st.session_state.selected_page = "Customer Hub"
            st.rerun()
        if st.button("Owner Dashboard", use_container_width=True, type="primary" if selected == "Owner Dashboard" else "secondary"):
            st.session_state.selected_page = "Owner Dashboard"
            st.rerun()
        if st.button("Statistical Analysis-Crowd ideas", use_container_width=True, type="primary" if selected == "Statistical Analysis-Crowd ideas" else "secondary"):
            st.session_state.selected_page = "Statistical Analysis-Crowd ideas"
            st.rerun()
        if st.button("Statistical analysis- Management Decisions", use_container_width=True, type="primary" if selected == "Statistical analysis- Management Decisions" else "secondary"):
            st.session_state.selected_page = "Statistical analysis- Management Decisions"
            st.rerun()
        if st.button("Management vs NLP model", use_container_width=True, type="primary" if selected == "Management vs NLP model" else "secondary"):
            st.session_state.selected_page = "Management vs NLP model"
            st.rerun()

# =========================================================
# PAGE 1: CUSTOMER HUB (Combined Feedback & Intelligence)
# =========================================================
if selected == "Customer Hub":
    logo = Image.open(logo_path)
    base_height = 100
    h_percent = (base_height / float(logo.size[1]))
    w_size = int((float(logo.size[0]) * float(h_percent)))
    logo = logo.resize((w_size, base_height))

    col1, col2 = st.columns([1, 6])
    with col1:
        st.image(logo, width=w_size)
    with col2:
        st.markdown("<h1 style='margin: 0; padding: 0; color:#1f77b4;'>Think & Win - CrowdChoice Reward</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin: 0; padding: 0; color:#8B4513;'>DreamShoe</h3>", unsafe_allow_html=True)
        st.markdown("<p style='margin-top: 10px; color:#2E8B57; font-size: 18px; font-weight: bold;'>Share your insight, innovative idea on the footware item you are using and stand a chance to win a Rs. 5,000 gift voucher each month...</p>", unsafe_allow_html=True)

    # AI Chatbot Feedback Collector Section
    st.markdown("---")
    st.subheader("AI Chatbot Feedback Collector")
    st.markdown("***Share your experience with the footwear you've used to help us improve future designs. Select the feature that matters most to you and chat with our AI assistant to contribute your ideas.***")

    product = "Product"
    
    # Initialize session state
    if "last_product" not in st.session_state or st.session_state.last_product != product:
        st.session_state.chat_history = []
        st.session_state.questions_asked = 0
        st.session_state.feedback_complete = False
        st.session_state.last_product = product

    # Load models
    try:
        client = OpenAI(api_key=_get_secret("OPENAI_API_KEY"))
        clf = joblib.load("models/model.pkl")
        vectorizer = joblib.load("models/vectorizer.pkl")
        models_loaded = True
    except Exception as e:
        st.warning(f"Models not loaded: {e}")
        models_loaded = False

    features_dict = {
        "Comfort & Fit": ["Cushioning & Support", "Breathability", "Sizing Accuracy"],
        "Durability & Quality": ["Material Strength", "Sole & Stitching", "Longevity"],
        "Design & Style": ["Aesthetics", "Versatility", "Brand Identity"]
    }

    if not st.session_state.feedback_complete:
        feature = st.selectbox("Select Feature", list(features_dict.keys()), key="feedback_feature")

        # Initialize session state for chat
        if "current_subfeature_index" not in st.session_state:
            st.session_state.current_subfeature_index = 0
        if "current_question_count" not in st.session_state:
            st.session_state.current_question_count = 0
        if "selected_feature" not in st.session_state:
            st.session_state.selected_feature = feature
        if "feedback_form_counter" not in st.session_state:
            st.session_state.feedback_form_counter = 0

        subfeatures = features_dict[feature]
        total_questions = len(subfeatures) * 2  # 2 questions per subfeature

        # Reset if feature changed
        if st.session_state.selected_feature != feature:
            st.session_state.current_subfeature_index = 0
            st.session_state.current_question_count = 0
            st.session_state.selected_feature = feature
            st.session_state.chat_history = []
            st.session_state.questions_asked = 0

        # Ask the first question if chat is empty
        if not st.session_state.chat_history:
            first_subfeature = subfeatures[0]
            try:
                if models_loaded:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": f"You are a helpful assistant for a product feedback system. Ask the FIRST specific, short question (maximum 15 words) about '{first_subfeature}' for product feedback. Be direct and concise."},
                            {"role": "user", "content": f"Ask me about {first_subfeature}"}
                        ],
                        max_tokens=50
                    )
                    assistant_response = response.choices[0].message.content
                else:
                    assistant_response = f"How would you rate the {first_subfeature.lower()} of this product?"
            except Exception:
                assistant_response = f"How would you rate the {first_subfeature.lower()} of this product?"
            st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Show input if questions remain
        if st.session_state.questions_asked < total_questions:
            user_input = st.text_area("Share your experience:", placeholder="Type your feedback here...", height=100, key=f"feedback_input_{st.session_state.feedback_form_counter}")

            if st.button("Submit Feedback", key="submit_feedback"):
                if not user_input.strip():
                    st.error("Please enter your feedback")
                elif not models_loaded:
                    st.error("Models not loaded. Please check configuration.")
                else:
                    current_subfeature_index = st.session_state.questions_asked // 2
                    current_subfeature = subfeatures[current_subfeature_index]

                    st.session_state.chat_history.append({"role": "user", "content": user_input})

                    # Save feedback to database
                    try:
                        combined_text = f"{feature} {current_subfeature} {user_input}"
                        X_vec = vectorizer.transform([combined_text]) #TF-IDF
                        prediction = clf.predict(X_vec)[0]
                        prediction_label = "Need Improvement" if prediction == 1 else "No Need Improvement"
                        customer_name = st.session_state.get('customer_name', '')
                        customer_email = st.session_state.get('customer_email', '')
                        save_feedback(product, feature, current_subfeature, user_input, prediction_label, customer_name, customer_email)
                    except Exception as e:
                        st.error(f"Error processing feedback: {e}")

                    st.session_state.questions_asked += 1

                    if st.session_state.questions_asked < total_questions:
                        next_subfeature_index = st.session_state.questions_asked // 2
                        next_subfeature = subfeatures[next_subfeature_index]
                        question_number_for_subfeature = (st.session_state.questions_asked % 2) + 1

                        try:
                            if question_number_for_subfeature == 1:
                                system_prompt = f"You are a helpful assistant for a product feedback system. Ask the FIRST specific, short question (maximum 15 words) about '{next_subfeature}' for product feedback. Be direct and concise."
                            else:
                                system_prompt = f"You are a helpful assistant for a product feedback system. Ask a SECOND different specific, short question (maximum 15 words) about '{next_subfeature}' for product feedback. Be direct and concise."

                            response = client.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content": system_prompt},
                                    {"role": "user", "content": f"Ask me about {next_subfeature}"}
                                ],
                                max_tokens=50
                            )
                            assistant_response = response.choices[0].message.content
                        except Exception:
                            fallback_questions = [
                                f"How would you rate the {next_subfeature.lower()} of this product?",
                                f"Any specific issues with the {next_subfeature.lower()}?"
                            ]
                            assistant_response = fallback_questions[(question_number_for_subfeature - 1) % 2]

                        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
                    else:
                        st.session_state.feedback_complete = True
                        st.session_state.chat_history.append({"role": "assistant", "content": f"Thank you for your detailed feedback about all aspects of {feature}! Your responses have been recorded."})

                    st.session_state.feedback_form_counter += 1
                    st.rerun()
    else:
        # Show completed chat but allow new session
        st.success("Feedback session completed!")
        if st.button("Start New Feedback Session"):
            st.session_state.chat_history = []
            st.session_state.questions_asked = 0
            st.session_state.feedback_complete = False
            st.session_state.feedback_form_counter = 0
            st.session_state.current_subfeature_index = 0
            st.session_state.current_question_count = 0
            st.rerun()

    # =========================================================
    # SECTION 2: ANALYTICS & INNOVATIVE IDEAS
    # =========================================================
    st.markdown("---")
    st.subheader("Current Analytics & Innovation Hub")

    # Get all feedback data for analytics
    feedback_rows = get_feedback(limit=100)
    
    if feedback_rows:
        df = pd.DataFrame(feedback_rows)
        df.rename(columns={"urgency": "Urgency", "feature": "Feature", "subfeature": "SubFeature"}, inplace=True)
        df['Urgency'] = df['Urgency'].replace({
            "Need improvements": "Need Improvement",
            "need improvement": "Need Improvement",
            "No need improvement": "No Need Improvement",
            "no need improvement": "No Need Improvement"
        })
        
        # Layout: Analytics (50%) | Form (50%)
        col_analytics, col_form = st.columns([1, 1])
        
        with col_analytics:
            # Charts side by side
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                # Feature chart
                feature_counts = df.groupby(['Feature', 'Urgency']).size().unstack(fill_value=0)
                for col in ["Need Improvement", "No Need Improvement"]:
                    if col not in feature_counts.columns:
                        feature_counts[col] = 0
                feature_percentages = feature_counts.div(feature_counts.sum(axis=1), axis=0) * 100
                
                st.markdown("**Feature Requirements**")
                st.bar_chart(feature_percentages, use_container_width=True)
            
            with chart_col2:
                # All 9 Sub-features chart
                st.markdown("**Sub-Feature Requirements**")
                
                all_subfeatures = [
                    "Cushioning & Support", "Breathability", "Sizing Accuracy",
                    "Material Strength", "Sole & Stitching", "Longevity", 
                    "Aesthetics", "Versatility", "Brand Identity"
                ]
                
                subfeature_data = []
                for subf in all_subfeatures:
                    subf_data = df[df['SubFeature'] == subf]
                    if not subf_data.empty:
                        need_improvement = (subf_data['Urgency'] == 'Need Improvement').sum()
                        total = len(subf_data)
                        need_pct = (need_improvement / total * 100) if total > 0 else 0
                        no_need_pct = 100 - need_pct
                    else:
                        need_pct = 0
                        no_need_pct = 0
                    
                    subfeature_data.append({
                        'SubFeature': subf,
                        'Need Improvement': need_pct,
                        'No Need Improvement': no_need_pct
                    })
                
                subf_df = pd.DataFrame(subfeature_data)
                subf_df.set_index('SubFeature', inplace=True)
                st.bar_chart(subf_df, use_container_width=True)
        
        with col_form:
            st.markdown("**Submit Your Innovative Idea**")
            
            # Initialize form counter
            if "form_counter" not in st.session_state:
                st.session_state.form_counter = 0
            
            with st.form(f"innovative_idea_form_{st.session_state.form_counter}"):
                innovative_idea = st.text_area("Your Innovative Idea", placeholder="Share your innovative idea...", height=200)
                submitted = st.form_submit_button("Submit Idea", use_container_width=True)
                
                if submitted:
                    customer_email = st.session_state.get('customer_email', '')
                    customer_name = st.session_state.get('customer_name', '')
                    if customer_email.strip() and innovative_idea.strip():
                        save_innovative_idea(customer_email, innovative_idea, customer_name)
                        st.success("Idea submitted for review!")
                        # Increment counter to create new form
                        st.session_state.form_counter += 1
                        st.rerun()
                    else:
                        st.error("Please fill in your email in the Customer Information section and enter your idea")
    else:
        # No analytics data - show form only
        st.markdown("**Submit Your Innovative Idea**")
        
        # Initialize form counter
        if "form_counter_no_data" not in st.session_state:
            st.session_state.form_counter_no_data = 0
        
        with st.form(f"innovative_idea_form_no_data_{st.session_state.form_counter_no_data}"):
            innovative_idea = st.text_area("Your Innovative Idea", placeholder="Share your innovative idea...", height=150)
            submitted = st.form_submit_button("Submit Idea", use_container_width=True)
            
            if submitted:
                customer_email = st.session_state.get('customer_email', '')
                customer_name = st.session_state.get('customer_name', '')
                if customer_email.strip() and innovative_idea.strip():
                    save_innovative_idea(customer_email, innovative_idea, "General", customer_name)
                    st.success("Idea submitted for review!")
                    # Increment counter to create new form
                    st.session_state.form_counter_no_data += 1
                    st.rerun()
                else:
                    st.error("Please fill in your email in the Customer Information section and enter your idea")
        
        st.info("No analytics data available yet.")

    # =========================================================
    # SECTION 3: VOTING ON INNOVATIVE IDEAS
    # =========================================================
    st.markdown("---")
    st.subheader("Vote on Innovative Ideas")
    
    # Get all innovative ideas
    all_ideas = get_all_innovative_ideas()
    
    if all_ideas:
        customer_email = st.session_state.get('customer_email', '')
        
        for idea in all_ideas:
            col_idea, col_up, col_down = st.columns([6, 1, 1])
            with col_idea:
                st.write(idea['idea_text'])
            with col_up:
                # Check if user has voted on this idea
                user_vote = check_user_vote(idea['id'], customer_email) if customer_email else None
                voted_up = user_vote == "up"
                button_type = "primary" if voted_up else "secondary"
                
                if st.button("👍", key=f"vote_up_{idea['id']}", type=button_type):
                    if not customer_email:
                        st.error("Please fill in your email in the Customer Information section")
                    elif user_vote is not None:
                        st.error("You cannot vote twice for same idea")
                    else:
                        update_innovative_idea_vote(idea['id'], "up")
                        record_user_vote(idea['id'], customer_email, "up")
                        st.success("Vote recorded!")
                        st.rerun()
            with col_down:
                # Check if user has voted on this idea
                user_vote = check_user_vote(idea['id'], customer_email) if customer_email else None
                voted_down = user_vote == "down"
                button_type = "primary" if voted_down else "secondary"
                
                if st.button("👎", key=f"vote_down_{idea['id']}", type=button_type):
                    if not customer_email:
                        st.error("Please fill in your email in the Customer Information section")
                    elif user_vote is not None:
                        st.error("You cannot vote twice for same idea")
                    else:
                        update_innovative_idea_vote(idea['id'], "down")
                        record_user_vote(idea['id'], customer_email, "down")
                        st.success("Vote recorded!")
                        st.rerun()
    else:
        st.info("No innovative ideas submitted yet.")

# =========================================================
# PAGE 2: OWNER DASHBOARD (Owner Only)
# =========================================================
if selected == "Feedback Collector":
    logo = Image.open(logo_path)
    base_height = 100
    h_percent = (base_height / float(logo.size[1]))
    w_size = int((float(logo.size[0]) * float(h_percent)))
    logo = logo.resize((w_size, base_height))

    col1, col2 = st.columns([1, 6])
    with col1:
        st.image(logo, width=w_size)
    with col2:
        st.markdown("<h1 style='margin: 0; padding: 0; color:#1f77b4;'>DreamShoe</h1>", unsafe_allow_html=True)

    st.subheader("Crowd Idea Collector - AI Chatbot based Feedback")
    st.markdown("***Share your experience with the footwear you've used to help us improve future designs. Select the feature that matters most to you and chat with our AI assistant to contribute your ideas.***")

    product = "Product"
    if "last_product" not in st.session_state or st.session_state.last_product != product:
        st.session_state.chat_history = []
        st.session_state.questions_asked = 0
        st.session_state.feedback_complete = False
        st.session_state.last_product = product

    try:
        client = OpenAI(api_key=_get_secret("OPENAI_API_KEY"))
        clf = joblib.load("models/model.pkl")
        vectorizer = joblib.load("models/vectorizer.pkl")
    except Exception as e:
        st.error(f"Error loading models or API: {e}")
        st.stop()

    FEATURES = {
        "Comfort & Fit": ["Cushioning & Support", "Breathability", "Sizing Accuracy"],
        "Durability & Quality": ["Material Strength", "Sole & Stitching", "Longevity"],
        "Design & Style": ["Aesthetics", "Versatility", "Brand Identity"]
    }

    feature = st.selectbox("Select Feature:", list(FEATURES.keys()))
    if "last_feature" not in st.session_state or st.session_state.last_feature != feature:
        st.session_state.chat_history = []
        st.session_state.questions_asked = 0
        st.session_state.feedback_complete = False
        st.session_state.last_feature = feature

    sub_features = FEATURES[feature]

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "questions_asked" not in st.session_state:
        st.session_state.questions_asked = 0
    if "feedback_complete" not in st.session_state:
        st.session_state.feedback_complete = False

    st.subheader("Chat with the Bot")

    if len(st.session_state.chat_history) == 0 and not st.session_state.feedback_complete:
        first_q = f"Please provide your feedback on **{feature}**."
        st.session_state.chat_history.append({"role": "bot", "content": first_q})

    for msg in st.session_state.chat_history:
        if msg["role"] == "bot":
            st.markdown(f"**Bot:** {msg['content']}")
        else:
            st.markdown(f"**You:** {msg['content']}")

    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Your Answer:", key="user_input")
        submit = st.form_submit_button("Send")

    if submit and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.questions_asked += 1

        try:
            # GPT determines which sub-feature the answer relates to
            sub_feature = classify_subfeature(user_input, sub_features)
            
            # Use only sub-feature and user answer for ML prediction
            combined_text = f"{sub_feature} {user_input}"
            X_vec = vectorizer.transform([combined_text])
            prediction = clf.predict(X_vec)[0]
            prediction_label = "Need Improvement" if prediction == 1 else "No Need Improvement"

            save_feedback(product, feature, sub_feature, user_input, prediction_label)
        except Exception as e:
            st.error(f"Error processing feedback: {e}")
            st.stop()

        if st.session_state.questions_asked >= 5:
            st.session_state.feedback_complete = True
        else:
            previous_answers = [m["content"] for m in st.session_state.chat_history if m["role"] == "user"]
            next_q = generate_question(previous_answers, sub_features)
            st.session_state.chat_history.append({"role": "bot", "content": next_q})
        st.rerun()

    if st.session_state.feedback_complete:
        st.success("Feedback collection complete!")
        if st.button("Start New Feedback"):
            st.session_state.chat_history = []
            st.session_state.questions_asked = 0
            st.session_state.feedback_complete = False
            st.rerun()

# =========================================================
# PAGE 2: COLLECTIVE INTELLIGENCE (Customer)
# =========================================================
elif selected == "Collective Intelligence":
    st.title("Pool of Collective Intelligence")
    
    if user_role == "owner":
        # Owner view - general feedback only
        st.markdown("Submit your ideas for product improvement and vote on others' ideas.")

        features_dict = {
            "Comfort & Fit": ["Cushioning & Support", "Breathability", "Sizing Accuracy"],
            "Durability & Quality": ["Material Strength", "Sole & Stitching", "Longevity"],
            "Design & Style": ["Aesthetics", "Versatility", "Brand Identity"]
        }

        idea_feature = st.selectbox("Select Feature", list(features_dict.keys()))
        if idea_feature:
            idea_subfeature = st.selectbox("Select Sub-feature", features_dict[idea_feature])

        new_idea = st.text_area("Describe your improvement idea:")
        if st.button("Submit Idea") and new_idea.strip() != "":
            try:
                save_idea(idea_feature, idea_subfeature, new_idea.strip())
                st.success("Idea submitted successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error submitting idea: {e}")

        if "vote_counter" not in st.session_state:
            st.session_state.vote_counter = 0

        idea_rows = get_ideas()
        if not idea_rows:
            st.info("No ideas submitted yet.")
        else:
            for row in idea_rows:
                st.markdown(f"**Feature:** {row['feature']} | **Sub-feature:** {row['subfeature']}")
                st.markdown(f"Idea: {row['idea_text']}")
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"👍 {row['thumbs_up']}", key=f"up_{row['id']}"):
                        update_idea_vote(row['id'], "up")
                        st.rerun()
                with col2:
                    if st.button(f"👎 {row['thumbs_down']}", key=f"down_{row['id']}"):
                        update_idea_vote(row['id'], "down")
                        st.rerun()
                st.markdown("---")
    
    else:
        # Customer view - general feedback only
        selected_fw = "General"
        
        # Get all feedback data for dashboard
        feedback_rows = get_feedback(limit=100)
        
        if feedback_rows:
            df = pd.DataFrame(feedback_rows)
            df.rename(columns={"urgency": "Urgency", "feature": "Feature", "subfeature": "SubFeature"}, inplace=True)
            df['Urgency'] = df['Urgency'].replace({
                "Need improvements": "Need Improvement",
                "need improvement": "Need Improvement",
                "No need improvement": "No Need Improvement",
                "no need improvement": "No Need Improvement"
            })
            
            # Main layout: Analytics (70%) | Form (30%)
            col_analytics, col_form = st.columns([7, 3])
            
            with col_analytics:
                st.subheader("📈 Current Analytics")
                
                # Feature chart
                feature_counts = df.groupby(['Feature', 'Urgency']).size().unstack(fill_value=0)
                for col in ["Need Improvement", "No Need Improvement"]:
                    if col not in feature_counts.columns:
                        feature_counts[col] = 0
                feature_percentages = feature_counts.div(feature_counts.sum(axis=1), axis=0) * 100
                
                st.markdown("**Feature Improvement Requirements**")
                st.bar_chart(feature_percentages, use_container_width=True)
                
                # All 9 Sub-features chart
                st.markdown("**Sub-Feature Improvement Requirements (All 9 Sub-Features)**")
                
                # Define all 9 sub-features
                all_subfeatures = [
                    "Cushioning & Support", "Breathability", "Sizing Accuracy",
                    "Material Strength", "Sole & Stitching", "Longevity", 
                    "Aesthetics", "Versatility", "Brand Identity"
                ]
                
                # Create sub-feature data for all 9 sub-features
                subfeature_data = []
                for subf in all_subfeatures:
                    subf_data = df[df['SubFeature'] == subf]
                    if not subf_data.empty:
                        need_improvement = (subf_data['Urgency'] == 'Need Improvement').sum()
                        total = len(subf_data)
                        need_pct = (need_improvement / total * 100) if total > 0 else 0
                        no_need_pct = 100 - need_pct
                    else:
                        need_pct = 0
                        no_need_pct = 0
                    
                    subfeature_data.append({
                        'SubFeature': subf,
                        'Need Improvement': need_pct,
                        'No Need Improvement': no_need_pct
                    })
                
                subf_df = pd.DataFrame(subfeature_data)
                subf_df.set_index('SubFeature', inplace=True)
                st.bar_chart(subf_df, use_container_width=True)
            
            with col_form:
                st.subheader("Submit Your Innovative Idea")
                with st.form("innovative_idea_form"):
                    customer_name = st.text_input("Your Name", placeholder="Enter your name")
                    innovative_idea = st.text_area("Your Innovative Idea", placeholder="Share your innovative idea to improve our products...", height=200)
                    submitted = st.form_submit_button("Submit Innovative Idea", use_container_width=True)
                    
                    if submitted:
                        if customer_name.strip() and innovative_idea.strip():
                            save_innovative_idea(customer_name, innovative_idea)
                            st.success("Your innovative idea has been submitted for review!")
                            st.rerun()
                        else:
                            st.error("Please fill in both your name and idea")
        else:
            # No analytics data available - show form only
            st.subheader("Submit Your Innovative Idea")
            with st.form("innovative_idea_form"):
                customer_name = st.text_input("Your Name", placeholder="Enter your name")
                innovative_idea = st.text_area("Your Innovative Idea", placeholder="Share your innovative idea to improve our products...", height=150)
                submitted = st.form_submit_button("Submit Innovative Idea", use_container_width=True)
                
                if submitted:
                    if customer_name.strip() and innovative_idea.strip():
                        save_innovative_idea(customer_name, innovative_idea, "General")
                        st.success("Your innovative idea has been submitted for review!")
                        st.rerun()
                    else:
                        st.error("Please fill in both your name and idea")
            
            st.info("No analytics data available yet.")
        
        # Display approved innovative ideas for voting
        st.subheader("🗳️ Vote on Approved Innovative Ideas")
        approved_ideas = get_approved_innovative_ideas()
        
        if approved_ideas:
            for idea in approved_ideas:
                with st.container():
                    col_idea, col_vote = st.columns([4, 1])
                    with col_idea:
                        st.markdown(f"**Idea by:** {idea['customer_name']}")
                        st.write(idea['idea_text'])
                    with col_vote:
                        col_up, col_down = st.columns(2)
                        with col_up:
                            if st.button("👍", key=f"inno_up_{idea['id']}"):
                                update_innovative_idea_vote(idea['id'], "up")
                                st.success("Vote recorded!")
                                st.rerun()
                        with col_down:
                            if st.button("👎", key=f"inno_down_{idea['id']}"):
                                update_innovative_idea_vote(idea['id'], "down")
                                st.success("Vote recorded!")
                                st.rerun()
                    st.divider()
        else:
            st.info("No approved innovative ideas available for voting yet.")

# =========================================================
# PAGE 3: OWNER DASHBOARD (Owner Only)
# =========================================================
elif selected == "Owner Dashboard":
    count = st_autorefresh(interval=60_000, key="dashboard_refresh")
    
    st.title("Crowd idea based Collective Intelligence analyzer")
    st.markdown("<p style='font-size:16px; color:gray;'>This dashboard analyzes crowd ideas and feedback to prioritize feature improvements.</p>", unsafe_allow_html=True)

    # Get all feedback
    feedback_rows = get_feedback(limit=100)
    
    if feedback_rows:
        df = pd.DataFrame(feedback_rows)
        df.rename(columns={"feedback_text": "Feedback", "urgency": "Urgency", "feature": "Feature", "subfeature": "SubFeature"}, inplace=True)
        df['Urgency'] = df['Urgency'].replace({
            "Need improvements": "Need Improvement",
            "need improvement": "Need Improvement",
            "No need improvement": "No Need Improvement",
            "no need improvement": "No Need Improvement"
        })

        st.subheader("Feature & Sub-Feature Improvement Requirements")

        # Charts side by side
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            feature_counts = df.groupby(['Feature', 'Urgency']).size().unstack(fill_value=0)
            for col in ["Need Improvement", "No Need Improvement"]:
                if col not in feature_counts.columns:
                    feature_counts[col] = 0
            feature_percentages = feature_counts.div(feature_counts.sum(axis=1), axis=0) * 100
            
            st.markdown("**Feature Requirements**")
            st.bar_chart(feature_percentages, use_container_width=True)
        
        with chart_col2:
            st.markdown("**Sub-Feature Requirements**")
            
            # All 9 Sub-features chart
            all_subfeatures = [
                "Cushioning & Support", "Breathability", "Sizing Accuracy",
                "Material Strength", "Sole & Stitching", "Longevity", 
                "Aesthetics", "Versatility", "Brand Identity"
            ]
            
            subfeature_data = []
            for subf in all_subfeatures:
                subf_data = df[df['SubFeature'] == subf]
                if not subf_data.empty:
                    need_improvement = (subf_data['Urgency'] == 'Need Improvement').sum()
                    total = len(subf_data)
                    need_pct = (need_improvement / total * 100) if total > 0 else 0
                    no_need_pct = 100 - need_pct
                else:
                    need_pct = 0
                    no_need_pct = 0
                
                subfeature_data.append({
                    'SubFeature': subf,
                    'Need Improvement': need_pct,
                    'No Need Improvement': no_need_pct
                })
            
            subf_df = pd.DataFrame(subfeature_data)
            subf_df.set_index('SubFeature', inplace=True)
            st.bar_chart(subf_df, use_container_width=True)
    else:
        st.info("No feedback data available yet.")

    # Innovative Ideas Table
    st.markdown("---")
    st.subheader("Innovative Ideas with Voting Results")
    
    # Get innovative ideas with vote counts
    try:
        with get_db_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            # Add thumbs_up and thumbs_down columns if they don't exist
            try:
                cur.execute("ALTER TABLE innovative_ideas ADD COLUMN IF NOT EXISTS thumbs_up INTEGER DEFAULT 0")
                cur.execute("ALTER TABLE innovative_ideas ADD COLUMN IF NOT EXISTS thumbs_down INTEGER DEFAULT 0")
            except:
                pass
            
            # Ensure idea_votes table exists before joining
            cur.execute("""
                CREATE TABLE IF NOT EXISTS idea_votes (
                    id SERIAL PRIMARY KEY,
                    idea_id INTEGER,
                    customer_email VARCHAR(100),
                    vote_type VARCHAR(10),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(idea_id, customer_email)
                )
            """)
            conn.commit()

            # Get all ideas with vote counts from idea_votes table
            cur.execute("""
                SELECT c.customer_name, ii.customer_email, ii.idea_text,
                       COUNT(CASE WHEN iv.vote_type = 'up' THEN 1 END) as thumbs_up,
                       COUNT(CASE WHEN iv.vote_type = 'down' THEN 1 END) as thumbs_down
                FROM innovative_ideas ii
                LEFT JOIN customers c ON ii.customer_email = c.customer_email
                LEFT JOIN idea_votes iv ON ii.id = iv.idea_id
                GROUP BY ii.id, c.customer_name, ii.customer_email, ii.idea_text
                ORDER BY COUNT(CASE WHEN iv.vote_type = 'up' THEN 1 END) DESC, ii.created_at DESC
            """)
            
            ideas = cur.fetchall()
            cur.close()
            
            if ideas:
                # Create DataFrame for display
                ideas_data = []
                for idea in ideas:
                    ideas_data.append({
                        'Customer Name': idea['customer_name'] or 'N/A',
                        'Email': idea['customer_email'] or 'N/A',
                        'Innovative Idea': idea['idea_text'],
                        '👍 Votes': idea['thumbs_up'],
                        '👎 Votes': idea['thumbs_down']
                    })
                
                ideas_df = pd.DataFrame(ideas_data)
                st.dataframe(ideas_df, use_container_width=True, hide_index=True)
                
                st.info(f"Total innovative ideas: {len(ideas)}")
            else:
                st.info("No innovative ideas submitted yet.")
                
    except Exception as e:
        st.error(f"Error loading innovative ideas: {e}")

# =========================================================
# PAGE 4: STATISTICAL ANALYSIS - MANAGEMENT DECISIONS (Owner Only)
# =========================================================
elif selected == "Statistical analysis- Management Decisions":
    st.title("Statistical Analysis - Management Decisions")
    st.markdown("Collect management team decisions on product improvements")
    
    # Management Decision Form
    col1, col2 = st.columns(2)
    
    with col1:
        feature = st.selectbox("Feature", ["Comfort & Fit", "Durability & Quality", "Design & Style"])
    
    with col2:
        # Dynamic sub-features based on selected feature
        if feature == "Comfort & Fit":
            sub_features = ["Cushioning & Support", "Breathability", "Sizing Accuracy"]
        elif feature == "Durability & Quality":
            sub_features = ["Material Strength", "Sole & Stitching", "Longevity"]
        else:  # Design & Style
            sub_features = ["Aesthetics", "Versatility", "Brand Identity"]
        
        sub_feature = st.selectbox("Sub Feature", sub_features)
        urgency = st.selectbox("Urgency", ["Need Improvement", "No Need Improvement"])
    
    if st.button("Submit Decision"):
        save_management_decision("All Products", feature, sub_feature, urgency)
        st.success("Management decision recorded successfully!")
    
    st.markdown("---")
    st.markdown("ANOVA test to identify which features need more attention based on management decisions.")
    st.markdown("**Null Hypothesis (H₀):** Mean Need improvement of all feature groups are equal")
    st.markdown("**Alternative Hypothesis (H₁):** At least one feature group mean Need Improvement is different.")
    
    # Get all management decisions data
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT feature, sub_feature, urgency FROM management_decisions")
        decisions_data = cur.fetchall()
        cur.close()
    
    if decisions_data:
        # Convert to DataFrame
        df_decisions = pd.DataFrame(decisions_data, columns=['feature', 'sub_feature', 'urgency'])
        
        # Convert urgency to numerical values
        df_decisions['urgency_score'] = df_decisions['urgency'].map({
            "Need Improvement": 1,
            "No Need Improvement": 0
        })
        
        # Remove any rows with missing urgency scores
        df_decisions = df_decisions.dropna(subset=['urgency_score'])
        
        if len(df_decisions) > 0 and len(df_decisions['feature'].unique()) > 1:
            # Group by feature for ANOVA
            comfort_fit = df_decisions[df_decisions['feature'] == 'Comfort & Fit']['urgency_score'].values
            durability_quality = df_decisions[df_decisions['feature'] == 'Durability & Quality']['urgency_score'].values
            design_style = df_decisions[df_decisions['feature'] == 'Design & Style']['urgency_score'].values
            
            # Perform one-way ANOVA
            f_stat, p_value = stats.f_oneway(comfort_fit, durability_quality, design_style)
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("### ANOVA Results")
                anova_results = pd.DataFrame({
                    'Statistic': ['F-statistic', 'p-value'],
                    'Value': [f"{f_stat:.6f}", f"{p_value:.6f}"]
                })
                st.dataframe(anova_results)
                st.markdown("* If p < 0.05: Reject the null hypothesis (H₀).")
                st.markdown("* If p ≥ 0.05: Fail to reject the null hypothesis (H1).")
                
                # If significant, perform Tukey HSD post-hoc test
                if p_value < 0.05:
                    st.write("### Tukey HSD Post-hoc Test")
                    tukey = pairwise_tukeyhsd(endog=df_decisions['urgency_score'], groups=df_decisions['feature'], alpha=0.05)
                    tukey_df = pd.DataFrame(data=tukey.summary().data[1:], columns=tukey.summary().data[0])
                    st.dataframe(tukey_df)
                    st.markdown("* p-adj < 0.05 → Statistically significant difference.")
                    st.markdown("* p-adj ≥ 0.05 → No statistically significant difference.")
                    
                    # Feature comparison interpretation
                    st.subheader("Management Analysis Interpretation")
                    mean_improvement = df_decisions.groupby('feature')['urgency_score'].mean().sort_values(ascending=False)
                    highest_feature = mean_improvement.index[0]
                    lowest_feature = mean_improvement.index[-1]
                    st.warning(f"**{highest_feature}** needs the most attention according to management (improvement rate: {mean_improvement.iloc[0]:.3f})")
                    st.success(f"**{lowest_feature}** is considered best performing by management (improvement rate: {mean_improvement.iloc[-1]:.3f})")
                else:
                    st.info("No significant differences found between features. Post-hoc test not needed.")
                    st.info("Management considers all features equally - no significant differences in priorities.")
            
            with col2:
                if p_value < 0.05:
                    st.write("### Confidence Interval Plot")
                    tukey = pairwise_tukeyhsd(endog=df_decisions['urgency_score'], groups=df_decisions['feature'], alpha=0.05)
                    fig = tukey.plot_simultaneous()
                    st.pyplot(fig)
            
            # Feature comparison summary
            st.write("### Mean 'Need Improvement' Rate per Feature")
            
            col1, col2 = st.columns(2)
            
            with col1:
                feature_stats = df_decisions.groupby('feature').agg({
                    'urgency_score': ['count', 'sum', 'mean']
                }).round(3)
                feature_stats.columns = ['Total_Decisions', 'Need_Improvement_Count', 'Need_Improvement_Rate']
                st.dataframe(feature_stats)
            
            with col2:
                # Bar chart
                mean_improvement = df_decisions.groupby('feature')['urgency_score'].mean().sort_values(ascending=False)
                st.bar_chart(mean_improvement, use_container_width=True)
        else:
            st.info("Not enough management decisions for ANOVA test. Need decisions from multiple features.")
    else:
        st.info("No management decisions recorded yet. Submit some decisions to see analysis.")

# =========================================================
# PAGE 5: MANAGEMENT VS NLP MODEL (Owner Only)
# =========================================================
elif selected == "Management vs NLP model":
    st.title("Statistical Analysis Comparison: Management vs NLP Model")
    st.markdown("Compare p-values from ANOVA tests between management decisions and NLP model predictions")

    # Get p-values from both analyses
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("NLP Model Analysis (Crowd Ideas)")

        # Same data & computation as "Statistical Analysis - Customer Perception" page
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT feature, subfeature, urgency FROM feedback")
                nlp_feedback_data = cur.fetchall()
                cur.close()
        except Exception:
            nlp_feedback_data = []

        if nlp_feedback_data:
            df_nlp = pd.DataFrame(nlp_feedback_data, columns=['feature', 'subfeature', 'urgency'])
            df_nlp['urgency'] = df_nlp['urgency'].replace({
                "Need improvements": "Need Improvement",
                "need improvement": "Need Improvement",
                "No need improvement": "No Need Improvement",
                "no need improvement": "No Need Improvement"
            })
            df_nlp['urgency_score'] = df_nlp['urgency'].map({"Need Improvement": 1, "No Need Improvement": 0})
            df_nlp = df_nlp.dropna(subset=['urgency_score'])

            if len(df_nlp) > 0 and len(df_nlp['feature'].unique()) > 1:
                try:
                    comfort_fit = df_nlp[df_nlp['feature'] == 'Comfort & Fit']['urgency_score'].values
                    durability_quality = df_nlp[df_nlp['feature'] == 'Durability & Quality']['urgency_score'].values
                    design_style = df_nlp[df_nlp['feature'] == 'Design & Style']['urgency_score'].values
                    f_stat, nlp_p_value = stats.f_oneway(comfort_fit, durability_quality, design_style)

                    if pd.isna(nlp_p_value):
                        st.warning("P-value is undefined — all feature groups have identical scores.")
                    else:
                        st.metric("P-value", f"{nlp_p_value:.6f}")
                        if nlp_p_value < 0.05:
                            st.success("Significant difference between the need improvement rate of the features.Consider Tukey's HSD result to prioritize the feature improvement decision")
                        else:
                            st.info("No significant difference between the need improvement rate of the features. Focus on all the feature's improvement.")
                except Exception as e:
                    st.error(f"Unable to calculate p-value: {e}")
            else:
                st.warning("Need feedback from multiple features for analysis")
        else:
            st.warning("No customer feedback data available")

    with col2:
        st.subheader("Management Decisions")

        # Same data & computation as "Statistical Analysis - Management Decisions" page
        try:
            with get_db_connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT feature, sub_feature, urgency FROM management_decisions")
                decisions_data = cur.fetchall()
                cur.close()
        except Exception:
            decisions_data = []

        if decisions_data:
            df_decisions = pd.DataFrame(decisions_data, columns=['feature', 'sub_feature', 'urgency'])
            df_decisions['urgency_score'] = df_decisions['urgency'].map({"Need Improvement": 1, "No Need Improvement": 0})
            df_decisions = df_decisions.dropna(subset=['urgency_score'])

            if len(df_decisions) > 0 and len(df_decisions['feature'].unique()) > 1:
                try:
                    comfort_fit = df_decisions[df_decisions['feature'] == 'Comfort & Fit']['urgency_score'].values
                    durability_quality = df_decisions[df_decisions['feature'] == 'Durability & Quality']['urgency_score'].values
                    design_style = df_decisions[df_decisions['feature'] == 'Design & Style']['urgency_score'].values
                    f_stat, mgmt_p_value = stats.f_oneway(comfort_fit, durability_quality, design_style)

                    if pd.isna(mgmt_p_value):
                        st.warning("P-value is undefined — all feature groups have identical scores.")
                    else:
                        st.metric("P-value", f"{mgmt_p_value:.6f}")
                        if mgmt_p_value < 0.05:
                            st.success("Significant difference between need improvement rate of the features. Consider Tueky's HSD result to priotize the features for improvement")
                        else:
                            st.info("No significant difference between the need improvement rate of the features. Focus on all the featres' improvement.")
                except Exception as e:
                    st.error(f"Unable to calculate p-value: {e}")
            else:
                st.warning("Need decisions from multiple features for analysis")
        else:
            st.warning("No management decisions recorded yet")
    
    # Comparison Summary
    st.markdown("---")
    st.subheader("P-Value Comparison Summary")
    
    # Try to get both p-values for comparison
    try:
        if 'nlp_p_value' in locals() and 'mgmt_p_value' in locals():
            comparison_df = pd.DataFrame({
                'Analysis Type': ['NLP Model (Crowd Ideas)', 'Management Decisions'],
                'P-value': [f"{nlp_p_value:.6f}", f"{mgmt_p_value:.6f}"],
                'Significance': ['Significant' if nlp_p_value < 0.05 else 'Not Significant',
                               'Significant' if mgmt_p_value < 0.05 else 'Not Significant']
            })
            st.dataframe(comparison_df)
            
            # Interpretation
            if nlp_p_value < 0.05 and mgmt_p_value < 0.05:
                st.success("Both analyses show significant differences - Strong agreement - Consider Tukey's HSD to prioritize features for improvement")
            elif nlp_p_value >= 0.05 and mgmt_p_value >= 0.05:
                st.info("Both analyses show no significant differences - Strong Agreement - Focus on all fetures' improvement decision")
            else:
                st.warning("Analyses disagree - Consider reviewing the data and management decisions")
        else:
            st.info("Complete both analyses to see comparison")
    except:
        st.info("Unable to generate comparison - ensure both analyses have sufficient data")

# =========================================================
# PAGE 5: STATISTICAL ANALYSIS (Owner Only)
# =========================================================
elif selected == "Statistical Analysis-Crowd ideas":
    st.title("Statistical Analysis- Crowd Perception")
    st.markdown("ANOVA test to identify which features need more attention based on 'Need Improvement' predictions.")
    st.markdown("**Null Hypothesis (H₀):** Mean Need improvement of all feature groups are equal")
    st.markdown("**Alternative Hypothesis (H₁):** At least one feature group mean Need Improvement is different.")

    # Get all feedback data from database
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT feature, subfeature, feedback_text, urgency FROM feedback")
        feedback_data = cur.fetchall()
        cur.close()

    if feedback_data:
        # Convert to DataFrame
        feedback_df = pd.DataFrame(feedback_data, columns=['feature', 'subfeature', 'feedback_text', 'urgency'])
        
        # Standardize urgency values and convert to numerical
        feedback_df['urgency'] = feedback_df['urgency'].replace({
            "Need improvements": "Need Improvement",
            "need improvement": "Need Improvement", 
            "No need improvement": "No Need Improvement",
            "no need improvement": "No Need Improvement"
        })
        
        # Convert urgency to numerical values
        feedback_df['urgency_score'] = feedback_df['urgency'].map({
            "Need Improvement": 1,
            "No Need Improvement": 0
        })
        
        # Remove any rows with missing urgency scores
        feedback_df = feedback_df.dropna(subset=['urgency_score'])
        
        if len(feedback_df) > 0 and len(feedback_df['feature'].unique()) > 1:
            # Group by feature for ANOVA
            comfort_fit = feedback_df[feedback_df['feature'] == 'Comfort & Fit']['urgency_score'].values
            durability_quality = feedback_df[feedback_df['feature'] == 'Durability & Quality']['urgency_score'].values
            design_style = feedback_df[feedback_df['feature'] == 'Design & Style']['urgency_score'].values
            
            # Perform one-way ANOVA
            f_stat, p_value = stats.f_oneway(comfort_fit, durability_quality, design_style)

            # NaN occurs when a group has zero variance (all values identical)
            if np.isnan(f_stat) or np.isnan(p_value):
                st.warning(
                    "ANOVA could not be computed because one or more feature groups have no variance "
                    "(all feedback has the same urgency score). Collect more diverse feedback to enable statistical comparison."
                )
            else:
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write("### ANOVA Results")
                    anova_results = pd.DataFrame({
                        'Statistic': ['F-statistic', 'p-value'],
                        'Value': [f"{f_stat:.6f}", f"{p_value:.6f}"]
                    })
                    st.dataframe(anova_results)
                    st.markdown("* If p < 0.05: Reject the null hypothesis (H₀)- Only some features should be improved. Consider Tukey's HSD result to prioritize the features for improvement.")
                    st.markdown("* If p ≥ 0.05: Fail to reject the null hypothesis (H₀)- All features should be improved.")

                    # If significant, perform Tukey HSD post-hoc test
                    if p_value < 0.05:
                        st.write("### Tukey HSD Post-hoc Test")
                        tukey = pairwise_tukeyhsd(endog=feedback_df['urgency_score'], groups=feedback_df['feature'], alpha=0.05)
                        tukey_df = pd.DataFrame(data=tukey.summary().data[1:], columns=tukey.summary().data[0])
                        st.dataframe(tukey_df)
                        st.markdown("* p-adj < 0.05 → Statistically significant difference of the improvement rates of the features.")
                        st.markdown("* p-adj ≥ 0.05 → No statistically significant difference of the improvement rates of the features.")

                        # Feature comparison interpretation
                        st.subheader("Analysis Interpretation")
                        mean_improvement = feedback_df.groupby('feature')['urgency_score'].mean().sort_values(ascending=False)
                        highest_feature = mean_improvement.index[0]
                        lowest_feature = mean_improvement.index[-1]
                        st.warning(f"**{highest_feature}** needs the most attention (highest need improvement rate: {mean_improvement.iloc[0]:.3f})")
                        st.success(f"**{lowest_feature}** is performing best (lowest improvement rate: {mean_improvement.iloc[-1]:.3f})")
                    else:
                        st.info("No significant differences found between features. Post-hoc test not needed.")
                        st.info("All features should be improved - no significant differences of need improvement detected.")

                with col2:
                    if p_value < 0.05:
                        st.write("### Confidence Interval Plot")
                        tukey = pairwise_tukeyhsd(endog=feedback_df['urgency_score'], groups=feedback_df['feature'], alpha=0.05)
                        fig = tukey.plot_simultaneous()
                        st.pyplot(fig)
            
            # Feature comparison summary
            st.write("### Mean 'Need Improvement' Rate per Feature")
            
            col1, col2 = st.columns(2)
            
            with col1:
                feature_stats = feedback_df.groupby('feature').agg({
                    'urgency_score': ['count', 'sum', 'mean']
                }).round(3)
                feature_stats.columns = ['Total_Feedback', 'Need_Improvement_Count', 'Need_Improvement_Rate']
                st.dataframe(feature_stats)
            
            with col2:
                # Bar chart
                mean_improvement = feedback_df.groupby('feature')['urgency_score'].mean().sort_values(ascending=False)
                st.bar_chart(mean_improvement, use_container_width=True)
        else:
            st.info("Not enough feedback data for ANOVA test. Need data from multiple features.")
    else:
        st.info("No feedback data available for analysis.")
