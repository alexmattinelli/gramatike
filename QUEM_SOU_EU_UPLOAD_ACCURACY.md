# "Quem Sou Eu" Dynamics - Photo Upload & Accuracy Tracking

## 📋 Overview

This document describes the enhancements made to the "Quem sou eu?" dynamics system, including photo upload functionality, improved form styling, and accuracy tracking for admin users.

## ✨ Features Implemented

### 1. 📸 Photo Upload

**Previous Behavior:**
- Users had to paste photo URLs manually
- Required external hosting for images

**New Behavior:**
- Direct file upload via `<input type="file">`
- Automatic upload to Supabase Storage
- Photos stored in organized path: `dinamicas/<user_id>/<timestamp>_<filename>`
- Preview link shown for existing photos in edit mode

**Technical Details:**
- Added `build_dinamica_image_path()` helper function in `storage.py`
- Form uses `enctype="multipart/form-data"`
- Backend processes `foto_<item_id>` file inputs
- Fallback to existing URL if no new upload

**Files Modified:**
- `gramatike_app/utils/storage.py` - Added helper function
- `gramatike_app/templates/dinamicas.html` - Updated create form
- `gramatike_app/templates/dinamica_edit.html` - Updated edit form
- `gramatike_app/routes/__init__.py` - Added upload handling

### 2. 🎨 Reset Password Form Styling

**Previous Design:**
- Simple labels and inputs
- Basic styling
- No password visibility toggle

**New Design:**
- Modern card with rounded corners and shadow
- Structured labels with uppercase descriptive text
- Password visibility toggle (👁 / 🙈)
- Improved color scheme matching app design
- Better spacing and hover effects

**Key Styling Changes:**
```css
/* Label Structure */
label {
  display: grid;
  gap: .4rem;
}
label span {
  font-size: .75rem;
  font-weight: 700;
  color: #666;
  text-transform: uppercase;
}

/* Input Styling */
input[type="password"] {
  padding: .75rem .85rem;
  border: 1px solid #cfd7e2;
  border-radius: 10px;
  transition: border .2s;
}
input[type="password"]:focus {
  border-color: #9B5DE5;
}

/* Card */
.card {
  border-radius: 20px;
  box-shadow: 0 10px 30px -6px rgba(0,0,0,.15);
}
```

**Files Modified:**
- `gramatike_app/templates/reset_senha.html` - Complete redesign

### 3. 📊 Accuracy Rate Tracking (Admin Only)

**New Feature:**
- Admins can set expected "correct answer" for each item
- System calculates accuracy statistics
- Displays overall and per-item accuracy
- Only visible to admin users

**Components:**

#### A. Correct Answer Field
- Added to create and edit forms
- Optional field: `resposta_correta`
- Stored in config JSON per item
- Used for accuracy calculation

#### B. Accuracy Calculation
- Compares user responses to `resposta_correta`
- Case-insensitive matching
- Calculates per-item accuracy: `(correct_count / total_responses) * 100`
- Calculates overall accuracy: average of all item accuracies

#### C. Admin View Display
Shows:
- **Overall Accuracy Card:**
  - Large percentage in purple card
  - "Taxa de Acertos Geral"
  
- **Per-Item Breakdown:**
  - Item number and type
  - Individual accuracy percentage
  - Item content preview
  - Expected answer
  - Count of correct responses (e.g., "12 de 15 acertaram")

**Example Display:**
```
Taxa de Acertos
┌──────────────────────────────┐
│           85.5%              │
│    Taxa de Acertos Geral     │
└──────────────────────────────┘

Por Item:

┌──────────────────────────────┐
│ Item 1   [frase]       92.3% │
│ "Eu me identifico como..."   │
│ Resposta correta: não-binário│
│ 12 de 13 acertaram           │
└──────────────────────────────┘

┌──────────────────────────────┐
│ Item 2   [foto]        78.6% │
│ Foto: ver imagem             │
│ Resposta correta: masculino  │
│ 11 de 14 acertaram           │
└──────────────────────────────┘
```

**Files Modified:**
- `gramatike_app/templates/dinamicas.html` - Added resposta_correta field
- `gramatike_app/templates/dinamica_edit.html` - Added resposta_correta field
- `gramatike_app/templates/dinamica_admin.html` - Added accuracy display
- `gramatike_app/routes/__init__.py` - Added accuracy calculation logic

## 🔧 Technical Implementation

### Storage Helper Function
```python
def build_dinamica_image_path(user_id: int, filename: str) -> str:
    """
    Gera um caminho de upload para imagens de dinâmicas
    """
    ts = int(time.time())
    safe_name = filename.replace(' ', '_')
    return f"dinamicas/{user_id}/{ts}_{safe_name}"
```

### Upload Processing (Create)
```python
if item_tipo == 'foto':
    foto_key = f'foto_{item_id}'
    if foto_key in request.files and request.files[foto_key].filename:
        file = request.files[foto_key]
        file_data = file.read()
        file_path = build_dinamica_image_path(current_user.id, file.filename)
        url = upload_bytes_to_supabase(file_path, file_data, file.content_type)
        if url:
            conteudo = url
```

### Accuracy Calculation
```python
# Per-item accuracy
for item in items:
    resposta_correta = item.get('resposta_correta', '').strip().lower()
    if resposta_correta:
        correct_count = 0
        for row in rows:
            respostas = row['payload'].get('respostas', [])
            item_idx = next((i for i, it in enumerate(items) 
                           if it.get('id') == item_id), None)
            if item_idx is not None and item_idx < len(respostas):
                resposta_usuario = respostas[item_idx].strip().lower()
                if resposta_usuario == resposta_correta:
                    correct_count += 1
        
        accuracy = (correct_count / total_responses) * 100
        item_stats.append({
            'accuracy': accuracy,
            'correct_count': correct_count,
            'total': total_responses,
            # ... other fields
        })

# Overall accuracy
overall_accuracy = sum(s['accuracy'] for s in item_stats) / len(item_stats)
```

### Data Structure

**Config JSON with Correct Answers:**
```json
{
  "questao_tipo": "gênero",
  "moral": "Mensagem final...",
  "items": [
    {
      "id": 1,
      "tipo": "frase",
      "conteudo": "Eu me identifico como...",
      "resposta_correta": "não-binário"
    },
    {
      "id": 2,
      "tipo": "foto",
      "conteudo": "https://supabase.co/storage/v1/object/public/avatars/dinamicas/123/1728591234_image.jpg",
      "resposta_correta": "masculino"
    }
  ]
}
```

**Response Payload:**
```json
{
  "respostas": [
    "não-binário",
    "masculino",
    "feminino"
  ]
}
```

## 📝 Usage Guide

### For Admins Creating Dynamics

1. **Navigate to Dinâmicas:**
   - Go to `/dinamicas`
   - Click "Criar dinâmica"

2. **Select Type:**
   - Choose "Quem sou eu?" from dropdown

3. **Configure Dynamic:**
   - Enter título and descrição
   - Fill "O que a pessoa deve descobrir?" (e.g., "gênero")
   - Write moral/message

4. **Add Items:**
   - Click "+ Item (Frase ou Foto)"
   - Choose type: Frase or Foto
   - For Frase: Enter text
   - For Foto: Upload image file
   - *Optional:* Enter "Resposta Correta" for accuracy tracking

5. **Submit:**
   - Click "Criar"
   - Dynamic is created with uploaded photos

### For Admins Viewing Accuracy

1. **Navigate to Admin View:**
   - Go to `/dinamicas/<id>/admin`

2. **View Statistics:**
   - See overall accuracy percentage
   - Review per-item breakdown
   - Check which items had most/least correct answers

3. **Analyze Results:**
   - Identify confusing items (low accuracy)
   - Validate expected answers are clear
   - Consider editing items if accuracy is unexpectedly low

### For Admins Editing Dynamics

1. **Open Edit:**
   - Click "Editar" on dynamic

2. **Update Items:**
   - Change frase text or upload new foto
   - Update "Resposta Correta" if needed
   - Add or remove items

3. **Save Changes:**
   - Click "Salvar alterações"
   - New photos replace old ones
   - Accuracy stats recalculate on next view

## 🧪 Testing Checklist

See `TESTING_CHECKLIST.md` for comprehensive testing guide.

**Key Tests:**
- [ ] Photo upload in create form
- [ ] Photo upload in edit form
- [ ] Photo display in dynamic view
- [ ] Reset password form styling
- [ ] Password visibility toggle
- [ ] Accuracy calculation with all correct
- [ ] Accuracy calculation with all wrong
- [ ] Accuracy calculation with partial correct
- [ ] Admin-only access to accuracy view

## 🔒 Security Considerations

1. **File Upload Validation:**
   - Accept only image files (`accept="image/*"`)
   - Validate content type in backend
   - Sanitize filename

2. **Storage Security:**
   - Files stored in Supabase with proper permissions
   - Unique paths prevent overwrites
   - Timestamp prevents collisions

3. **Admin-Only Features:**
   - Accuracy view requires admin/superadmin
   - Upload functionality requires login
   - CSRF protection on all forms

## 📚 Related Documentation

- `QUEM_SOU_EU_IMPLEMENTATION.md` - Original "Quem sou eu" feature
- `FIX_CSRF_DELETE_AND_DESIGN.md` - Form design patterns
- `VISUAL_CHANGES_GUIDE.md` - Visual changes overview

## 🎯 Future Enhancements

Potential improvements:
- [ ] Image preview before upload
- [ ] Drag-and-drop upload
- [ ] Image cropping/resizing
- [ ] Export accuracy data to CSV
- [ ] Fuzzy matching for answers (partial credit)
- [ ] Time-based accuracy (faster = better)
- [ ] Leaderboard based on accuracy
