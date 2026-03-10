# Lipiflow - AI Study Buddy Frontend

![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB) ![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=for-the-badge&logo=vite&logoColor=white) ![TailwindCSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white) ![Framer Motion](https://img.shields.io/badge/Framer_Motion-black?style=for-the-badge&logo=framer&logoColor=blue)

Lipiflow is a modern, high-performance intelligent study companion application. It transforms traditional learning materials (like uploaded PDFs, camera captures, and audio lectures) into comprehensive, structured, and interactive study guides using advanced AI.

## 🚀 The Problem It Solves

Students and professionals often struggle to distill large textbooks, dense research papers, or lengthy lecture recordings into actionable study material. 
Lipiflow eliminates the friction of manual note-taking and formatting by dynamically analyzing inputs and producing high-quality, formatted insights—including mathematical equations correctly formatted natively via KaTeX, interactive flashcards, logical breakdowns, and vital summaries.

## ✨ Core Features

- **Multi-modal Input**: Supports uploading local PDF files, capturing images directly via device camera, and recording/uploading audio files.
- **Smart Analysis Display**: Dynamically renders complex AI-generated study data (Key Priorities, Logical Topics, Summaries, and Flashcards) into an intuitive, glassmorphic UI.
- **Advanced LaTeX Rendering**: Seamlessly handles and renders dense mathematical and chemical formulas (via `react-katex`) directly inline with generated sentences.
- **Fluid Animations**: High-end micro-interactions, page transitions, and staggered list animations utilizing Framer Motion and GSAP.
- **Responsive & Accessible**: A truly responsive layout built with Tailwind CSS, ensuring a premium experience on desktop and mobile platforms.

## 🏗️ Architecture & Major Components

The frontend strictly adheres to a modular, component-driven React architecture. State and routing are managed client-side, communicating with a backend AI microservice to process intensive document logic.

### Major Components Navigation
- `<PageWrapper />`: Reusable animate-presence wrapper handling enter/exit transitions for all route pages.
- `<PdfInput /> / <AudioInput />`: Complex state machines handling drag-and-drop file staging, camera constraints, microphone access, and asynchronous submission status.
- `<PdfResult /> / <AudioResult />`: Dynamic presentation layers that digest the structured JSON response from the API. They compartmentalize "Concept Explanations" and "Key Priorities" and use iterative mapping to handle arrays.
- `<LatexRenderer />`: A heavily customized robust utility component resolving mixed LaTeX strings (`\\[ \\]`, `\\( \\)`, `$$`) and formatting them smoothly within the React tree using KaTeX.

## 📂 Project Structure

```text
frontend/
├── public/                 # Static assets
├── src/
│   ├── assets/             # Images, icons, local static styles
│   ├── components/         # Reusable atomic & modular React components
│   │   ├── common/         # Buttons, Inputs, LatexRenderer
│   │   ├── layout/         # Page wrappers, Navigation
│   │   ├── result/         # Cards, Markdown utilities, Synthesis renderers
│   │   └── ui/             # Complex unclassed UI (FileUpload, Animations)
│   ├── context/            # React context providers for global state
│   ├── hooks/              # Custom React hooks (e.g., useAudioRecorder)
│   ├── pages/              # High-level route views (Home, PdfInput, PdfResult)
│   ├── services/           # API abstraction layer (Axios configurations)
│   ├── styles/             # Global CSS and Tailwind directives
│   ├── utils/              # Helper functions (Animations, Markdown parsing)
│   ├── App.jsx             # Root component and Router configuration
│   └── main.jsx            # React DOM execution entry point
├── .env.production         # Environment variables for production build
├── index.html              # Vite HTML template
├── package.json            # Project manifests & dependencies
├── tailwind.config.js      # Tailwind CSS theme extension
└── vite.config.js          # Vite build and dev server configuration
```

## 🛠️ Setup Instructions

### Prerequisites
- [Node.js](https://nodejs.org/) (v18+ recommended)
- `npm` or `yarn`

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/lipiflow-frontend.git
cd lipiflow-frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Environment Variables
Create a `.env` file in the root directory mirroring your required configuration:
```env
VITE_API_URL=http://localhost:8000/api
```

### 4. Run the Development Server
```bash
npm run dev
```
The application will be hot-reloaded and accessible at `http://localhost:5173`.

### 5. Build for Production
To generate a static build:
```bash
npm run build
```
You can preview the built production bundle using:
```bash
npm run preview
```

## 💻 Tech Stack Highlights

- **Framework**: [React 18](https://react.dev/) + [Vite](https://vitejs.dev/)
- **Routing**: [React Router v6](https://reactrouter.com/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **Animations**: [Framer Motion](https://www.framer.com/motion/) & [GSAP](https://gsap.com/)
- **Math Rendering**: [KaTeX](https://katex.org/)
- **HTTP Client**: [Axios](https://axios-http.com/)
