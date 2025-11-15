"""
Algoritmo: CTP (Capable-to-Promise - Johnson)

Responsabilidades:
- Resolver rutas críticas con trade-offs costo/tiempo
- Johnson algorithm para two-stage flow shop
- Minimizar makespan (duración total)

Complejidad: O(n log n) sorting + O(n²) rule processing
Estrategia: Johnson's rule para secuenciación óptima
"""

from typing import Tuple, List, Dict, Any
from dataclasses import dataclass
import logging

from .base_algorithm import (
    BaseAlgorithm, AlgorithmType, AlgorithmInput, AlgorithmOutput,
    AlgorithmStatus
)

logger = logging.getLogger(__name__)


@dataclass
class SchedulingJob:
    """Trabajo en two-stage flow shop"""
    job_id: str
    stage1_time: float  # Tiempo en máquina 1
    stage2_time: float  # Tiempo en máquina 2
    processing_cost: float
    deadline: str


@dataclass
class ScheduleAnalysis:
    """Análisis de scheduling"""
    optimal_sequence: List[str]
    makespan: float
    total_cost: float
    utilization_stage1: float
    utilization_stage2: float
    delay_penalty: float
    lateness_avg: float


class CTPJohnsonAlgorithm(BaseAlgorithm):
    """Johnson algorithm para two-stage flow shop scheduling
    
    Minimiza makespan usando Johnson's rule:
    1. Si min(stage1) < min(stage2): agendar primero
    2. Si min(stage1) >= min(stage2): agendar al final
    """
    
    def __init__(self):
        super().__init__(AlgorithmType.CTP_JOHNSON)
    
    def validate_input(self, input_data: AlgorithmInput) -> Tuple[bool, str]:
        """Valida que hay fecha requerida y demand > 0"""
        if not input_data.item_id:
            return False, "item_id requerido"
        if input_data.demand_quantity <= 0:
            return False, "demand_quantity debe ser > 0"
        if input_data.required_date is None:
            return False, "required_date obligatoria"
        return True, "OK"
    
    def execute(self, input_data: AlgorithmInput) -> AlgorithmOutput:
        """Ejecuta scheduling mediante Johnson's algorithm (7 pasos)"""
        try:
            # 1. Construir lista de trabajos
            if input_data.db_session:
                jobs = self._fetch_bom_from_db(
                    input_data.db_session,
                    input_data.item_id
                )
            else:
                jobs = self._build_job_list(input_data)
            
            # 2. Aplicar Johnson's rule
            sequence = self._apply_johnson_rule(jobs)
            
            # 3. Calcular makespan
            makespan = self._calculate_makespan(sequence, jobs)
            
            # 4. Calcular análisis de scheduling
            analysis = self._calculate_schedule_analysis(sequence, jobs, makespan)
            
            # 5. Determinar decisión
            schedule_decision = self._determine_schedule_decision(analysis, input_data.criticality)
            
            # 6. Generar reasoning detallado
            reasoning = self._generate_reasoning(analysis, schedule_decision)
            
            # 7. Calcular confidence
            confidence = min(
                (1.0 - analysis.lateness_avg / 100.0) * 0.6 +
                (analysis.utilization_stage1 + analysis.utilization_stage2) / 2.0 * 0.4,
                1.0
            )
            confidence = max(0.0, confidence)
            
            return AlgorithmOutput(
                algorithm_type=AlgorithmType.CTP_JOHNSON,
                item_id=input_data.item_id,
                success=True,
                status=AlgorithmStatus.COMPLETED,
                selected_option=schedule_decision,
                proposed_quantity=input_data.demand_quantity,
                estimated_cost=analysis.total_cost,
                confidence_score=confidence,
                reasoning=reasoning
            )
            
        except Exception as e:
            logger.error(f"Error en CTPJohnsonAlgorithm: {e}")
            return AlgorithmOutput(
                algorithm_type=AlgorithmType.CTP_JOHNSON,
                item_id=input_data.item_id,
                success=False,
                status=AlgorithmStatus.FAILED,
                selected_option="scheduling_error",
                proposed_quantity=0.0,
                estimated_cost=0.0,
                confidence_score=0.0,
                reasoning=f"Error: {str(e)}"
            )
    
    def _fetch_bom_from_db(self, session, item_id: str) -> List[SchedulingJob]:
        """Consulta BOM real desde base de datos y convierte a jobs"""
        try:
            from services.planner.repositories import ItemRepository
            
            repo = ItemRepository(session)
            bom_components = repo.get_bom_components(item_id)
            
            jobs = []
            for idx, component in enumerate(bom_components):
                # Simular tiempos de procesamiento basados en cantidad
                stage1_time = component.quantity * 2.0  # Preparación
                stage2_time = component.quantity * 1.5  # Ensamble
                processing_cost = component.quantity * 10.0
                
                jobs.append(SchedulingJob(
                    job_id=f"JOB-{component.component_id}",
                    stage1_time=stage1_time,
                    stage2_time=stage2_time,
                    processing_cost=processing_cost,
                    deadline="2024-12-31"  # Default
                ))
            
            if not jobs:
                self.logger.warning(f"No BOM components found for {item_id}, using simulated")
                return self._build_job_list_simulated()
            
            return jobs
            
        except Exception as e:
            self.logger.warning(f"Failed to fetch BOM from DB: {e}")
            return self._build_job_list_simulated()
    
    def _build_job_list_simulated(self) -> List[SchedulingJob]:
        """Jobs simulados para backward compatibility"""
        return [
            SchedulingJob("JOB-1", 3.0, 5.0, 120.0, "2024-12-15"),
            SchedulingJob("JOB-2", 2.0, 4.0, 90.0, "2024-12-20"),
            SchedulingJob("JOB-3", 4.0, 3.0, 150.0, "2024-12-10"),
        ]
    
    def _build_job_list(self, input_data: AlgorithmInput) -> List[SchedulingJob]:
        """Mock job list para scheduling demo"""
        criticality_multiplier = {
            "CRITICAL": 1.3,
            "HIGH": 1.1,
            "MEDIUM": 1.0,
            "LOW": 0.8
        }.get(input_data.criticality, 1.0)
        
        jobs = [
            SchedulingJob("JOB-001", 5.0, 4.0, 15.0, input_data.required_date),
            SchedulingJob("JOB-002", 3.0, 7.0, 12.0, input_data.required_date),
            SchedulingJob("JOB-003", 4.0, 3.0, 10.0, input_data.required_date),
            SchedulingJob("JOB-004", 6.0, 2.0, 18.0, input_data.required_date),
            SchedulingJob("JOB-005", 2.0, 5.0, 8.0, input_data.required_date),
        ]
        
        # Ajustar tiempos por criticidad
        for job in jobs:
            job.stage1_time *= criticality_multiplier
            job.stage2_time *= criticality_multiplier
        
        return jobs
    
    def _apply_johnson_rule(self, jobs: List[SchedulingJob]) -> List[str]:
        """Aplica Johnson's rule para optimizar secuencia
        
        Regla: Si min(stage1) < min(stage2), agendar primero
                Si min(stage1) >= min(stage2), agendar al final
        """
        left = []
        right = []
        
        for job in jobs:
            if job.stage1_time <= job.stage2_time:
                left.append(job.job_id)
            else:
                right.append(job.job_id)
        
        # Ordenar left por stage1_time ascendente
        left.sort(key=lambda jid: next(j.stage1_time for j in jobs if j.job_id == jid))
        
        # Ordenar right por stage2_time descendente
        right.sort(key=lambda jid: next(j.stage2_time for j in jobs if j.job_id == jid), 
                  reverse=True)
        
        return left + right
    
    def _calculate_makespan(self, sequence: List[str], jobs: List[SchedulingJob]) -> float:
        """Calcula makespan (tiempo total de todas las máquinas)"""
        job_dict = {j.job_id: j for j in jobs}
        
        time_stage1 = 0.0
        time_stage2 = 0.0
        
        for job_id in sequence:
            job = job_dict[job_id]
            # Stage 1 secuencial
            time_stage1 += job.stage1_time
            # Stage 2 comienza después de que Stage 1 termina
            time_stage2 = max(time_stage2 + job.stage2_time, time_stage1 + job.stage2_time)
        
        return time_stage2
    
    def _calculate_schedule_analysis(
        self, 
        sequence: List[str], 
        jobs: List[SchedulingJob],
        makespan: float
    ) -> ScheduleAnalysis:
        """Calcula análisis completo del scheduling"""
        job_dict = {j.job_id: j for j in jobs}
        total_cost = sum(j.processing_cost for j in jobs)
        
        # Utilización
        total_stage1_time = sum(j.stage1_time for j in jobs)
        total_stage2_time = sum(j.stage2_time for j in jobs)
        util_stage1 = total_stage1_time / makespan if makespan > 0 else 0.0
        util_stage2 = total_stage2_time / makespan if makespan > 0 else 0.0
        
        # Lateness (asumiendo deadline = required_date)
        delay_penalty = 0.0 if makespan <= 10.0 else (makespan - 10.0) * 2.0
        lateness_avg = (delay_penalty / len(sequence)) if sequence else 0.0
        
        return ScheduleAnalysis(
            optimal_sequence=sequence,
            makespan=makespan,
            total_cost=total_cost,
            utilization_stage1=min(util_stage1, 1.0),
            utilization_stage2=min(util_stage2, 1.0),
            delay_penalty=delay_penalty,
            lateness_avg=lateness_avg
        )
    
    def _determine_schedule_decision(self, analysis: ScheduleAnalysis, criticality: str) -> str:
        """Decide si schedule es OPTIMAL, FEASIBLE, o RISKY"""
        if analysis.lateness_avg < 2.0 and (analysis.utilization_stage1 + analysis.utilization_stage2) / 2 > 0.75:
            return "schedule_optimal"
        elif analysis.lateness_avg < 5.0:
            return "schedule_feasible"
        else:
            return "schedule_risky"
    
    def _generate_reasoning(self, analysis: ScheduleAnalysis, decision: str) -> str:
        """Genera explicación detallada"""
        return (
            f"Secuencia óptima (Johnson): {' → '.join(analysis.optimal_sequence[:3])}... "
            f"(total: {len(analysis.optimal_sequence)} trabajos). "
            f"Makespan: {analysis.makespan:.1f}h | Costo: ${analysis.total_cost:.0f}. "
            f"Utilización: Stage1={analysis.utilization_stage1:.1%}, Stage2={analysis.utilization_stage2:.1%}. "
            f"Lateness promedio: {analysis.lateness_avg:.1f}h | Decisión: {decision.replace('schedule_', '').upper()}"
        )


# Factory function
def get_ctp_johnson_algorithm() -> CTPJohnsonAlgorithm:
    """Obtiene instancia del algoritmo CTP Johnson"""
    return CTPJohnsonAlgorithm()
