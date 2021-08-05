from django.db import models
from users.models import Member

# Create your models here.


# class MemberMessages(models.Model):
#     class Meta:
#         db_table = 'members_messages'
#
#     def __str__(self):
#         return f"Message from {self.sender} to {self.receiver}, it's title {self.subject}"
#
#     sender = models.ForeignKey(to=Member, on_delete=models.CASCADE, related_name='messages_send')
#     receiver = models.ForeignKey(to=Member, on_delete=models.CASCADE, related_name="messages_received")
#     subject = models.CharField(max_length=250, null=True, blank=True)
#     file_attachment = models.FileField(upload_to='message_attachments', null=True, blank=True)
#     message = models.TextField()
#     send_date = models.DateTimeField(auto_now_add=True)
#     is_seen = models.BooleanField(default=False, null=True, blank=True)
#     is_deleted = models.BooleanField(default=False, null=True, blank=True)

