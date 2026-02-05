const fs = require('fs');
const file = 'src/pages/Chat.jsx';
let content = fs.readFileSync(file, 'utf8');

// Substitui a chamada api.post por fetch
content = content.replace(
  /try \{\s+const response = await api\.post\("\/api\/v1\/chat", \{[^}]+\}\);/s,
  `try {
      const token = localStorage.getItem('token') || '';
      
      console.log("í´§ [CHAT DEBUG] Usando fetch direto...");
      console.log("í´§ [CHAT DEBUG] URL:", "http://localhost:8080/api/v1/chat");
      
      const fetchResponse = await fetch("http://localhost:8080/api/v1/chat", {
        method: "POST",
        headers: {
          "Authorization": \`Bearer \${token}\`,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          message: messageToSend,
          context: safeContext,
          mode: mode === "executive" ? "bullet_journal_ceo" : undefined,
        })
      });
      
      console.log("í´§ [CHAT DEBUG] Fetch status:", fetchResponse.status);
      
      if (!fetchResponse.ok) {
        const errorText = await fetchResponse.text();
        throw new Error(\`HTTP \${fetchResponse.status}: \${errorText}\`);
      }
      
      const responseData = await fetchResponse.json();
      const response = { data: responseData };`
);

fs.writeFileSync(file, content);
console.log('âœ… Patch aplicado!');
