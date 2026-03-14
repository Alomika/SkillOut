<template>
  <main class="page">
    <section class="card wide">
      <h1>Detected Study Subjects</h1>
      <p v-if="loading">Loading subjects...</p>
      
      <div v-else-if="subjects.length">
        <ul class="subjects-list">
          <li v-for="(subject, index) in subjects" :key="index" class="subject-item">
            <span class="number">{{ index + 1 }}.</span> {{ subject }}
          </li>
        </ul>
        <button @click="$router.push('/')" class="btn-back">Go Back</button>
      </div>

      <p v-else class="error-message">No subjects found. Please try scraping again.</p>
    </section>
  </main>
</template>

<script>
export default {
  name: "SubjectsPage",
  data() {
    return {
      subjects: [],
      loading: true,
    };
  },
  async mounted() {
    try {
      const response = await fetch("/api/get-latest-subjects/");
      const data = await response.json();
      if (data.study_subjects) {
        this.subjects = data.study_subjects;
      }
    } catch (error) {
      console.error("Error loading subjects:", error);
    } finally {
      this.loading = false;
    }
  },
};
</script>

<style scoped>
/* Išlaikome tavo pasirinktą stilių */
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
}

.subjects-list {
  list-style: none;
  padding: 0;
  margin: 1.5rem 0;
  text-align: left;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 0.5rem;
}

.subject-item {
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #1976d2;
  font-size: 0.95rem;
}

.number {
  font-weight: bold;
  color: #1976d2;
  margin-right: 5px;
}

.btn-back {
  margin-top: 1rem;
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