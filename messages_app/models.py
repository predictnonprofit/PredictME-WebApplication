import os
import random
import string

from django.db import models

from predict_me.constants.vars import SUBJECTS_TYPES
from users.models import Member


def generate_file_path(instance, filename):
    length = 5
    random_prefix = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    ext = filename.split('.')[-1]
    base_filename = filename.split('.')[0]
    filename = f"msg_attachment_{random_prefix}_{base_filename}.{ext}"
    return os.path.join('message_attachments', filename)


class MemberMessages(models.Model):
    sender = models.ForeignKey(to=Member, on_delete=models.CASCADE, related_name='messages_sent')
    reply = models.ForeignKey(to='self', on_delete=models.CASCADE, null=True, blank=True,
                              related_name='message_replies')
    subject = models.CharField(choices=SUBJECTS_TYPES, max_length=100, null=True, blank=True)
    other_subject = models.CharField(max_length=100, null=True, blank=True)
    attachment = models.FileField(upload_to=generate_file_path, null=True, blank=True)
    message = models.TextField(null=False)
    send_date = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False, null=True, blank=True)
    is_deleted = models.BooleanField(default=False, null=True, blank=True)

    class Meta:
        db_table = 'member_messages'
        ordering = ['-send_date']

    def __str__(self):
        return f"Message from {self.sender}, it's title {self.get_subject_display() or self.other_subject}"

    @property
    def get_replies_total_for_single_msg(self):
        return self.message_replies.all().count()
