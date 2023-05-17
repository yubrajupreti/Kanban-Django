from django.db import models
from base.models import TimeStampedModel
from user.models import User

# Create your models here.
def card_attachment_image_path(instance, filename):
    return "card/attachment/{}/{}".format(instance.id, filename)

class Board(TimeStampModel):
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(
        User, on_delete=models.RESTRICT, related_name="board_owner"
    )
    members = models.ManyToManyField(User, related_name="board_member")


    def __str__(self):
        return self.name


class Tag(TimeStampedModel):
    name = models.CharField(max_length=150)
    board = models.ForeignKey("Board", on_delete=models.CASCADE, related_name="tags")


    def __str__(self):
        return self.name
    

class Column(TimeStampedModel):
    title = models.CharField(max_length=255)
    board = models.ForeignKey("Board", on_delete=models.CASCADE, related_name="column")
    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title
    

class Card(TimeStampedModel):
    PRIORITY=(
        ('low','low'),
        ('medium','medium'),
        ('high','high')

    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=1, choices=PRIORITY, default='medium')
    tags = models.ManyToManyField(Tag, related_name="card_tag")
    assignees = models.ManyToManyField(User, related_name="card_assigned")
    attachmnet=models.FieldFile(upload_to=card_attachment_image_path,blank=True,null=True)

    repoter=models.ForeignKey(User,on_delete=models.RESTRICT)
    column = models.ForeignKey(Column, on_delete=models.CASCADE, related_name="card_column")
    order = models.PositiveIntegerField(default=0, editable=False, db_index=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title
    

class Comment(TimeStampedModel):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="card_comment")
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name="commentor")
    text = models.TextField()

    # class Meta:
    #     ordering = ["created"]


