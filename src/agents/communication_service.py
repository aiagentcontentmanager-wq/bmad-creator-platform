from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import logging
import asyncio
from datetime import datetime, timedelta
from enum import Enum
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CommunicationChannel(Enum):
    """Enum for communication channels."""
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    PHONE = "phone"
    VIDEO_CALL = "video_call"
    IN_PERSON = "in_person"

class CommunicationStatus(Enum):
    """Enum for communication statuses."""
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    SCHEDULED = "scheduled"

@dataclass
class CommunicationTemplate:
    """Represents a communication template."""
    id: int
    name: str
    channel: CommunicationChannel
    subject: str
    message: str
    variables: List[str]
    is_active: bool
    created_at: str

@dataclass
class Communication:
    """Represents a communication record."""
    id: int
    model_id: int
    recruiter_id: Optional[int]
    template_id: Optional[int]
    channel: CommunicationChannel
    subject: str
    message: str
    direction: str
    status: CommunicationStatus
    sent_at: str
    delivered_at: Optional[str]
    read_at: Optional[str]
    scheduled_at: Optional[str]
    metadata: Dict[str, Any]

@dataclass
class FollowUpSequence:
    """Represents an automated follow-up sequence."""
    id: int
    name: str
    trigger_event: str
    steps: List[Dict]
    is_active: bool
    created_at: str

class CommunicationService:
    """Service for managing automated communications and messaging."""
    
    def __init__(self, database_path: str = "bmad.db"):
        self.database = CommunicationDatabase(database_path)
        self.templates = {}
        self.follow_up_sequences = {}
        self.scheduled_communications = []
        self.channel_integrations = {}
        
    async def initialize(self):
        """Initialize communication service."""
        logger.info("Initializing CommunicationService")
        await self._load_templates()
        await self._load_follow_up_sequences()
        await self._setup_channel_integrations()
        await self._start_scheduler()
        
    async def _load_templates(self):
        """Load communication templates from database."""
        logger.info("Loading communication templates")
        templates = self.database.get_all_templates()
        for template in templates:
            self.templates[template['id']] = CommunicationTemplate(
                id=template['id'],
                name=template['name'],
                channel=CommunicationChannel(template['channel']),
                subject=template['subject'],
                message=template['message'],
                variables=json.loads(template['variables']),
                is_active=template['is_active'],
                created_at=template['created_at']
            )
        logger.info(f"Loaded {len(self.templates)} templates")
        
    async def _load_follow_up_sequences(self):
        """Load follow-up sequences from database."""
        logger.info("Loading follow-up sequences")
        sequences = self.database.get_all_follow_up_sequences()
        for sequence in sequences:
            self.follow_up_sequences[sequence['id']] = FollowUpSequence(
                id=sequence['id'],
                name=sequence['name'],
                trigger_event=sequence['trigger_event'],
                steps=json.loads(sequence['steps']),
                is_active=sequence['is_active'],
                created_at=sequence['created_at']
            )
        logger.info(f"Loaded {len(self.follow_up_sequences)} follow-up sequences")
        
    async def _setup_channel_integrations(self):
        """Setup integrations for different communication channels."""
        logger.info("Setting up channel integrations")
        
        # Email integration
        self.channel_integrations[CommunicationChannel.EMAIL] = {
            'send_function': self._send_email,
            'validate_function': self._validate_email
        }
        
        # SMS integration
        self.channel_integrations[CommunicationChannel.SMS] = {
            'send_function': self._send_sms,
            'validate_function': self._validate_phone_number
        }
        
        # WhatsApp integration
        self.channel_integrations[CommunicationChannel.WHATSAPP] = {
            'send_function': self._send_whatsapp,
            'validate_function': self._validate_phone_number
        }
        
        # Phone integration
        self.channel_integrations[CommunicationChannel.PHONE] = {
            'send_function': self._send_phone_call,
            'validate_function': self._validate_phone_number
        }
        
        logger.info("Channel integrations setup complete")
        
    async def _start_scheduler(self):
        """Start the communication scheduler."""
        logger.info("Starting communication scheduler")
        asyncio.create_task(self._run_scheduler())
        
    async def _run_scheduler(self):
        """Run the communication scheduler loop."""
        while True:
            await self._process_scheduled_communications()
            await asyncio.sleep(60)  # Check every minute
            
    async def _process_scheduled_communications(self):
        """Process scheduled communications that are due."""
        now = datetime.now().isoformat()
        due_communications = [
            comm for comm in self.scheduled_communications 
            if comm['scheduled_at'] <= now
        ]
        
        for comm in due_communications:
            try:
                await self._send_communication(comm)
                self.scheduled_communications.remove(comm)
            except Exception as e:
                logger.error(f"Error processing scheduled communication: {e}")
                
    async def create_template(self, template_data: Dict[str, Any]) -> CommunicationTemplate:
        """Create a new communication template."""
        logger.info(f"Creating template: {template_data['name']}")
        
        # Validate template data
        if not template_data.get('name'):
            raise ValueError("Template name is required")
        if not template_data.get('channel'):
            raise ValueError("Communication channel is required")
        if not template_data.get('subject'):
            raise ValueError("Template subject is required")
        if not template_data.get('message'):
            raise ValueError("Template message is required")
        
        # Create template in database
        template = self.database.create_template({
            'name': template_data['name'],
            'channel': template_data['channel'],
            'subject': template_data['subject'],
            'message': template_data['message'],
            'variables': json.dumps(template_data.get('variables', [])),
            'is_active': template_data.get('is_active', True),
            'created_at': datetime.now().isoformat()
        })
        
        # Add to cache
        self.templates[template['id']] = CommunicationTemplate(
            id=template['id'],
            name=template['name'],
            channel=CommunicationChannel(template['channel']),
            subject=template['subject'],
            message=template['message'],
            variables=json.loads(template['variables']),
            is_active=template['is_active'],
            created_at=template['created_at']
        )
        
        logger.info(f"Template created: {template['id']}")
        return self.templates[template['id']]
        
    async def create_follow_up_sequence(self, sequence_data: Dict[str, Any]) -> FollowUpSequence:
        """Create a new follow-up sequence."""
        logger.info(f"Creating follow-up sequence: {sequence_data['name']}")
        
        # Validate sequence data
        if not sequence_data.get('name'):
            raise ValueError("Sequence name is required")
        if not sequence_data.get('trigger_event'):
            raise ValueError("Trigger event is required")
        if not sequence_data.get('steps'):
            raise ValueError("Sequence steps are required")
        
        # Create sequence in database
        sequence = self.database.create_follow_up_sequence({
            'name': sequence_data['name'],
            'trigger_event': sequence_data['trigger_event'],
            'steps': json.dumps(sequence_data['steps']),
            'is_active': sequence_data.get('is_active', True),
            'created_at': datetime.now().isoformat()
        })
        
        # Add to cache
        self.follow_up_sequences[sequence['id']] = FollowUpSequence(
            id=sequence['id'],
            name=sequence['name'],
            trigger_event=sequence['trigger_event'],
            steps=json.loads(sequence['steps']),
            is_active=sequence['is_active'],
            created_at=sequence['created_at']
        )
        
        logger.info(f"Follow-up sequence created: {sequence['id']}")
        return self.follow_up_sequences[sequence['id']]
        
    async def send_communication(self, model_id: int, template_id: int, variables: Dict[str, Any] = None, 
                               custom_subject: str = None, custom_message: str = None) -> Communication:
        """Send a communication using a template."""
        logger.info(f"Sending communication for model {model_id} using template {template_id}")
        
        # Get template
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Get model information
        model = self.database.get_model(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        # Prepare message
        subject = custom_subject or template.subject
        message = custom_message or template.message
        
        # Apply variables if provided
        if variables:
            try:
                subject = subject.format(**variables)
                message = message.format(**variables)
            except KeyError as e:
                raise ValueError(f"Missing variable in template: {e}")
        
        # Create communication record
        communication = self.database.create_communication({
            'model_id': model_id,
            'recruiter_id': model.get('recruiter_id'),
            'template_id': template_id,
            'channel': template.channel.value,
            'subject': subject,
            'message': message,
            'direction': 'outbound',
            'status': 'sent',
            'sent_at': datetime.now().isoformat(),
            'read_at': None,
            'metadata': json.dumps({
                'template_id': template_id,
                'variables': variables
            })
        })
        
        # Send through appropriate channel
        await self._send_through_channel(communication)
        
        # Update model last contacted
        self.database.update_model_last_contacted(model_id, datetime.now().isoformat())
        
        logger.info(f"Communication sent: {communication['id']}")
        return Communication(
            id=communication['id'],
            model_id=communication['model_id'],
            recruiter_id=communication['recruiter_id'],
            template_id=communication['template_id'],
            channel=CommunicationChannel(communication['channel']),
            subject=communication['subject'],
            message=communication['message'],
            direction=communication['direction'],
            status=CommunicationStatus(communication['status']),
            sent_at=communication['sent_at'],
            delivered_at=communication['delivered_at'],
            read_at=communication['read_at'],
            scheduled_at=communication['scheduled_at'],
            metadata=json.loads(communication['metadata'])
        )
        
    async def schedule_communication(self, model_id: int, template_id: int, send_at: str, 
                                   variables: Dict[str, Any] = None) -> Communication:
        """Schedule a communication for future delivery."""
        logger.info(f"Scheduling communication for model {model_id} at {send_at}")
        
        # Get template
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Get model information
        model = self.database.get_model(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        # Prepare message
        subject = template.subject
        message = template.message
        
        # Apply variables if provided
        if variables:
            try:
                subject = subject.format(**variables)
                message = message.format(**variables)
            except KeyError as e:
                raise ValueError(f"Missing variable in template: {e}")
        
        # Create scheduled communication
        communication = self.database.create_communication({
            'model_id': model_id,
            'recruiter_id': model.get('recruiter_id'),
            'template_id': template_id,
            'channel': template.channel.value,
            'subject': subject,
            'message': message,
            'direction': 'outbound',
            'status': 'scheduled',
            'sent_at': send_at,
            'read_at': None,
            'metadata': json.dumps({
                'template_id': template_id,
                'variables': variables
            })
        })
        
        # Add to scheduled communications
        self.scheduled_communications.append({
            'id': communication['id'],
            'model_id': model_id,
            'template_id': template_id,
            'send_at': send_at,
            'subject': subject,
            'message': message,
            'variables': variables
        })
        
        # Update model next follow-up
        self.database.update_model_next_follow_up(model_id, send_at)
        
        logger.info(f"Communication scheduled: {communication['id']}")
        return Communication(
            id=communication['id'],
            model_id=communication['model_id'],
            recruiter_id=communication['recruiter_id'],
            template_id=communication['template_id'],
            channel=CommunicationChannel(communication['channel']),
            subject=communication['subject'],
            message=communication['message'],
            direction=communication['direction'],
            status=CommunicationStatus(communication['status']),
            sent_at=communication['sent_at'],
            delivered_at=communication['delivered_at'],
            read_at=communication['read_at'],
            scheduled_at=communication['scheduled_at'],
            metadata=json.loads(communication['metadata'])
        )
        
    async def trigger_follow_up_sequence(self, model_id: int, trigger_event: str) -> List[Communication]:
        """Trigger a follow-up sequence for a model."""
        logger.info(f"Triggering follow-up sequence for model {model_id} on event {trigger_event}")
        
        communications = []
        
        # Find matching sequences
        for sequence in self.follow_up_sequences.values():
            if sequence.trigger_event == trigger_event and sequence.is_active:
                for step in sequence.steps:
                    try:
                        # Schedule each step
                        send_at = (datetime.fromisoformat(step['delay']) + 
                                  datetime.now()).isoformat()
                        comm = await self.schedule_communication(
                            model_id, 
                            step['template_id'], 
                            send_at,
                            step.get('variables')
                        )
                        communications.append(comm)
                    except Exception as e:
                        logger.error(f"Error scheduling step in sequence {sequence.id}: {e}")
                        continue
        
        logger.info(f"Follow-up sequence triggered: {len(communications)} communications scheduled")
        return communications
        
    async def get_communication_analytics(self, date_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Get communication analytics."""
        logger.info(f"Getting communication analytics for date range {date_range}")
        
        # Get all communications
        communications = self.database.get_all_communications()
        
        if date_range:
            start_date = datetime.fromisoformat(date_range.get('start'))
            end_date = datetime.fromisoformat(date_range.get('end'))
            communications = [
                comm for comm in communications 
                if start_date <= datetime.fromisoformat(comm['sent_at']) <= end_date
            ]
        
        # Calculate analytics
        total_communications = len(communications)
        
        # Channel breakdown
        channel_counts = {}
        for comm in communications:
            channel = comm['channel']
            channel_counts[channel] = channel_counts.get(channel, 0) + 1
        
        # Status breakdown
        status_counts = {}
        for comm in communications:
            status = comm['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Response time analysis
        response_times = []
        for comm in communications:
            if comm['direction'] == 'inbound' and comm['read_at']:
                sent_time = datetime.fromisoformat(comm['sent_at'])
                read_time = datetime.fromisoformat(comm['read_at'])
                response_time = (read_time - sent_time).total_seconds() / 3600  # hours
                response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        analytics = {
            'total_communications': total_communications,
            'channel_breakdown': channel_counts,
            'status_breakdown': status_counts,
            'average_response_time_hours': avg_response_time,
            'analytics_date': datetime.now().isoformat(),
            'date_range': date_range
        }
        
        logger.info(f"Communication analytics calculated: {analytics}")
        return analytics
        
    async def generate_communication_report(self, date_range: Dict[str, str]) -> Dict[str, Any]:
        """Generate a comprehensive communication report."""
        logger.info(f"Generating communication report for date range {date_range}")
        
        # Get analytics
        analytics = await self.get_communication_analytics(date_range)
        
        # Generate insights
        insights = []
        
        # Channel effectiveness
        if analytics['channel_breakdown']:
            best_channel = max(analytics['channel_breakdown'].items(), key=lambda x: x[1])
            insights.append(f"Best channel: {best_channel[0]} with {best_channel[1]} communications")
        
        # Response time insights
        if analytics['average_response_time_hours'] > 24:
            insights.append('Average response time exceeds 24 hours - consider faster follow-ups')
        elif analytics['average_response_time_hours'] < 4:
            insights.append('Excellent response times - maintaining quick candidate engagement')
        
        # Status analysis
        if analytics['status_breakdown'].get('failed', 0) > 0:
            insights.append(f"There are {analytics['status_breakdown']['failed']} failed communications")
        
        report = {
            'date_range': date_range,
            'analytics': analytics,
            'insights': insights,
            'report_date': datetime.now().isoformat(),
            'summary': self._generate_report_summary(analytics)
        }
        
        logger.info(f"Communication report generated: {report}")
        return report
        
    def _generate_report_summary(self, analytics: Dict[str, Any]) -> str:
        """Generate a summary for the communication report."""
        summary = f"Communication Report ({analytics['date_range']['start']} to {analytics['date_range']['end']}): "
        summary += f"{analytics['total_communications']} total communications. "
        summary += f"Average response time: {analytics['average_response_time_hours']:.2f} hours. "
        
        if analytics['channel_breakdown']:
            summary += "Channels: "
            summary += ", ".join([f"{k}: {v}" for k, v in analytics['channel_breakdown'].items()])
            
        return summary
        
    async def _send_through_channel(self, communication: Dict[str, Any]):
        """Send communication through the appropriate channel."""
        channel = communication['channel']
        
        if channel not in self.channel_integrations:
            raise ValueError(f"Channel {channel} not supported")
        
        send_function = self.channel_integrations[channel]['send_function']
        await send_function(communication)
        
    async def _send_email(self, communication: Dict[str, Any]):
        """Send email communication."""
        logger.info(f"Sending email to model {communication['model_id']}")
        # TODO: Implement actual email sending logic
        # This would integrate with an email service like SendGrid, Mailgun, etc.
        logger.info(f"Email sent: {communication['subject']}")
        
    async def _send_sms(self, communication: Dict[str, Any]):
        """Send SMS communication."""
        logger.info(f"Sending SMS to model {communication['model_id']}")
        # TODO: Implement actual SMS sending logic
        # This would integrate with an SMS service like Twilio, Plivo, etc.
        logger.info(f"SMS sent: {communication['subject']}")
        
    async def _send_whatsapp(self, communication: Dict[str, Any]):
        """Send WhatsApp communication."""
        logger.info(f"Sending WhatsApp message to model {communication['model_id']}")
        # TODO: Implement actual WhatsApp sending logic
        # This would integrate with WhatsApp Business API
        logger.info(f"WhatsApp message sent: {communication['subject']}")
        
    async def _send_phone_call(self, communication: Dict[str, Any]):
        """Send phone call communication."""
        logger.info(f"Initiating phone call to model {communication['model_id']}")
        # TODO: Implement actual phone call logic
        # This would integrate with a telephony service
        logger.info(f"Phone call initiated: {communication['subject']}")
        
    async def _validate_email(self, email: str) -> bool:
        """Validate email address."""
        # Simple email validation
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
        
    async def _validate_phone_number(self, phone: str) -> bool:
        """Validate phone number."""
        # Simple phone number validation (digits only, 10-15 characters)
        return phone.isdigit() and 10 <= len(phone) <= 15
        
    def close(self):
        """Close the database connection."""
        self.database.close()
        
    async def initialize(self):
        """Initialize communication service."""
        logger.info("Initializing CommunicationService")
        await self._load_templates()
        await self._load_follow_up_sequences()
        await self._setup_channel_integrations()
        await self._start_scheduler()
        
    async def _load_templates(self):
        """Load communication templates from database."""
        logger.info("Loading communication templates")
        templates = self.database.get_all_templates()
        for template in templates:
            self.templates[template['id']] = CommunicationTemplate(
                id=template['id'],
                name=template['name'],
                channel=CommunicationChannel(template['channel']),
                subject=template['subject'],
                message=template['message'],
                variables=json.loads(template['variables']),
                is_active=template['is_active'],
                created_at=template['created_at']
            )
        logger.info(f"Loaded {len(self.templates)} templates")
        
    async def _load_follow_up_sequences(self):
        """Load follow-up sequences from database."""
        logger.info("Loading follow-up sequences")
        sequences = self.database.get_all_follow_up_sequences()
        for sequence in sequences:
            self.follow_up_sequences[sequence['id']] = FollowUpSequence(
                id=sequence['id'],
                name=sequence['name'],
                trigger_event=sequence['trigger_event'],
                steps=json.loads(sequence['steps']),
                is_active=sequence['is_active'],
                created_at=sequence['created_at']
            )
        logger.info(f"Loaded {len(self.follow_up_sequences)} follow-up sequences")
        
    async def _setup_channel_integrations(self):
        """Setup integrations for different communication channels."""
        logger.info("Setting up channel integrations")
        
        # Email integration
        self.channel_integrations[CommunicationChannel.EMAIL] = {
            'send_function': self._send_email,
            'validate_function': self._validate_email
        }
        
        # SMS integration
        self.channel_integrations[CommunicationChannel.SMS] = {
            'send_function': self._send_sms,
            'validate_function': self._validate_phone_number
        }
        
        # WhatsApp integration
        self.channel_integrations[CommunicationChannel.WHATSAPP] = {
            'send_function': self._send_whatsapp,
            'validate_function': self._validate_phone_number
        }
        
        # Phone integration
        self.channel_integrations[CommunicationChannel.PHONE] = {
            'send_function': self._send_phone_call,
            'validate_function': self._validate_phone_number
        }
        
        logger.info("Channel integrations setup complete")
        
    async def _start_scheduler(self):
        """Start the communication scheduler."""
        logger.info("Starting communication scheduler")
        asyncio.create_task(self._run_scheduler())
        
    async def _run_scheduler(self):
        """Run the communication scheduler loop."""
        while True:
            await self._process_scheduled_communications()
            await asyncio.sleep(60)  # Check every minute
            
    async def _process_scheduled_communications(self):
        """Process scheduled communications that are due."""
        now = datetime.now().isoformat()
        due_communications = [
            comm for comm in self.scheduled_communications 
            if comm['scheduled_at'] <= now
        ]
        
        for comm in due_communications:
            try:
                await self._send_communication(comm)
                self.scheduled_communications.remove(comm)
            except Exception as e:
                logger.error(f"Error processing scheduled communication: {e}")
                
    async def create_template(self, template_data: Dict[str, Any]) -> CommunicationTemplate:
        """Create a new communication template."""
        logger.info(f"Creating template: {template_data['name']}")
        
        # Validate template data
        if not template_data.get('name'):
            raise ValueError("Template name is required")
        if not template_data.get('channel'):
            raise ValueError("Communication channel is required")
        if not template_data.get('subject'):
            raise ValueError("Template subject is required")
        if not template_data.get('message'):
            raise ValueError("Template message is required")
        
        # Create template in database
        template = self.database.create_template({
            'name': template_data['name'],
            'channel': template_data['channel'],
            'subject': template_data['subject'],
            'message': template_data['message'],
            'variables': json.dumps(template_data.get('variables', [])),
            'is_active': template_data.get('is_active', True),
            'created_at': datetime.now().isoformat()
        })
        
        # Add to cache
        self.templates[template['id']] = CommunicationTemplate(
            id=template['id'],
            name=template['name'],
            channel=CommunicationChannel(template['channel']),
            subject=template['subject'],
            message=template['message'],
            variables=json.loads(template['variables']),
            is_active=template['is_active'],
            created_at=template['created_at']
        )
        
        logger.info(f"Template created: {template['id']}")
        return self.templates[template['id']]
        
    async def create_follow_up_sequence(self, sequence_data: Dict[str, Any]) -> FollowUpSequence:
        """Create a new follow-up sequence."""
        logger.info(f"Creating follow-up sequence: {sequence_data['name']}")
        
        # Validate sequence data
        if not sequence_data.get('name'):
            raise ValueError("Sequence name is required")
        if not sequence_data.get('trigger_event'):
            raise ValueError("Trigger event is required")
        if not sequence_data.get('steps'):
            raise ValueError("Sequence steps are required")
        
        # Create sequence in database
        sequence = self.database.create_follow_up_sequence({
            'name': sequence_data['name'],
            'trigger_event': sequence_data['trigger_event'],
            'steps': json.dumps(sequence_data['steps']),
            'is_active': sequence_data.get('is_active', True),
            'created_at': datetime.now().isoformat()
        })
        
        # Add to cache
        self.follow_up_sequences[sequence['id']] = FollowUpSequence(
            id=sequence['id'],
            name=sequence['name'],
            trigger_event=sequence['trigger_event'],
            steps=json.loads(sequence['steps']),
            is_active=sequence['is_active'],
            created_at=sequence['created_at']
        )
        
        logger.info(f"Follow-up sequence created: {sequence['id']}")
        return self.follow_up_sequences[sequence['id']]
        
    async def send_communication(self, model_id: int, template_id: int, variables: Dict[str, Any] = None, 
                               custom_subject: str = None, custom_message: str = None) -> Communication:
        """Send a communication using a template."""
        logger.info(f"Sending communication for model {model_id} using template {template_id}")
        
        # Get template
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Get model information
        model = self.database.get_model(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        # Prepare message
        subject = custom_subject or template.subject
        message = custom_message or template.message
        
        # Apply variables if provided
        if variables:
            try:
                subject = subject.format(**variables)
                message = message.format(**variables)
            except KeyError as e:
                raise ValueError(f"Missing variable in template: {e}")
        
        # Create communication record
        communication = self.database.create_communication({
            'model_id': model_id,
            'recruiter_id': model.get('recruiter_id'),
            'template_id': template_id,
            'channel': template.channel.value,
            'subject': subject,
            'message': message,
            'direction': 'outbound',
            'status': 'sent',
            'sent_at': datetime.now().isoformat(),
            'read_at': None,
            'metadata': json.dumps({
                'template_id': template_id,
                'variables': variables
            })
        })
        
        # Send through appropriate channel
        await self._send_through_channel(communication)
        
        # Update model last contacted
        self.database.update_model_last_contacted(model_id, datetime.now().isoformat())
        
        logger.info(f"Communication sent: {communication['id']}")
        return Communication(
            id=communication['id'],
            model_id=communication['model_id'],
            recruiter_id=communication['recruiter_id'],
            template_id=communication['template_id'],
            channel=CommunicationChannel(communication['channel']),
            subject=communication['subject'],
            message=communication['message'],
            direction=communication['direction'],
            status=CommunicationStatus(communication['status']),
            sent_at=communication['sent_at'],
            delivered_at=communication['delivered_at'],
            read_at=communication['read_at'],
            scheduled_at=communication['scheduled_at'],
            metadata=json.loads(communication['metadata'])
        )
        
    async def schedule_communication(self, model_id: int, template_id: int, send_at: str, 
                                   variables: Dict[str, Any] = None) -> Communication:
        """Schedule a communication for future delivery."""
        logger.info(f"Scheduling communication for model {model_id} at {send_at}")
        
        # Get template
        template = self.templates.get(template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        # Get model information
        model = self.database.get_model(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        # Prepare message
        subject = template.subject
        message = template.message
        
        # Apply variables if provided
        if variables:
            try:
                subject = subject.format(**variables)
                message = message.format(**variables)
            except KeyError as e:
                raise ValueError(f"Missing variable in template: {e}")
        
        # Create scheduled communication
        communication = self.database.create_communication({
            'model_id': model_id,
            'recruiter_id': model.get('recruiter_id'),
            'template_id': template_id,
            'channel': template.channel.value,
            'subject': subject,
            'message': message,
            'direction': 'outbound',
            'status': 'scheduled',
            'sent_at': send_at,
            'read_at': None,
            'metadata': json.dumps({
                'template_id': template_id,
                'variables': variables
            })
        })
        
        # Add to scheduled communications
        self.scheduled_communications.append({
            'id': communication['id'],
            'model_id': model_id,
            'template_id': template_id,
            'send_at': send_at,
            'subject': subject,
            'message': message,
            'variables': variables
        })
        
        # Update model next follow-up
        self.database.update_model_next_follow_up(model_id, send_at)
        
        logger.info(f"Communication scheduled: {communication['id']}")
        return Communication(
            id=communication['id'],
            model_id=communication['model_id'],
            recruiter_id=communication['recruiter_id'],
            template_id=communication['template_id'],
            channel=CommunicationChannel(communication['channel']),
            subject=communication['subject'],
            message=communication['message'],
            direction=communication['direction'],
            status=CommunicationStatus(communication['status']),
            sent_at=communication['sent_at'],
            delivered_at=communication['delivered_at'],
            read_at=communication['read_at'],
            scheduled_at=communication['scheduled_at'],
            metadata=json.loads(communication['metadata'])
        )
        
    async def trigger_follow_up_sequence(self, model_id: int, trigger_event: str) -> List[Communication]:
        """Trigger a follow-up sequence for a model."""
        logger.info(f"Triggering follow-up sequence for model {model_id} on event {trigger_event}")
        
        communications = []
        
        # Find matching sequences
        for sequence in self.follow_up_sequences.values():
            if sequence.trigger_event == trigger_event and sequence.is_active:
                for step in sequence.steps:
                    try:
                        # Schedule each step
                        send_at = (datetime.fromisoformat(step['delay']) + 
                                  datetime.now()).isoformat()
                        comm = await self.schedule_communication(
                            model_id, 
                            step['template_id'], 
                            send_at,
                            step.get('variables')
                        )
                        communications.append(comm)
                    except Exception as e:
                        logger.error(f"Error scheduling step in sequence {sequence.id}: {e}")
                        continue
        
        logger.info(f"Follow-up sequence triggered: {len(communications)} communications scheduled")
        return communications
        
    async def get_communication_analytics(self, date_range: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Get communication analytics."""
        logger.info(f"Getting communication analytics for date range {date_range}")
        
        # Get all communications
        communications = self.database.get_all_communications()
        
        if date_range:
            start_date = datetime.fromisoformat(date_range.get('start'))
            end_date = datetime.fromisoformat(date_range.get('end'))
            communications = [
                comm for comm in communications 
                if start_date <= datetime.fromisoformat(comm['sent_at']) <= end_date
            ]
        
        # Calculate analytics
        total_communications = len(communications)
        
        # Channel breakdown
        channel_counts = {}
        for comm in communications:
            channel = comm['channel']
            channel_counts[channel] = channel_counts.get(channel, 0) + 1
        
        # Status breakdown
        status_counts = {}
        for comm in communications:
            status = comm['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Response time analysis
        response_times = []
        for comm in communications:
            if comm['direction'] == 'inbound' and comm['read_at']:
                sent_time = datetime.fromisoformat(comm['sent_at'])
                read_time = datetime.fromisoformat(comm['read_at'])
                response_time = (read_time - sent_time).total_seconds() / 3600  # hours
                response_times.append(response_time)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        analytics = {
            'total_communications': total_communications,
            'channel_breakdown': channel_counts,
            'status_breakdown': status_counts,
            'average_response_time_hours': avg_response_time,
            'analytics_date': datetime.now().isoformat(),
            'date_range': date_range
        }
        
        logger.info(f"Communication analytics calculated: {analytics}")
        return analytics
        
    async def generate_communication_report(self, date_range: Dict[str, str]) -> Dict[str, Any]:
        """Generate a comprehensive communication report."""
        logger.info(f"Generating communication report for date range {date_range}")
        
        # Get analytics
        analytics = await self.get_communication_analytics(date_range)
        
        # Generate insights
        insights = []
        
        # Channel effectiveness
        if analytics['channel_breakdown']:
            best_channel = max(analytics['channel_breakdown'].items(), key=lambda x: x[1])
            insights.append(f"Best channel: {best_channel[0]} with {best_channel[1]} communications")
        
        # Response time insights
        if analytics['average_response_time_hours'] > 24:
            insights.append('Average response time exceeds 24 hours - consider faster follow-ups')
        elif analytics['average_response_time_hours'] < 4:
            insights.append('Excellent response times - maintaining quick candidate engagement')
        
        # Status analysis
        if analytics['status_breakdown'].get('failed', 0) > 0:
            insights.append(f"There are {analytics['status_breakdown']['failed']} failed communications")
        
        report = {
            'date_range': date_range,
            'analytics': analytics,
            'insights': insights,
            'report_date': datetime.now().isoformat(),
            'summary': self._generate_report_summary(analytics)
        }
        
        logger.info(f"Communication report generated: {report}")
        return report
        
    def _generate_report_summary(self, analytics: Dict[str, Any]) -> str:
        """Generate a summary for the communication report."""
        summary = f"Communication Report ({analytics['date_range']['start']} to {analytics['date_range']['end']}): "
        summary += f"{analytics['total_communications']} total communications. "
        summary += f"Average response time: {analytics['average_response_time_hours']:.2f} hours. "
        
        if analytics['channel_breakdown']:
            summary += "Channels: "
            summary += ", ".join([f"{k}: {v}" for k, v in analytics['channel_breakdown'].items()])
            
        return summary
        
    async def _send_through_channel(self, communication: Dict[str, Any]):
        """Send communication through the appropriate channel."""
        channel = communication['channel']
        
        if channel not in self.channel_integrations:
            raise ValueError(f"Channel {channel} not supported")
        
        send_function = self.channel_integrations[channel]['send_function']
        await send_function(communication)
        
    async def _send_email(self, communication: Dict[str, Any]):
        """Send email communication."""
        logger.info(f"Sending email to model {communication['model_id']}")
        # TODO: Implement actual email sending logic
        # This would integrate with an email service like SendGrid, Mailgun, etc.
        logger.info(f"Email sent: {communication['subject']}")
        
    async def _send_sms(self, communication: Dict[str, Any]):
        """Send SMS communication."""
        logger.info(f"Sending SMS to model {communication['model_id']}")
        # TODO: Implement actual SMS sending logic
        # This would integrate with an SMS service like Twilio, Plivo, etc.
        logger.info(f"SMS sent: {communication['subject']}")
        
    async def _send_whatsapp(self, communication: Dict[str, Any]):
        """Send WhatsApp communication."""
        logger.info(f"Sending WhatsApp message to model {communication['model_id']}")
        # TODO: Implement actual WhatsApp sending logic
        # This would integrate with WhatsApp Business API
        logger.info(f"WhatsApp message sent: {communication['subject']}")
        
    async def _send_phone_call(self, communication: Dict[str, Any]):
        """Send phone call communication."""
        logger.info(f"Initiating phone call to model {communication['model_id']}")
        # TODO: Implement actual phone call logic
        # This would integrate with a telephony service
        logger.info(f"Phone call initiated: {communication['subject']}")
        
    async def _validate_email(self, email: str) -> bool:
        """Validate email address."""
        # Simple email validation
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
        
    async def _validate_phone_number(self, phone: str) -> bool:
        """Validate phone number."""
        # Simple phone number validation (digits only, 10-15 characters)
        return phone.isdigit() and 10 <= len(phone) <= 15