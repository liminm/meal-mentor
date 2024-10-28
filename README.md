# Meal Mentor
**Meal Mentor** is an intelligent recipe recommendation system designed to help users discover healthy and nutritious meals tailored to their dietary preferences and nutritional goals. Leveraging advanced technologies like Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs) from OpenAI, Meal Mentor provides personalized recipe suggestions based on diet types and specific nutritional values.

<p align="center">
  <img src="images/meal_mentor_logo.png" width="600">
</p>

## Table of Contents

- [Introduction](#introduction)
- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [System Architecture](#system-architecture)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Evaluation](#evaluation)
  - [RAG Evaluation](#rag-evaluation)
- [Monitoring and Feedback](#monitoring-and-feedback)
  - [Grafana Dashboard](#grafana-dashboard)
- [Ingestion Pipeline](#ingestion-pipeline)
- [Interface](#interface)
- [Containerization](#containerization)
- [Reproducibility](#reproducibility)
- [Best Practices](#best-practices)
- [Future Enhancements](#future-enhancements)
- [Acknowledgments](#acknowledgments)
- [License](#license)

---

## Introduction

Maintaining a healthy diet can be challenging due to the overwhelming number of recipes and dietary information available. **Meal Mentor** simplifies this process by providing personalized recipe recommendations based on users' dietary requirements and nutritional goals.

## Project Overview

Meal Mentor is an end-to-end application that combines a knowledge base of recipes with powerful search and AI capabilities to provide customized meal recommendations. The application utilizes:

- **Retrieval-Augmented Generation (RAG)**
- **OpenAI API**
- **Minsearch**
- **FastAPI**
- **JavaScript and HTML Frontend**
- **PostgreSQL**
- **Grafana**

## Features

- **Personalized Recipe Recommendations**: Suggests recipes based on diet type and specific nutritional values.
- **User Feedback Collection**: Allows users to provide feedback to improve recommendations.
- **Real-Time Monitoring**: Tracks user interactions and system performance.
- **Conversational Interface**: Supports natural language queries for an enhanced user experience.

## Technologies Used

- **Python 3.11**
- **FastAPI**
- **OpenAI API**
- **Minsearch**
- **PostgreSQL**
- **Grafana**
- **JavaScript and HTML**
- **Docker and Docker Compose**

## System Architecture

The Meal Mentor application consists of:

- **Frontend**: A user interface for inputting preferences and viewing recommendations.
- **Backend (FastAPI)**: Handles API requests and processes user queries.
- **Knowledge Base (Minsearch)**: Indexes recipe data for efficient search and retrieval.
- **Database (PostgreSQL)**: Stores user data, feedback, and logs.
- **LLM Integration (OpenAI API)**: Processes queries to generate personalized responses.
- **Monitoring (Grafana)**: Visualizes system performance and user interactions.

## Setup and Installation

### Prerequisites

- **Python 3.11**
- **Docker and Docker Compose**
- **OpenAI API Key**
- **Elasticsearch** (Docker image)
- **PostgreSQL** (Docker image)

### Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/meal-mentor.git
   cd meal-mentor
   ```

2. **Set Up Environment Variables**

   Create a `.env` file in the project root directory:

   ```env
   OPENAI_API_KEY=your_openai_api_key
   ELASTICSEARCH_HOST=elasticsearch
   ELASTICSEARCH_PORT=9200
   POSTGRES_USER=your_postgres_user
   POSTGRES_PASSWORD=your_postgres_password
   POSTGRES_DB=meal_mentor_db
   ```

3. **Install Python Dependencies**

   Create and activate a virtual environment:

   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
   ```

   Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. **Build and Run Services with Docker Compose**

   ```bash
   docker-compose up --build
   ```

   This starts the FastAPI application, Elasticsearch, PostgreSQL, and Grafana (if configured).

5. **Initialize the Database and Elasticsearch Index**

   ```bash
   python ingest_data.py
   ```

   *Ensure Docker containers are running before executing the script.*

## Usage

Access the application at `http://localhost:8000`.

### API Example

```bash
curl -X POST "http://localhost:8000/recommendations" \
     -H "Content-Type: application/json" \
     -d '{
           "diet_type": "keto",
           "min_protein": 20,
           "max_carbs": 10,
           "include_ingredients": ["chicken", "spinach"],
           "exclude_ingredients": ["nuts"]
         }'
```

### Example Response:

```json
{
  "recipes": [
    {
      "title": "Grilled Chicken with Spinach",
      "ingredients": ["chicken breast", "spinach", "olive oil", "garlic"],
      "instructions": "Season the chicken breast with salt and pepper...",
      "nutrition": {
        "calories": 350,
        "protein": 30,
        "carbs": 8,
        "fat": 20
      }
    }
  ]
}
```

## Evaluation

### RAG Evaluation

Two RAG approaches were tested to optimize the integration between the knowledge base and the LLM:

#### **Approach 1**: LLM-as-a-Judge metric on `gpt-4o-mini`

| Relevance       | Count | Proportion |
|-----------------|-------|------------|
| RELEVANT        | 151   | 0.755      |
| PARTLY_RELEVANT | 29    | 0.145      |
| NON_RELEVANT    | 20    | 0.100      |

#### **Approach 2**: LLM-as-a-Judge metric on `gpt-4o`

| Relevance       | Count | Proportion |
|-----------------|-------|------------|
| RELEVANT        | 95    | 0.475      |
| PARTLY_RELEVANT | 76    | 0.380      |
| NON_RELEVANT    | 29    | 0.145      |

**Insight**: Based on these results, **gpt-4o-mini** was chosen due to its higher proportion of fully relevant responses.

## Monitoring and Feedback

Meal Mentor collects user feedback and monitors system performance using Grafana dashboards.

### Grafana Dashboard

The Grafana dashboard provides comprehensive insights into the application's performance, user interactions, and resource utilization. The dashboard includes the following panels:

1. **Question / Answer** (Table)
2. **Most Frequent Keywords in Questions** (Table)
3. **Average Response Time Over Time By Day** (Timeseries)
4. **Relevance Ratings Over Time By Hour** (Bar Chart)
5. **Average Response Time Last 10 Requests** (Gauge)
6. **Feedback Ratings Distribution** (Bar Chart)
7. **Feedback Submission Over Time** (Bar Chart)
8. **Retrieved Document Relevancy Share** (Pie Chart)
9. **Conversations Over Time By Date** (Table)
10. **Total OpenAI Cost Over Time By Day** (Table)
11. **Average Tokens Used Per Conversation** (Table)

These panels help in monitoring the performance, quality, and cost-efficiency of the Meal Mentor application, aiming to optimize user engagement and experience.

### Feedback Mechanism

Users can rate the relevance of the recommendations and provide comments. This data is stored in PostgreSQL and used to refine the recommendation algorithms.

## Ingestion Pipeline

An automated ingestion pipeline was implemented to process and index recipe data into the knowledge base.

### Steps:

1. **Data Collection**: Recipes were sourced from open datasets and APIs.
2. **Data Cleaning and Transformation**: Ensured consistency in data formats and fields.
3. **Indexing**: Recipes were indexed into Elasticsearch with appropriate mappings.
4. **Database Population**: Recipe metadata and user-related data were stored in PostgreSQL.

## Interface

### Web Interface

- Built with HTML, CSS, and JavaScript for a responsive user experience.
- Supports natural language and structured queries.
- Enables question submission via Enter key or a button.
- Includes a feedback feature for rating recommendations.
- Displays recipes with detailed information and nutritional values.

## Containerization

The application is containerized using Docker and orchestrated with Docker Compose for easy deployment.

## Reproducibility

- **Setup Instructions**: Detailed steps provided.
- **Dependencies**: Specified in `requirements.txt`.
- **Version Control**: Specific package versions to avoid compatibility issues.
- **Sample Data**: Included for testing and validation.

## Best Practices

- **Hybrid Search**: Combines text and vector search for improved accuracy.
- **Document Re-ranking**: Custom scoring to prioritize relevant recipes.
- **Prompt Engineering**: Optimized prompts for clarity and relevance.
- **Error Handling**: Robust backend error handling.
- **Security**: Secure management of API keys and user data.
- **Logging**: Comprehensive logging for debugging and monitoring.

## Future Enhancements

- **Advanced Nutritional Analysis**
- **User Accounts and Profiles**
- **Machine Learning-Based Recommendations**
- **Integration with Wearables**
- **Mobile Applications**
- **Multi-Language Support**
- **Social Sharing Features**

## Acknowledgments

This project was developed as part of the **LLM Zoomcamp** program. Special thanks to **Alexey Grigorev**, the **DataTalks team**, and the community for their invaluable support.

## License

This project is licensed under the MIT License.

---

**Enjoy discovering healthy meals with Meal Mentor!**

---