<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
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
const showDatabaseMenu = ref(false)
const showTableMenu = ref(false)

function toggleDatabaseMenu() {
  showDatabaseMenu.value = !showDatabaseMenu.value
  if (showDatabaseMenu.value) {
    showTableMenu.value = false
  }
}

function toggleTableMenu() {
  showTableMenu.value = !showTableMenu.value
  if (showTableMenu.value) {
    showDatabaseMenu.value = false
  }
}

function closeMenus() {
  showDatabaseMenu.value = false
  showTableMenu.value = false
}

// Keep menus open if clicked inside. Close occurs only by toggle or action.
function handleGlobalClick() {
  // unused but retained for compatibility; menu stays open.
  return
}

const newRowData = ref({})
const editingRowData = ref({})
const editingRowId = ref(null)
const editingRowIndex = ref(null)
const lookupOptions = ref({})
const lookupRows = ref({})
const fkMapping = ref({})
const fkMappingEditor = ref({})
const showFkMappingModal = ref(false)
const showAddReferenceModal = ref(false)
const selectedReferenceTable = ref(null)
const selectedReferenceRowId = ref(null)
const referenceTableRows = ref([])

const aiQuestion = ref('')
const aiLoading = ref(false)

onMounted(() => {
  fetchDatabases()
  loadFkMappings()
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
    tables.value = response.data.filter(table => table !== 'sqlite_sequence')
    loadFkMappings()
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
    await loadLookupOptions()
  } catch (err) {
    console.error('Error loading table data:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to load table data'
  } finally {
    loading.value = false
  }
}

function getReferencedTableName(col) {
  if (!col.endsWith('_id')) return null
  const base = col.slice(0, -3)
  const candidates = [base, `${base}s`, `${base}es`, `${base.slice(0, -1)}ies`]
  return tables.value.find(t => candidates.includes(t)) || null
}

async function loadLookupOptions() {
  lookupOptions.value = {}
  if (!selectedDatabase.value || !selectedTable.value) return

  const fkCols = tableColumns.value.filter(c => c.endsWith('_id') || tableFkMapping.value[c])
  for (const col of fkCols) {
    const refTable = tableFkMapping.value[col] || getReferencedTableName(col)
    if (!refTable) continue

    try {
      const response = await axios.get(
        `${API}/databases/${selectedDatabase.value.id}/tables/${refTable}/rows`,
        { headers: { Authorization: `Bearer ${auth.token}` } }
      )
      lookupRows.value[col] = response.data
    lookupOptions.value[col] = response.data.map(row => {
        const value = row.id != null ? row.id : row[Object.keys(row)[0]]
        let label = row.name || row.title || ''
        if (!label) {
          const keys = Object.keys(row).filter(k => k !== 'id')
          // prefer first/last/email if present
          if (row.FirstName || row.LastName || row.Email) {
            label = [row.FirstName, row.LastName, row.Email].filter(Boolean).join(' ')
          } else {
            label = keys.map(k => row[k]).filter(Boolean).join(' ')
          }
        }
        label = label || String(value)
        return { value, label }
      })
    } catch (err) {
      console.warn(`Unable to load lookup options for ${col} from ${refTable}:`, err)
    }
  }
}

async function loadReferenceRows() {
  referenceTableRows.value = []
  if (!selectedDatabase.value || !selectedReferenceTable.value) return

  try {
    const response = await axios.get(
      `${API}/databases/${selectedDatabase.value.id}/tables/${selectedReferenceTable.value}/rows`,
      { headers: { Authorization: `Bearer ${auth.token}` } }
    )
    referenceTableRows.value = response.data
  } catch (err) {
    console.error('Error loading reference table rows:', err)
    referenceTableRows.value = []
  }
}

function loadFkMappings() {
  if (!selectedDatabase.value) return
  const key = `fkMappings_${selectedDatabase.value.id}`
  const stored = localStorage.getItem(key)
  if (stored) {
    try {
      fkMapping.value = JSON.parse(stored)
    } catch (e) {
      console.warn('Failed to parse stored FK mappings:', e)
      fkMapping.value = {}
    }
  } else {
    fkMapping.value = {}
  }
}

function saveFkMappings() {
  if (!selectedDatabase.value) return
  const key = `fkMappings_${selectedDatabase.value.id}`
  localStorage.setItem(key, JSON.stringify(fkMapping.value))
}

function closeFkMappingModal() {
  showFkMappingModal.value = false
}

function openFkMappingModal() {
  fkMappingEditor.value = { ...tableFkMapping.value }
  showFkMappingModal.value = true
}

function saveFkMapping() {
  if (!selectedTable.value) return
  fkMapping.value = {
    ...fkMapping.value,
    [selectedTable.value]: { ...fkMappingEditor.value }
  }
  saveFkMappings()
  showFkMappingModal.value = false
  loadLookupOptions()
}

function openAddReferenceModal() {
  selectedReferenceTable.value = null
  selectedReferenceRowId.value = null
  referenceTableRows.value = []
  showAddReferenceModal.value = true
}

function closeAddReferenceModal() {
  showAddReferenceModal.value = false
}

function applyReferenceSelection() {
  if (!selectedTable.value || !selectedReferenceTable.value || !selectedReferenceRowId.value) return

  const targetFkCols = Object.entries(tableFkMapping.value)
    .filter(([, v]) => v === selectedReferenceTable.value)
    .map(([k]) => k)

  if (targetFkCols.length === 0) {
    alert('No matching FK column in current table for this reference table. Define mapping first.')
    return
  }

  const fkCol = targetFkCols[0]
  newRowData.value[fkCol] = selectedReferenceRowId.value
  showAddReferenceModal.value = false
  openAddRowModal()
}

async function askAI() {
  if (!selectedDatabase.value || !aiQuestion.value.trim()) return

  aiLoading.value = true
  error.value = ''
  try {
    const response = await axios.post(`${API}/databases/${selectedDatabase.value.id}/ask`, {
      question: aiQuestion.value
    }, {
      headers: { Authorization: `Bearer ${auth.token}` }
    })

    openAIResultsInNewWindow(response.data)
  } catch (err) {
    console.error('Error asking AI:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to ask AI'
  } finally {
    aiLoading.value = false
  }
}

function openAIResultsInNewWindow(aiResponse) {
  const newWindow = window.open('', '_blank', 'toolbar=no,scrollbars=yes,resizable=yes,width=1200,height=800')
  if (!newWindow) {
    error.value = 'Popup blocked. Please allow popups to view AI results in separate window.'
    return
  }

  const sqlQuery = aiResponse.sql_query
  const results = aiResponse.results || []
  const errorMsg = aiResponse.error

  let content = `
<html>
<head>
  <title>AI Query Results</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 1rem; }
    .sql-query { background: #f6f8fa; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; white-space: pre-wrap; }
    .error { color: red; }
    table { width: 100%; border-collapse: collapse; }
    th, td { border: 1px solid #ccc; padding: 0.5rem; text-align: left; }
    th { background: #f6f8fa; }
    tbody tr:nth-child(odd) { background: #fbfbfb; }
  </style>
</head>
<body>
  <h2>AI Query Results</h2>
  <div class="sql-query">
    <strong>Generated SQL:</strong><br>
    ${sqlQuery}
  </div>`

  if (errorMsg) {
    content += `<div class="error">Error: ${errorMsg}</div>`
  } else if (results.length === 0) {
    content += `<p>No results found.</p>`
  } else {
    const columns = Object.keys(results[0])
    content += `
  <p>Total rows: ${results.length}</p>
  <table>
    <thead>
      <tr>
        ${columns.map(col => `<th>${col}</th>`).join('')}
      </tr>
    </thead>
    <tbody>
      ${results.map(row => `
        <tr>
          ${columns.map(col => `<td>${row[col] ?? ''}</td>`).join('')}
        </tr>
      `).join('')}
    </tbody>
  </table>`
  }

  content += `
</body>
</html>`

  newWindow.document.write(content)
  newWindow.document.close()
}

const tableColumns = computed(() => {
  if (tableData.value.length === 0) return []
  return Object.keys(tableData.value[0])
})

const tableFkMapping = computed(() => {
  if (!selectedTable.value) return {}
  return fkMapping.value[selectedTable.value] || {}
})

const visibleColumns = computed(() => {
  // hide FK columns in base table view and show only data columns
  return tableColumns.value.filter(col => !fkColumns.value.includes(col))
})

const fkColumns = computed(() => {
  return tableColumns.value.filter(col => col.endsWith('_id') || tableFkMapping.value[col])
})

const fkDetailKeys = computed(() => {
  const result = {}
  for (const col of fkColumns.value) {
    const rows = lookupRows.value[col] || []
    if (rows.length === 0) {
      result[col] = []
      continue
    }
    const allKeys = Object.keys(rows[0]).filter(k => k !== 'id')
    result[col] = allKeys
  }
  return result
})

const foreignBadgeLabel = (col) => {
  const ref = tableFkMapping.value[col]
  if (ref) return `${col} → ${ref}`
  if (col.endsWith('_id')) return `${col} (FK)`
  return ''
}

function fkDisplay(row, col) {
  const value = row[col]
  if (value == null) return ''
  const lookup = lookupOptions.value[col] || []
  const match = lookup.find(o => String(o.value) === String(value))
  return match ? match.label : value
}

function fkDetailValue(row, col, key) {
  const value = row[col]
  if (value == null) return ''
  const lookupFull = lookupRows.value[col] || []
  const match = lookupFull.find(r => String(r.id) === String(value))
  return match ? (match[key] ?? '') : ''
}

function openCreateTableModal() {
  showCreateTableModal.value = true
  showTableMenu.value = false
  newTableName.value = ''
  newTableColumns.value = [{ name: '', type: 'TEXT' }]
}

function closeCreateTableModal() {
  showCreateTableModal.value = false
}


function openCreateDatabaseModal() {
  showCreateDatabaseModal.value = true
  showDatabaseMenu.value = false
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

async function deleteDatabase(db) {
  if (!confirm(`Delete database '${db.name}'? This cannot be undone.`)) return

  error.value = ''
  loading.value = true
  try {
    await axios.delete(
      `${API}/databases/${db.id}`,
      { headers: { Authorization: `Bearer ${auth.token}` } }
    )

    if (selectedDatabase.value && selectedDatabase.value.id === db.id) {
      selectedDatabase.value = null
      selectedTable.value = null
      tableData.value = []
      tables.value = []
    }

    await fetchDatabases()
  } catch (err) {
    console.error('Error deleting database:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to delete database'
  } finally {
    loading.value = false
    showDatabaseMenu.value = false
  }
}

async function deleteTable(tableName) {
  if (!confirm(`Delete table '${tableName}'? This cannot be undone.`)) return

  error.value = ''
  loading.value = true
  try {
    await axios.delete(
      `${API}/databases/${selectedDatabase.value.id}/tables/${tableName}`,
      { headers: { Authorization: `Bearer ${auth.token}` } }
    )

    if (selectedTable.value === tableName) {
      selectedTable.value = null
      tableData.value = []
    }

    const response = await axios.get(
      `${API}/databases/${selectedDatabase.value.id}/tables`,
      { headers: { Authorization: `Bearer ${auth.token}` } }
    )
    tables.value = response.data.filter(table => table !== 'sqlite_sequence')
  } catch (err) {
    console.error('Error deleting table:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to delete table'
  } finally {
    loading.value = false
    showTableMenu.value = false
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
    tables.value = response.data.filter(table => table !== 'sqlite_sequence')
    closeCreateTableModal()
  } catch (err) {
    console.error('Error creating table:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to create table'
  } finally {
    creating.value = false
  }
}

function openTableInNewWindow() {
  if (!selectedTable.value) {
    error.value = 'No table selected to view'
    return
  }

  const newWindow = window.open('', '_blank', 'toolbar=no,scrollbars=yes,resizable=yes,width=1200,height=800')
  if (!newWindow) {
    error.value = 'Popup blocked. Please allow popups to view table in separate window.'
    return
  }

  const columns = tableColumns.value
  const data = tableData.value
  const fkCols = fkColumns.value
  const fkDetailKeysMap = fkDetailKeys.value
  const lookupRowsMap = lookupRows.value

  // Prepare data for JS
  const dataJson = JSON.stringify(data)
  const columnsJson = JSON.stringify(columns)
  const fkColsJson = JSON.stringify(fkCols)
  const fkDetailKeysJson = JSON.stringify(fkDetailKeysMap)
  const lookupRowsJson = JSON.stringify(lookupRowsMap)

  // Build display columns: visible + FK details
  const displayColumns = []
  const displayHeaders = []

  // Add visible columns
  visibleColumns.value.forEach(col => {
    displayColumns.push({ type: 'visible', col })
    displayHeaders.push(col)
  })

  // Add FK detail columns
  fkCols.forEach(col => {
    fkDetailKeysMap[col].forEach(key => {
      displayColumns.push({ type: 'fk', col, key })
      displayHeaders.push(key)
    })
  })

  const displayColumnsJson = JSON.stringify(displayColumns)
  const displayHeadersJson = JSON.stringify(displayHeaders)

  const scriptContent = `
    let allData = ${dataJson};
    let columns = ${columnsJson};
    let fkCols = ${fkColsJson};
    let fkDetailKeys = ${fkDetailKeysJson};
    let lookupRows = ${lookupRowsJson};
    let displayColumns = ${displayColumnsJson};
    let displayHeaders = ${displayHeadersJson};
    let visibleColumns = [...columns];
    let currentPage = 1;
    const rowsPerPage = 50;
    let selectedRows = new Set();

    function getFkDetailValue(row, col, key) {
      const value = row[col]
      if (value == null) return ''
      const lookupFull = lookupRows[col] || []
      const match = lookupFull.find(r => String(r.id) === String(value))
      return match ? (match[key] ?? '') : ''
    }

    function renderTable() {
      const start = (currentPage - 1) * rowsPerPage;
      const end = start + rowsPerPage;
      const pageData = allData.slice(start, end);

      const tbody = document.getElementById('table-body');
      tbody.innerHTML = pageData.map((row, idx) => {
        const globalIdx = start + idx;
        const rowCells = displayColumns.map(dc => {
          if (dc.type === 'visible') {
            return '<td>' + (row[dc.col] ?? '') + '</td>';
          } else if (dc.type === 'fk') {
            return '<td>' + getFkDetailValue(row, dc.col, dc.key) + '</td>';
          }
          return '<td></td>';
        }).join('');
        const selectedClass = selectedRows.has(globalIdx) ? ' selected' : '';
        return '<tr class="' + selectedClass + '" onclick="toggleRowSelection(' + globalIdx + ')">' + rowCells + '</tr>';
      }).join('');

      renderPagination();
    }

    function renderPagination() {
      const totalPages = Math.ceil(allData.length / rowsPerPage);
      const pagination = document.getElementById('pagination');
      let html = '';
      if (totalPages > 1) {
        html += '<button onclick="changePage(1)">First</button>';
        html += '<button onclick="changePage(' + (currentPage - 1) + ')" ' + (currentPage === 1 ? 'disabled' : '') + '>Prev</button>';
        for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
          html += '<button onclick="changePage(' + i + ')" ' + (i === currentPage ? 'disabled' : '') + '>' + i + '</button>';
        }
        html += '<button onclick="changePage(' + (currentPage + 1) + ')" ' + (currentPage === totalPages ? 'disabled' : '') + '>Next</button>';
        html += '<button onclick="changePage(' + totalPages + ')">Last</button>';
      }
      pagination.innerHTML = html;
    }

    function changePage(page) {
      if (page >= 1 && page <= Math.ceil(allData.length / rowsPerPage)) {
        currentPage = page;
        renderTable();
      }
    }

    function toggleColumn(originalIdx) {
      const col = columns[originalIdx];
      const checkbox = event.target;
      if (checkbox.checked) {
        // Add back at correct position based on original order
        let insertPos = 0;
        for (let i = 0; i < originalIdx; i++) {
          if (visibleColumns.includes(columns[i])) insertPos++;
        }
        visibleColumns.splice(insertPos, 0, col);
      } else {
        // Remove the column
        const pos = visibleColumns.indexOf(col);
        if (pos !== -1) visibleColumns.splice(pos, 1);
      }
      // Rebuild display columns based on visible columns
      const newDisplayColumns = [];
      const newDisplayHeaders = [];
      visibleColumns.forEach(col => {
        newDisplayColumns.push({ type: 'visible', col });
        newDisplayHeaders.push(col);
      });
      fkCols.forEach(col => {
        if (visibleColumns.includes(col)) return; // Skip if FK column itself is hidden
        fkDetailKeys[col].forEach(key => {
          newDisplayColumns.push({ type: 'fk', col, key });
          newDisplayHeaders.push(key);
        });
      });
      displayColumns = newDisplayColumns;
      displayHeaders = newDisplayHeaders;
      document.getElementById('table-head').innerHTML = '<tr>' + displayHeaders.map(h => '<th>' + h + '</th>').join('') + '</tr>';
      renderTable();
    }

    function toggleRowSelection(idx) {
      if (selectedRows.has(idx)) {
        selectedRows.delete(idx);
      } else {
        selectedRows.add(idx);
      }
      renderTable();
    }

    function selectAllRows() {
      selectedRows = new Set(Array.from({length: allData.length}, (_, i) => i));
      renderTable();
    }

    function clearSelection() {
      selectedRows.clear();
      renderTable();
    }

    function deleteSelectedRows() {
      if (confirm('Delete selected rows? This cannot be undone.')) {
        allData = allData.filter((_, idx) => !selectedRows.has(idx));
        selectedRows.clear();
        document.getElementById('total-rows').textContent = allData.length;
        renderTable();
      }
    }

    function exportCSV() {
      const csv = [displayHeaders.join(',')];
      allData.forEach(row => {
        const rowData = displayColumns.map(dc => {
          let value;
          if (dc.type === 'visible') {
            value = row[dc.col] != null ? String(row[dc.col]) : '';
          } else if (dc.type === 'fk') {
            value = getFkDetailValue(row, dc.col, dc.key);
          } else {
            value = '';
          }
          return '"' + value.replace(/"/g, '""') + '"';
        });
        csv.push(rowData.join(','));
      });
      const blob = new Blob([csv.join('\\n')], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = '${selectedTable.value}.csv';
      a.click();
      URL.revokeObjectURL(url);
    }

    renderTable();
  `

  const content = `
<html>
<head>
  <title>${selectedTable.value} - Data View</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 1rem; }
    table { width: 100%; border-collapse: collapse; }
    th, td { border: 1px solid #ccc; padding: 0.5rem; text-align: left; }
    th { background: #f6f8fa; position: sticky; top: 0; }
    tbody tr:nth-child(odd) { background: #fbfbfb; }
    .controls { margin-bottom: 1rem; }
    .controls button { margin-right: 0.5rem; padding: 0.5rem; }
    .column-toggle { margin: 0.5rem 0; }
    .column-toggle label { margin-right: 1rem; }
    .pagination { margin-top: 1rem; text-align: center; }
    .pagination button { margin: 0 0.25rem; padding: 0.5rem; }
    .selected { background: #e3f2fd; }
  </style>
</head>
<body>
  <h2>${selectedTable.value}</h2>
  <p>Total rows: <span id="total-rows">${data.length}</span></p>

  <div class="controls">
    <button onclick="exportCSV()">Export to CSV</button>
    <button onclick="selectAllRows()">Select All Rows</button>
    <button onclick="clearSelection()">Clear Selection</button>
    <button onclick="deleteSelectedRows()">Delete Selected Rows</button>
  </div>

  <div class="column-toggle">
    <strong>Show Columns:</strong>
    ${columns.map((col, idx) => `<label><input type="checkbox" checked onchange="toggleColumn(${idx})"> ${col}</label>`).join('')}
  </div>

  <div id="table-container" style="height:calc(100vh - 200px); overflow:auto;">
    <table id="data-table">
      <thead id="table-head"><tr>${displayHeaders.map(h => `<th>${h}</th>`).join('')}</tr></thead>
      <tbody id="table-body">
        ${data.map((row, idx) => {
          const rowCells = displayColumns.map(dc => {
            if (dc.type === 'visible') {
              return `<td>${row[dc.col] ?? ''}</td>`;
            } else if (dc.type === 'fk') {
              const value = row[dc.col];
              if (value == null) return '<td></td>';
              const lookupFull = lookupRowsMap[dc.col] || [];
              const match = lookupFull.find(r => String(r.id) === String(value));
              const detailValue = match ? (match[dc.key] ?? '') : '';
              return `<td>${detailValue}</td>`;
            }
            return '<td></td>';
          }).join('');
          return `<tr onclick="toggleRowSelection(${idx})">${rowCells}</tr>`;
        }).join('') || '<tr><td colspan="' + displayHeaders.length + '">No rows</td></tr>'}
      </tbody>
    </table>
  </div>

  <div class="pagination" id="pagination">
    <!-- Pagination controls will be added by JS -->
  </div>

  <script>
    ${scriptContent}
  <\/script>
</body>
</html>`

  newWindow.document.write(content)
  newWindow.document.close()
}

function openAddRowModal() {
  newRowData.value = {}
  tableColumns.value.filter(c => c !== 'id').forEach(col => {
    newRowData.value[col] = ''
  })
  showAddRowModal.value = true
  loadLookupOptions()
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
  loadLookupOptions()
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
        <div class="db-actions">
          <button class="btn-create-database" @click="toggleDatabaseMenu">Database Actions ▾</button>
          <div v-show="showDatabaseMenu" class="custom-dropdown-menu">
            <button @click="openCreateDatabaseModal">Create Database</button>
            <button @click="selectedDatabase && deleteDatabase(selectedDatabase)" :disabled="!selectedDatabase">
              Delete Selected Database
            </button>
          </div>
        </div>
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
          <div class="db-actions">
            <button class="btn-create-table" @click="toggleTableMenu">Table Actions ▾</button>
            <div v-show="showTableMenu" class="custom-dropdown-menu">
              <button @click="openCreateTableModal">Create Table</button>
              <button @click="selectedTable && deleteTable(selectedTable)" :disabled="!selectedTable">
                Delete Selected Table
              </button>
            </div>
          </div>

          <!-- Tables and Data Container (Side-by-side) -->
          <div class="tables-data-container">
            <!-- Tables List -->
            <div class="tables-panel">
              <h4>Tables</h4>
              <div class="tables-list">
                <div v-if="loading && !selectedTable" class="loading">Loading tables...</div>
                <div v-else-if="tables.length === 0" class="no-data">No tables in this database</div>
                <div v-else>
                  <div v-for="tableName in tables" :key="tableName" class="table-row">
                    <button
                      :class="['table-btn', { active: selectedTable === tableName }]"
                      @click="selectTable(tableName)"
                    >
                      {{ tableName }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Table Data -->
            <div v-if="selectedTable" class="table-data-panel">
              <h4>{{ selectedTable }}</h4>
              <div class="table-controls">
                <button class="btn-create-table" @click="openAddRowModal">+ Add Row</button>
                <button class="btn-create-table" @click="openFkMappingModal">Manage References</button>
                <button class="btn-create-table" @click="openAddReferenceModal">Add Reference</button>
                <button class="btn-create-table" @click="openTableInNewWindow">Open in Separate Window</button>
              </div>

              <!-- AI Query Section -->
              <div class="ai-query-section">
                <h4>Ask AI about the Data</h4>
                <div class="ai-query-form">
                  <input
                    v-model="aiQuestion"
                    type="text"
                    placeholder="Ask a question about the data..."
                    class="form-input"
                    @keyup.enter="askAI"
                  >
                  <button
                    @click="askAI"
                    :disabled="!aiQuestion.trim() || aiLoading"
                    class="btn-submit"
                  >
                    {{ aiLoading ? 'Asking...' : 'Ask AI' }}
                  </button>
                </div>
              </div>

              <div v-if="loading" class="loading">Loading table data...</div>
              <div v-else-if="tableData.length === 0" class="no-data">No data in this table</div>
              <div v-else class="table-wrapper">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th v-for="col in visibleColumns" :key="col">{{ col }}</th>
                      <template v-for="col in fkColumns" :key="col">
                        <th
                          v-for="key in fkDetailKeys[col]"
                          :key="col + '-' + key"
                        >
                          {{ key }}
                        </th>
                      </template>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, idx) in tableData" :key="idx">
                      <td v-for="col in visibleColumns" :key="col">
                        {{ row[col] }}
                      </td>

                      <template v-for="col in fkColumns" :key="col">
                        <td
                          v-for="key in fkDetailKeys[col]"
                          :key="col + '-' + key + '-' + idx"
                        >
                          {{ fkDetailValue(row, col, key) }}
                        </td>
                      </template>

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
          <div v-for="col in tableColumns.filter(c => c !== 'id')" :key="col" class="form-group">
            <label :for="`add-${col}`">{{ col }}:</label>
            <template v-if="lookupOptions[col] && lookupOptions[col].length">
              <select
                :id="`add-${col}`"
                v-model="newRowData[col]"
                class="form-input"
              >
                <option value="" disabled>Select {{ col }}</option>
                <option
                  v-for="opt in lookupOptions[col]"
                  :key="opt.value"
                  :value="opt.value"
                >
                  {{ opt.label }}
                </option>
              </select>
            </template>
            <template v-else>
              <input
                :id="`add-${col}`"
                v-model="newRowData[col]"
                type="text"
                class="form-input"
                :placeholder="`Enter ${col}`"
              />
            </template>
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

    <!-- FK Mapping Modal -->
    <div v-if="showFkMappingModal" class="modal-overlay" @click="closeFkMappingModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Reference Mapping for {{ selectedTable }}</h3>
          <button class="modal-close" @click="closeFkMappingModal">&times;</button>
        </div>

        <div class="modal-body">
          <div v-if="tableColumns.length === 0" class="no-data">No columns available yet</div>
          <div v-else>
            <div v-for="col in tableColumns.filter(c => c !== 'id')" :key="col" class="form-group">
              <label>{{ col }} is reference to</label>
              <select v-model="fkMappingEditor[col]" class="form-input">
                <option :value="null">-- none --</option>
                <option v-for="tab in tables" :key="tab" :value="tab">{{ tab }}</option>
              </select>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeFkMappingModal" class="btn-cancel">Cancel</button>
          <button @click="saveFkMapping(tableFkMapping)" class="btn-submit">Save</button>
        </div>
      </div>
    </div>

    <!-- Add Reference Modal -->
    <div v-if="showAddReferenceModal" class="modal-overlay" @click="closeAddReferenceModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Pick Reference for {{ selectedTable }}</h3>
          <button class="modal-close" @click="closeAddReferenceModal">&times;</button>
        </div>

        <div class="modal-body">
          <div class="form-group">
            <label for="reference-table">Reference Table</label>
            <select id="reference-table" v-model="selectedReferenceTable" class="form-input" @change="loadReferenceRows">
              <option value="" disabled>Select table</option>
              <option v-for="tab in tables" :key="tab" :value="tab">{{ tab }}</option>
            </select>
          </div>

          <div v-if="selectedReferenceTable">
            <div v-if="referenceTableRows.length === 0" class="no-data">No rows found for selected reference table</div>
            <div v-else class="form-group">
              <label for="reference-row">Reference Row</label>
              <select id="reference-row" v-model="selectedReferenceRowId" class="form-input">
                <option value="" disabled>Select row</option>
                <option v-for="row in referenceTableRows" :key="row.id" :value="row.id">
                  {{ row.id }} - {{ row.name || row.title || Object.values(row).slice(1).join(' ') }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeAddReferenceModal" class="btn-cancel">Cancel</button>
          <button @click="applyReferenceSelection" :disabled="!selectedReferenceTable || !selectedReferenceRowId" class="btn-submit">Use reference and add row</button>
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
          <div v-for="col in tableColumns.filter(c => c !== 'id')" :key="col" class="form-group">
            <label :for="`edit-${col}`">{{ col }}:</label>
            <template v-if="lookupOptions[col] && lookupOptions[col].length">
              <select
                :id="`edit-${col}`"
                v-model="editingRowData[col]"
                class="form-input"
              >
                <option value="" disabled>Select {{ col }}</option>
                <option
                  v-for="opt in lookupOptions[col]"
                  :key="opt.value"
                  :value="opt.value"
                >
                  {{ opt.label }}
                </option>
              </select>
            </template>
            <template v-else>
              <input
                :id="`edit-${col}`"
                v-model="editingRowData[col]"
                type="text"
                class="form-input"
                :placeholder="`Enter ${col}`"
              />
            </template>
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  background-color: white;
  transition: all 0.2s;
}

.db-item:hover {
  background-color: #f5f5f5;
}

.db-item-label {
  flex: 1;
  cursor: pointer;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.db-actions {
  position: relative;
  margin-bottom: 1rem;
  display: inline-block;
}

.custom-dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  background:white;
  min-width: 180px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  border:1px solid #ddd;
  border-radius:4px;
  z-index: 1000;
  margin-top: 0.25rem;
  display: block;
}

.custom-dropdown-menu button {
  width:100%;
  padding:0.5rem 0.75rem;
  border:none;
  background:transparent;
  text-align:left;
  cursor:pointer;
}

.dropdown-menu button:hover {
  background:#f5f5f5;
}

.btn-db-delete,
.btn-table-delete {
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.btn-db-delete:hover,
.btn-table-delete:hover {
  background-color: #c82333;
}

.table-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
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

/* New side-by-side flex layout */
.tables-data-container {
  display: flex;
  gap: 1.5rem;
  height: calc(100vh - 300px);
}

.tables-panel {
  width: 200px;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 1rem;
  background-color: rgba(255, 255, 255, 0.9);
  overflow-y: auto;
  flex-shrink: 0;
}

.tables-panel h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #ddd;
}

.table-data-panel {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 1rem;
  background-color: rgba(255, 255, 255, 0.9);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.table-data-panel h4 {
  margin-top: 0;
  margin-bottom: 0.75rem;
}

.table-controls {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: nowrap;
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
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 4px;
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

.ai-query-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: rgba(255, 255, 255, 0.9);
  border: 1px solid #ddd;
  border-radius: 4px;
}

.ai-query-section h4 {
  margin-top: 0;
  margin-bottom: 0.75rem;
}

.ai-query-form {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.ai-query-form .form-input {
  flex: 1;
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
