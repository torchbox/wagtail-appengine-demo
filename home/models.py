from __future__ import absolute_import, unicode_literals

from django.db import models
from wagtail.wagtailcore.models import Page
from wagtail.wagtailadmin.edit_handlers import FieldPanel
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore import blocks
from wagtail.wagtailadmin.edit_handlers import StreamFieldPanel
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtailembeds.blocks import EmbedBlock


class HomePage(Page):
    date = models.DateField("Post date")
    summary = models.CharField(max_length=250)
    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title", icon="title")),
        ('paragraph', blocks.RichTextBlock(
            icon="pilcrow", 
            features=['bold', 'italic', 'link']
        )),
        ('image', ImageChooserBlock(icon="image")),
        ('embed', EmbedBlock(icon="media")),
    ])
    
    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('summary'),
        StreamFieldPanel('body', classname="full"),
    ]
