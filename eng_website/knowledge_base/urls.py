from django.urls import path

from .views import (IndexView, HandbookTopicsListView, LessonDetailView, TopicsCategoriesListView,
                    TopicsListView, TopicDetailView, PhrasebookCategoriesListView, PhrasesArticlesListView,
                    PhrasesArticleDetailView, ArticleCategoriesListView, ArticlesListView, ArticleDetailView,
                    QuizCategoriesListView, QuizzesListView, QuizDetailView)

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('handbook/', HandbookTopicsListView.as_view(), name='handbook'),
    path('handbook/<slug:slug>/', LessonDetailView.as_view(), name='lesson'),
    path('topics/', TopicsCategoriesListView.as_view(), name='topics-categories'),
    path('topics/<slug:slug>/', TopicsListView.as_view(), name='topics'),
    path('topics/<slug:category_slug>/<slug:slug>', TopicDetailView.as_view(), name='topic'),
    path('phrasebook/', PhrasebookCategoriesListView.as_view(), name='phrasebook-categories'),
    path('phrasebook/<slug:slug>/', PhrasesArticlesListView.as_view(), name='phrasebook-category'),
    path('phrasebook/<slug:category_slug>/<slug:slug>', PhrasesArticleDetailView.as_view(), name='phrase-article'),
    path('articles/', ArticleCategoriesListView.as_view(), name='articles-categories'),
    path('articles/<slug:slug>/', ArticlesListView.as_view(), name='articles-category'),
    path('articles/<slug:category_slug>/<slug:slug>', ArticleDetailView.as_view(), name='article'),
    path('quizzes/', QuizCategoriesListView.as_view(), name='quizzes-categories'),
    path('quizzes/<slug:slug>/', QuizzesListView.as_view(), name='quizzes-category'),
    path('quizzes/<slug:category_slug>/<slug:slug>', QuizDetailView.as_view(), name='quiz'),
]
