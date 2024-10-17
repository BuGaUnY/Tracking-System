from django.views.generic import TemplateView
from django.shortcuts import render
class IndexView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        open_liff = self.request.GET.get('open_liff')
        if open_liff:
            return render(request, 'spinners.html')
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
