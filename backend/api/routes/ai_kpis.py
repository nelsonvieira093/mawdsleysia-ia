# backend/api/routes/ai_kpis.py
from  fastapi import APIRouter, HTTPException, Depends
from  pydantic import BaseModel
from  typing import Optional, Dict, Any, List
import os
from  datetime import datetime

from middleware.auth import require_any_auth

router = APIRouter(prefix="/ai/kpis", tags=["AI KPIs"])

class AnalyzeKPIRequest(BaseModel):
    kpi_data: str
    metrics: Optional[Dict[str, Any]] = None
    current_value: Optional[float] = None
    target_value: Optional[float] = None
    timeframe: str = "monthly"

@router.post("/analyze")
async def analyze_kpi(
    data: AnalyzeKPIRequest,
    current_user: dict = Depends(require_any_auth)
):
    """
    Analisar KPI usando IA
    """
    try:
        # Modo demo
        if not os.getenv("OPENAI_API_KEY"):
            demo_analysis = f"""
��� **Análise do KPI (Modo Demo)**

**Dados fornecidos:**
{data.kpi_data}

**Métricas:** {data.metrics or "Não informadas"}
**Valor atual:** {data.current_value or "N/A"}
**Meta:** {data.target_value or "N/A"}
**Período:** {data.timeframe}

**Análise:**
Este é um KPI importante que deve ser monitorado regularmente.
Recomenda-se definir metas claras e acompanhar o progresso semanalmente.

**Recomendações:**
1. Estabelecer linha de base
2. Definir metas SMART
3. Monitorar periodicamente
4. Ajustar estratégia conforme necessário

---
*Para análise com IA real, adicione OPENAI_API_KEY no .env*
"""
            
            return {
                "analysis": demo_analysis.strip(),
                "risk_level": "medium",
                "trend": "stable",
                "recommendations": [
                    "Monitorar periodicamente",
                    "Definir metas claras",
                    "Documentar progresso"
                ],
                "generated_by": "demo",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # IA real
        try:
            from agents.kpi_agent import analyze_kpi as ai_analyze
            response = ai_analyze(data.kpi_data)
        except ImportError:
            # Fallback
            import openai
            
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            system_prompt = """
Você é um analista especializado em KPIs corporativos.
Analise o KPI fornecido e forneça insights sobre performance, riscos e recomendações.
"""
            
            user_prompt = f"""
KPI Description: {data.kpi_data}
Current Value: {data.current_value}
Target Value: {data.target_value}
Timeframe: {data.timeframe}
Metrics: {data.metrics}
"""
            
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=800
            )
            
            response = completion.choices[0].message.content
        
        # Extrair nível de risco da resposta (simplificado)
        risk_level = "medium"
        if any(word in response.lower() for word in ["alto", "high", "critical", "urgent"]):
            risk_level = "high"
        elif any(word in response.lower() for word in ["baixo", "low", "safe", "stable"]):
            risk_level = "low"
        
        return {
            "analysis": response,
            "risk_level": risk_level,
            "trend": "to_be_analyzed",
            "recommendations": [
                "Monitorar periodicamente",
                "Definir metas claras",
                "Documentar progresso"
            ],
            "generated_by": "gpt-4o-mini",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Erro na análise: {str(e)}"
        )

@router.get("/metrics")
async def get_kpi_metrics():
    """
    Listar métricas comuns de KPIs
    """
    return {
        "common_metrics": [
            {"name": "Revenue", "unit": "currency", "frequency": "monthly"},
            {"name": "Customer Acquisition Cost", "unit": "currency", "frequency": "monthly"},
            {"name": "Customer Satisfaction", "unit": "score", "frequency": "quarterly"},
            {"name": "Employee Turnover", "unit": "percentage", "frequency": "quarterly"},
            {"name": "Project Completion Rate", "unit": "percentage", "frequency": "weekly"}
        ]
    }
