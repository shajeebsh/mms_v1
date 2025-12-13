from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page


class HomePage(Page):
    intro = models.CharField(max_length=250, blank=True)
    template = "home/home_page.html"

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]
