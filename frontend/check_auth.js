// Execute no console do navegador
function checkAuthState() {
  const token = localStorage.getItem('token');
  const user = localStorage.getItem('user');
  
  console.log("Ì¥ê ESTADO DE AUTENTICA√á√ÉO:");
  console.log("==========================");
  console.log("Token:", token ? `‚úÖ PRESENTE (${token.length} chars)` : "‚ùå AUSENTE");
  console.log("User:", user ? `‚úÖ ${JSON.parse(user).name || 'Usu√°rio'}` : "‚ùå N√£o logado");
  
  if (!token) {
    console.log("\nÌ∫® PROBLEMA: Usu√°rio n√£o est√° logado!");
    console.log("Ì≤° Solu√ß√£o: Fa√ßa login primeiro ou adicione token de teste:");
    console.log(`
      // No console, execute:
      localStorage.setItem('token', 'test-token-123');
      localStorage.setItem('user', JSON.stringify({id: 1, name: "Test User"}));
      location.reload();
    `);
  }
}

checkAuthState();
