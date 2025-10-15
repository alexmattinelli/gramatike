# 🧪 Testing Guide: Article Save Fix

## ✅ Test Case 1: Save Article with Long Resumo

### Prerequisites
- Be logged in as admin or superadmin
- Have at least one article in the system

### Steps
1. Navigate to `/artigos`
2. Click the "Edit" button on any article
3. In the "Resumo" field, paste the following text (1090 characters):

```
Neste texto, proponho uma abordagem de neutralização de gênero em português brasileiro na perspectiva do sistema linguístico. Para isso, parto de considerações sobre a caracterização de mudanças deliberadas e sobre os padrões de marcação e produtividade de gênero gramatical na língua. São avaliados, nessa perspectiva, quatro tipos de empregos correntes de gênero inclusivo: uso de feminino marcado no caso de substantivos comuns de dois gêneros (ex. a presidenta); emprego de formas femininas e masculinas, sobretudo em vocativos, em vez do uso genérico do masculino (ex. alunas e alunos); inclusão de novas marcas no final de nomes e adjetivos, como x e @ (ex. amigx, amig@), ou ampliação da função de marcas já existentes, como -e (ex. amigue); alteração na base de pronomes e artigos (ex. ile, le). Desses empregos, além do feminino marcado e do contraste entre formas femininas e masculinas, que já têm uso significativo na língua, proponho que, no domínio da palavra, -e encontra condições menos limitadas para expansão no sistema no subconjunto de substantivos e adjetivos sexuados.
```

4. Click "Salvar" (Save)

### Expected Result
✅ The modal closes
✅ The page reloads
✅ The article is updated with the new resumo
✅ No "Falha ao salvar" error appears

### What to Check
- Open browser DevTools (F12) → Network tab
- Look for the POST request to `/admin/edu/content/<id>/update`
- Status should be **200 OK**
- Response should be `{"success": true, "message": "Conteúdo atualizado."}`

---

## ✅ Test Case 2: Verify CSRF Token

### Steps
1. Navigate to `/artigos`
2. Open browser DevTools (F12) → Elements/Inspector
3. Find the edit form dialog: `<dialog id="editArtigoDialog">`
4. Locate the CSRF hidden input: `<input type="hidden" name="csrf_token" .../>`

### Expected Result
✅ The CSRF token value should be a long string (approximately 91 characters)
✅ The value should NOT be empty
✅ The value should look like: `"IjZmMTllMGU2NTBiNzZhZDE3NGY2MmJkNzdhZTY1..."`

---

## ✅ Test Case 3: Test with Special Characters

### Steps
1. Edit an article
2. In the resumo field, include text with Portuguese special characters:
   - á, à, ã, â
   - é, ê
   - í
   - ó, ô, õ
   - ú
   - ç
3. Save the article

### Expected Result
✅ Article saves successfully
✅ Special characters are preserved correctly
✅ No encoding errors

---

## ✅ Test Case 4: Test Maximum Length

### Steps
1. Edit an article
2. Paste a very long resumo (close to 2000 characters)
3. Save the article

### Expected Result
✅ Article saves successfully (up to 2000 characters)
✅ No truncation occurs

---

## ❌ Test Case 5: Verify Error Handling (Delete)

### Steps
1. Navigate to `/artigos`
2. Click the "⋮" menu on any article
3. Click "Excluir" (Delete)
4. Confirm deletion

### Expected Result
✅ Article is deleted successfully
✅ No CSRF errors
✅ Page reloads showing updated list

---

## 🐛 What to Check if Errors Occur

### If you see "Falha ao salvar":
1. Open DevTools → Console
2. Look for any JavaScript errors
3. Check Network tab for the POST request
4. Verify the request includes `csrf_token` in the form data
5. Check the response status code

### If you see "400 Bad Request":
- The CSRF token is missing or invalid
- Check that the form has: `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />`

### If you see "403 Forbidden":
- The user doesn't have admin permissions
- Check that `current_user.is_admin` or `current_user.is_superadmin` is True

---

## 🔍 Browser Console Checks

### Before Fix (Expected Error):
```
POST /admin/edu/content/1/update → 400 Bad Request
Error: The CSRF token is missing.
```

### After Fix (Expected Success):
```
POST /admin/edu/content/1/update → 200 OK
Response: {"success": true, "message": "Conteúdo atualizado."}
```

---

## ✨ Summary

The fix ensures that:
1. ✅ CSRF token is always present in the form
2. ✅ Long resumos (up to 2000 chars) can be saved
3. ✅ Special characters are preserved
4. ✅ The pattern matches the proven working podcasts template
