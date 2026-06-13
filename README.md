# 🖼️ Image Vault

**Image Vault** is a warm, cozy, and minimalist web application designed to save and share group memories. Whether it's memories with friends, classmates, or family, users can create private vaults, invite members, share photos, and leave comments in a collaborative, welcoming environment.

The application features a custom, premium branding scheme (highlighted by our warm Polaroid & sunset-safe dial vector logo) and follows a cozy, minimalist design system of amber, peach, rose, and cream tones.

---

## 📖 Table of Contents
1. [Tech Stack](#-tech-stack)
2. [Key Features](#-key-features)
3. [Project Structure](#-project-structure)
4. [Getting Started (Local Setup)](#-getting-started-local-setup)
   - [Prerequisites](#prerequisites)
   - [Step 1: Database Setup (Docker)](#step-1-database-setup-docker)
   - [Step 2: Backend Setup (Django)](#step-2-backend-setup-django)
   - [Step 3: Frontend Setup (Vue)](#step-3-frontend-setup-vue)
5. [How to Use](#-how-to-use)
6. [Architecture & Core Concepts](#-architecture--core-concepts)

---

## 🛠️ Tech Stack

### Backend
- **Framework:** Python 3 + [Django 4.2](https://www.djangoproject.com/)
- **API Engine:** [Django REST Framework (DRF)](https://www.django-rest-framework.org/)
- **Authentication:** Token-based Authentication
- **Database:** PostgreSQL (via docker-compose)

### Frontend
- **Framework:** [Vue 3](https://vuejs.org/) (Composition API)
- **Build Tool:** [Vite](https://vite.dev/) (Vite Dev Server handles API & Media proxying to the Django backend)
- **State Management:** [Pinia](https://pinia.vuejs.org/) (stores auth state, vault list, photos, and comments)
- **Router:** Vue Router 4
- **Styles:** Custom Vanilla CSS Design System (Cozy Warm palette)

---

## ✨ Key Features

- **Cozy Minimalist UI:** Handcrafted CSS tokens (amber-rose sunset gradients, soft card shadows, micro-animations, and responsive grids).
- **Custom User Profiles:** Initials-based avatar generation with custom email logins.
- **Dynamic Vaults:** Private albums that represent a specific group (e.g. family summer trip, graduation class) decorated with a selected emoji.
- **Secure Code Invites:** Owner can add members directly via email, or generate a 6-character secure invite code for users to join.
- **Photo Memories:** Simple URL-based image uploading, preview caching, and lightbox zoom display.
- **Conversational Spaces:** Interactive comment sections attached directly to photos.

---

## 📂 Project Structure

```text
Image_Vault/
│
├── backend/                       # Django REST API Backend
│   ├── core/                      # Core settings, WSGI, URLs
│   │   ├── settings.py            # Database configuration, middleware, CORS
│   │   └── urls.py                # Base routing (includes api urls)
│   ├── api/                       # API Application
│   │   ├── models.py              # User, Vault, Photo, Comment Database Schema
│   │   ├── serializers.py         # JSON serialization & validation logic
│   │   ├── views.py               # REST endpoints & CRUD handlers
│   │   └── urls.py                # Django API endpoint mappings
│   ├── manage.py                  # Django administrative script
│   ├── requirements.txt           # Python backend dependencies
│   ├── .env.example               # Template for local environment config
│   └── .env                       # Local environment secrets (ignored by git)
│
├── frontend/                      # Vue 3 Frontend
│   ├── public/                    # Static assets
│   │   ├── vault-icon.svg         # Premium Polaroid Vault logo
│   │   └── favicon.svg            # Branding-aligned browser tab icon
│   ├── src/                       # Source code
│   │   ├── components/            # Reusable Vue components (AppNav, VaultCard)
│   │   ├── views/                 # Top-level Page Views (Home, Auth, Vault)
│   │   ├── stores/                # Pinia State Management (index.js)
│   │   ├── router.js              # Routing with route-level Auth Guards
│   │   ├── api.js                 # API wrappers & REST Client (fetch)
│   │   ├── style.css              # Cozy Minimalist Global Design System
│   │   └── main.js                # App entrypoint
│   ├── vite.config.js             # Vite configuration with Backend Port Proxying
│   ├── package.json               # Frontend dependencies & npm scripts
│   └── README.md                  # Frontend specific instructions
│
├── docker-compose.yml             # Docker config for the PostgreSQL Database
└── TODO.md                        # Task tracker
```

---

## 🚀 Getting Started (Local Setup)

### Prerequisites
- [Docker & Docker Compose](https://www.docker.com/products/docker-desktop/)
- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js v18+](https://nodejs.org/)

---

### Step 1: Database Setup (Docker)

Start the PostgreSQL service using Docker Compose in the root of the project:
```bash
docker-compose up -d
```
*Note: This spins up a PostgreSQL container named `image_vault_db` on port `5432` with user `vault_user` and database `image_vault`.*

---

### Step 2: Backend Setup (Django)

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Activate the pre-created virtual environment in the root, or create one:
   - **Windows (CMD/PowerShell):**
     ```powershell
     ..\.venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source ../.venv/bin/activate
     ```

3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

4. Create your local configuration file:
   Copy `.env.example` to a new file named `.env` and fill out any fields or keep defaults for local dev:
   ```bash
   cp .env.example .env
   ```

5. Run Django migrations:
   ```bash
   python manage.py migrate
   ```

6. Start the backend server:
   ```bash
   python manage.py runserver
   ```
   *The backend api will start running at `http://localhost:8000`.*

---

### Step 3: Frontend Setup (Vue)

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install the required Node modules:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```
   *The frontend application will start running at `http://localhost:5173`.*

4. Open your browser and navigate to `http://localhost:5173` to access **Image Vault**.

---

## 🎨 How to Use

1. **Authentication:**
   - Register a new account on the auth screen. The system uses your name to automatically compute and render a stylized initials badge.

2. **Managing Vaults:**
   - On the homepage, click **＋ New Vault** to create a new vault. Give it a name, a description, and select a themed emoji.
   - Click **🔑 Join Vault** to enter a 6-character code shared by a friend.

3. **Collaborating:**
   - Inside a vault, view the **Invite Code** (click to copy) in the upper right. Share it with friends so they can join!
   - View members of the vault listed at the top. The owner will be marked with a crown (`👑`).
   - If you are the owner, click **⚙️** (Vault Settings) to delete the vault or add members directly by their email address.

4. **Posting & Commenting:**
   - Click **📷 Add Photo** and paste an image URL (e.g. from Unsplash or other sources) along with a caption to add a memory to the vault.
   - Click on any photo in the masonry grid to open the lightboxed overlay to view comments, delete the photo (if uploaded by you or if you own the vault), and post your own comments.

---

## 🏗️ Architecture & Core Concepts

### Database Schema ([backend/api/models.py](file:///D:/LT/Image_Vault/backend/api/models.py))
- **User:** Inherits Django's `AbstractUser` but uses email logins. Auto-computes and saves 2-letter uppercase initials on save.
- **Vault:** UUID primary keys. Holds a list of members via a ManyToMany relationship. Automatically generates random 6-character uppercase invite codes.
- **Photo:** Linked to a Vault and Uploader. Stores a direct URL to the image and a caption.
- **Comment:** Linked to a Photo and Author. Stores text and the timestamp.

### Global State ([frontend/src/stores/index.js](file:///D:/LT/Image_Vault/frontend/src/stores/index.js))
Uses Pinia for asynchronous requests and cache storage:
- `useAuthStore`: Restores token sessions, registers/logins/logouts users, and maintains a local cache of user objects to prevent duplicate fetch calls.
- `useVaultStore`: Fetches member vaults, handles invites/memberships, performs CRUD operations on photos, and manages comments on lightboxed photos.
