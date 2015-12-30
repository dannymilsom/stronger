from django.conf import settings as stronger_settings
from django.views.generic import TemplateView


class HomeTemplateView(TemplateView):
    """
    Renders the homepage template - with links for users to authenticate 
    or register new accounts.
    """
    template_name = 'home.html'


class AboutTemplateView(TemplateView):
    """
    Renders the about template - describing the motivations behind the 
    site and the technology used to create it.
    """
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        context = super(AboutTemplateView, self).get_context_data(**kwargs)
        context['github_url'] = stronger_settings.GITHUB_URL
        return context
