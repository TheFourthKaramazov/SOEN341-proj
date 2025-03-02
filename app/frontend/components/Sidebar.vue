<template>
  <div class="sidebar">
    <h2>Channels</h2>
    <ul>
      <li
        v-for="channel in channels"
        :key="channel.id"
        @click="selectChannel(channel)"
        :class="{ 'highlighted': selectedChannel && selectedChannel.id === channel.id }"
      >
        {{ channel.name }}
      </li>
    </ul>

    <h2>Users</h2>
    <ul>
      <li
        v-for="user in users"
        :key="user.id"
        @click="selectUser(user)"
        :class="{ 'highlighted': selectedUser && selectedUser.id === user.id }"
      >
        {{ user.name }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  props: ["channels", "selectedChannel"],
  data() {
    return {
      users: [
        { id: 1, name: "User1" },
        { id: 2, name: "User2" },
        { id: 3, name: "User3" },
        { id: 4, name: "User4" },
      ],
      selectedUser: null,
    };
  },
  methods: {
    selectChannel(channel) {
      this.$emit("selectChannel", channel);
    },
    selectUser(user) {
      this.selectedUser = user;
      this.$emit("selectUser", user);
    },
  },
};
</script>

<style scoped>
.sidebar {
  width: 250px;
  background-color: #2f3542;
  color: white;
  padding: 20px;
  overflow-y: auto;
  position: sticky;
  top: 0;
}

.sidebar h2 {
  margin-top: 0;
}

.sidebar ul {
  list-style-type: none;
  padding-left: 0;
}

.sidebar li {
  padding: 10px;
  margin: 5px 0;
  background-color: #3e4451;
  cursor: pointer;
  border-radius: 5px;
  transition: background-color 0.2s;
}

.sidebar li:hover {
  background-color: #4e5b67;
}

.sidebar li.highlighted {
  background-color: #4e5b67;
}
</style>
