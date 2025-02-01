# Description

This project is a real-time communication platform designed for seamless interaction through text channels and direct messaging. Users can join topic-specific channels, engage in one-on-one conversations, and share messages in a structured and organized interface. The platform supports role-based permissions, allowing administrators to create and manage channels while moderating conversations. Built with a focus on usability and security, it ensures efficient communication with real-time updates. 

## Objective

To complete

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



## Custom Feature 

## Team Members
- Brandon Leblanc - 40058666 @TheFourthKaramazov
- Malcolm Arcand Laliberté - 26334792 @Shredsauce
- Emy Om Sobodker - 40300379
- Moeid Abbasi - 40201670
- Luis Miguel Gomez - 40174754
- Christopher Liang - 40174418
- Mohamed-Rabah-Ishaq Loucif - 40282580 @Tropometrie

To complete


## Languages & Technologies 

To complete





