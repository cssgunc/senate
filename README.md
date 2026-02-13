# Senate

A CS+SG project for the Undergraduate Senate at UNC Chapel Hill.

## Contributors

| Name          | Role            |
| ------------- | --------------- |
| Caleb Han     | Tech Lead       |
| Mason Mines   | Project Manager |
| Xander Pak    | Developer       |
| Gabriel Great | Developer       |
| Chris Kim     | Developer       |

## About the Undergraduate Senate

The Senate of the Undergraduate Student Body at the University of North Carolina at Chapel Hill consists of elected student Senators across diverse academic backgrounds, representing approximately 20,000 undergraduate students. These Senators work together with student organizations to address issues on and off campus.

## Project Mission

- Create an intuitive, modern frontend that allows students to easily navigate senate resources, contact senators by district, search legislation, and understand senate processes
- Implement a robust admin dashboard that allows non-technical staff to update content (news, roster, legislation, events, committee assignments) without developer intervention
- Build interactive features including searchable legislation database, district-based senator lookup, finance hearing scheduling, and budget visualization to increase transparency and engagement

## Tech Stack

### Backend

- **Python 3.13**
- **FastAPI 0.115**
- **SQLAlchemy 2.0**
- **SQL Server Express**
- **pyodbc**

### Frontend

- **Node.js 24 LTS**
- **Next.js 15.5**
- **React 19**
- **TypeScript 5.7**
- **Tailwind CSS 3.4**

## Project Structure

```
senate/
├── .devcontainer/       # Development container configuration
├── backend/             # FastAPI application
│   ├── app/
│   │   ├── main.py      # FastAPI entry point
│   │   ├── database.py  # Database configuration
│   │   ├── models/      # SQLAlchemy models
│   │   ├── routers/     # API routes
│   │   └── schemas/     # Pydantic schemas
│   ├── tests/
│   └── requirements.txt
├── frontend/            # Next.js application
│   ├── src/
│   │   ├── app/         # Next.js App Router
│   │   ├── components/  # React components
│   │   └── lib/         # Utilities
│   └── package.json
└── README.md
```

## Onboarding

Clone the repository into your preferred directory

```
git clone https://github.com/cssgunc/senate.git
```

Open a terminal at the project root and run the following commands

```bash
cd frontend
cp .env.local.example .env.local # duplicates the template and renames it to .env.local

cd ../backend
cp .env.example .env # duplicates the template and renames it to .env
```

Or you can do the actions manually. Then,

- Ensure you have Docker and the Dev Containers extension installed
- Open the VS Code Command Palette (Mac - Cmd+Shift+P and Windows - Ctrl+Shift+P)
- Run the command **Dev Containers: Rebuild and Reopen in Container**
- This should open the dev container with the same file directory mounted so any changes in the dev container will be seen in the local repo
- The dev container is fully built once the file directory is populated and the post create script finished running

## Running The App

_If you haven't run in a day or more, run `python -m script.reset_dev` from the `/backend` directory to ensure all mock data is updated to be centered around today's date_

### VSCode Debugger (Recommended)

Navigate to the "Debug and Run" tab on the VSCode side bar.

At the top of the side bar, next to the green play button, select the desired module to run

- **Backend**: Starts the FastAPI backend on http://localhost:8000
- **Purge & Frontend**: Starts the Next.js frontend on http://localhost:3000
  - _The "Purge" part of this is referring to the task that kills any `next dev` processes in order to address a devcontainer issue. Note that this prevents you from running multiple of these debug sessions concurrently. If mulitple are needed, refer to the manual instructions below_
- **Full Stack**: Starts both of the above in separate terminals

Then simply press the green play button

### Manually

**Backend**: Open a new terminal and run these commands

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**: Open another new terminal and run these commands to start the frontend

```bash
cd frontend
npm run dev
```

Navigate to [http://localhost:3000](http://localhost:3000) to view the website

## Running Backend Tests

### Manual Testing

After running the backend, navigate to [http://localhost:8000/docs](http://localhost:8000/docs). You can then make any requests using the provided GUI.

### Unit Tests

The best way to run unit tests is by using the "Testing" window on the sidebar. This provides an intuitive GUI for running tests within the IDE.
You can also run all tests by opening a new terminal and simply running

```sh
pytest
```

## Accessing the Database

You can access the SQL Server Express instance using the **SQL Server** extension for VS Code (left sidebar).

Enter the connection string from the "Load from Connection String" button:

**Connection String:**

```
Server=db,1433;Database=senate;User Id=sa;Password=SenateDev2026!;TrustServerCertificate=True;
```

**Initial Setup:**

Before first use, create the database and tables:

```bash
cd backend
python -m script.create_db
python -m script.create_test_db  # Optional: for running tests
```
