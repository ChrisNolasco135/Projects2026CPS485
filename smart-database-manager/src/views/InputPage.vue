<script setup>
import { ref } from 'vue'

const query = ref('')
const savedQuery = ref('')
const postStatus = ref('')

const saveQuery = async () => {
  savedQuery.value = query.value
  postStatus.value = 'Saving...'

  try {
    //change the URL to match the backend endpoint
    const response = await fetch('http://localhost:8000/api/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ value: savedQuery.value }),
    })

    if (!response.ok) {
      throw new Error(`Request failed: ${response.status}`)
    }

    postStatus.value = 'Saved.'
  } catch (error) {
    postStatus.value = error instanceof Error ? error.message : 'Save failed.'
  }
}
</script>

<template>
  <main>
    <label for="query-input">Input: </label>
    <input id="query-input" v-model="query" name="query" type="text" />
    <button type="button" @click="saveQuery">Enter</button>
    <p>Saved value: {{ savedQuery }}</p>
    <p>{{ postStatus }}</p>
  </main>
</template>
