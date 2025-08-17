# Secretary

1. **Clarity and Measurability:** Smaller tasks are easier to understand, assign, and measure progress. You'll know exactly what needs to be done at any given time.
2. **More Accurate Estimation:** It's much easier to estimate the time needed for a 2-4 hour task than for a 2-3 day one. This improves planning and predictability.
3. **Improved Focus:** By focusing on a micro-task, you avoid overwhelm and stay focused on the immediate objective.
4. **Early Problem Detection:** If a smaller task encounters an obstacle, you identify it earlier in the development cycle, allowing for quick fixes and minimizing the impact on the overall schedule.
5. **Increased Motivation:** Completing small tasks and marking them "done" provides a continuous sense of accomplishment, which is great for motivation, especially on complex projects. 6. **Flexibility and Adaptability:** If requirements change or new ideas emerge, it is easier to adjust or rearrange granular tasks than larger components of a phase.

Let's take **Phase 1: MVP Core Foundation and Setup (Scheduling)** and break it down into even smaller tasks to illustrate:

---

### **Phase 1: MVP Core Foundation and Setup (Scheduling)**

* **1. Project Initialization and Dependency Management:**
* 1.1. Install `uv` (if not already installed globally).
* 1.2. Create the project root directory (e.g., `chatbot_recepcionista_ai`).
* 1.3. Run `uv init` in the root directory to create `pyproject.toml` and `.venv`.
* 1.4. Add essential dependencies to `pyproject.toml`: `fastapi`, `uvicorn`, `langchain`, `langgraph`, `sqlalchemy`, `google-api-python-client`, `python-dotenv`.
* 1.5. Run `uv sync` or `uv install` to install the dependencies in the virtual environment.
* 1.6. Configure `.gitignore` for the virtual environment and sensitive configuration files.

* **2. Folder Structure and Modularity:**
* 2.1. Create the `src/` folder.
* 2.2. Within `src/`, create the subfolders: `agents/`, `tools/`, `models/`, `config/`.
* 2.3. Create `__init__.py` files within each subfolder to make them Python packages.
* 2.4. Create the files `src/main.py`, `src/database.py`, `src/graph.py`.

* **3. Scheduling Agent Implementation and Tools:**
* **3.1. Google Calendar Tools (`src/tools/google_calendar_tools.py`):**
* 3.1.1. Configure the Google API client and authentication (OAuth 2.0 or Service Account).
* 3.1.2. Develop the function/class for the `list_events` tool (check availability).
* 3.1.3. Develop the function/class for the `create_event` tool (schedule a new appointment).
* 3.1.4. Write basic unit tests for the Google Calendar tools.
* **3.2. Database Tools (`src/tools/database_tools.py` and `src/database.py`):**
* 3.2.1. Configure the SQLAlchemy Engine and Session (for initial SQLite).
* 3.2.2. Define the SQLAlchemy models (`Patient`, `Doctor`, `Appointment`) in `src/models/`.
* 3.2.3. Develop the function/class for the `create_appointment` tool.
* 3.2.4. Develop the function/class for the `get_appointment_details` tool (for basic querying).
* 3.2.5. Write basic unit tests for the database tools.
* **3.3. Scheduling Agent (`src/agents/calendar_agent.py`):**
* 3.3.1. Define the `CalendarAgent` function/class.
* 3.3.2. Integrate the `list_events` and `create_appointment` tools into the agent.
* 3.3.3. Implement the logic to collect user information for scheduling (date, time, professional, appointment type).
* 3.3.4. Formulate appropriate responses to the user during the scheduling flow (e.g., "Which date and time do you prefer?").
* **3.4. Orchestrator Agent (`src/agents/orchestrator_agent.py`):**
* 3.4.1. Define the `OrchestratorAgent` function/class.
* 3.4.2. Implement the initial intent detection logic using an LLM (e.g., if the message contains "schedule," "book," etc., route to the `CalendarAgent`).
* 3.4.3. Implement the logic to pass control and conversation state to the appropriate agent. * **3.5. LangGraph Definition (`src/graph.py`):**
* 3.5.1. Define the `AgentState` class with the required attributes (e.g., `messages`, `intent`, `collected_params`, `required_params`).
* 3.5.2. Add the `OrchestratorAgent` and `CalendarAgent` nodes to the graph.
* 3.5.3. Define the conditional edges (`add_conditional_edges`) for the transition between the orchestrator and the scheduling agent.
* 3.5.4. Create the `StateGraph` instance and compile the graph.

* **4. Basic FastAPI Setup:**
* 4.1. Initialize the FastAPI application in `src/main.py`.
* 4.2. Create a `POST /test_agent` endpoint that accepts a JSON file with the user's message.
* 4.3. Call the LangGraph instance from this endpoint, pass the user's message, and get the response.
* 4.4. Return the chatbot's response via API.
* 4.5. Configure Uvicorn to run `src.main:app`.

* **5. Credential Management:**
* 5.1. Identify all necessary environment variables (Google API keys, `DATABASE_URL`).
* 5.2. Create a `.env.example` file to document the variables.
* 5.3. Implement environment variable loading using `python-dotenv`.
* 5.4. Ensure that sensitive credentials are not committed to Git.

---

As you can see, each phase breaks down into much clearer and more actionable tasks, facilitating management, testing, and, most importantly, your ability to make steady and effective progress. I highly recommend this granular approach for the entire project!

---

### **Phase 2: Real-Time Communication and Channel Integration**

**Objective:** Enable two-way communication via WhatsApp through the Meta API, configuring the webhook infrastructure in FastAPI and implementing the notification agent.

* **1. Integration with Meta API (WhatsApp Business API):**
* 1.1. Obtain access to the Meta Developer Platform and create an App.
* 1.2. Configure the WhatsApp Business Platform product in the Meta App.
* 1.3. Obtain a Temporary (for development) or Permanent (for production) Access Token.
* 1.4. Register a test phone number for the WhatsApp Business Account.
### * 1.5. In `src/tools/whatsapp_tools.py`:

| * 1.5.1. Develop a function/class to send text messages (using the official Meta API). |
|---|

* 1.5.2. Develop a function/class to send messages based on templates (required for proactive notifications on WhatsApp).
* 1.5.3. Write unit tests for WhatsApp's messaging tools.
* 1.6. Add Meta API credentials to `.env` and `config/` (token, phone number ID, Business account ID).

* **2. Webhook Infrastructure with FastAPI:**
### * 2.1. In `src/main.py`:

| * 2.1.1. Create the `GET /webhook` endpoint for Meta API validation (with `hub.mode`, `hub.challenge`, `hub.verify_token`). |
|---|

* 2.1.2. Create the `POST /webhook` endpoint to receive WhatsApp messages.
* 2.1.3. Implement `verify_token` validation in `POST /webhook`.
* 2.1.4. Implement user message extraction from the WhatsApp webhook payload.
* 2.1.5. Log the full webhook payload for initial debugging.
### * 2.2. Create the `POST /webhook_test` endpoint:

| * 2.2.1. Accept a JSON payload that simulates a WhatsApp message (e.g., `{"object": "whatsapp_business_account", "entry": [{"changes": [{"value": {"messages": [{"from": "user_phone", "text": {"body": "Hello!"}}]}}]}]}`). |
|---|

* 2.2.2. Internally call the main `POST /webhook` processing logic with this simulated payload.
* 2.2.3. Return the processing response (to verify that the chatbot responded correctly).
* 2.3. Configure the Meta API to point the webhook to your FastAPI's public URL (using Ngrok or equivalent for local development).

* **3. Notification Agent (`src/agents/notification_agent.py`):**
* 3.1. Define the `NotificationAgent` function/class.
* 3.2. Implement the logic to format the content of appointment reminders (date, time, professional, etc.).
* 3.3. Integrate with the `whatsapp_tools.py` tools to send reminders via WhatsApp.
### * 3.4. Define how to trigger the notification agent:

| * 3.4.1. As an optional node in the LangGraph that is activated after a successful schedule to send immediate confirmation. |
|---|

* 3.4.2. **(Optional, for a later phase)** As a separate process (e.g., cron job or worker service) that queries the schedule database and calls the notification agent for future reminders.
* 3.5. Write unit tests for the `NotificationAgent`.

* **4. Refining the LangGraph for Channels:**
* 4.1. Update `src/orchestrator_agent.py` to receive the user's message from the webhook.
* 4.2. Adapt the `AgentState` to include the `channel_id` (e.g., the user's WhatsApp phone number) so that the response can be sent back to the correct channel.
* 4.3. Implement the logic in `main.py` to send the final LangGraph response back to the user via `whatsapp_tools.py`.
* 4.4. Test the complete flow: WhatsApp message -> FastAPI webhook -> LangGraph -> LangGraph response -> send via WhatsApp.

---
### **Phase 3: Expanding Chatbot Capabilities and Data Robustness**

**Objective:** Implement the clinic information agent, complete data persistence operations, and refine LangGraph orchestration to handle multiple intents and error scenarios.

* **1. Clinic Information Agent:**
* 1.1. Define the format and location of the clinic information (e.g., `src/config/clinic_info.json`).
* 1.2. Populate `clinic_info.json` with sample data (address, phone number, hours, services, specialties, insurance plans).
### * 1.3. In `src/tools/clinic_info_tools.py`:

| * 1.3.1. Develop a function/class to load and query data from `clinic_info.json` (e.g., `get_address()`, `get_opening_hours()`, `check_convenio(name)`). |
|---|

* 1.3.2. Write unit tests for the clinic information tools.
### * 1.4. In `src/agents/clinic_info_agent.py`:

| * 1.4.1. Define the `ClinicInfoAgent` function/class. |
|---|

* 1.4.2. Implement the logic to answer general questions using `clinic_info_tools`.
* 1.4.3. Write unit tests for `ClinicInfoAgent`.
* 1.5. Update `src/orchestrator_agent.py` to detect intents related to clinic information and route them to `ClinicInfoAgent`.
* 1.6. Update `src/graph.py` with the new `ClinicInfoAgent` node and the appropriate conditional edges.

* **2. Complete CRUD Operations on the Database:**
### * 2.1. In `src/tools/database_tools.py`:

| * 2.1.1. Extend existing tools to include: |
|---|

* `update_appointment_status(appointment_id, new_status)`
* `update_appointment_datetime(appointment_id, new_datetime)`
* `cancel_appointment(appointment_id)` (can be an `update_status` to 'canceled')
* `get_appointments_by_patient(patient_id)` or `get_appointments_by_date(date)`
* 2.1.2. Write unit tests for the new CRUD operations.
* 2.2. Update `src/agents/calendar_agent.py` to use these new tools for rescheduling and canceling appointments.
* 2.3. Update `src/notification_agent.py` to query appointments (e.g., for future appointments to send reminders).

* **3. Orchestrator and Graph Improvements (Robustness):**
### * 3.1. In `src/orchestrator_agent.py`:

| * 3.1.1. Refine the intent detection logic to handle more complexity and overlap. |
|---|

* 3.1.2. Implement fallback logic for when the intent is unclear or out of scope.
* 3.1.3. Implement a mechanism to collect "slots" (parameters) for each intent, interacting with the user until all are collected.
### * 3.2. In `src/graph.py`:

| * 3.2.1. Review and optimize conditional edges for smooth navigation between agents. |
|---|

* 3.2.2. Add specific error and exception handling within nodes (agents) and at the graph level.
* 3.2.3. Define an "error" or "generic_fallback_response" node where the graph can transition in case of failure or ambiguity.
### * 3.3. Improve chatbot memory (passing `AgentState`):

| * 3.3.1. Ensure that message history (`messages`) is maintained and used for context. |
|---|

* 3.3.2. Ensure that `collected_params` and `required_params` are updated consistently.

* **4. Email Integration (Optional, if relevant to the project):**
### * 4.1. In `src/tools/email_tools.py`:

| * 4.1.1. Configure the email client (SMTP with `smtplib` or integration with SendGrid/Mailgun). |
|---|

* 4.1.2. Develop the function/class to send emails with text and/or HTML.
* 4.1.3. Write unit tests for the email tools.
* 4.2. Integrate `email_tools` into `src/agents/notification_agent.py` to enable email notifications in addition to WhatsApp.
* 4.3. Add email credentials (`.env`).

---
### **Phase 4: Doctor Interface and Deployment with Docker**

**Objective:** Develop a simple interface for the doctor, containerize the entire application with Docker, and perform final integration and deployment preparation tests.

* **1. Doctor Interface Development:**
### * 1.1. In `src/main.py`:

| * 1.1.1. Configure FastAPI to serve static files (HTML, CSS, JS) from a `src/static/` directory. |
|---|

* 1.1.2. Create the `src/static/index.html`, `src/static/style.css`, `src/static/script.js` files for the basic interface.
### * 1.2. Implement Backend Endpoints for the UI:

| * 1.2.1. `GET /api/appointments/today`: Returns a list of appointments for the current day (using `database_tools`). |
|---|

* 1.2.2. `POST /api/appointment/{id}/remind`: Triggers the `NotificationAgent` to send a reminder for a specific appointment.
* 1.2.3. `POST /api/appointment/{id}/reschedule`: Triggers the `CalendarAgent` to start an appointment rescheduling flow.
* 1.2.4. `POST /api/chat_with_patient`: Allows the doctor to send a direct message to a patient via `whatsapp_tools`.
* 1.2.5. **(Optional)** `POST /api/chatbot_test`: An endpoint that allows the doctor to test interactions with the chatbot, perhaps by simulating a patient.
### * 1.3. In `src/static/script.js`:

| * 1.3.1. Make AJAX requests to FastAPI endpoints to list appointments. |
|---|

* 1.3.2. Implement the interface logic to trigger the "remind", "reschedule", and "send message" actions.
* 1.3.3. Display appointments in a list and provide interactive controls.

* **2. Containerization with Docker:**
### * 2.1. Create a `Dockerfile` in the project root:

| * 2.1.1. Define the base image (e.g., `python:3.9-slim-buster`). |
|---|

* 2.1.2. Copy `pyproject.toml` and `pyproject.lock` (if using `uv lock`) and install dependencies with `uv install --system` (for production) or `uv sync`.
* 2.1.3. Copy the rest of the code (`src/`, `config/`).
* 2.1.4. Define the `WORKDIR`.
* 2.1.5. Expose the FastAPI port (e.g., `EXPOSE 8000`).
* 2.1.6. Define the startup command with Uvicorn (e.g., `CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]`).
### * 2.2. Create a `docker-compose.yml`:

| * 2.2.1. Define the `chatbot_app` service that uses the `Dockerfile`. |
|---|

* 2.2.2. Map the container port to a host port.
* 2.2.3. Pass the necessary environment variables (from `.env` or directly) to the container.
* 2.2.4. **(Optional, for production)** Add a database service (e.g., `postgres`) and configure the connection between the containers.
* 2.3. Create `.dockerignore` to exclude unnecessary files (e.g., `.venv`, `__pycache__`, `.git`).
* 2.4. Build the Docker image: `docker build -t chatbot-recepcionista .`
* 2.5. Run the Docker container: `docker run -p 8000:8000 chatbot-recepcionista` (or `docker-compose up`).

* **3. Optimization and Final Testing:**
### * 3.1. Perform comprehensive integration testing:

| * 3.1.1. Test the complete scheduling flow via WhatsApp. |
|---|

* 3.1.2. Test sending reminders and messages.
* 3.1.3. Test the doctor's interface and its functionalities.
* 3.1.4. Test response to clinic information questions.
* 3.2. Test behavior in case of errors and edge cases (e.g., scheduling during busy times, incomplete information).
### * 3.3. Performance Optimization:

| * 3.3.1. Analyze logs and response times. |
|---|

* 3.3.2. Optimize calls to the LLM and database.
### * 3.4. Refine project documentation:

| * 3.4.1. `README.md` with local and Docker setup instructions. |
|---|

* 3.4.2. API documentation (FastAPI already generates OpenAPI/Swagger UI, but add descriptions).
* 3.5. Consider monitoring strategies (logs, metrics) for production.

---
By breaking each step down into tasks, each step becomes a mini-project in itself, facilitating monitoring, testing, and ensuring that the overall project will be delivered with high quality. It's an approach that minimizes risk and maximizes productivity.