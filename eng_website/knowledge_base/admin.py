from django.contrib import admin

from knowledge_base.models import Category, TopicCategory, HandbookCategory, PhrasesCategory, ArticleCategory, \
    QuizCategory, \
    Article, Topic, PhrasesArticle, Lesson, Quiz,Question,Answer


class CategoryAdminBase(admin.ModelAdmin):
    type = None

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs.filter(type=self.type)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs['queryset'] = Category.objects.filter(type=self.type)

        return super(CategoryAdminBase, self).formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == 'type':
            if "choices" not in kwargs:
                kwargs["choices"] = filter(lambda choice: choice[0] == self.type, Category.TYPE_CHOICES)
        return db_field.formfield(**kwargs)


@admin.register(TopicCategory)
class TopicCategoryAdmin(CategoryAdminBase):
    type = Category.TOPIC


@admin.register(HandbookCategory)
class HandbookCategoryAdmin(CategoryAdminBase):
    type = Category.HANDBOOK


@admin.register(PhrasesCategory)
class PhrasebookCategoryAdmin(CategoryAdminBase):
    type = Category.PHRASEBOOK


@admin.register(ArticleCategory)
class ArticleCategoryAdmin(CategoryAdminBase):
    type = Category.ARTICLE


@admin.register(QuizCategory)
class QuizCategoryAdmin(CategoryAdminBase):
    type = Category.QUIZ


class ArticleTypedAdminBase(admin.ModelAdmin):
    type = None

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs.filter(category__type=self.type)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            kwargs['queryset'] = Category.objects.filter(type=self.type)

        if db_field.name == "parent":
            kwargs['queryset'] = Article.objects.filter(category__type=self.type)

        return super(ArticleTypedAdminBase, self).formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Topic)
class TopicArticleAdmin(ArticleTypedAdminBase):
    type = Category.TOPIC


@admin.register(Lesson)
class HandbookArticleAdmin(ArticleTypedAdminBase):
    type = Category.HANDBOOK


@admin.register(PhrasesArticle)
class PhrasebookArticleAdmin(ArticleTypedAdminBase):
    type = Category.PHRASEBOOK


@admin.register(Article)
class ArticleAdmin(ArticleTypedAdminBase):
    type = Category.ARTICLE


@admin.register(Quiz)
class QuizAdmin(ArticleTypedAdminBase):
    type = Category.QUIZ

admin.site.register(Question)
admin.site.register(Answer)
