# ECCD MVP Core Features — Walkthrough

We have successfully developed the core functional modules of the Early Childhood Development (ECCD) Monitoring System. All pages in the React client are connected to the live ASP.NET Core API endpoints and persist data directly into the MySQL database.

## Accomplishments

### 1. Database Seeding
- Pre-seeded Child Development Centers (CDCs) under `ChildDevelopmentCenters` table:
  - `CDC Barangay Central`
  - `CDC Barangay East`
- Added `/api/v1/cdc` endpoint allowing unauthenticated query of these CDCs.

### 2. User Authentication & Onboarding
- **Onboarding Flow**:
  - Exposed `POST /api/v1/auth/register/teacher` and `POST /api/v1/auth/register/parent`.
  - Registration captures profile data (position, employee ID, relation to learner, mobile, address) and creates ASP.NET Identity users in MySQL.
  - Automatically records timestamped Data Privacy Act (DPA) consent.
- **Login Session**:
  - Exposed `POST /api/v1/auth/login` returning JWT access tokens (expiring in 60 mins) and client user DTO profiles.
  - Linked profile IDs to the corresponding user account.
- **Forgot Password Flow**:
  - Exposed `/api/v1/auth/forgot-password` and `/api/v1/auth/reset-password`. Generates 6-digit verification codes (printed to the API console output during local development).

### 3. Classrooms Management
- Exposed `POST /api/v1/classrooms` and `GET /api/v1/classrooms`.
- Users with the `Teacher` or `Administrator` roles can create new classes (specifying Name, Subject preset, Age group, School year, Schedule, Max learners, and Theme color).
- Creating a classroom automatically generates the subject-based classwork folders (Mathematics, Science, English, etc.) per PRD requirements.
- Exposed `DELETE /api/v1/classrooms/{id}` which soft-archives class cohorts.

### 4. Learners Directory
- Exposed `GET /api/v1/parents` to list registered parents.
- Exposed `POST /api/v1/learners` and `GET /api/v1/learners` (with query searching by name/LRN and classroom filters).
- Exposed `POST /api/v1/learners/{id}/enroll` to enroll a child in a class cohort (creating a `ClassroomEnrollment` junction record), checking classroom capacities.
---

## Validation Results

### Backend Build
```powershell
> dotnet build ECCD.sln
Build succeeded. 0 Warnings, 0 Errors.
```

### Frontend Build
```powershell
> npm run build
dist/assets/index-CBJcJpOQ.css    6.19 kB
dist/assets/index-CIR6RUPo.js   347.07 kB
✓ built in 374ms
```

---

## How to Manually Verify functionality

1. **Start the API Server**:
   ```powershell
   dotnet run --project src/ECCD.API/ECCD.API.csproj
   ```
2. **Start the React Client**:
   ```powershell
   cmd /c "cd src\eccd-client && npm run dev"
   ```
3. Open `http://localhost:5173` in your browser.
4. Click **Register Here** on the login page.
5. Register a **Parent** account first (e.g. username `parentjuan`, password `Password123!`).
6. Register a **Teacher** account (e.g. username `teachermary`, password `Password123!`). Select one of the seeded CDCs.
7. Log in as the **Teacher**.
8. Go to **My Classrooms** and click **+ Create New Classroom**. Populate the form.
9. Go to **My Learners** and click **+ Add New Learner**. Select `parentjuan` from the dropdown list.
10. Click **Enroll in Class** next to the newly registered child and select the classroom you created.
11. Go back to **My Classrooms** to verify the enrollment counts have updated.
