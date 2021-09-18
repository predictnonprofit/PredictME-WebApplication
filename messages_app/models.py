from django.db import models
from users.models import Member
from predict_me.constants.vars import SUBJECTS_TYPES


class MemberMessages(models.Model):
    sender = models.ForeignKey(to=Member, on_delete=models.CASCADE, related_name='messages_sent')
    reply = models.ForeignKey(to='self', on_delete=models.CASCADE, null=True, blank=True, related_name='message_replies')
    # reply = models.One
    subject = models.CharField(choices=SUBJECTS_TYPES, max_length=100, null=True, blank=True)
    other_subject = models.CharField(max_length=100, null=True, blank=True)
    attachment = models.FileField(upload_to='message_attachments', null=True, blank=True)
    message = models.TextField(null=False)
    send_date = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False, null=True, blank=True)
    is_deleted = models.BooleanField(default=False, null=True, blank=True)

    class Meta:
        db_table = 'member_messages'
        ordering = ['-send_date']

    def __str__(self):
        return f"Message from {self.sender}, it's title {self.subject}"
