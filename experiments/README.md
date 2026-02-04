# Experiment Notebooks

Google Colab notebooks for running LLM-based pipelines with locally hosted models using Ollama.

## Notebooks

| Notebook | Description |
|----------|-------------|
| `crewai_experiment.ipynb` | CrewAI trip planner with Qwen3:8b / Llama3.2 |
| `pipeline_node_agents_experiment.ipynb` | Pipeline Node Agents framework with Qwen3:8b / Llama3.2 |

## Prerequisites

- Google account with access to Google Colab
- **T4 GPU or higher** (required for running 8B parameter models)
- **SERPER API key** (required for CrewAI notebook) — get a free key at [serper.dev](https://serper.dev/) (limited free quota)

### Tested Configuration

| Resource | Minimum |
|----------|---------|
| GPU RAM | 15 GB |
| Drive Storage | 112.6 GB |
| System RAM | 12.7 GB |

## How to Run

### 1. Upload to Google Drive

Upload the notebook (`.ipynb` file) to your Google Drive.

### 2. Open in Google Colab

Right-click the notebook in Google Drive → **Open with** → **Google Colaboratory**

### 3. Configure Runtime

1. Go to **Runtime** → **Change runtime type**
2. Select **T4 GPU** (or higher: L4, A100, H100)
3. Click **Save**

### 4. Install Dependencies

Execute cells 1–5 sequentially to:
- Verify GPU availability
- Install Ollama and start the server
- Download required models (Qwen3:8b, Llama3.2)
- Clone the project repository
- Install project dependencies with Poetry

### 5. Run Pipeline

Follow the instructions in section **"6. Run Pipeline"** of each notebook.

Open the **terminal** in Colab and run commands manually as described.

## Troubleshooting

- **Notebook timeout**: Restart the session and re-run all cells
- **SERPER_API_KEY missing**: Add the API key to the "Secrets" section in Google Colab and **enable** access using toggle
- **Out of memory**: Ensure you're using T4 GPU or higher
- **Ollama server failed**: Re-run the server startup cell
