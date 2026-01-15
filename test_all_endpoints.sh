#!/bin/bash
echo "Ì∑™ TESTANDO TODOS OS ENDPOINTS DO FRONTEND"
echo "=========================================="

# Lista de todos os endpoints que o frontend precisa
endpoints=(
  # Endpoints b√°sicos
  "http://localhost:8000/ping"
  "http://localhost:8000/health"
  
  # Dashboard
  "http://localhost:8000/api/dashboard"
  "http://localhost:8000/api/automations/status"
  
  # Frontend compatibility
  "http://localhost:8000/followups"
  "http://localhost:8000/followups/"
  "http://localhost:8000/deliverables"
  "http://localhost:8000/deliverables/"
  "http://localhost:8000/history"
  "http://localhost:8000/history/"
  "http://localhost:8000/meetings"
  "http://localhost:8000/meetings/"
  "http://localhost:8000/notes"
  "http://localhost:8000/notes/"
  "http://localhost:8000/kpis/overview"
  "http://localhost:8000/api/kpis/overview"
  
  # Knowledge
  "http://localhost:8000/knowledge/items"
  "http://localhost:8000/knowledge/stats"
  
  # Agenda
  "http://localhost:8000/api/agenda"
  
  # API routes
  "http://localhost:8000/api/followups"
  "http://localhost:8000/api/followups/"
  "http://localhost:8000/api/deliverables"
  "http://localhost:8000/api/deliverables/"
  "http://localhost:8000/api/history"
  "http://localhost:8000/api/history/"
)

echo "Ì¥ç Testando ${#endpoints[@]} endpoints..."
echo ""

success=0
fail=0

for url in "${endpoints[@]}"; do
  echo -n "   ${url} ... "
  status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
  
  if [ "$status" = "200" ]; then
    echo "‚úÖ OK"
    ((success++))
  elif [ "$status" = "404" ]; then
    echo "‚ùå 404 (N√£o encontrado)"
    ((fail++))
  elif [ "$status" = "500" ]; then
    echo "Ì≤• 500 (Erro interno)"
    ((fail++))
  else
    echo "‚ö†Ô∏è  $status"
    ((fail++))
  fi
done

echo ""
echo "Ì≥ä RESULTADO:"
echo "   ‚úÖ Sucesso: $success"
echo "   ‚ùå Falhas: $fail"
echo "   Ì≥à Taxa de sucesso: $((success * 100 / (success + fail)))%"

if [ $fail -eq 0 ]; then
  echo ""
  echo "Ìæâ TODOS OS ENDPOINTS EST√ÉO FUNCIONANDO!"
  echo "Ì∫Ä O frontend N√ÉO deve ter mais erros 404!"
else
  echo ""
  echo "Ì¥ß Alguns endpoints precisam de ajuste."
fi
