from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
import asyncio
from datetime import datetime
from .communication_service import CommunicationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CandidateEvaluation:
    """Represents the evaluation results for a candidate model."""
    model_id: int
    overall_score: float
    criteria_scores: Dict[str, float]
    recommendations: List[str]
    evaluation_date: str

@dataclass
class RecruitmentMetrics:
    """Represents recruitment analytics and metrics."""
    total_applicants: int
    active_candidates: int
    hired_count: int
    rejection_rate: float
    average_time_to_hire: float
    conversion_rate: float
    metrics_date: str

class RecruiterAgent:
    """
    The RecruiterAgent is responsible for handling the core AI recruiter functionality,
    including candidate evaluation, recruitment funnel management, automated communications,
    and analytics tracking.
    """

    async def manage_recruitment_funnel(self, model_id: int, stage: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """Manage the recruitment funnel stages for a candidate."""
        logger.info(f"Managing recruitment funnel for model {model_id} at stage {stage}")
        
        try:
            # Validate stage
            valid_stages = ['applied', 'screened', 'interviewed', 'offered', 'hired', 'rejected']
            if stage not in valid_stages:
                raise ValueError(f"Invalid stage: {stage}. Must be one of {valid_stages}")
            
            # Create or update funnel entry
            funnel_entry = self.database.create_recruitment_funnel_entry({
                'model_id': model_id,
                'stage': stage,
                'recruiter_id': None,  # Will be set when recruiter is assigned
                'status': 'active',
                'notes': notes,
                'applied_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            })
            
            # Update model recruitment status
            self.database.update_model_recruitment_status(model_id, stage)
            
            logger.info(f"Recruitment funnel updated for model {model_id}: {stage}")
            return funnel_entry
            
        except Exception as e:
            logger.error(f"Error managing recruitment funnel for model {model_id}: {e}")
            raise
    
    async def get_funnel_stage(self, model_id: int) -> Dict[str, Any]:
        """Get the current funnel stage for a candidate."""
        logger.info(f"Getting funnel stage for model {model_id}")
        
        try:
            # Get the latest funnel entry for this model
            funnel_entries = self.database.get_all_funnel_entries()
            model_entries = [entry for entry in funnel_entries if entry['model_id'] == model_id]
            
            if not model_entries:
                return {"model_id": model_id, "stage": "unassigned", "status": "inactive"}
            
            # Get the most recent entry
            latest_entry = max(model_entries, key=lambda x: x['applied_at'])
            return latest_entry
            
        except Exception as e:
            logger.error(f"Error getting funnel stage for model {model_id}: {e}")
            raise
    
    async def advance_stage(self, model_id: int, current_stage: str, new_stage: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """Advance a candidate to the next stage in the recruitment funnel."""
        logger.info(f"Advancing model {model_id} from {current_stage} to {new_stage}")
        
        try:
            # Validate stage progression
            valid_progression = {
                'applied': ['screened'],
                'screened': ['interviewed'],
                'interviewed': ['offered', 'rejected'],
                'offered': ['hired', 'rejected'],
                'rejected': [],
                'hired': []
            }
            
            if new_stage not in valid_progression.get(current_stage, []):
                raise ValueError(f"Invalid stage progression from {current_stage} to {new_stage}")
            
            # Update funnel entry
            funnel_entry = self.database.create_recruitment_funnel_entry({
                'model_id': model_id,
                'stage': new_stage,
                'recruiter_id': None,
                'status': 'active',
                'notes': notes,
                'applied_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            })
            
            # Update model recruitment status
            self.database.update_model_recruitment_status(model_id, new_stage)
            
            logger.info(f"Model {model_id} advanced to {new_stage}")
            return funnel_entry
            
        except Exception as e:
            logger.error(f"Error advancing stage for model {model_id}: {e}")
            raise
    
    async def send_communication(self, model_id: int, communication_type: str, subject: str, message: str, direction: str = 'outbound') -> Dict[str, Any]:
        """Send automated communication to a candidate."""
        logger.info(f"Sending {communication_type} communication to model {model_id}")
        
        try:
            # Validate communication type
            valid_types = ['email', 'sms', 'whatsapp', 'phone', 'video_call', 'in_person']
            if communication_type not in valid_types:
                raise ValueError(f"Invalid communication type: {communication_type}. Must be one of {valid_types}")
            
            # Validate direction
            valid_directions = ['outbound', 'inbound']
            if direction not in valid_directions:
                raise ValueError(f"Invalid direction: {direction}. Must be one of {valid_directions}")
            
            # Get model information
            model = self.database.get_model(model_id)
            
            # Create communication record using CommunicationService
            communication = await self.communication_service.send_communication(
                model_id,
                template_id=None,
                variables=None,
                custom_subject=subject,
                custom_message=message
            )
            
            logger.info(f"Communication sent to model {model_id}: {communication_type}")
            return communication
            
        except Exception as e:
            logger.error(f"Error sending communication to model {model_id}: {e}")
            raise
    
    async def get_communication_history(self, model_id: int) -> List[Dict[str, Any]]:
        """Get communication history for a candidate."""
        logger.info(f"Getting communication history for model {model_id}")
        
        try:
            # Get all communications for this model
            communications = self.database.get_all_communications()
            model_communications = [comm for comm in communications if comm['model_id'] == model_id]
            
            # Sort by sent date
            model_communications.sort(key=lambda x: x['sent_at'], reverse=True)
            
            logger.info(f"Found {len(model_communications)} communications for model {model_id}")
            return model_communications
            
        except Exception as e:
            logger.error(f"Error getting communication history for model {model_id}: {e}")
            raise
    
    async def schedule_follow_up(self, model_id: int, follow_up_date: str, message: str) -> Dict[str, Any]:
        """Schedule a follow-up communication."""
        logger.info(f"Scheduling follow-up for model {model_id} on {follow_up_date}")
        
        try:
            # Create scheduled communication using CommunicationService
            communication = await self.communication_service.schedule_communication(
                model_id,
                template_id=None,
                send_at=follow_up_date,
                variables=None,
                custom_subject='Follow-up: Your Application Status',
                custom_message=message
            )
            
            logger.info(f"Follow-up scheduled for model {model_id} on {follow_up_date}")
            return communication
            
        except Exception as e:
            logger.error(f"Error scheduling follow-up for model {model_id}: {e}")
            raise
    
    async def get_recruitment_analytics(self, date_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Get comprehensive recruitment analytics."""
        logger.info(f"Getting recruitment analytics for date range {date_range}")
        
        try:
            # Get all models and filter by date range if specified
            models = self.database.get_all_models()
            
            if date_range:
                start_date = datetime.fromisoformat(date_range.get('start'))
                end_date = datetime.fromisoformat(date_range.get('end'))
                models = [
                    model for model in models 
                    if start_date <= datetime.fromisoformat(model['created_at']) <= end_date
                ]
            
            # Calculate analytics
            total_applicants = len(models)
            
            # Recruitment status breakdown
            status_counts = {}
            for model in models:
                status = model.get('recruitment_status', 'unassigned')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Source breakdown
            source_counts = {}
            for model in models:
                source = model.get('source', 'unknown')
                source_counts[source] = source_counts.get(source, 0) + 1
            
            # Tags analysis
            tag_counts = {}
            for model in models:
                tags = model.get('tags', [])
                if isinstance(tags, str):
                    tags = tags.split(',')
                for tag in tags:
                    tag = tag.strip()
                    if tag:
                        tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # Time-based metrics
            if models:
                creation_dates = [datetime.fromisoformat(model['created_at']) for model in models]
                time_span = (max(creation_dates) - min(creation_dates)).days
                average_applicants_per_day = total_applicants / time_span if time_span > 0 else 0
            else:
                average_applicants_per_day = 0
            
            analytics = {
                'total_applicants': total_applicants,
                'status_breakdown': status_counts,
                'source_breakdown': source_counts,
                'tag_analysis': tag_counts,
                'average_applicants_per_day': average_applicants_per_day,
                'analytics_date': datetime.now().isoformat(),
                'date_range': date_range
            }
            
            logger.info(f"Recruitment analytics calculated: {analytics}")
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting recruitment analytics: {e}")
            raise
    
    async def get_performance_metrics(self, recruiter_id: Optional[int] = None) -> Dict[str, Any]:
        """Get recruiter performance metrics."""
        logger.info(f"Getting performance metrics for recruiter {recruiter_id}")
        
        try:
            # Get all funnel entries
            funnel_entries = self.database.get_all_funnel_entries()
            
            if recruiter_id:
                funnel_entries = [entry for entry in funnel_entries if entry['recruiter_id'] == recruiter_id]
            
            # Calculate performance metrics
            total_candidates = len(funnel_entries)
            
            # Stage progression analysis
            stage_counts = {}
            for entry in funnel_entries:
                stage = entry['stage']
                stage_counts[stage] = stage_counts.get(stage, 0) + 1
            
            # Time in each stage
            stage_times = {}
            for entry in funnel_entries:
                if entry['applied_at'] and entry['updated_at']:
                    days_in_stage = (datetime.fromisoformat(entry['updated_at']) - datetime.fromisoformat(entry['applied_at'])).days
                    stage = entry['stage']
                    if stage not in stage_times:
                        stage_times[stage] = []
                    stage_times[stage].append(days_in_stage)
            
            # Calculate average days per stage
            avg_days_per_stage = {}
            for stage, times in stage_times.items():
                if times:
                    avg_days_per_stage[stage] = sum(times) / len(times)
                else:
                    avg_days_per_stage[stage] = 0
            
            # Conversion rates between stages
            conversion_rates = {}
            stages = ['applied', 'screened', 'interviewed', 'offered', 'hired', 'rejected']
            for i, stage in enumerate(stages[:-1]):
                next_stage = stages[i + 1]
                current_count = stage_counts.get(stage, 0)
                next_count = stage_counts.get(next_stage, 0)
                
                if current_count > 0:
                    conversion_rates[f"{stage}>{next_stage}"] = (next_count / current_count) * 100
                else:
                    conversion_rates[f"{stage}>{next_stage}"] = 0
            
            metrics = {
                'total_candidates': total_candidates,
                'stage_counts': stage_counts,
                'average_days_per_stage': avg_days_per_stage,
                'conversion_rates': conversion_rates,
                'performance_date': datetime.now().isoformat(),
                'recruiter_id': recruiter_id
            }
            
            logger.info(f"Performance metrics calculated: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            raise
    
    async def get_communication_metrics(self, date_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Get communication metrics."""
        logger.info(f"Getting communication metrics for date range {date_range}")
        
        try:
            # Get communication metrics using CommunicationService
            metrics = await self.communication_service.get_communication_analytics(date_range)
            
            logger.info(f"Communication metrics calculated: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting communication metrics: {e}")
            raise
    
    async def generate_recruitment_report(self, date_range: Dict[str, str]) -> Dict[str, Any]:
        """Generate a comprehensive recruitment report."""
        logger.info(f"Generating recruitment report for date range {date_range}")
        
        try:
            # Get all metrics
            analytics = await self.get_recruitment_analytics(date_range)
            performance = await self.get_performance_metrics()
            communications = await self.communication_service.generate_communication_report(date_range)
            
            # Generate insights
            insights = []
            
            # Conversion rate insights
            if analytics['total_applicants'] > 0:
                conversion_rate = analytics.get('status_breakdown', {}).get('hired', 0) / analytics['total_applicants']
                if conversion_rate < 0.1:
                    insights.append('Low conversion rate - consider improving screening process')
                elif conversion_rate > 0.3:
                    insights.append('High conversion rate - recruitment process is effective')
            
            # Response time insights
            if communications['analytics']['average_response_time_hours'] > 24:
                insights.append('Average response time exceeds 24 hours - consider faster follow-ups')
            elif communications['analytics']['average_response_time_hours'] < 4:
                insights.append('Excellent response times - maintaining quick candidate engagement')
            
            # Source effectiveness
            if analytics['source_breakdown']:
                best_source = max(analytics['source_breakdown'].items(), key=lambda x: x[1])
                insights.append(f"Best source: {best_source[0]} with {best_source[1]} applicants")
            
            report = {
                'date_range': date_range,
                'analytics': analytics,
                'performance': performance,
                'communications': communications,
                'insights': insights,
                'report_date': datetime.now().isoformat(),
                'summary': self._generate_report_summary(analytics, performance, communications)
            }
            
            logger.info(f"Recruitment report generated: {report}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating recruitment report: {e}")
            raise
    
    async def assign_recruiter_to_model(self, model_id: int, recruiter_id: int) -> Dict[str, Any]:
        """Assign a recruiter to a specific model."""
        logger.info(f"Assigning recruiter {recruiter_id} to model {model_id}")
        
        try:
            # Update model with recruiter assignment
            self.database.update_model_recruiter(model_id, recruiter_id)
            
            # Update all related records with recruiter_id
            self.database.update_funnel_recruiter(model_id, recruiter_id)
            self.database.update_contracts_recruiter(model_id, recruiter_id)
            self.database.update_communications_recruiter(model_id, recruiter_id)
            
            # Update assigned models tracking
            self.assigned_models[model_id] = {
                'recruiter_id': recruiter_id,
                'assigned_at': datetime.now().isoformat()
            }
            
            logger.info(f"Recruiter {recruiter_id} assigned to model {model_id}")
            return self.database.get_model(model_id)
            
        except Exception as e:
            logger.error(f"Error assigning recruiter {recruiter_id} to model {model_id}: {e}")
            raise
    
    async def get_assigned_models(self, recruiter_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get all models assigned to a specific recruiter."""
        logger.info(f"Getting models assigned to recruiter {recruiter_id}")
        
        try:
            # Get all models and filter by recruiter_id if specified
            models = self.database.get_all_models()
            
            if recruiter_id:
                models = [model for model in models if model.get('recruiter_id') == recruiter_id]
            else:
                models = [model for model in models if model.get('recruiter_id') is not None]
            
            logger.info(f"Found {len(models)} models assigned to recruiter {recruiter_id}")
            return models
            
        except Exception as e:
            logger.error(f"Error getting assigned models for recruiter {recruiter_id}: {e}")
            raise
    
    async def get_unassigned_models(self) -> List[Dict[str, Any]]:
        """Get all models that are not yet assigned to a recruiter."""
        logger.info("Getting unassigned models")
        
        try:
            # Get all models and filter for unassigned
            models = self.database.get_all_models()
            unassigned = [model for model in models if model.get('recruiter_id') is None]
            
            logger.info(f"Found {len(unassigned)} unassigned models")
            return unassigned
            
        except Exception as e:
            logger.error(f"Error getting unassigned models: {e}")
            raise
    
    async def get_model_evaluation_history(self, model_id: int) -> List[Dict[str, Any]]:
        """Get evaluation history for a specific model."""
        logger.info(f"Getting evaluation history for model {model_id}")
        
        try:
            # Get all funnel entries for this model
            funnel_entries = self.database.get_all_funnel_entries()
            model_entries = [entry for entry in funnel_entries if entry['model_id'] == model_id]
            
            # Get all communications for this model
            communications = self.database.get_all_communications()
            model_communications = [comm for comm in communications if comm['model_id'] == model_id]
            
            # Get all contracts for this model
            contracts = self.database.get_all_contracts()
            model_contracts = [contract for contract in contracts if contract['model_id'] == model_id]
            
            history = {
                'model_id': model_id,
                'funnel_entries': model_entries,
                'communications': model_communications,
                'contracts': model_contracts,
                'history_date': datetime.now().isoformat()
            }
            
            logger.info(f"Evaluation history retrieved for model {model_id}")
            return history
            
        except Exception as e:
            logger.error(f"Error getting evaluation history for model {model_id}: {e}")
            raise
    
    async def send_bulk_communication(self, model_ids: List[int], communication_type: str, subject: str, message: str) -> List[Dict[str, Any]]:
        """Send bulk communication to multiple candidates."""
        logger.info(f"Sending bulk {communication_type} communication to {len(model_ids)} models")
        
        try:
            communications = []
            for model_id in model_ids:
                try:
                    comm = await self.send_communication(model_id, communication_type, subject, message)
                    communications.append(comm)
                except Exception as e:
                    logger.error(f"Error sending communication to model {model_id}: {e}")
                    continue
            
            logger.info(f"Bulk communication sent to {len(communications)} models")
            return communications
            
        except Exception as e:
            logger.error(f"Error sending bulk communication: {e}")
            raise
    
    async def evaluate_candidate(self, model_id: int) -> CandidateEvaluation:
        """Evaluate a candidate model based on predefined criteria."""
        logger.info(f"Evaluating candidate model {model_id}")
        
        try:
            model = self.database.get_model(model_id)
            
            # Calculate evaluation scores
            criteria_scores = {
                'technical_skills': self._evaluate_technical_skills(model),
                'communication': self._evaluate_communication(model),
                'personality_fit': self._evaluate_personality(model),
                'availability': self._evaluate_availability(model),
                'market_demand': self._evaluate_market_demand(model)
            }
            
            # Calculate weighted overall score
            overall_score = sum(
                criteria_scores[criteria] * weight 
                for criteria, weight in self.evaluation_criteria.items()
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(criteria_scores, overall_score)
            
            # Create evaluation record
            evaluation = CandidateEvaluation(
                model_id=model_id,
                overall_score=overall_score,
                criteria_scores=criteria_scores,
                recommendations=recommendations,
                evaluation_date=datetime.now().isoformat()
            )
            
            # Update model recruitment status
            self.database.update_model_recruitment_status(model_id, 'evaluated')
            
            logger.info(f"Candidate {model_id} evaluation complete: {overall_score:.2f}")
            return evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating candidate {model_id}: {e}")
            raise
    
    def _evaluate_technical_skills(self, model: Dict[str, Any]) -> float:
        """Evaluate technical skills of the candidate."""
        # For demonstration, use persona tags as technical indicators
        persona = model.get('persona', {})
        technical_tags = persona.get('technical_tags', [])
        
        # Score based on number of technical tags
        tag_count = len(technical_tags)
        return min(1.0, tag_count * 0.2)  # Max 1.0 for 5+ tags
    
    def _evaluate_communication(self, model: Dict[str, Any]) -> float:
        """Evaluate communication skills."""
        # Use language proficiency and persona communication traits
        language = model.get('language', 'en')
        persona = model.get('persona', {})
        
        # English speakers get higher score, plus communication traits
        score = 0.7 if language == 'en' else 0.5
        communication_traits = persona.get('communication_traits', [])
        
        if 'articulate' in communication_traits:
            score += 0.2
        if 'engaging' in communication_traits:
            score += 0.1
        
        return min(1.0, score)
    
    def _evaluate_personality(self, model: Dict[str, Any]) -> float:
        """Evaluate personality fit."""
        persona = model.get('persona', {})
        personality_traits = persona.get('personality_traits', [])
        
        # Score based on desirable personality traits
        desirable_traits = ['friendly', 'professional', 'adaptable', 'creative']
        matching_traits = [trait for trait in desirable_traits if trait in personality_traits]
        
        return min(1.0, len(matching_traits) * 0.25)
    
    def _evaluate_availability(self, model: Dict[str, Any]) -> float:
        """Evaluate availability for work."""
        # Check if model has availability information in persona
        persona = model.get('persona', {})
        availability = persona.get('availability', 'flexible')
        
        if availability == 'full-time':
            return 1.0
        elif availability == 'part-time':
            return 0.7
        elif availability == 'flexible':
            return 0.8
        else:
            return 0.5
    
    def _evaluate_market_demand(self, model: Dict[str, Any]) -> float:
        """Evaluate market demand for this type of model."""
        # For demonstration, use persona tags to estimate demand
        persona = model.get('persona', {})
        tags = persona.get('tags', [])
        
        # High demand tags get higher scores
        high_demand_tags = ['fashion', 'lifestyle', 'tech', 'fitness']
        matching_tags = [tag for tag in high_demand_tags if tag in tags]
        
        return min(1.0, len(matching_tags) * 0.3)
    
# Example usage
if __name__ == "__main__":
    import asyncio
    from database import Database
    
    # Initialize database
    db = Database()
    
    # Initialize RecruiterAgent
    recruiter = RecruiterAgent(db)
    
    async def main():
        # Create a test model
        model_data = {
            "external_id": "M001",
            "name": "Test Model",
            "email": "test@example.com",
            "language": "en",
            "persona": {
                "tags": ["fashion", "lifestyle", "creative"],
                "technical_tags": ["photography", "social_media"],
                "communication_traits": ["articulate", "engaging"],
                "personality_traits": ["friendly", "professional"],
                "availability": "flexible"
            },
            "consent": True,
            "source": "website"
        }
        model = db.create_model(model_data)
        print(f"Created model: {model}")
        
        # Evaluate candidate
        evaluation = await recruiter.evaluate_candidate(model["id"])
        print(f"Candidate evaluation: {evaluation}")
        
        # Manage recruitment funnel
        funnel_entry = await recruiter.manage_recruitment_funnel(model["id"], "applied", "Applied through website")
        print(f"Funnel entry: {funnel_entry}")
        
        # Send communication
        communication = await recruiter.send_communication(
            model["id"], 
            "email", 
            "Application Received", 
            "Thank you for your application! We will review it shortly."
        )
        print(f"Communication sent: {communication}")
        
        # Get analytics
        analytics = await recruiter.get_recruitment_analytics()
        print(f"Recruitment analytics: {analytics}")
        
        # Generate report
        report = await recruiter.generate_recruitment_report({
            "start": "2026-01-01",
            "end": "2026-01-31"
        })
        print(f"Recruitment report: {report}")
        
        # Assign recruiter
        assigned_model = await recruiter.assign_recruiter_to_model(model["id"], 1)
        print(f"Model assigned to recruiter: {assigned_model}")
        
        # Get assigned models
        assigned_models = await recruiter.get_assigned_models(1)
        print(f"Models assigned to recruiter 1: {assigned_models}")
        
        # Get unassigned models
        unassigned_models = await recruiter.get_unassigned_models()
        print(f"Unassigned models: {unassigned_models}")
        
        # Get model evaluation history
        history = await recruiter.get_model_evaluation_history(model["id"])
        print(f"Model evaluation history: {history}")
    
    asyncio.run(main())