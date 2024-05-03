

1. Copy the contents of `/backend/.env.example` into `/backend/.env`.
2. Replace the placeholder `...` in the newly created `/backend/.env` file with your actual Gemini API key:
   ```
   GEMINI_API_KEY=...
   ```
3. Run the following command to start the services:
   ```
   docker-compose up
   ```
4. Monitor the terminal output for any issues. If Gemini gets stuck debugging streamlit app rerun using the following commands
   - Stop the running services:
     ```
     docker-compose down
     ```
   - Restart the services:
     ```
     docker-compose up
     ```
