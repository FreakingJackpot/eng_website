from django.http import Http404
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from django.views.generic.list import ListView

from .models import Category, HandbookCategory, Article, Lesson, TopicCategory, Topic, PhrasesCategory, \
    PhrasesArticle, ArticleCategory, QuizCategory, Quiz


class IndexView(TemplateView):
    template_name = 'base.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault("view", self)
        if self.extra_context is not None:
            kwargs.update(self.extra_context)
        self.add_template_data(kwargs)
        return kwargs

    def add_template_data(self, context):
        context['large_feed'] = Article.get_large_feed_data()
        materials_by_sections = Article.get_most_raited_materials_by_sections()
        materials_by_sections['tests'] = Quiz.get_most_raited_materials()
        context['materials_by_sections'] = materials_by_sections


class HandbookTopicsListView(ListView):
    home_label = _("На главную!")
    template_name = "knowledge_base/handbook/topics.html"

    def get_queryset(self):
        return HandbookCategory.objects.none()

    @cached_property
    def get_crumbs(self):
        return (('На главную!', '/'), ('Справочник', reverse("handbook")))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["topics"] = HandbookCategory.get_topics_with_lessons()
        context['breadcrumbs'] = self.get_crumbs
        return context


class DetailViewWithViewsIncrement(DetailView):
    model = Article
    section_name = None

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        if slug is not None and (pk is None or self.query_pk_and_slug):
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        if pk is None and slug is None:
            raise AttributeError(
                "Generic detail view %s must be called with either an object "
                "pk or a slug in the URLconf." % self.__class__.__name__
            )

        try:
            obj = queryset.get()
            obj.views += 1
            obj.save()
        except queryset.model.DoesNotExist:
            raise Http404(
                _("No %(verbose_name)s found matching the query")
                % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return obj

    def add_crumbs(self, context):
        context_name = self.context_object_name or self.model._meta.model_name
        object = context[context_name]
        _, section_slug, category_slug, detail_slug = self.request.path.split('/')
        context['breadcrumbs'] = (
            ('На главную!', '/'),
            (self.section_name, f'/{section_slug}'),
            (object.category.title, f'/{section_slug}/{category_slug}'),
            (object.title, f'/{section_slug}/{category_slug}/{detail_slug}'),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.add_crumbs(context)
        return context


class LessonDetailView(DetailView):
    model = Lesson
    template_name = 'knowledge_base/handbook/lesson.html'

    def get_queryset(self):
        return self.model.objects.select_related('parent').prefetch_related('child_article')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.add_crumbs(context)
        self.add_previous_and_next_ancestor_urls(context)
        return context

    def add_crumbs(self, context):
        context_name = self.context_object_name or self.model._meta.model_name
        object = context[context_name]
        context['breadcrumbs'] = (
            ('На главную!', '/'),
            ('Справочник', reverse("handbook")),
            (object.title, reverse("lesson", kwargs={'slug': object.slug}))
        )

    def add_previous_and_next_ancestor_urls(self, context):
        context_name = self.context_object_name or self.model._meta.model_name
        object = context[context_name]
        childs = object.child_article.all()
        context['next_url'] = reverse("lesson", kwargs={'slug': childs[0].slug}) if childs else None
        context['previous_url'] = reverse("lesson", kwargs={'slug': object.parent.slug}) if object.parent else None


class CategoriesBaseListView(ListView):
    type = None
    model = Category
    section_name = None

    def get_queryset(self):
        return self.model.all_with_child_count(self.type)

    def add_crumbs(self, context):
        index, section_slug, category = self.request.path.split('/')
        context['breadcrumbs'] = (
            ('На главную!', '/'),
            (self.section_name, f'/{section_slug}'),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.add_crumbs(context)
        return context


class TopicsCategoriesListView(CategoriesBaseListView):
    context_object_name = 'categories'
    model = TopicCategory
    template_name = 'knowledge_base/topics/categories.html'
    section_name = 'Топики'


class ArticlesBaseListView(ListView):
    model = Article
    category_model = Category
    section_name = 'Статьи'

    def get_queryset(self):
        return self.model.all_in_category(self.kwargs.get('slug'))

    def add_crumbs(self, context):
        _, section_slug, category, _ = self.request.path.split('/')
        category_obj = self.category_model.objects.get(slug=category)
        context['breadcrumbs'] = (
            ('На главную!', '/'),
            (self.section_name, f'/{section_slug}'),
            (category_obj.title, f'/{section_slug}/{category}'),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category_model.objects.get(slug=self.kwargs.get('slug'))
        self.add_crumbs(context)
        return context


class TopicsListView(ArticlesBaseListView):
    context_object_name = 'articles'
    model = Topic
    category_model = TopicCategory
    template_name = 'knowledge_base/topics/topics.html'
    section_name = 'Топики'


class TopicDetailView(DetailViewWithViewsIncrement):
    model = Topic
    section_name = 'Топики'
    template_name = 'knowledge_base/topics/topic.html'


class PhrasebookCategoriesListView(CategoriesBaseListView):
    context_object_name = 'categories'
    model = PhrasesCategory
    template_name = 'knowledge_base/phrasebook/categories.html'
    section_name = 'Разговорник'


class PhrasesArticlesListView(ArticlesBaseListView):
    context_object_name = 'articles'
    model = PhrasesArticle
    category_model = PhrasesCategory
    template_name = 'knowledge_base/phrasebook/phrases_articles.html'
    section_name = 'Разговорник'


class PhrasesArticleDetailView(DetailViewWithViewsIncrement):
    context_object_name = 'phrases_article'
    model = PhrasesArticle
    section_name = 'Разговорник'
    template_name = 'knowledge_base/phrasebook/phrases_article.html'


class ArticleCategoriesListView(CategoriesBaseListView):
    context_object_name = 'categories'
    model = ArticleCategory
    template_name = 'knowledge_base/articles/categories.html'
    section_name = 'Статьи'


class ArticlesListView(ArticlesBaseListView):
    context_object_name = 'articles'
    category_model = ArticleCategory
    template_name = 'knowledge_base/articles/articles.html'


class ArticleDetailView(DetailViewWithViewsIncrement):
    section_name = 'Статьи'
    template_name = 'knowledge_base/articles/article.html'


class QuizCategoriesListView(CategoriesBaseListView):
    context_object_name = 'categories'
    model = QuizCategory
    template_name = 'knowledge_base/quizzes/categories.html'
    section_name = 'Тесты'


class QuizzesListView(ArticlesBaseListView):
    model = Quiz
    category_model = QuizCategory
    context_object_name = 'quizzes'
    template_name = 'knowledge_base/quizzes/quizzes.html'
    section_name = 'Тесты'


class QuizDetailView(DetailView):
    model = Quiz
    context_object_name = 'quiz_data'
    template_name = 'knowledge_base/quizzes/quiz.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)

    def add_crumbs(self, context):
        _, section_slug, category_slug, detail_slug = self.request.path.split('/')
        object = self.model.objects.select_related('category').get(slug=detail_slug)
        context['breadcrumbs'] = (
            ('На главную!', '/'),
            ('Тесты', f'/{section_slug}'),
            (object.category.title, f'/{section_slug}/{category_slug}'),
            (object.title, f'/{section_slug}/{category_slug}/{detail_slug}')
        )

    def get_context_data(self, **kwargs):
        context = {}
        slug = self.kwargs.get(self.slug_url_kwarg)

        if slug:
            try:
                self.object = self.model.get_quiz_article_data(slug)
                context[self.context_object_name] = self.object
                self.model.increase_views_by_one(slug)

            except self.model.DoesNotExist:
                raise Http404(
                    _("No %(verbose_name)s found matching the query") % {"verbose_name": self.model._meta.verbose_name})

        else:
            raise AttributeError(
                "Generic detail view %s must be called with either an object "
                "pk or a slug in the URLconf." % self.__class__.__name__
            )
        context.update(kwargs)
        self.add_crumbs(context)
        return super().get_context_data(**context)
