<template>
    <div class="direct-message">
        <h2>Direct Message: {{ activeConversationName }}</h2>
        <DirectMessageBox />
    </div>
</template>

<script>
import DirectMessageBox from "@/components/DirectMessageBox.vue";
import { useDirectMessageStore } from "@/store/directMessageStore";

export default {
    components: { DirectMessageBox },
    computed: {
        activeConversationName() {
            return useDirectMessageStore().activeConversationName;
        },
    },
};
</script>

<!-- Same as TextChannel.vue -->
<style scoped>
.direct-message {
    display: flex;
    flex-direction: column;
    height: 100vh;
    padding: 10px;
}
</style>