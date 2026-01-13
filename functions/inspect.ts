// functions/inspect.ts
export const onRequestGet = async ({ env }) => {
  try {
    // Verificar todas as tabelas e colunas
    const tables = await env.DB.prepare(
      "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).all();
    
    let html = '<h1>📊 Database Inspection</h1>';
    
    for (const table of tables.results) {
      // Colunas
      const columns = await env.DB.prepare(
        `PRAGMA table_info(${table.name})`
      ).all();
      
      // Contar registros
      const count = await env.DB.prepare(
        `SELECT COUNT(*) as total FROM ${table.name}`
      ).first();
      
      html += `
        <h2>📁 ${table.name} (${count?.total || 0} registros)</h2>
        <table border="1" cellpadding="8">
          <tr>
            <th>#</th>
            <th>Nome</th>
            <th>Tipo</th>
            <th>NotNull</th>
            <th>Default</th>
            <th>Primary Key</th>
          </tr>
      `;
      
      columns.results.forEach((col, i) => {
        html += `
          <tr>
            <td>${i + 1}</td>
            <td><strong>${col.name}</strong></td>
            <td>${col.type}</td>
            <td>${col.notnull ? '✅' : '❌'}</td>
            <td>${col.dflt_value || '-'}</td>
            <td>${col.pk ? '🔑' : ''}</td>
          </tr>
        `;
      });
      
      html += '</table>';
      
      // Mostrar alguns dados (se tiver)
      if (count?.total > 0 && count.total < 100) {
        const data = await env.DB.prepare(
          `SELECT * FROM ${table.name} LIMIT 5`
        ).all();
        
        html += `<h3>📝 Sample Data (first 5):</h3>
                <pre>${JSON.stringify(data.results, null, 2)}</pre>`;
      }
    }
    
    return new Response(html, {
      headers: { 'Content-Type': 'text/html' }
    });
    
  } catch (error: any) {
    return new Response(`
      <h1>❌ Inspection Error</h1>
      <pre>${error.message}</pre>
      <p>${error.stack}</p>
    `, {
      status: 500,
      headers: { 'Content-Type': 'text/html' }
    });
  }
};
