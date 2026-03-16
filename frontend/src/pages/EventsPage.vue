<template>
  <pre>{{ output }}</pre>
</template>

<script>
export default {
  name: "EventsPage",
  data() {
    return {
      output: "Loading...",
    };
  },
  async mounted() {
    try {
      const response = await fetch("/api/events/");
      const data = await response.json();
      this.output = JSON.stringify(data, null, 2);
    } catch (error) {
      this.output = JSON.stringify({ error: error.message || "Failed to load events." }, null, 2);
    }
  },
};
</script>
