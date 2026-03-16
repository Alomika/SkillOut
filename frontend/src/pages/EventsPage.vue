<template>
  <main class="page">
    <section class="card wide">
      <h1>Events</h1>
      <p>This page is ready for event output.</p>
      <p class="muted">No event logic is connected yet.</p>

      <div class="button-group">
        <button @click="$router.push('/subjects')" class="btn-back">Back to Subjects</button>
      </div>
    </section>
  </main>
</template>

<script>
export default {
  name: "EventsPage",
};
</script>

<style scoped>
.page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #f3f8ff 0%, #e3f2eb 100%);
  padding: 2rem;
  font-family: "Segoe UI", sans-serif;
}

.card.wide {
  width: min(800px, 100%);
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  padding: 2rem;
  text-align: center;
}

h1 {
  margin: 0 0 0.5rem;
}

p {
  margin: 0.5rem 0;
}

.muted {
  color: #4a5565;
}

.button-group {
  display: flex;
  justify-content: center;
  margin-top: 1.5rem;
}

.btn-back {
  padding: 0.65rem 1.5rem;
  border: 1px solid #1976d2;
  background: transparent;
  color: #1976d2;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.btn-back:hover {
  background: #e3f2fd;
}
</style>
