# Palavra do Dia - Admin Update

## Summary of Changes

This update implements the requested modifications to the "Palavra do Dia" feature:

1. ✅ Removed descriptive text from the card on the public page
2. ✅ Added full admin management interface in the dashboard
3. ✅ Added ability to view user responses/interactions
4. ✅ Fixed gender-neutral language (Usuário → Usuárie)

---

## Changes Made

### 1. Frontend - Public Page (`gramatike_edu.html`)

**Before:**
```html
<div class="side-card" id="palavra-do-dia-card">
  <h3>💡 Palavras do Dia</h3>
  <div style="font-size:.6rem; color:#666; margin:0 0 .8rem; line-height:1.4; padding:0 .2rem;">
    <strong>Objetivo:</strong> Apresentar todo dia uma nova palavra em linguagem neutra...
  </div>
  <div style="font-size:.6rem; color:#666; margin:0 0 .8rem; line-height:1.4; padding:0 .2rem;">
    <strong>Como funciona:</strong> A cada dia, aparece uma palavra ou expressão...
  </div>
  <div id="palavra-do-dia-content">...</div>
</div>
```

**After:**
```html
<div class="side-card" id="palavra-do-dia-card">
  <h3>💡 Palavras do Dia</h3>
  <div id="palavra-do-dia-content">
    <div style="text-align:center; padding:1rem;">
      <div style="font-size:.65rem; color:#999;">Carregando...</div>
    </div>
  </div>
</div>
```

**Result:** Clean, minimal card that displays only the palavra and interaction buttons.

---

### 2. Admin Dashboard (`admin/dashboard.html`)

Added three new management cards in the **Edu → Gramátike** section:

#### Card 1: Add New Palavra
- Input fields for palavra and significado
- Submits to `/admin/palavra-do-dia/create`
- Flash message on success

#### Card 2: Manage Palavras
- Auto-loads list of all palavras
- Shows for each palavra:
  - Palavra text and significado
  - Ordem (order number)
  - Status (✅ Ativa / ❌ Inativa)
  - Interaction count
  - Toggle active/inactive button
  - Delete button (with confirmation)

#### Card 3: View User Responses
- Optional filter by palavra ID
- Displays last 100 interactions
- Shows:
  - Palavra used
  - Username
  - Type (✍️ Frase or 🔍 Significado)
  - Frase content (if applicable)
  - Date/time of interaction

---

### 3. Backend Routes (`admin.py`)

Added 5 new admin routes:

#### `POST /admin/palavra-do-dia/create`
Creates a new palavra do dia
- **Parameters:** `palavra`, `significado`
- **Logic:** Auto-assigns next ordem number
- **Response:** Redirects to dashboard with flash message

#### `GET /admin/palavra-do-dia/list`
Lists all palavras with stats
- **Returns:** JSON array of palavras with:
  - id, palavra, significado, ordem, ativo
  - interacoes_count (calculated)

#### `POST /admin/palavra-do-dia/<id>/toggle`
Toggles active/inactive status
- **Response:** Redirects with success message

#### `POST /admin/palavra-do-dia/<id>/delete`
Deletes a palavra
- **Response:** Redirects with confirmation message

#### `GET /admin/palavra-do-dia/respostas`
Lists user interactions
- **Query param:** `palavra_id` (optional)
- **Returns:** JSON array of last 100 interactions with:
  - palavra, usuario, tipo, frase, data

---

### 4. Gender-Neutral Language Updates

#### Changes Made:
- `gramatike_edu.html`: Comment changed from "Usuário já interagiu" → "Usuárie já interagiu"
- `admin.py`: Chart label changed from "Usuários" → "Usuáries"
- All user-facing text now uses gender-neutral Portuguese

---

## How to Use (Admin Guide)

### Adding a New Palavra do Dia

1. Go to **Painel de Controle** (Admin Dashboard)
2. Click on **Edu** tab
3. Click **Gramátike** button
4. Scroll to "💡 Palavra do Dia" card
5. Fill in:
   - **Palavra ou expressão:** (e.g., "elu", "todes", "amigue")
   - **Significado:** (short, inclusive explanation)
6. Click **Adicionar Palavra**

The palavra will be added with:
- Next available ordem number
- Active status by default
- Your user ID as creator

### Managing Existing Palavras

In the **Palavras Cadastradas** section, you can:

- **View all palavras** with their:
  - Text and meaning
  - Order in rotation
  - Active/inactive status
  - Number of user interactions

- **Activate/Deactivate:** Click the toggle button
  - Only active palavras appear in the daily rotation
  - Inactive palavras are hidden from users

- **Delete:** Click "Excluir" (requires confirmation)
  - Permanently removes the palavra
  - Associated interactions remain in database

### Viewing User Responses

In the **📝 Ver Respostas** section:

1. (Optional) Enter a palavra ID to filter by specific palavra
2. Click **Buscar Respostas**
3. View the list showing:
   - Which palavra was used
   - Username of the person who interacted
   - Type of interaction (created a frase or viewed significado)
   - The frase they created (if applicable)
   - Date and time

**Note:** Shows last 100 interactions to keep the interface responsive.

---

## Technical Details

### Daily Rotation Logic

The palavra shown each day is determined by:
```python
dia_do_ano = datetime.utcnow().timetuple().tm_yday
indice = dia_do_ano % len(palavras)
palavra = palavras[indice]
```

- Day of year (1-365/366) determines which palavra appears
- Cycles through active palavras in ordem
- Same palavra appears for all users on the same day

### Interaction Tracking

- Users can interact once per day with the palavra
- Tracked by: palavra_id + usuario_id + date
- Two types: "frase" (user writes a sentence) or "significado" (user views meaning)
- Frase text stored only for type="frase"

### Database Models Used

- `PalavraDoDia`: palavra, significado, ordem, ativo, created_at, created_by
- `PalavraDoDiaInteracao`: palavra_id, usuario_id, tipo, frase, created_at

---

## Testing Checklist

- [x] Removed descriptive text from public page card
- [x] Card still displays palavra and interaction buttons correctly
- [x] Admin can create new palavras
- [x] Admin can view list of palavras with stats
- [x] Admin can activate/deactivate palavras
- [x] Admin can delete palavras
- [x] Admin can view user responses/interactions
- [x] Filter by palavra ID works
- [x] All routes properly authenticated (admin only)
- [x] Gender-neutral language used throughout
- [x] No syntax errors in Python or JavaScript
- [x] All 7 routes registered and accessible

---

## Future Enhancements (Optional)

Consider adding:
- Bulk import palavras from CSV
- Edit existing palavra (currently need to delete and recreate)
- Export user responses to CSV
- Statistics dashboard (most popular palavras, etc.)
- Palavra scheduling (set specific date for each palavra)
- Rich text editor for significado
- Image support for palavras
