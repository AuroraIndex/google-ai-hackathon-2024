# Aurora GeminiLit
A way to create, edit, launch, and store impressive dashboards with no code and no background in data.

## Description
Aurora GeminiLit is a platform that allows users to upload a CSV file and generate a custom Streamlit dashboard through a conversational interface. The platform uses the Gemini API to examine the data, ask the user questions, and generate a dashboard that can be iteratively improved. The dashboard is validated and refined through a self-healing loop that runs the code and captures any errors, which are then fixed by Gemini. Once the dashboard is generated, it is launched on a dedicated port and rendered in an iframe within the same window as the chat interface. Users can then iterate on the dashboard, asking to make changes such as renaming it, adding graphs, or modifying parameters, and can cycle through past revisions as needed.

## Instructions for running locally

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

### Notes:
- This may or may not work on Windows due to file endings in the shell script used to launch the dashboards.
A quick solution is to go into the Docker container, find the `launch_streamlit.sh` file, make a superficial change and save the file. This will sanitize it for Unix.

- We have provided a simple dataset to test with. Please try it with your own! Size of the file may impact processing times, but not by much.

- This is an early work in progress. If you have any comments or suggestions please feel free to open an issue or contact the developers through our website.