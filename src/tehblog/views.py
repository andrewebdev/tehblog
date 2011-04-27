from django.views.generic import DetailView

from models import Category, Entry

class CategoryView(DetailView):
    slug_field = 'slug'
    template_name = 'tehblog/list_view.html'
    model = Category
    context_object_name = "category"

    def get_context_data(self, **kwargs):
        context = super(CategoryView, self).get_context_data(**kwargs)
        context['object_list'] = Entry.objects.public().filter(
            categories=self.get_object())
        return context
