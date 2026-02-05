#!/bin/bash
echo "Ì¥ß Aplicando patch de debug ao Chat.jsx..."

FILE="src/pages/Chat.jsx"
BACKUP="${FILE}.$(date +%s).bak"

# Backup
cp "$FILE" "$BACKUP"
echo "Ì≥¶ Backup criado: $BACKUP"

# Primeiro, encontre a linha do try
TRY_LINE=$(grep -n "try {" "$FILE" | head -1 | cut -d: -f1)
if [ -z "$TRY_LINE" ]; then
    echo "‚ùå N√£o encontrei 'try {' no arquivo"
    exit 1
fi

# Adicione logs antes do try
sed -i "$((TRY_LINE-1))i\\
    // DEBUG LOGS\\
    console.log(\"Ì¥ç [CHAT DEBUG] =============== IN√çCIO ===============\");\\
    console.log(\"Ì¥ç [CHAT DEBUG] Usu√°rio:\", user);\\
    console.log(\"Ì¥ç [CHAT DEBUG] User ID:\", user?.id);\\
    console.log(\"Ì¥ç [CHAT DEBUG] Token:\", localStorage.getItem(\"token\") ? \"PRESENTE\" : \"AUSENTE\");\\
    console.log(\"Ì¥ç [CHAT DEBUG] Mensagem:\", messageToSend);\\
    console.log(\"Ì¥ç [CHAT DEBUG] Contexto:\", safeContext);\\
    console.log(\"Ì¥ç [CHAT DEBUG] Mode:\", mode);\\
    console.log(\"Ì¥ç [CHAT DEBUG] API baseURL:\", api.defaults?.baseURL);" "$FILE"

# Adicione log antes da chamada API
API_LINE=$(grep -n "const response = await api.post" "$FILE" | head -1 | cut -d: -f1)
sed -i "$((API_LINE-1))i\\
      console.log(\"Ì∫Ä [CHAT DEBUG] Chamando API POST...\");" "$FILE"

# Encontre e melhore o catch
CATCH_LINE=$(grep -n "} catch (error) {" "$FILE" | head -1 | cut -d: -f1)
if [ ! -z "$CATCH_LINE" ]; then
    sed -i "$CATCH_LINE a\\
      console.error(\"‚ùå [CHAT DEBUG] ERRO COMPLETO =====================\");\\
      console.error(\"‚ùå [CHAT DEBUG] Error object:\", error);\\
      console.error(\"‚ùå [CHAT DEBUG] Error message:\", error.message);\\
      console.error(\"‚ùå [CHAT DEBUG] Error stack:\", error.stack);\\
      \\
      // Axios error specifics\\
      if (error.response) {\\
        console.error(\"‚ùå [CHAT DEBUG] Response data:\", error.response.data);\\
        console.error(\"‚ùå [CHAT DEBUG] Response status:\", error.response.status);\\
      } else if (error.request) {\\
        console.error(\"‚ùå [CHAT DEBUG] No response received:\", error.request);\\
        console.error(\"‚ùå [CHAT DEBUG] Network Error detected\");\\
        \\
        // Teste manual da conex√£o\\
        console.log(\"Ì¥ß [CHAT DEBUG] Testando conex√£o manualmente...\");\\
        try {\\
          const test = await fetch(api.defaults.baseURL + \"/health\");\\
          const testData = await test.json();\\
          console.log(\"Ì¥ß [CHAT DEBUG] Teste manual OK:\", testData);\\
        } catch (e) {\\
          console.error(\"Ì¥ß [CHAT DEBUG] Teste manual FALHOU:\", e.message);\\
        }\\
      } else {\\
        console.error(\"‚ùå [CHAT DEBUG] Setup error:\", error.config);\\
      }\\
      \\
      console.error(\"‚ùå [CHAT DEBUG] ===================================\");" "$FILE"
fi

echo "‚úÖ Patch aplicado!"
echo ""
echo "Ì≥ä Diferen√ßas principais:"
diff -u "$BACKUP" "$FILE" | grep -A5 -B5 "console\.\|DEBUG" | head -30
