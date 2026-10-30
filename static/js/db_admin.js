// ========================================================
// TubeFlow - MySQL Database Admin & Query Console Controller
// ========================================================

function setQuery(sql) {
  const queryInput = document.getElementById("sqlQueryInput");
  if (queryInput) {
    queryInput.value = sql;
    executeQuery();
  }
}

function loadTableQuery(tableName) {
  setQuery(`SELECT * FROM ${tableName} LIMIT 50;`);
}

document.addEventListener("DOMContentLoaded", () => {
  const testBtn = document.getElementById("testConnBtn");
  const configForm = document.getElementById("mysqlConfigForm");
  const runBtn = document.getElementById("runQueryBtn");

  if (testBtn) {
    testBtn.addEventListener("click", testMySQLConnection);
  }

  if (configForm) {
    configForm.addEventListener("submit", switchMySQLConnection);
  }

  if (runBtn) {
    runBtn.addEventListener("click", executeQuery);
  }

  // Run initial query on page load to populate table preview
  executeQuery();
});

// Test Connection
async function testMySQLConnection() {
  const host = document.getElementById("cfgHost").value.trim();
  const port = parseInt(document.getElementById("cfgPort").value.trim() || "3306", 10);
  const user = document.getElementById("cfgUser").value.trim();
  const password = document.getElementById("cfgPassword").value;
  const database = document.getElementById("cfgDatabase").value.trim();
  const resBox = document.getElementById("connResultBox");

  resBox.style.display = "block";
  resBox.style.background = "rgba(62, 166, 255, 0.1)";
  resBox.style.color = "#93c5fd";
  resBox.style.border = "1px solid #1e3a8a";
  resBox.textContent = `Pinging MySQL at ${host}:${port}...`;

  try {
    const res = await fetch("/api/db/test-connection", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ host, port, user, password, database })
    });
    const data = await res.json();
    if (data.success) {
      resBox.style.background = "rgba(34, 197, 94, 0.15)";
      resBox.style.color = "#4ade80";
      resBox.style.border = "1px solid #166534";
      resBox.innerHTML = `<strong>Success!</strong> ${data.message}. Databases on host: ${data.databases.join(", ")}`;
      showToast("MySQL Connection Successful!");
    } else {
      resBox.style.background = "rgba(239, 68, 68, 0.15)";
      resBox.style.color = "#f87171";
      resBox.style.border = "1px solid #991b1b";
      resBox.innerHTML = `<strong>Failed:</strong> ${data.message}`;
      showToast("MySQL Connection Failed", true);
    }
  } catch (err) {
    resBox.style.background = "rgba(239, 68, 68, 0.15)";
    resBox.style.color = "#f87171";
    resBox.innerHTML = `<strong>Error:</strong> ${err.message}`;
  }
}

// Switch Connection & Migrate
async function switchMySQLConnection(e) {
  e.preventDefault();

  const host = document.getElementById("cfgHost").value.trim();
  const port = parseInt(document.getElementById("cfgPort").value.trim() || "3306", 10);
  const user = document.getElementById("cfgUser").value.trim();
  const password = document.getElementById("cfgPassword").value;
  const database = document.getElementById("cfgDatabase").value.trim();
  const migrate = document.getElementById("cfgMigrate").checked;
  const resBox = document.getElementById("connResultBox");

  resBox.style.display = "block";
  resBox.style.background = "rgba(62, 166, 255, 0.1)";
  resBox.style.color = "#93c5fd";
  resBox.style.border = "1px solid #1e3a8a";
  resBox.textContent = `Connecting to MySQL & migrating relational schema...`;

  try {
    const res = await fetch("/api/db/switch-mysql", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ host, port, user, password, database, migrate_data: migrate })
    });
    const data = await res.json();
    if (res.ok && data.success) {
      resBox.style.background = "rgba(34, 197, 94, 0.15)";
      resBox.style.color = "#4ade80";
      resBox.style.border = "1px solid #166534";
      const migInfo = data.migrated_tables ? `Migrated: ${data.migrated_tables.join(", ")}` : "";
      resBox.innerHTML = `<strong>Success!</strong> ${data.message} <br>${migInfo}`;
      showToast("Switched live to MySQL!");
      setTimeout(() => window.location.reload(), 1200);
    } else {
      resBox.style.background = "rgba(239, 68, 68, 0.15)";
      resBox.style.color = "#f87171";
      resBox.style.border = "1px solid #991b1b";
      resBox.innerHTML = `<strong>Switch Failed:</strong> ${data.detail || data.message || "Unknown error"}`;
      showToast("Switch failed", true);
    }
  } catch (err) {
    resBox.style.background = "rgba(239, 68, 68, 0.15)";
    resBox.style.color = "#f87171";
    resBox.innerHTML = `<strong>Error:</strong> ${err.message}`;
  }
}

// Execute Raw SQL Query
async function executeQuery() {
  const queryInput = document.getElementById("sqlQueryInput");
  const metricText = document.getElementById("queryMetricText");
  const container = document.getElementById("queryResultContainer");
  const thead = document.getElementById("queryResultHead");
  const tbody = document.getElementById("queryResultBody");

  if (!queryInput || !container || !thead || !tbody) return;

  const sql = queryInput.value.trim();
  if (!sql) return;

  metricText.textContent = "Executing query...";

  try {
    const res = await fetch("/api/db/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sql })
    });
    const data = await res.json();

    if (data.success) {
      metricText.innerHTML = `<span style="color: #4ade80;">&#10003; Success:</span> ${data.row_count} rows returned in <strong>${data.duration_ms} ms</strong>`;
      
      // Render columns
      thead.innerHTML = "";
      tbody.innerHTML = "";

      if (data.columns && data.columns.length > 0) {
        const headerRow = document.createElement("tr");
        data.columns.forEach(col => {
          const th = document.createElement("th");
          th.textContent = col;
          headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);

        // Render rows
        data.rows.forEach(row => {
          const tr = document.createElement("tr");
          row.forEach(val => {
            const td = document.createElement("td");
            td.textContent = val !== null && val !== undefined ? String(val) : "NULL";
            tr.appendChild(td);
          });
          tbody.appendChild(tr);
        });
        container.style.display = "block";
      } else {
        container.style.display = "none";
        metricText.innerHTML += ` &bull; ${data.message || 'Statement completed.'}`;
      }
    } else {
      metricText.innerHTML = `<span style="color: #ef4444;">&#10007; Query Error (${data.duration_ms} ms):</span> ${data.error}`;
      container.style.display = "none";
    }
  } catch (err) {
    metricText.innerHTML = `<span style="color: #ef4444;">Execution Error:</span> ${err.message}`;
  }
}
