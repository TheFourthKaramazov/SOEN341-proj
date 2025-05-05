<!-- two screenshots side‑by‑side, identical size -->
<p align="center">
  <img
    src="https://github.com/user-attachments/assets/5ed34e74-de7f-4db8-bf08-f6cef40928f3"
    alt="Screenshot – chat UI"
    width="100%" style="min-width:300px; margin-right:1%">

</p>


# Description

This project is a real-time communication platform designed for seamless interaction through text channels and direct messaging. Users can join topic-specific channels, engage in one-on-one conversations, and share messages in a structured and organized interface. The platform supports role-based permissions, allowing administrators to create and manage channels while moderating conversations. Built with a focus on usability and security, it ensures efficient communication with real-time updates. 

## Objective

The goal is to develop a real-time communication platform for seamless text-based interactions, including text channels, direct messages, and role-based permissions, prioritizing responsiveness, scalability, and security with FastAPI, WebSockets, and Vue.js. In the short term, we aim to set up backend infrastructure, secure user authentication with JWT, real-time messaging, and a dynamic frontend with Vue.js, while ensuring secure deployment via Vercel and Docker. Long-term goals focus on enhancing scalability, adding advanced features, strengthening security, and implementing CI/CD pipelines. Deliverables are structured across four sprints: Sprint 1 covers setting up the environment; Sprint 2 focuses on core features, testing, and CI setup; Sprint 3 adds new features with TA feedback; Sprint 4 handles bug fixing, final testing, and documentation.



## Completed Features

### Direct Real‑Time Messaging
- Private DM threads between any two users  
- Typing indicator & instant delivery via persistent WebSocket channels  

### Text Channels
- Topic‑specific chat rooms listable, joinable, and leavable at will  
- Live message streams with automatic scroll and lazy‑loaded history  
- Media sharing (images & videos) identical to DMs
- Admin can create and delete channels
- Users can subscribe and unsubscribe 

### Channel & Role Management
- **Admin**: create / delete channels, delete any message  
- **Member**: post, edit own messages in joined channels  
- UI clearly labels role; permission checks enforced server‑side

### Secure Authentication
- Email + password login page with client‑side validation  
- Separate admin and member token scopes

### Media Uploads
- Drag‑and‑drop or clipboard paste for images and videos 
- Re‑rendered thumbnails for faster previews

### Interactive Home Page
- Unified feed showing:
  - Sent and Received Images/Videos
  - Inline media previews  


## Team Members
- Brandon Leblanc - 40058666 @TheFourthKaramazov
- Malcolm Arcand Laliberté - 26334792 @Shredsauce
- Emy Om Sobodker - 40300379 @emyeatGrass
- Moeid Abbasi - 40201670 @moeidabbasi
- Luis Miguel Gomez - 40174754 @mediis23
- Christopher Liang - 40174418 @chrix1234
- Mohamed-Rabah-Ishaq Loucif - 40282580 @Tropometrie
- Benjamin Zitella -40211380 @summoningstrife

## Languages & Technologies 

#### Backend (Python-based)
- FastAPI (Python) – High-performance API framework, auto-generates OpenAPI documentation.
- SQLite (Python) or PostgreSQL – Database for storing users, messages, and channels.
- WebSockets (Python - FastAPI WebSockets) – Real-time chat feature.
- JWT (Python - pyjwt) – Authentication and user session management.
- CORS Middleware (Python - FastAPI) – Allows frontend to interact with backend API.
- Pydantic (Python) – Data validation and request serialization.
- Dependency Injection (Python - FastAPI) – Simplifies API dependency management.

#### Frontend (JavaScript-based)
- Vue.js – Frontend framework for dynamic UI.
- Vue Router – Client-side navigation.
- Pinia or Vuex – State management for chat and user sessions.
- Axios – API requests to the FastAPI backend.
- Tailwind CSS or Bootstrap (CSS) – UI styling.
- WebSockets (JavaScript - Browser API) – Real-time chat updates.

#### Deployment
- Docker (optional) – Containerized backend/frontend.
- Vercel (frontend auto-deploy) – Free and simple hosting for Vue.js.





