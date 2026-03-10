# SkewPlay: A No-Code Web Platform for Handling Imbalanced Datasets

**SkewPlay** is an interactive, browser-based Machine Learning platform designed specifically to tackle the pervasive problem of **Class Imbalance** in tabular datasets. 

By abstracting away the complexities of Python programming, SkewPlay provides a visual, step-by-step pipeline wizard that allows users of any skill level to perform automated data analysis, apply sophisticated balancing techniques, train models, and evaluate them using specialized metrics.

---

## 🛑 Problem Statement

In real-world Machine Learning applications—spanning domains like fraud detection, medical diagnosis, and predictive maintenance—datasets are rarely balanced. Often, the class we are most interested in predicting (e.g., fraudulent transactions or rare diseases) represents a tiny fraction of the overall data. 

**The Challenge:**
Standard Machine Learning algorithms are designed to maximize overall accuracy. When trained on highly skewed data, these models inevitably become biased toward the majority class. A model might achieve "99% accuracy" simply by predicting the majority class every single time, while completely failing to identify the crucial minority instances.

**The Current Barrier:**
Addressing class imbalance requires specialized knowledge (e.g., SMOTE, undersampling, ADASYN) and proficiency in coding (Python, scikit-learn, imbalanced-learn). This creates a steep learning curve and a high barrier to entry for researchers, analysts, and students who understand their domains but lack deep programming expertise. 

---

## 🎯 Project Objectives

SkewPlay was developed to dismantle these barriers through the following core objectives:

1. **Democratize Machine Learning:** Provide an intuitive, no-code web environment where users can resolve dataset imbalance and train models without writing a single line of script.
2. **Automate End-to-End Experimentation:** Guide users effortlessly through a structured pipeline: Data Upload ➔ Automated EDA ➔ Preprocessing ➔ Resampling Strategeis ➔ Model Selection ➔ Evaluation.
3. **Integrate Intelligent AI Guidance:** Leverage Large Language Models to instantly analyze complex dataset characteristics and recommend optimal preprocessing configurations and balancing strategies.
4. **Enforce Robust Evaluation Metrics:** Shift reliance away from misleading standard accuracy by evaluating performance exclusively through robust, imbalance-aware metrics like **F1-Minority, PR-AUC, G-Mean**, and interactive visualizations (Confusion Matrices, Precision-Recall Curves).
5. **Scale Automated Data Collection (Telemetry):** Systematically collect and aggregate anonymized pipeline statistics to create a massive, longitudinal dataset of Machine Learning experiments.

---

## 📊 Data Collection & Telemetry Engine

A unique and powerful feature of SkewPlay is its built-in data collection engine. 

As users interact with the platform and run experiments, the system silently records the end-to-end lifecycle of every pipeline executed. We are not just building a tool; we are building a dataset of how Machine Learning models respond to various interventions on skewed data.

**What is Collected?**
For every executed workflow, the system aggregates:
*   **Dataset Meta-Stats:** Number of instances, feature count, missing value ratios, and precise class imbalance severity (e.g., 1:100 ratio).
*   **Pipeline Configuration:** The exact preprocessing steps chosen, the balancing strategy applied (e.g., SMOTE + ENN), and the model hyperparameters.
*   **Execution Results:** The resulting model performance measured against our specialized metrics (F1-Minority, G-Mean, PR-AUC).

**The Goal of Telemetry:**
By capturing the relationship between `[Dataset Stats] + [Chosen Pipeline] = [Final Result]`, we are generating a massive, highly structured "Metadataset." This aggregated dataset will eventually be used to train specialized Meta-Learning models capable of predicting the absolute optimal pipeline configuration for any new, unseen imbalanced dataset automatically.

---

## 🛠️ Technology Stack

SkewPlay relies on a highly professional, decoupled architecture:

*   **Frontend (UI/UX):** **Vue.js 3** (Composition API) powers the responsive Single Page Application.
*   **Backend Server:** **FastAPI** handles high-concurrency API requests bridging the frontend with the ML logic.
*   **Core Logic:** **Python** powers the data wrangling and modeling, utilizing `Pandas`, `scikit-learn`, and `imbalanced-learn`.
*   **Cloud Infrastructure:** **Firebase** manages secure User Authentication and NoSQL database storage for user profiles and workflow metadata.

---

## 🚀 Setup & Installation

*(If you plan to open-source or share the code, you can add setup instructions here)*

```bash
# 1. Clone the repository
git clone https://github.com/your-username/SkewPlay.git

# 2. Setup the Frontend
cd frontend
npm install
npm run dev

# 3. Setup the Backend
cd backend
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```
