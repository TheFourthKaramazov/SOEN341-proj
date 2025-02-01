# Description

This project is a real-time communication platform designed for seamless interaction through text channels and direct messaging. Users can join topic-specific channels, engage in one-on-one conversations, and share messages in a structured and organized interface. The platform supports role-based permissions, allowing administrators to create and manage channels while moderating conversations. Built with a focus on usability and security, it ensures efficient communication with real-time updates. 

## Objective

The goal is to develop a real-time communication platform for seamless text-based interactions, including text channels, direct messages, and role-based permissions, prioritizing responsiveness, scalability, and security with FastAPI, WebSockets, and Vue.js. In the short term, we aim to set up backend infrastructure, secure user authentication with JWT, real-time messaging, and a dynamic frontend with Vue.js, while ensuring secure deployment via Vercel and Docker. Long-term goals focus on enhancing scalability, adding advanced features, strengthening security, and implementing CI/CD pipelines. Deliverables are structured across four sprints: Sprint 1 covers setting up the environment; Sprint 2 focuses on core features, testing, and CI setup; Sprint 3 adds new features with TA feedback; Sprint 4 handles bug fixing, final testing, and documentation.

## Core Features

To complete

### Direct Messaging

#### What is direct messaging?
Direct messaging is one of the core features in our app that allows users to communicate in real time. When a user sends a message, the receiving user sees the message instantly without needing to refresh their screen.

#### Direct Message User Experience
Users can start a private conversation in the following way:
* User clicks on another user's username.
* A small popup appears with an input field.
    * The input field has the placeholder text
    
```sh
Private message OtherUser
```

#### Direct Message Functionality
* User's client establishes a persistent connection with the server using WebSockets.
* When the user sends a private message, their client will send their message over the WebSocket connection to the server.


This message will be sent as a JSON string and include the IDs of both the sender and the receiver, a timestamp and the actual text.

```sh
{
  "sender": {
    "id": "12345",
  },
  "receiver": {
    "id": "67890",
  },
  "timestamp": "2025-01-31T12:34:56Z",
  "text": "This new messaging app is pretty cool!"
}
```

* The server receives the message and sends it to the reciever.
    * The receiver's client immediately updates their view to show the message in real time.

#### Direct Messaging Roadmap
For the moment, our main goal is to allow a user to send a simple message over the server and have it appear instantly for the receiver. Once this is functional, we will refactor to improve efficiency as well as adding security by encrypting the messages.

### Role-Based User Permissions

#### What is role-based user permission?
Role-based user permissions are defined roles in the app that allow different actions to a user based on their assigned role. In our app, there are two roles: Admin and Member.

#### Admin and Member permissions
The admin role in the app can create and delete channels and moderate messages, which includes deleting those messages. They can also send messages in channels.
The member can only send and view messages in the allowed channels.

### Text Channels

#### What Are Text Channels?
Text channels are dedicated spaces where users can send and receive messages. They help organize conversations by keeping them relevant to their given topic.

#### Text Channel Functionality
- Users can browse a list of available text channels and join the ones they are interested in.
- Users can send and receive messages in their respective text channels using WebSockets, which allows real-time communication. Messages are stored in the database table associated with the channel.
- Messages are displayed with real-time updates, which is implemented using Vue.js on the frontend.

## Custom Feature 

## Team Members
- Brandon Leblanc - 40058666 @TheFourthKaramazov
- Malcolm Arcand Laliberté - 26334792 @Shredsauce
- Emy Om Sobodker - 40300379
- Moeid Abbasi - 40201670
- Luis Miguel Gomez - 40174754
- Christopher Liang - 40174418
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





