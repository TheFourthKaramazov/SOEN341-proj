<template>
    <div class="chat-container">
        <!-- Messages Display -->
        <div class="messages" ref="messageContainer">
            <div
                v-for="msg in messages"
                :key="msg.id"
                :class="{ 'my-message': msg.senderId === userId, 'other-message': msg.senderId !== userId }"
            >
                <strong>{{ msg.senderName }}:</strong> {{ msg.content }}
            </div>
        </div>

        <!-- Message Input -->
        <div class="message-input">
            <input v-model="newMessage" @keyup.enter="sendMessage" placeholder="Type a message..." />
            <button @click="sendMessage">Send</button>
        </div>
    </div>
</template>

<script>
import { sendDirectMessage, onMessage } from "@/services/websocketService";
import { useUserStore } from "@/store/userStore";
import { useDirectMessageStore } from "@/store/directMessageStore";

export default {
    data() {
        return {
            newMessage: "",
        };
    },
    computed: {
        userId() {
            return useUserStore().userId;
        },
        receiverId() {
            return useDirectMessageStore().activeConversationId;
        },
        messages() {
            return useDirectMessageStore().messages[this.receiverId] || [];
        },
    },
    methods: {
        sendMessage() {
            if (this.newMessage.trim()) {
                sendDirectMessage(this.receiverId, this.newMessage);
                this.newMessage = "";
            }
        },
        receiveMessage(message) {
            if (message.receiverId === this.receiverId) {
                useDirectMessageStore().addMessage(this.receiverId, message);
                this.scrollToBottom();
            }
        },
        scrollToBottom() {
            this.$nextTick(() => {
                const container = this.$refs.messageContainer;
                if (container) {
                    container.scrollTop = container.scrollHeight;
                }
            });
        },
    },
    mounted() {
        onMessage(this.receiveMessage);
        this.scrollToBottom();
    },
    watch: {
        messages() {
            this.scrollToBottom();
        },
    },
};
</script>

<!-- Same as ChatBox.vue -->
<style scoped>
.chat-container {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.messages {
    flex-grow: 1;
    overflow-y: auto;
    padding: 10px;
    height: 300px;
}

.message-input {
    display: flex;
    padding: 10px;
}

input {
    flex-grow: 1;
    padding: 8px;
}

button {
    margin-left: 10px;
}

.my-message {
    text-align: right;
    background-color: #dcf8c6;
    padding: 5px;
    border-radius: 5px;
}

.other-message {
    text-align: left;
    background-color: #ebebeb;
    padding: 5px;
    border-radius: 5px;
}
</style>