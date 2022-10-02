from django.http import Http404
from django.utils.translation import gettext as _
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Category, HandbookCategory, Article, Lesson, TopicCategory, Topic, PhrasesCategory, \
    PhrasesArticle, ArticleCategory, QuizCategory, Quiz


class HandbookTopicsListView(ListView):
    def get(self, request, *args, **kwargs):
        topics = HandbookCategory.get_topics_with_lessons()
        return render(request, 'knowledge_base/handbook/topics.html', {'topics': topics, })


class DetailViewWithViewsIncrement(DetailView):
    model = Article

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


class LessonDetailView(DetailView):
    model = Lesson
    template_name = 'knowledge_base/handbook/lesson.html'


class CategoriesBaseListView(ListView):
    type: str | None = None
    model = Category

    def get_queryset(self):
        return self.model.all_with_child_count(self.type)


class TopicsCategoriesListView(CategoriesBaseListView):
    context_object_name = 'categories'
    model = TopicCategory
    template_name = 'knowledge_base/topics/categories.html'


class ArticlesBaseListView(ListView):
    model = Article
    category_model = Category

    def get_queryset(self):
        return self.model.all_in_category(self.kwargs.get('slug'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category_model.objects.get(slug=self.kwargs.get('slug'))
        return context


class TopicsListView(ArticlesBaseListView):
    context_object_name = 'articles'
    model = Topic
    category_model = TopicCategory
    template_name = 'knowledge_base/topics/topics.html'


class TopicDetailView(DetailViewWithViewsIncrement):
    model = Topic
    template_name = 'knowledge_base/topics/topic.html'


class PhrasebookCategoriesListView(CategoriesBaseListView):
    context_object_name = 'categories'
    model = PhrasesCategory
    template_name = 'knowledge_base/phrasebook/categories.html'


class PhrasesArticlesListView(ArticlesBaseListView):
    context_object_name = 'articles'
    model = PhrasesArticle
    category_model = PhrasesCategory
    template_name = 'knowledge_base/phrasebook/phrases_articles.html'


class PhrasesArticleDetailView(DetailViewWithViewsIncrement):
    context_object_name = 'phrases_article'
    model = PhrasesArticle
    template_name = 'knowledge_base/phrasebook/phrases_article.html'


class ArticleCategoriesListView(CategoriesBaseListView):
    context_object_name = 'categories'
    model = ArticleCategory
    template_name = 'knowledge_base/articles/categories.html'


class ArticlesListView(ArticlesBaseListView):
    context_object_name = 'articles'
    category_model = ArticleCategory
    template_name = 'knowledge_base/articles/articles.html'


class ArticleDetailView(DetailViewWithViewsIncrement):
    template_name = 'knowledge_base/articles/article.html'


class QuizCategoriesListView(CategoriesBaseListView):
    context_object_name = 'categories'
    model = QuizCategory
    template_name = 'knowledge_base/quizzes/categories.html'


class QuizzesListView(ArticlesBaseListView):
    model = Quiz
    category_model = QuizCategory
    context_object_name = 'quizzes'
    template_name = 'knowledge_base/quizzes/quizzes.html'


class QuizDetailView(DetailView):
    model = Quiz
    context_object_name = 'quiz_data'
    template_name = 'knowledge_base/quizzes/quiz.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = {}
        slug = self.kwargs.get(self.slug_url_kwarg)

        if slug:
            try:
                self.object = self.model.get_quiz_article_data(slug)
                context[self.context_object_name] = self.object

            except self.model.DoesNotExist:
                raise Http404(
                    _("No %(verbose_name)s found matching the query") % {"verbose_name": self.model._meta.verbose_name})

        else:
            raise AttributeError(
                "Generic detail view %s must be called with either an object "
                "pk or a slug in the URLconf." % self.__class__.__name__
            )
        context.update(kwargs)
        return super().get_context_data(**context)
