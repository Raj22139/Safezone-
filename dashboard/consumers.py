"""
SafeZone AI — WebSocket Consumers
Real-time crime feed and live safety updates
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from datetime import datetime


class CrimeFeedConsumer(AsyncWebsocketConsumer):
    """Live crime feed — broadcasts new crime records to all connected clients."""

    async def connect(self):
        self.room_group = 'crime_feed'
        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type':    'connected',
            'message': 'Connected to SafeZone AI Live Feed',
            'time':    datetime.now().strftime('%H:%M:%S'),
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        """Handle messages from client (e.g., area filter)."""
        try:
            data    = json.loads(text_data)
            area_id = data.get('area_id')
            level   = data.get('level', '')
            feed    = await self.get_feed(area_id, level)
            await self.send(text_data=json.dumps({'type': 'feed_update', 'data': feed}))
        except Exception as e:
            await self.send(text_data=json.dumps({'type': 'error', 'message': str(e)}))

    async def crime_update(self, event):
        """Receive broadcast from channel layer and forward to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'new_crime',
            'data': event['data'],
        }))

    @database_sync_to_async
    def get_feed(self, area_id=None, level=''):
        from crime.models import CrimeRecord
        from django.db.models import Q
        qs = CrimeRecord.objects.filter(status='approved').select_related('area').order_by('-created_at')
        if area_id:
            qs = qs.filter(area_id=area_id)
        if level:
            qs = qs.filter(area__risk_level=level)
        result = []
        for r in qs[:20]:
            result.append({
                'id':         r.id,
                'area':       str(r.area),
                'area_id':    r.area.id,
                'crime_type': r.get_crime_type_display(),
                'severity':   r.severity,
                'risk_level': r.area.risk_level,
                'risk_score': r.area.risk_score,
                'description':r.description[:100],
                'date':       r.incident_date.strftime('%b %d, %Y'),
                'time':       r.created_at.strftime('%H:%M'),
            })
        return result


class SafetyAlertConsumer(AsyncWebsocketConsumer):
    """Per-user safety alerts — notifies user when subscribed area risk changes."""

    async def connect(self):
        if self.scope['user'].is_anonymous:
            await self.close()
            return
        self.user_group = f"user_{self.scope['user'].id}"
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'user_group'):
            await self.channel_layer.group_discard(self.user_group, self.channel_name)

    async def safety_alert(self, event):
        """Forward alert to this user's WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'safety_alert',
            'data': event['data'],
        }))

    async def receive(self, text_data):
        pass
