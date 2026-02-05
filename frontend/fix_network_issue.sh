#!/bin/bash
echo "Ì¥ß Corrigindo Network Error no Chat.jsx..."

FILE="src/pages/Chat.jsx"
BACKUP="${FILE}.backup.$(date +%s)"

# Backup
cp "$FILE" "$BACKUP"
echo "Ì≥¶ Backup criado: $BACKUP"

# Encontre a linha do try
TRY_LINE=$(grep -n "try {" "$FILE" | grep -A5 "handleSendMessage" | head -1 | cut -d: -f1)

if [ -z "$TRY_LINE" ]; then
    echo "‚ùå N√£o encontrei 'try {'"
    exit 1
fi

# Encontre a linha da chamada api.post
API_LINE=$(grep -n "const response = await api.post" "$FILE" | head -1 | cut -d: -f1)

if [ -z "$API_LINE" ]; then
    echo "‚ùå N√£o encontrei a chamada api.post"
    exit 1
fi

# Calcule quantas linhas entre try e api.post
LINES_BETWEEN=$((API_LINE - TRY_LINE))

echo "Ì¥ç Encontrado:"
echo "   - try na linha: $TRY_LINE"
echo "   - api.post na linha: $API_LINE"
echo "   - linhas entre: $LINES_BETWEEN"

# Substitua a se√ß√£o
sed -i "${TRY_LINE},$((API_LINE+2))d" "$FILE"

# Insira o novo c√≥digo
sed -i "${TRY_LINE}i\\
    try {\\
      const token = localStorage.getItem('token') || '';\\
      \\
      console.log(\"Ì¥ß [CHAT DEBUG] Usando fetch direto...\");\\
      console.log(\"Ì¥ß [CHAT DEBUG] URL:\", \"http://localhost:8080/api/v1/chat\");\\
      \\
      const fetchResponse = await fetch(\"http://localhost:8080/api/v1/chat\", {\\
        method: \"POST\",\\
        headers: {\\
          \"Authorization\": \`Bearer \${token}\`,\\
          \"Content-Type\": \"application/json\"\\
        },\\
        body: JSON.stringify({\\
          message: messageToSend,\\
          context: safeContext,\\
          mode: mode === \"executive\" ? \"bullet_journal_ceo\" : undefined,\\
        })\\
      });\\
      \\
      console.log(\"Ì¥ß [CHAT DEBUG] Fetch status:\", fetchResponse.status);\\
      \\
      if (!fetchResponse.ok) {\\
        const errorText = await fetchResponse.text();\\
        throw new Error(\`HTTP \${fetchResponse.status}: \${errorText}\`);\\
      }\\
      \\
      const responseData = await fetchResponse.json();\\
      const response = { data: responseData };" "$FILE"

echo "‚úÖ Patch aplicado!"
echo ""
echo "Ì≥ä Diferen√ßas:"
diff -u "$BACKUP" "$FILE" | head -40
