from django.http import Http404
from django.views.generic import DetailView, TemplateView

from tagging.models import Tag, TaggedItem
from models import Category, Entry

class CategoryView(DetailView):
    model = Category
    context_object_name = "category"
    template_name = 'tehblog/list_view.html'

    def get_context_data(self, **kwargs):
        context = super(CategoryView, self).get_context_data(**kwargs)
        context['object_list'] = Entry.objects.public().filter(
            categories=self.get_object())
        return context

class TagView(TemplateView):
    template_name = 'tehblog/list_view.html'

    def get_context_data(self, **kwargs):
        context = super(TagView, self).get_context_data(**kwargs)
        tagname = kwargs.get('tag', None)
        if tagname:
            tag = Tag.objects.get(name=tagname)
            context['object_list'] = TaggedItem.objects.get_by_model(
                Entry.objects.public(), [tag])
            context['object'] = tag
            return context
        else:
            raise Http404
