<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import axios from 'axios'

const auth = useAuthStore()
const API = 'http://localhost:8000'

const databases = ref([])
const selectedDatabase = ref(null)
const selectedTable = ref(null)
const tableData = ref([])
const tables = ref([])
const error = ref('')
const loading = ref(false)
const showCreateDatabaseModal = ref(false)
const newDatabaseName = ref('')
const showCreateTableModal = ref(false)
const newTableName = ref('')
const newTableColumns = ref([{ name: '', type: 'TEXT' }])
const creating = ref(false)
const showAddRowModal = ref(false)
const showEditRowModal = ref(false)
const newRowData = ref({})
const editingRowData = ref({})
const editingRowId = ref(null)
const editingRowIndex = ref(null)

onMounted(() => {
  fetchDatabases()
})

async function fetchDatabases() {
  loading.value = true
  error.value = ''
  try {
    if (!auth.token) {
      error.value = 'No authentication token found. Please log in again.'
      return
    }
    const response = await axios.get(`${API}/databases/`, {
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    databases.value = response.data
  } catch (err) {
    console.error('Error loading databases:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to load databases'
  } finally {
    loading.value = false
  }
}

async function selectDatabase(db) {
  selectedDatabase.value = db
  selectedTable.value = null
  tableData.value = []
  tables.value = []
  error.value = ''
  loading.value = true
  try {
    const response = await axios.get(
      `${API}/databases/${db.id}/tables`,
      { headers: { Authorization: `Bearer ${auth.token}` } }
    )
    tables.value = response.data
  } catch (err) {
    console.error('Error loading tables:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to load tables'
  } finally {
    loading.value = false
  }
}

async function selectTable(tableName) {
  selectedTable.value = tableName
  tableData.value = []
  error.value = ''
  loading.value = true
  try {
    const response = await axios.get(
      `${API}/databases/${selectedDatabase.value.id}/tables/${tableName}/rows`,
      { headers: { Authorization: `Bearer ${auth.token}` } }
    )
    tableData.value = response.data
  } catch (err) {
    console.error('Error loading table data:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to load table data'
  } finally {
    loading.value = false
  }
}

const tableColumns = computed(() => {
  if (tableData.value.length === 0) return []
  return Object.keys(tableData.value[0])
})

function openCreateTableModal() {
  showCreateTableModal.value = true
  newTableName.value = ''
  newTableColumns.value = [{ name: '', type: 'TEXT' }]
}

function closeCreateTableModal() {
  showCreateTableModal.value = false
}

function openCreateDatabaseModal() {
  showCreateDatabaseModal.value = true
  newDatabaseName.value = ''
}

function closeCreateDatabaseModal() {
  showCreateDatabaseModal.value = false
}

async function createDatabase() {
  error.value = ''
  if (!newDatabaseName.value.trim()) {
    error.value = 'Database name is required'
    return
  }

  creating.value = true
  try {
    await axios.post(
      `${API}/databases/`,
      { name: newDatabaseName.value },
      { headers: { Authorization: `Bearer ${auth.token}` } }
    )

    // Refresh databases list
    const response = await axios.get(`${API}/databases/`, {
      headers: { Authorization: `Bearer ${auth.token}` }
    })
    databases.value = response.data
    closeCreateDatabaseModal()
  } catch (err) {
    console.error('Error creating database:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to create database'
  } finally {
    creating.value = false
  }
}

function addColumn() {
  newTableColumns.value.push({ name: '', type: 'TEXT' })
}

function removeColumn(index) {
  newTableColumns.value.splice(index, 1)
}

async function createTable() {
  error.value = ''
  if (!newTableName.value.trim()) {
    error.value = 'Table name is required'
    return
  }

  if (newTableColumns.value.some(col => !col.name.trim())) {
    error.value = 'All column names are required'
    return
  }

  creating.value = true
  try {
    await axios.post(
      `${API}/databases/${selectedDatabase.value.id}/tables`,
      {
        name: newTableName.value,
        columns: newTableColumns.value
      },
      { headers: { Authorization: `Bearer ${auth.token}` } }
    )

    // Refresh tables list
    const response = await axios.get(
      `${API}/databases/${selectedDatabase.value.id}/tables`,
      { headers: { Authorization: `Bearer ${auth.token}` } }
    )
    tables.value = response.data
    closeCreateTableModal()
  } catch (err) {
    console.error('Error creating table:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to create table'
  } finally {
    creating.value = false
  }
}

function openAddRowModal() {
  newRowData.value = {}
  tableColumns.value.forEach(col => {
    newRowData.value[col] = ''
  })
  showAddRowModal.value = true
}

function closeAddRowModal() {
  showAddRowModal.value = false
  newRowData.value = {}
}

function openEditRowModal(row, rowIndex) {
  editingRowData.value = { ...row }
  editingRowIndex.value = rowIndex
  // Find the row_id (assuming it's stored as 'id' column)
  editingRowId.value = row.id
  showEditRowModal.value = true
}

function closeEditRowModal() {
  showEditRowModal.value = false
  editingRowData.value = {}
  editingRowId.value = null
  editingRowIndex.value = null
}

async function addRow() {
  error.value = ''
  creating.value = true
  try {
    await axios.post(
      `${API}/databases/${selectedDatabase.value.id}/tables/${selectedTable.value}/rows`,
      { data: newRowData.value },
      { headers: { Authorization: `Bearer ${auth.token}` } }
    )

    // Refresh table data
    const response = await axios.get(
      `${API}/databases/${selectedDatabase.value.id}/tables/${selectedTable.value}/rows`,
      { headers: { Authorization: `Bearer ${auth.token}` } }
    )
    tableData.value = response.data
    closeAddRowModal()
  } catch (err) {
    console.error('Error adding row:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to add row'
  } finally {
    creating.value = false
  }
}

async function updateRow() {
  error.value = ''
  creating.value = true
  try {
    await axios.put(
      `${API}/databases/${selectedDatabase.value.id}/tables/${selectedTable.value}/rows/${editingRowId.value}`,
      { data: editingRowData.value },
      { headers: { Authorization: `Bearer ${auth.token}` } }
    )

    // Refresh table data
    const response = await axios.get(
      `${API}/databases/${selectedDatabase.value.id}/tables/${selectedTable.value}/rows`,
      { headers: { Authorization: `Bearer ${auth.token}` } }
    )
    tableData.value = response.data
    closeEditRowModal()
  } catch (err) {
    console.error('Error updating row:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to update row'
  } finally {
    creating.value = false
  }
}

async function deleteRow(rowId) {
  if (!confirm('Are you sure you want to delete this row?')) {
    return
  }

  error.value = ''
  creating.value = true
  try {
    await axios.delete(
      `${API}/databases/${selectedDatabase.value.id}/tables/${selectedTable.value}/rows/${rowId}`,
      { headers: { Authorization: `Bearer ${auth.token}` } }
    )

    // Refresh table data
    const response = await axios.get(
      `${API}/databases/${selectedDatabase.value.id}/tables/${selectedTable.value}/rows`,
      { headers: { Authorization: `Bearer ${auth.token}` } }
    )
    tableData.value = response.data
  } catch (err) {
    console.error('Error deleting row:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to delete row'
  } finally {
    creating.value = false
  }
}
</script>

<template>
  <main class="database-view">
    <h2>Database Manager</h2>

    <div v-if="error" class="alert alert-danger">{{ error }}</div>

    <div class="db-container">
      <!-- Databases List -->
      <div class="db-sidebar">
        <h3>Databases</h3>
        <button class="btn-create-database" @click="openCreateDatabaseModal">+ Create Database</button>
        <div v-if="loading && !selectedDatabase" class="loading">Loading...</div>
        <div v-else-if="databases.length === 0" class="no-data">No databases</div>
        <div v-else class="db-list">
          <div
            v-for="db in databases"
            :key="db.id"
            :class="['db-item', { active: selectedDatabase?.id === db.id }]"
            @click="selectDatabase(db)"
          >
            {{ db.name }}
          </div>
        </div>
      </div>

      <!-- Tables and Data -->
      <div class="db-content">
        <div v-if="!selectedDatabase" class="placeholder">
          Select a database to view its tables
        </div>

        <div v-else>
          <h3>{{ selectedDatabase.name }} - Tables</h3>
          <button class="btn-create-table" @click="openCreateTableModal">+ Create Table</button>

          <!-- Tables List -->
          <div class="tables-list">
            <div v-if="loading && !selectedTable" class="loading">Loading tables...</div>
            <div v-else-if="tables.length === 0" class="no-data">No tables in this database</div>
            <div v-else>
              <button
                v-for="tableName in tables"
                :key="tableName"
                :class="['table-btn', { active: selectedTable === tableName }]"
                @click="selectTable(tableName)"
              >
                {{ tableName }}
              </button>
            </div>
          </div>

          <!-- Table Data -->
          <div v-if="selectedTable" class="table-data">
            <h4>{{ selectedTable }}</h4>
            <button class="btn-create-table" @click="openAddRowModal">+ Add Row</button>
            <div v-if="loading" class="loading">Loading table data...</div>
            <div v-else-if="tableData.length === 0" class="no-data">No data in this table</div>
            <div v-else class="table-wrapper">
              <table class="data-table">
                <thead>
                  <tr>
                    <th v-for="col in tableColumns" :key="col">{{ col }}</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, idx) in tableData" :key="idx">
                    <td v-for="col in tableColumns" :key="col">{{ row[col] }}</td>
                    <td class="actions-cell">
                      <button class="btn-action btn-edit" @click="openEditRowModal(row, idx)">Edit</button>
                      <button class="btn-action btn-delete" @click="deleteRow(row.id)">Delete</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Table Modal -->
    <div v-if="showCreateTableModal" class="modal-overlay" @click="closeCreateTableModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Create New Table</h3>
          <button class="modal-close" @click="closeCreateTableModal">&times;</button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label for="table-name">Table Name:</label>
            <input
              id="table-name"
              v-model="newTableName"
              type="text"
              class="form-input"
              placeholder="Enter table name"
            />
          </div>

          <div class="form-group">
            <label>Columns:</label>
            <div v-for="(col, idx) in newTableColumns" :key="idx" class="column-row">
              <input
                v-model="col.name"
                type="text"
                class="form-input"
                placeholder="Column name"
              />
              <select v-model="col.type" class="form-select">
                <option value="TEXT">TEXT</option>
                <option value="INTEGER">INTEGER</option>
                <option value="REAL">REAL</option>
                <option value="BLOB">BLOB</option>
              </select>
              <button
                v-if="newTableColumns.length > 1"
                @click="removeColumn(idx)"
                class="btn-remove"
              >
                Remove
              </button>
            </div>
            <button @click="addColumn" class="btn-add-column">+ Add Column</button>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeCreateTableModal" class="btn-cancel">Cancel</button>
          <button @click="createTable" :disabled="creating" class="btn-submit">
            {{ creating ? 'Creating...' : 'Create Table' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Create Database Modal -->
    <div v-if="showCreateDatabaseModal" class="modal-overlay" @click="closeCreateDatabaseModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Create New Database</h3>
          <button class="modal-close" @click="closeCreateDatabaseModal">&times;</button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label for="database-name">Database Name:</label>
            <input
              id="database-name"
              v-model="newDatabaseName"
              type="text"
              class="form-input"
              placeholder="Enter database name"
            />
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeCreateDatabaseModal" class="btn-cancel">Cancel</button>
          <button @click="createDatabase" :disabled="creating" class="btn-submit">
            {{ creating ? 'Creating...' : 'Create Database' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Add Row Modal -->
    <div v-if="showAddRowModal" class="modal-overlay" @click="closeAddRowModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Add New Row</h3>
          <button class="modal-close" @click="closeAddRowModal">&times;</button>
        </div>

        <div class="modal-body">
          <div v-for="col in tableColumns" :key="col" class="form-group">
            <label :for="`add-${col}`">{{ col }}:</label>
            <input
              :id="`add-${col}`"
              v-model="newRowData[col]"
              type="text"
              class="form-input"
              :placeholder="`Enter ${col}`"
            />
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeAddRowModal" class="btn-cancel">Cancel</button>
          <button @click="addRow" :disabled="creating" class="btn-submit">
            {{ creating ? 'Adding...' : 'Add Row' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Row Modal -->
    <div v-if="showEditRowModal" class="modal-overlay" @click="closeEditRowModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Edit Row</h3>
          <button class="modal-close" @click="closeEditRowModal">&times;</button>
        </div>

        <div class="modal-body">
          <div v-for="col in tableColumns" :key="col" class="form-group">
            <label :for="`edit-${col}`">{{ col }}:</label>
            <input
              :id="`edit-${col}`"
              v-model="editingRowData[col]"
              type="text"
              class="form-input"
              :placeholder="`Enter ${col}`"
            />
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeEditRowModal" class="btn-cancel">Cancel</button>
          <button @click="updateRow" :disabled="creating" class="btn-submit">
            {{ creating ? 'Updating...' : 'Update Row' }}
          </button>
        </div>
      </div>
    </div>
  </main>
</template>

<style scoped>
.database-view {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

h2 { margin-bottom: 1.5rem; }
h3 { margin-bottom: 1rem; }
h4 { margin-top: 1rem; margin-bottom: 0.5rem; }

.alert {
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 4px;
  background-color: #f8d7da;
  color: #721c24;
}

.db-container {
  display: flex;
  gap: 2rem;
  height: calc(100vh - 200px);
}

.db-sidebar {
  width: 200px;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 1rem;
  background-color: rgba(255, 255, 255, 0.8);
  overflow-y: auto;
}

.db-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.db-item {
  padding: 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  background-color: white;
  transition: all 0.2s;
}

.db-item:hover {
  background-color: #f5f5f5;
}

.db-item.active {
  background-color: #0d6efd;
  color: white;
  border-color: #0d6efd;
}

.db-content {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 1rem;
  background-color: rgba(255, 255, 255, 0.8);
  overflow-y: auto;
}

.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  font-size: 1.1rem;
}

.no-data, .loading {
  padding: 1rem;
  text-align: center;
  color: #666;
}

.tables-list {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.table-btn {
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.table-btn:hover {
  background-color: #f5f5f5;
}

.table-btn.active {
  background-color: #0d6efd;
  color: white;
  border-color: #0d6efd;
}

.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
}

.data-table thead {
  background-color: #f8f9fa;
}

.data-table th, .data-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.data-table th {
  font-weight: 600;
  background-color: #f8f9fa;
}

.data-table tbody tr:hover {
  background-color: #f5f5f5;
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem !important;
}

.btn-action {
  padding: 0.35rem 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  transition: background-color 0.2s;
  white-space: nowrap;
}

.btn-edit {
  background-color: #0d6efd;
  color: white;
}

.btn-edit:hover {
  background-color: #0b5ed7;
}

.btn-delete {
  background-color: #dc3545;
  color: white;
}

.btn-delete:hover {
  background-color: #c82333;
}

.btn-create-database {
  width: 100%;
  padding: 0.5rem 1rem;
  margin-bottom: 1rem;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.btn-create-database:hover {
  background-color: #218838;
}

.btn-create-table {
  padding: 0.5rem 1rem;
  margin-bottom: 1rem;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.btn-create-table:hover {
  background-color: #218838;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #ddd;
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.form-input, .form-select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
  width: 100%;
  box-sizing: border-box;
}

.column-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  align-items: center;
}

.column-row .form-input {
  flex: 1;
}

.column-row .form-select {
  flex: 0 0 120px;
}

.btn-remove {
  padding: 0.5rem 0.75rem;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
  white-space: nowrap;
}

.btn-remove:hover {
  background-color: #c82333;
}

.btn-add-column {
  padding: 0.5rem 1rem;
  background-color: #17a2b8;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.btn-add-column:hover {
  background-color: #138496;
}

.btn-cancel {
  padding: 0.6rem 1.2rem;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-cancel:hover {
  background-color: #5a6268;
}

.btn-submit {
  padding: 0.6rem 1.2rem;
  background-color: #0d6efd;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-submit:hover:not(:disabled) {
  background-color: #0b5ed7;
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
