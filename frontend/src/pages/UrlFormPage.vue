<template>
  <main class="page">
    <section class="card">
      <h1>Submit a URL</h1>
      <p>Enter a valid URL of your university programme page and click submit.</p>

      <form @submit.prevent="handleSubmit" class="url-form">
        <label for="urlInput">URL</label>
        <input
          id="urlInput"
          v-model.trim="url"
          type="url"
          placeholder="https://vilniustech.lt/stojantiesiems/studiju-programos/..."
          required
        />
        <button type="submit">Submit</button>
      </form>

      <p v-if="submittedUrl" class="result">Submitted URL: {{ submittedUrl }}</p>
    </section>
  </main>
</template>

<script>
export default {
  name: "UrlFormPage",
  data() {
    return {
      url: "",
      submittedUrl: "",
    };
  },
  methods: {
    handleSubmit() {
      this.submittedUrl = this.url;
    },
  },
};
</script>

<style scoped>
.page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #f3f8ff 0%, #e3f2eb 100%);
  padding: 1rem;
  font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
}

.card {
  width: min(560px, 100%);
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  padding: 1.5rem;
}

h1 {
  margin: 0 0 0.5rem;
}

p {
  margin: 0 0 1rem;
  color: #4a5565;
}

.url-form {
  display: grid;
  gap: 0.75rem;
}

label {
  font-weight: 600;
}

input {
  padding: 0.65rem 0.75rem;
  border: 1px solid #bfcad8;
  border-radius: 8px;
  font-size: 1rem;
}

input:focus {
  outline: 2px solid #1976d2;
  border-color: transparent;
}

button {
  width: fit-content;
  padding: 0.65rem 1rem;
  border: none;
  border-radius: 8px;
  background: #1976d2;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

button:hover {
  background: #115aa0;
}

.result {
  margin-top: 1rem;
  font-weight: 600;
  color: #1b5e20;
  word-break: break-all;
}
</style>
