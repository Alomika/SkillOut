<template>
  <main class="page">
    <section class="card wide">
      <h1>Detected Study Subjects</h1>
      <p v-if="loading">Loading subjects...</p>
      
      <div v-else-if="subjects.length">
        <ul class="subjects-list">
          <li v-for="(subject, index) in subjects" :key="index" class="subject-item">
            <div class="subject-content">
              <span class="number">{{ index + 1 }}.</span> {{ subject }}
            </div>
            <!-- Ištrynimo mygtukas -->
            <button @click="removeSubject(index)" class="btn-delete" title="Remove subject">❌</button>
          </li>
        </ul>
        <button @click="$router.push('/')" class="btn-back">Go Back</button>
      </div>

      <!-- Čia automatiškai parodoma, jei ištrinsi viską (tavo reikalavimas SD-117) -->
      <p v-else class="error-message">⚠️ No subjects left. Please try scraping again or add subjects manually.</p>
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
  // --- ŠITA DALIS BUVO PRALEISTA ---
  methods: {
    removeSubject(index) {
      // Ištriname elementą iš masyvo
      this.subjects.splice(index, 1);
    }
  },
  // --------------------------------
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
/* Tavo esami stiliai... */
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
}

.subject-item {
  display: flex; /* Pridėta, kad mygtukas būtų šone */
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #1976d2;
  font-size: 0.95rem;
  margin-bottom: 0.5rem;
}

/* Mygtuko stilius */
.btn-delete {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  transition: background 0.2s;
}

.btn-delete:hover {
  background: #ffebee;
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

.error-message {
  color: #d32f2f;
  font-weight: 600;
}
</style>